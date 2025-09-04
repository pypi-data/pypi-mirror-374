from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
from click.testing import CliRunner

from whitecircle_cli.__main__ import cli
from whitecircle_cli.config.paths import get_config_file


@pytest.fixture(autouse=True)
def _isolate_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg_dir = tmp_path / ".config"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(cfg_dir))
    yield


def write_profile(region: str = "eu", token: str = "wc-abc123456") -> None:
    cfg_path = get_config_file()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(
        json.dumps(
            {"profiles": {"default": {"region": region, "api_token": token}}}),
        encoding="utf-8",
    )


def _make_response(status: int = 200, json_body: dict | None = None, url: str = "https://example.invalid/") -> httpx.Response:
    req = httpx.Request("GET", url)
    if json_body is None:
        return httpx.Response(status, request=req)
    return httpx.Response(status, json=json_body, request=req)


def test_setup_non_interactive_creates_profile():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "setup",
            "--non-interactive",
            "--region",
            "eu",
            "--api-token",
            "wc-xyz987654",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(get_config_file().read_text())
    assert data["profiles"]["default"]["api_token"].startswith("wc-")


def test_usage_error_exit_code_64_when_no_settings():
    runner = CliRunner()
    result = runner.invoke(cli, ["session", "get", "abc"])
    assert result.exit_code == 64


def test_precedence_env_over_profile(monkeypatch: pytest.MonkeyPatch):
    write_profile(region="eu", token="wc-profile")
    monkeypatch.setenv("WHITECIRCLE_REGION", "us")
    monkeypatch.setenv("WHITECIRCLE_API_TOKEN", "wc-env-token")

    def fake_get(_self, _method, _url, **_kwargs):
        return _make_response(200, {"list": []})

    runner = CliRunner()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(httpx.Client, "request", fake_get)
        result = runner.invoke(cli, ["session", "get", "abc"])
    assert result.exit_code == 0


def test_check_text_exit_codes():
    write_profile()

    def fake_post(_self, _method, _url, **_kwargs):
        return _make_response(200, {"violation": True, "violations": {}, "internal_id": "id"})

    runner = CliRunner()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(httpx.Client, "request", fake_post)
        result = runner.invoke(cli, ["check", "text", "hello"])
    assert result.exit_code == 2


@pytest.mark.parametrize("status,exit_code", [
    (400, 78), (401, 78), (403, 78), (404, 78), (429, 69), (500, 69)
])
def test_error_mapping(status: int, exit_code: int):
    write_profile()

    def fake_req(_self, _method, _url, **_kwargs):
        return _make_response(status)

    runner = CliRunner()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(httpx.Client, "request", fake_req)
        result = runner.invoke(cli, ["session", "get", "abc"])  # any command
    assert result.exit_code == exit_code


def test_json_output_flag():
    write_profile()

    def fake_get(_self, _method, _url, **_kwargs):
        return _make_response(200, {"list": [{"internal_id": "x", "violation": False, "violations": {}}]})

    runner = CliRunner()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(httpx.Client, "request", fake_get)
        result = runner.invoke(cli, ["session", "get", "abc", "--json"])
    assert result.exit_code == 0
    assert result.output.strip().startswith("{")
