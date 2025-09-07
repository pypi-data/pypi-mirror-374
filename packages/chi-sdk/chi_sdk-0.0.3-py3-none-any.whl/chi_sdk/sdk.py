from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, get_origin, get_args
import json
import os
import importlib.metadata as importlib_metadata

import click
from pydantic import BaseModel, ValidationError

from .models import Envelope, ErrorPayload


@dataclass
class CommandSpec:
    name: str
    func: Callable[..., Any]
    input_model: Optional[Type[BaseModel]]
    output_model: Optional[Type[BaseModel]]
    description: str


_REGISTRY: Dict[str, CommandSpec] = {}


def chi_command(
    name: Optional[str] = None,
    *,
    input_model: Optional[Type[BaseModel]] = None,
    output_model: Optional[Type[BaseModel]] = None,
    description: str = "",
):
    """Decorator to register a CLI command with typed I/O."""

    def _wrap(func: Callable[..., Any]):
        cmd_name = name or func.__name__.replace("_", "-")
        if cmd_name in _REGISTRY:
            raise RuntimeError(f"Command already registered: {cmd_name}")
        _REGISTRY[cmd_name] = CommandSpec(
            name=cmd_name,
            func=func,
            input_model=input_model,
            output_model=output_model,
            description=description.strip(),
        )
        return func

    return _wrap


def _json_mode(ctx: Optional[click.Context] = None) -> bool:
    ctx = ctx or click.get_current_context(silent=True)
    env = os.getenv("CHI_TUI_JSON", "")
    return bool(
        (ctx and ctx.obj and ctx.obj.get("json")) or env in ("1", "true", "yes")
    )


def emit_ok(
    data: Any, *, command: Optional[str] = None, meta: Optional[Dict[str, Any]] = None
):
    env = Envelope(ok=True, type="result", data=data, command=command, meta=meta or {})
    click.echo(env.model_dump_json())


def emit_error(
    code: str,
    message: str,
    *,
    command: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    exit_code: int = 1,
):
    payload = ErrorPayload(code=code, message=message, details=details)
    env = Envelope(ok=False, type="error", data=payload.model_dump(), command=command)
    click.echo(env.model_dump_json(), err=True)
    raise click.exceptions.Exit(exit_code)


def emit_progress(
    message: Optional[str] = None,
    *,
    percent: Optional[float] = None,
    stage: Optional[str] = None,
    command: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
):
    """Emit a progress event as a JSON envelope (NDJSON-friendly).

    - Use alongside long-running commands to stream updates.
    - `message` is a short human-readable status.
    - `percent` in [0,100].
    - `stage` optional label for current phase.
    - `extra` for arbitrary additional fields.
    """
    payload: Dict[str, Any] = {}
    if message is not None:
        payload["message"] = message
    if percent is not None:
        try:
            payload["percent"] = float(percent)
        except Exception:
            payload["percent"] = percent
    if stage is not None:
        payload["stage"] = stage
    if extra:
        payload.update(extra)

    env = Envelope(ok=True, type="progress", data=payload, command=command)
    click.echo(env.model_dump_json())


def _pyd_type_to_click(name: str, field) -> click.Parameter:
    """Map basic Pydantic v2 field to a Click option.

    Supports: bool, int, float, str, Optional[T], List[T] (T in {int,float,str}).
    Falls back to JSON string for complex types.
    """

    # Always derive flag name from the actual field key
    let_name = name.replace("_", "-")
    opt = f"--{let_name}"
    ann = field.annotation
    origin = get_origin(ann)

    if ann is bool:
        return click.Option([opt], is_flag=True, help=field.description or "")
    if ann is int:
        return click.Option(
            [opt],
            type=click.INT,
            required=field.is_required(),
            default=field.default,
            help=field.description or "",
        )
    if ann is float:
        return click.Option(
            [opt],
            type=click.FLOAT,
            required=field.is_required(),
            default=field.default,
            help=field.description or "",
        )
    if ann is str:
        return click.Option(
            [opt],
            type=click.STRING,
            required=field.is_required(),
            default=field.default,
            help=field.description or "",
        )

    # Optional[T]
    if origin is Optional or origin is type(Optional):
        inner = get_args(ann)[0]
        if inner is bool:
            return click.Option([opt], is_flag=True, help=field.description or "")
        ctype: click.ParamType = click.STRING
        if inner is int:
            ctype = click.INT
        elif inner is float:
            ctype = click.FLOAT
        return click.Option(
            [opt],
            type=ctype,
            required=False,
            default=field.default,
            help=field.description or "",
        )

    # List[T]
    if origin in (list, List):
        inner = get_args(ann)[0] if get_args(ann) else str
        ctype_list: click.ParamType
        if inner is int:
            ctype_list = click.INT
        elif inner is float:
            ctype_list = click.FLOAT
        else:
            ctype_list = click.STRING
        return click.Option(
            [opt],
            type=ctype_list,
            multiple=True,
            required=field.is_required(),
            default=(),
            help=field.description or "",
        )

    # Fallback: JSON string for complex types
    help_text = (field.description or "") + " (JSON)"
    return click.Option(
        [opt],
        type=click.STRING,
        required=field.is_required(),
        default=field.default,
        help=help_text,
    )


