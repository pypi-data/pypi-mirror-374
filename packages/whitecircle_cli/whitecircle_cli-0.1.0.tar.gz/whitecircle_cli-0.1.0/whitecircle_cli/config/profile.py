from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional

from .paths import get_config_file


ENV_PROFILE = "WHITECIRCLE_PROFILE"
ENV_REGION = "WHITECIRCLE_REGION"
ENV_API_TOKEN = "WHITECIRCLE_API_TOKEN"
ENV_ENDPOINT = "WHITECIRCLE_ENDPOINT"

DEFAULT_PROFILE_NAME = "default"


@dataclass
class Profile:
    region: str
    api_token: str
    endpoint: Optional[str] = None


def _read_config_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"profiles": {}}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed config file at {path}") from exc


def _atomic_write(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as tf:
        json.dump(data, tf, ensure_ascii=False, indent=2)
        tf.flush()
        os.fsync(tf.fileno())
        tmp_name = tf.name
    os.replace(tmp_name, path)


def save_profile(name: str, profile: Profile) -> None:
    path = get_config_file()
    cfg = _read_config_file(path)
    profiles = cfg.get("profiles", {})
    profiles[name] = asdict(profile)
    cfg["profiles"] = profiles
    _atomic_write(path, cfg)


def load_profile(name: str) -> Optional[Profile]:
    cfg = _read_config_file(get_config_file())
    raw = cfg.get("profiles", {}).get(name)
    if not raw:
        return None
    return Profile(**raw)


def list_profiles() -> Dict[str, Profile]:
    cfg = _read_config_file(get_config_file())
    result: Dict[str, Profile] = {}
    for name, raw in cfg.get("profiles", {}).items():
        result[name] = Profile(**raw)
    return result


@dataclass
class EffectiveSettings:
    region: str
    api_token: str
    endpoint: Optional[str]
    profile_name: str


def resolve_effective_settings(
    *,
    selected_profile: Optional[str],
    cli_region: Optional[str] = None,
    cli_api_token: Optional[str] = None,
    cli_endpoint: Optional[str] = None,
) -> EffectiveSettings:
    profile_name = (
        (selected_profile or os.environ.get(ENV_PROFILE)) or DEFAULT_PROFILE_NAME
    )

    saved = load_profile(profile_name)

    region = (
        cli_region
        or os.environ.get(ENV_REGION)
        or (saved.region if saved else None)
    )
    api_token = (
        cli_api_token
        or os.environ.get(ENV_API_TOKEN)
        or (saved.api_token if saved else None)
    )
    endpoint = (
        cli_endpoint
        or os.environ.get(ENV_ENDPOINT)
        or (saved.endpoint if saved else None)
    )

    if not region:
        raise ValueError(
            "Region is not configured. Use --region or set WHITECIRCLE_REGION or run 'wcircle setup'.")
    if not api_token:
        raise ValueError(
            "API token is not configured. Use --api-token or set WHITECIRCLE_API_TOKEN or run 'wcircle setup'.")

    return EffectiveSettings(
        region=region,
        api_token=api_token,
        endpoint=endpoint,
        profile_name=profile_name,
    )
