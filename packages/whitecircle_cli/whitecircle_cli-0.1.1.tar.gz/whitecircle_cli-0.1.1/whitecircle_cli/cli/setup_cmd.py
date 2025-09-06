from __future__ import annotations

import click

from whitecircle_cli.config.profile import (
    DEFAULT_PROFILE_NAME,
    Profile,
    save_profile,
)


@click.command("setup")
@click.option("profile_name", "--profile", default=DEFAULT_PROFILE_NAME, show_default=True)
@click.option("region", "--region", type=click.Choice(["eu", "us"]))
@click.option("api_token", "--api-token", type=str)
@click.option("endpoint", "--endpoint", type=str)
@click.option("non_interactive", "--non-interactive", is_flag=True, help="Disable prompts")
def setup_cmd(
    profile_name: str,
    region: str | None,
    api_token: str | None,
    endpoint: str | None,
    non_interactive: bool,
) -> None:
    """Create or update a profile."""
    if not non_interactive:
        if not region:
            region = click.prompt("Region", type=click.Choice(["eu", "us"]))
        if not api_token:
            api_token = click.prompt("API Token", type=str, hide_input=True)
        if endpoint is None:
            endpoint = click.prompt(
                "Custom endpoint (leave blank for region)", default="", show_default=False)
            endpoint = endpoint or None

    if not region or not api_token:
        raise click.UsageError(
            "--region and --api-token are required in non-interactive mode")

    profile = Profile(region=region, api_token=api_token, endpoint=endpoint)
    save_profile(profile_name, profile)
    click.echo(f"Saved profile '{profile_name}'.")