def _build_click_command(spec: CommandSpec) -> click.Command:
    params: List[click.Parameter] = []

    if spec.input_model:
        for name, field in spec.input_model.model_fields.items():
            opt = _pyd_type_to_click(name, field)
            params.append(opt)

    def _callback(**kwargs):
        ctx = click.get_current_context()
        try:
            if spec.input_model:
                # Convert JSON-like strings to objects when applicable
                for k, v in list(kwargs.items()):
                    if isinstance(v, str) and (
                        v.strip().startswith("{") or v.strip().startswith("[")
                    ):
                        try:
                            kwargs[k] = json.loads(v)
                        except Exception:
                            pass
                input_obj = spec.input_model(**kwargs)
            else:
                input_obj = None

            result = spec.func(input_obj) if input_obj is not None else spec.func()
            if spec.output_model:
                data = spec.output_model.model_validate(result).model_dump()
            else:
                data = result

            if _json_mode(ctx):
                emit_ok(data, command=spec.name)
            else:
                click.echo(
                    data
                    if isinstance(data, str)
                    else json.dumps(data, indent=2, ensure_ascii=False)
                )
        except ValidationError as ve:
            emit_error(
                "validation_error",
                "Invalid input/output payload",
                command=spec.name,
                details={"errors": ve.errors()},
            )
        except click.ClickException as ce:
            emit_error("cli_error", str(ce), command=spec.name)
        except Exception as e:
            emit_error("runtime_error", str(e), command=spec.name)

    return click.Command(
        name=spec.name, params=params, callback=_callback, help=spec.description or None
    )


def _dist_version(dist_name: str) -> Optional[str]:
    try:
        return str(importlib_metadata.version(dist_name))
    except Exception:
        return None


def build_cli(
    app_name: str = "chi",
    *,
    app_version: Optional[str] = None,
    app_dist: Optional[str] = None,
) -> click.Group:
    """Build a Click CLI group for registered commands.

    - `app_name`: logical application name shown in help.
    - `app_version`: explicit version string (optional).
    - `app_dist`: Python distribution name to resolve version from metadata (defaults to `app_name`).
    """
    resolved_app_version = (
        app_version or _dist_version(app_dist or app_name) or "0.0.0.dev"
    )
    sdk_version = _dist_version("chi-sdk") or "0.0.0.dev"

    @click.group(
        help=f"{app_name} — CHI TUI CLI (Python source of truth)",
        invoke_without_command=True,
    )
    @click.option(
        "--json", "json_mode", is_flag=True, help="Emit JSON envelope to stdout"
    )
    @click.option(
        "--version", "show_version", is_flag=True, help="Show version and exit"
    )
    @click.pass_context
    def cli(ctx, json_mode: bool, show_version: bool):
        ctx.ensure_object(dict)
        ctx.obj["json"] = json_mode
        if show_version:
            # honor JSON mode
            if _json_mode(ctx):
                emit_ok(
                    {
                        "app": app_name,
                        "version": resolved_app_version,
                        "sdk": {"name": "chi-sdk", "version": sdk_version},
                    },
                    command="version",
                )
            else:
                click.echo(f"{app_name} {resolved_app_version} (chi-sdk {sdk_version})")
            raise click.exceptions.Exit(0)

    @cli.command("schema", help="Emit JSON Schema for all commands")
    @click.pass_context
    def schema_cmd(ctx):
        cmds = []
        for spec in _REGISTRY.values():
            cmds.append(
                {
                    "name": spec.name,
                    "description": spec.description,
                    "input_schema": (
                        spec.input_model.model_json_schema()
                        if spec.input_model
                        else None
                    ),
                    "output_schema": (
                        spec.output_model.model_json_schema()
                        if spec.output_model
                        else None
                    ),
                }
            )
        payload = {"app": app_name, "version": "1.0", "commands": cmds}
        if _json_mode(ctx):
            emit_ok(payload, command="schema")
        else:
            click.echo(json.dumps(payload, indent=2, ensure_ascii=False))

    for spec in _REGISTRY.values():
        cli.add_command(_build_click_command(spec))

    return cli
