"""Axur Analyzer: dynamic wrapper around AxurClient to call API routes.

Usage example (programmatic):

    from sentineliqsdk import WorkerInput
    from sentineliqsdk.analyzers.axur import AxurAnalyzer

    payload = {"method": "customers", "params": {}}
    input_data = WorkerInput(data_type="other", data=json.dumps(payload))
    report = AxurAnalyzer(input_data).execute()

Configuration:
- Provide API token via environment variable `AXUR_API_TOKEN`.
- HTTP proxies honored via `WorkerConfig.proxy` or environment.
- For generic/raw calls, use method "call" with params: {"http_method", "path",
  "query"?, "json"?, "data"?, "headers"?, "dry_run"?}
"""

from __future__ import annotations

import json
import urllib.error
from collections.abc import Mapping
from typing import Any

from sentineliqsdk.analyzers.base import Analyzer
from sentineliqsdk.clients.axur import AxurClient
from sentineliqsdk.models import AnalyzerReport

# Allowlist of AxurClient methods exposed for dynamic calls
ALLOWED_METHODS: set[str] = {
    # Generic
    "call",
    # Convenience wrappers
    "customers",
    "users",
    "users_stream",
    "tickets_search",
    "ticket_create",
    "tickets_by_keys",
    "filter_create",
    "filter_results",
    "ticket_get",
    "ticket_types",
    "ticket_texts",
    "integration_feed",
}


class AxurAnalyzer(Analyzer):
    """Analyzer that calls Axur Platform API endpoints programmatically."""

    def _client(self) -> AxurClient:
        token = self.get_env("AXUR_API_TOKEN", message="Missing AXUR_API_TOKEN in environment.")
        return AxurClient(api_token=token)

    def _call_dynamic(self, method: str, params: Mapping[str, Any] | None = None) -> Any:
        client = self._client()
        if method not in ALLOWED_METHODS:
            self.error(f"Unsupported Axur method: {method}")
        if params is not None and not isinstance(params, Mapping):
            self.error("Axur params must be a mapping object (JSON object).")
        kwargs = dict(params or {})
        try:
            if method == "call":
                http_method = str(kwargs.pop("http_method", kwargs.pop("method", "GET")))
                path = kwargs.pop("path", None)
                if not path or not isinstance(path, str):
                    self.error("For method 'call', 'path' (string) is required in params.")
                query = kwargs.pop("query", None)
                headers = kwargs.pop("headers", None)
                data = kwargs.pop("data", None)
                json_body = kwargs.pop("json", None)
                dry_run = bool(kwargs.pop("dry_run", False))
                # Any remaining kwargs are ignored; only documented keys used
                return client.call(
                    http_method,
                    path,
                    query=query if isinstance(query, Mapping) else None,
                    headers=headers if isinstance(headers, Mapping) else None,
                    data=data,
                    json_body=json_body if isinstance(json_body, Mapping) else None,
                    dry_run=dry_run,
                )

            func = getattr(client, method)
            return func(**kwargs)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            self.error(f"Axur API call failed: {e}")

    def execute(self) -> AnalyzerReport:
        """Execute analysis via dynamic API call.

        Supported invocation styles:
        - Environment variables:
            AXUR_METHOD and optional AXUR_PARAMS (JSON object)
        - Dataclass input with data_type == "other" and data as JSON string
            {"method": "...", "params": { ... }}
        """
        observable = self.get_data()

        # 1) Dynamic call via environment variables
        env_method = self.get_env("AXUR_METHOD")
        if env_method:
            params: dict[str, Any] = {}
            env_params = self.get_env("AXUR_PARAMS")
            if env_params:
                try:
                    parsed = json.loads(env_params)
                except json.JSONDecodeError:
                    self.error("Invalid AXUR_PARAMS (must be valid JSON).")
                if not isinstance(parsed, Mapping):
                    self.error("AXUR_PARAMS must be a JSON object.")
                params = dict(parsed)

            details = {
                "method": env_method,
                "params": params,
                "result": self._call_dynamic(env_method, params),
            }
            taxonomy = self.build_taxonomy(
                level="info",
                namespace="axur",
                predicate="api-call",
                value=env_method,
            )
            full_report = {
                "observable": observable,
                "verdict": "info",
                "taxonomy": [taxonomy.to_dict()],
                "source": "axur",
                "data_type": self.data_type,
                "details": details,
            }
            return self.report(full_report)

        # 2) Dynamic call via data payload when dtype == other
        if self.data_type == "other":
            try:
                payload = json.loads(str(observable))
            except json.JSONDecodeError:
                self.error(
                    "For data_type 'other', data must be JSON with keys 'method' and 'params'."
                )
            if not isinstance(payload, Mapping):
                self.error("For data_type 'other', JSON payload must be an object.")
            if "method" not in payload:
                self.error("Missing 'method' in payload for data_type 'other'.")
            method = str(payload["method"])  # force str
            params_val = payload.get("params", {})
            if params_val is None:
                params_val = {}
            if not isinstance(params_val, Mapping):
                self.error("Payload 'params' must be a JSON object.")

            details = {
                "method": method,
                "params": dict(params_val),
                "result": self._call_dynamic(method, params_val),
            }
            taxonomy = self.build_taxonomy(
                level="info",
                namespace="axur",
                predicate="api-call",
                value=method,
            )
            full_report = {
                "observable": observable,
                "verdict": "info",
                "taxonomy": [taxonomy.to_dict()],
                "source": "axur",
                "data_type": self.data_type,
                "details": details,
            }
            return self.report(full_report)

        self.error(
            "Unsupported data type for AxurAnalyzer. Use env AXUR_METHOD or data_type 'other' with JSON."
        )

    def run(self) -> None:
        self.execute()
