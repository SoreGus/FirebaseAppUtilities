from __future__ import annotations

from typing import Any

import requests


class FunctionsService:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url.rstrip("/") if base_url else None

    def url(self, function_name: str) -> str:
        if not self.base_url:
            raise RuntimeError("Functions base_url is not configured")
        return f"{self.base_url}/{function_name.lstrip('/')}"

    def request(
        self,
        function_name: str,
        *,
        method: str = "POST",
        json: dict[str, Any] | None = None,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        response = requests.request(
            method=method.upper(),
            url=self.url(function_name),
            json=json,
            timeout=timeout,
            headers=headers,
        )
        response.raise_for_status()
        return response
