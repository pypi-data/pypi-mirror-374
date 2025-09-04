from __future__ import annotations

import sys

import click
import httpx

from ..api.client import APIConfig, WhiteCircleAPI
from ..config.profile import resolve_effective_settings
from ..output import echo_json, human_get_output


@click.group("session")
def session_group() -> None:
    """Session-related operations."""


@session_group.command("get")
@click.argument("session_id", type=str)
@click.option("as_json", "--json", is_flag=True, help="Print JSON only")
@click.pass_context
def session_get(ctx: click.Context, session_id: str, as_json: bool) -> None:
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
        result = client.get_by_internal_id(session_id)
    except httpx.HTTPStatusError as exc:
        _handle_http_error(exc.response)
        return
    except (httpx.TimeoutException, httpx.TransportError):
        click.echo("Service unavailable. Please try again later.", err=True)
        sys.exit(69)

    if as_json:
        echo_json(result)
    else:
        click.echo(human_get_output(result))


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
