from __future__ import annotations

import json
import sys
from typing import Any, Dict


def echo_json(data: Any) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stdout.flush()


def human_check_output(result: Dict[str, Any]) -> str:
    status = "VIOLATIONS FOUND" if result.get("violation") else "No violations"
    lines = [status]
    violations = result.get("violations") or {}
    for policy_id, detail in violations.items():
        v = detail.get("violation")
        mark = "✗" if v else "✓"
        name = detail.get("name") or policy_id
        src = ",".join(detail.get("violation_source") or [])
        extra = f" [{src}]" if src else ""
        lines.append(f"  {mark} {name}{extra}")
    return "\n".join(lines)


def human_get_output(result: Dict[str, Any]) -> str:
    items = result.get("list") or []
    lines = [f"Results: {len(items)}"]
    for item in items:
        internal_id = item.get("internal_id")
        status = "violation" if item.get("violation") else "ok"
        lines.append(f"- {internal_id}: {status}")
    return "\n".join(lines)
