# White Circle CLI (wcircle)

White Circle CLI is a thin wrapper over the White Circle API.

- Requires Python 3.13.7+
- Binary: `wcircle`
- Package: `whitecircle_cli`

## Features

- Profiles with XDG config: `${XDG_CONFIG_HOME:-~/.config}/wcircle/config.json`
- Env/flag precedence: CLI > env > saved profile
- Regions and endpoint override
- Auth via Bearer API key; `User-Agent: wcircle/<version>` and required API version header
- Robust HTTP client: timeouts, retries/backoff for 429/5xx, proxy support via env
- Output modes: human-readable (default) or `--json`
- Commands:
  - `wcircle setup` — create/update profile; interactive prompts or `--non-interactive`
  - `wcircle session get <session_id>` — fetch a session by internal id
  - `wcircle check text "<message>"` — check text against all policies; prints `internal_id` and summary
- Exit codes:
  - 0 success; for check: no violations
  - 2 violations found (configurable)
  - 64 invalid usage/config
  - 69 service unavailable (network/5xx)
  - 78 bad data (malformed request/response)

## Install

From source:

```bash
uv sync --dev
```

## Usage

```bash
wcircle --help
```

Environment variables:
- `WHITECIRCLE_PROFILE`
- `WHITECIRCLE_REGION`
- `WHITECIRCLE_API_TOKEN`
- `WHITECIRCLE_ENDPOINT`
