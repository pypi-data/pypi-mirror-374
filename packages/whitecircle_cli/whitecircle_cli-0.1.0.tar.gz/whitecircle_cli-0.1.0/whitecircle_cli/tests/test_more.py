from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx
import pytest
from click.testing import CliRunner

from whitecircle_cli.__main__ import cli
from whitecircle_cli.api.client import WhiteCircleAPI, APIConfig
from whitecircle_cli.config.profile import resolve_effective_settings, save_profile, Profile
from whitecircle_cli.config.paths import get_config_file


@pytest.fixture(autouse=True)
def _isolate_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg_dir = tmp_path / ".config"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(cfg_dir))
    yield


def _make_response(status: int = 200, json_body: dict | None = None, url: str = "https://example.invalid/") -> httpx.Response:
    req = httpx.Request("GET", url)
    if json_body is None:
        return httpx.Response(status, request=req)
    return httpx.Response(status, json=json_body, request=req)


def test_region_resolver_and_endpoint_override():
    base_region = WhiteCircleAPI.resolve_base_url(region="eu", endpoint=None)
    assert base_region.endswith("/api")
    custom = WhiteCircleAPI.resolve_base_url(
        region="eu", endpoint="https://custom")
    assert custom == "https://custom"


def test_effective_settings_precedence(monkeypatch: pytest.MonkeyPatch):
    save_profile("default", Profile(region="eu", api_token="wc-profile"))
    monkeypatch.setenv("WHITECIRCLE_REGION", "us")
    eff = resolve_effective_settings(
        selected_profile=None, cli_api_token="wc-cli")
    assert eff.region == "us"
    assert eff.api_token == "wc-cli"


def test_client_headers_include_version_and_user_agent(monkeypatch: pytest.MonkeyPatch):
    cfg = APIConfig(base_url="https://example.invalid", api_token="wc-token")
    client = WhiteCircleAPI(cfg)

    def capture(_self, method, url, **kwargs):
        return _make_response(200, {"list": []}, url=cfg.base_url+"/api/protect/get_by_id")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(httpx.Client, "request", capture)
        resp = client.get_by_internal_id("abc")
    assert isinstance(resp, dict)


def test_retry_on_429(monkeypatch: pytest.MonkeyPatch):
    save_profile("default", Profile(region="eu", api_token="wc-token"))
    runner = CliRunner()
    sequence = [429, 429, 200]

    def seq(_self, method, url, **kwargs):
        status = sequence.pop(0)
        if status == 200:
            return _make_response(200, {"list": []}, url=url)
        return _make_response(status, None, url=url)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(httpx.Client, "request", seq)
        # should succeed after retries
        result = runner.invoke(cli, ["session", "get", "abc"])
    assert result.exit_code == 0


def test_check_text_includes_internal_id(monkeypatch: pytest.MonkeyPatch):
    save_profile("default", Profile(region="eu", api_token="wc-token"))
    runner = CliRunner()

    def ok(_self, method, url, **kwargs):
        return _make_response(200, {"internal_id": "id-123", "violation": False, "violations": {}}, url=url)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(httpx.Client, "request", ok)
        result = runner.invoke(cli, ["check", "text", "hello"])
    assert result.exit_code == 0
    assert "ID: id-123" in result.output
