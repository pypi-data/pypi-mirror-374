from __future__ import annotations

import logging
import os
import re
import sys
from typing import Iterable


REDACTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"wc-[A-Za-z0-9]{6,}")
]


class RedactingFilter(logging.Filter):
    """Filter that redacts secrets in log records."""

    def __init__(self, patterns: Iterable[re.Pattern[str]] | None = None) -> None:
        super().__init__()
        self.patterns = list(patterns) if patterns else REDACTION_PATTERNS

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003 - name required by API
        # Format first to incorporate args, then redact and clear args to avoid re-formatting.
        formatted = record.getMessage()
        for pattern in self.patterns:
            formatted = pattern.sub("***REDACTED***", formatted)
        record.msg = formatted
        record.args = ()
        return True


def setup_logging(level: str) -> None:
    """Configure application logging.

    Logs go to stderr. Secrets are redacted.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(numeric_level)

    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(numeric_level)
    handler.addFilter(RedactingFilter())

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    if os.environ.get("NO_COLOR"):
        os.environ["CLICOLOR"] = "0"
