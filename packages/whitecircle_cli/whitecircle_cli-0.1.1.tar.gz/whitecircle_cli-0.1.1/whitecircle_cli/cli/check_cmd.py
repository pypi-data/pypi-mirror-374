from __future__ import annotations

import sys

import click
import httpx

from ..api.client import APIConfig, WhiteCircleAPI
from ..config.profile import resolve_effective_settings
from ..output import echo_json, human_check_output


@click.group("check")
def check_group() -> None:
    """Content policy checks."""


@check_group.command("text")
@click.argument("message", type=str)
@click.option("as_json", "--json", is_flag=True, help="Print JSON only")
@click.option("exit_code_on_violation", "--exit-code-on-violation", default=2, show_default=True, type=int)
@click.pass_context
def check_text(ctx: click.Context, message: str, as_json: bool, exit_code_on_violation: int) -> None:
    try:
        settings = resolve_effective_settings(
            selected_profile=ctx.obj.get("profile"))
    except ValueError as exc:
        click.echo(str(exc), err=True)
        sys.exit(64)

    base_url = WhiteCircleAPI.resolve_base_url(
        region=settings.region, endpoint=settings.endpoint)
    client = WhiteCircleAPI(
        APIConfig(base_url=base_url, api_token=settings.api_token))

    try:
        result = client.check_text(message)
    except httpx.HTTPStatusError as exc:
        _handle_http_error(exc.response)
        return
    except (httpx.TimeoutException, httpx.TransportError):
        click.echo("Service unavailable. Please try again later.", err=True)
        sys.exit(69)

    if as_json:
        echo_json(result)
    else:
        internal_id = result.get("internal_id")
        id_line = f"ID: {internal_id}" if internal_id else None
        text = human_check_output(result)
        if id_line:
            text = f"{id_line}\n{text}"
        click.echo(text)

    if isinstance(result, dict) and bool(result.get("violation")):
        sys.exit(exit_code_on_violation)


def _handle_http_error(resp: httpx.Response) -> None:
    code = resp.status_code
    if code == 400:
        click.echo("Bad request.", err=True)
        sys.exit(78)
    if code in (401, 403):
        click.echo("Unauthorized or forbidden. Check your API token.", err=True)
        sys.exit(78)
    if code == 404:
        click.echo("Not found.", err=True)
        sys.exit(78)
    if code in (429, 500, 502, 503, 504):
        click.echo("Service unavailable. Please try again later.", err=True)
        sys.exit(69)
    click.echo("Unexpected error occurred.", err=True)
    sys.exit(69)
