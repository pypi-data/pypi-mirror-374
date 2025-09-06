from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from .. import __version__


logger = logging.getLogger(__name__)

REGION_BASE_URLS: dict[str, str] = {
    "eu": "https://eu.whitecircle.ai/api",
    "us": "https://us.whitecircle.ai/api",
}

API_VERSION_HEADER = "whitecircle-version"
API_VERSION_VALUE = "2025-06-15"

DEFAULT_TIMEOUT = httpx.Timeout(10.0, read=30.0)


@dataclass
class APIConfig:
    base_url: str
    api_token: str


class WhiteCircleAPI:
    def __init__(self, config: APIConfig, *, client: Optional[httpx.Client] = None) -> None:
        self.config = config
        self._client = client or httpx.Client(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_token}",
                "User-Agent": f"wcircle/{__version__}",
                API_VERSION_HEADER: API_VERSION_VALUE,
            },
            timeout=DEFAULT_TIMEOUT,
        )

    @staticmethod
    def resolve_base_url(*, region: str, endpoint: Optional[str]) -> str:
        if endpoint:
            return endpoint
        if region not in REGION_BASE_URLS:
            raise ValueError(
                f"Unknown region '{region}'. Expected one of: {', '.join(sorted(REGION_BASE_URLS))}")
        return REGION_BASE_URLS[region]

    def _request_with_retries(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        backoff_base: float = 0.5,
    ) -> httpx.Response:
        attempt = 0
        last_exc: Optional[Exception] = None
        while attempt <= max_retries:
            try:
                response = self._client.request(
                    method, url, params=params, json=json_body)
                if response.status_code in (429, 500, 502, 503, 504):
                    if attempt == max_retries:
                        return response
                    delay = backoff_base * (2 ** attempt)
                    logger.warning(
                        "Transient error %s, retrying in %.1fs", response.status_code, delay)
                    time.sleep(delay)
                    attempt += 1
                    continue
                return response
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as exc:
                last_exc = exc
                if attempt == max_retries:
                    raise
                delay = backoff_base * (2 ** attempt)
                logger.warning("Network error %s, retrying in %.1fs",
                               type(exc).__name__, delay)
                time.sleep(delay)
                attempt += 1
        assert last_exc is not None
        raise last_exc

    def check_text(self, message: str, policies: Optional[list[str]] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "messages": [
                {"role": "user", "content": message},
            ]
        }
        if policies is not None:
            body["policies"] = policies
        resp = self._request_with_retries(
            "POST", "/protect/check", json_body=body)
        resp.raise_for_status()
        return resp.json()

    def get_by_internal_id(self, internal_id: str) -> Dict[str, Any]:
        params = {"internal_id": internal_id}
        resp = self._request_with_retries(
            "GET", "/protect/get_by_id", params=params)
        resp.raise_for_status()
        return resp.json()
