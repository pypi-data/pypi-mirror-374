from __future__ import annotations

from typing import Dict, List, Optional, TypedDict


class PolicyStatus(TypedDict, total=False):
    name: Optional[str]
    violation: bool
    violation_source: List[str]


class CheckResponse(TypedDict):
    external_id: Optional[str]
    internal_id: str
    violation: bool
    violations: Dict[str, PolicyStatus]


class GetByIdResponse(TypedDict):
    list: List[CheckResponse]
