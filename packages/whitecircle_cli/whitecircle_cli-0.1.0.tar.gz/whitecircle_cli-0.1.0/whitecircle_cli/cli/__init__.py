from __future__ import annotations

import click

from ..logging_utils import setup_logging
from ..config.profile import DEFAULT_PROFILE_NAME
from .setup_cmd import setup_cmd
from .session_cmd import session_group
from .check_cmd import check_group


@click.group()
@click.option("--profile", default=None, help=f"Profile name (default: {DEFAULT_PROFILE_NAME})")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR",
                      "CRITICAL"], case_sensitive=False),
    default="INFO",
    show_default=True,
)
@click.pass_context
def cli(ctx: click.Context, profile: str | None, log_level: str) -> None:
    """White Circle CLI."""
    setup_logging(log_level)
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile


cli.add_command(setup_cmd)
cli.add_command(session_group)
cli.add_command(check_group)
