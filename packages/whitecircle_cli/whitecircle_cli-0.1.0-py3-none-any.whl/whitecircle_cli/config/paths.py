from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "wcircle"


def get_config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        base = Path(xdg)
    else:
        base = Path.home() / ".config"
    return base / APP_NAME


def get_config_file() -> Path:
    return get_config_dir() / "config.json"
