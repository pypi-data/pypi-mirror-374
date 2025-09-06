"""Axur Platform HTTP client (stdlib only).

Covers all documented routes generically and common convenience wrappers
from https://docs.axur.com/en/axur/api/openapi-axur.yaml using urllib.

Features:
- Standard library only (urllib.request)
- Respects environment proxies (set by Worker/SDK)
- Injects Authorization: Bearer <token>
- Returns parsed JSON for JSON responses; text otherwise

Requirements: Python >= 3.13
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


def _merge_query(url: str, params: Mapping[str, Any] | None) -> str:
    if not params:
        return url
    parts = urllib.parse.urlsplit(url)
    current = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    extra = []
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, bool):
            v = str(v).lower()
        extra.append((k, str(v)))
    query = urllib.parse.urlencode(current + extra)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


@dataclass(frozen=True)
class AxurClient:
    """Minimal Axur HTTP client with generic and convenience methods.

    - Use ``call()`` to perform any HTTP method/path with optional query/body
    - Convenience wrappers implement the most common API operations
    """

    api_token: str
    base_url: str = "https://api.axur.com/gateway/1.0/api"
    timeout: float = 30.0
    user_agent: str = "sentineliqsdk-axur/1.0"

    # --- Core HTTP helpers ---
    def _request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        data: Mapping[str, Any] | bytes | None = None,
        json_body: Mapping[str, Any] | None = None,
        dry_run: bool = False,
    ) -> Any:
        url = self.base_url.rstrip("/") + ("/" + path.lstrip("/"))
        url = _merge_query(url, query)

        req_headers = {"User-Agent": self.user_agent, "Authorization": f"Bearer {self.api_token}"}
        if headers:
            req_headers.update(headers)

        body: bytes | None = None
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            req_headers.setdefault("Content-Type", "application/json")
        elif isinstance(data, (dict, tuple)):
            body = urllib.parse.urlencode(data).encode("utf-8")
            req_headers.setdefault(
                "Content-Type", "application/x-www-form-urlencoded; charset=utf-8"
            )
        elif isinstance(data, bytes):
            body = data

        # If dry-run, just return the request plan
        if dry_run:
            return {
                "dry_run": True,
                "method": method.upper(),
                "url": url,
                "headers": dict(req_headers),
                "body": (
                    json_body
                    if json_body is not None
                    else (data if isinstance(data, (dict, tuple)) else None)
                ),
            }

        req = urllib.request.Request(url=url, method=method.upper(), headers=req_headers, data=body)
        context = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=context) as resp:
                ctype = resp.headers.get("Content-Type", "application/json")
                raw = resp.read()
                if not raw:
                    return None
                if "json" in ctype:
                    try:
                        return json.loads(raw.decode("utf-8"))
                    except json.JSONDecodeError:
                        return raw.decode("utf-8", errors="replace")
                return raw.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            detail = None
            try:
                detail = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            if detail:
                raise urllib.error.HTTPError(e.url, e.code, detail, e.headers, None)
            raise

    # Public generic method
    def call(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        data: Mapping[str, Any] | bytes | None = None,
        json_body: Mapping[str, Any] | None = None,
        dry_run: bool = False,
    ) -> Any:
        return self._request(
            method=method,
            path=path,
            query=query,
            headers=headers,
            data=data,
            json_body=json_body,
            dry_run=dry_run,
        )

    # --- Convenience wrappers (selected) ---
    def customers(self) -> Any:
        return self._request("GET", "/customers/customers")

    def users(
        self,
        *,
        customers: str | None = None,
        accessToAreas: str | None = None,
        freeText: str | None = None,
        offset: int | None = None,
        pageSize: int | None = None,
    ) -> Any:
        return self._request(
            "GET",
            "/identity/users",
            query={
                "customers": customers,
                "accessToAreas": accessToAreas,
                "freeText": freeText,
                "offset": offset,
                "pageSize": pageSize,
            },
        )

    def users_stream(
        self,
        *,
        customers: str | None = None,
        accessToAreas: str | None = None,
        freeText: str | None = None,
        offset: int | None = None,
        pageSize: int | None = None,
    ) -> Any:
        return self._request(
            "GET",
            "/identity/users/stream",
            query={
                "customers": customers,
                "accessToAreas": accessToAreas,
                "freeText": freeText,
                "offset": offset,
                "pageSize": pageSize,
            },
        )

    def tickets_search(self, query_params: Mapping[str, Any]) -> Any:
        return self._request("GET", "/tickets-api/tickets", query=query_params)

    def ticket_create(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/tickets-api/tickets", json_body=payload)

    def tickets_by_keys(
        self, keys: str, *, timezone: str | None = None, include: str | None = None
    ) -> Any:
        return self._request(
            "GET",
            "/tickets-api/ticket",
            query={"keys": keys, "timezone": timezone, "include": include},
        )

    def filter_create(self, filter_body: Mapping[str, Any]) -> Any:
        return self._request("POST", "/tickets-filters/filters/tickets", json_body=filter_body)

    def filter_results(
        self,
        query_id: str,
        *,
        page: int | None = None,
        pageSize: int | None = None,
        sortBy: str | None = None,
        order: str | None = None,
    ) -> Any:
        return self._request(
            "GET",
            "/tickets-filters/filters/tickets",
            query={
                "q": query_id,
                "page": page,
                "pageSize": pageSize,
                "sortBy": sortBy,
                "order": order,
            },
        )

    def ticket_get(self, ticket_key: str) -> Any:
        return self._request("GET", f"/tickets-core/tickets/{urllib.parse.quote(ticket_key)}")

    def ticket_types(self) -> Any:
        return self._request("GET", "/tickets-core/fields/types")

    def ticket_texts(self, ticket_key: str) -> Any:
        return self._request(
            "GET", f"/tickets-texts/texts/tickets/{urllib.parse.quote(ticket_key)}"
        )

    def integration_feed(self, feed_id: str, *, dry_run_param: bool | None = None) -> Any:
        return self._request(
            "GET",
            f"/integration-feed/feeds/feed/{urllib.parse.quote(feed_id)}",
            query={"dry-run": dry_run_param} if dry_run_param is not None else None,
        )
