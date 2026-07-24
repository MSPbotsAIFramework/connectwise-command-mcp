import asyncio
import base64
from typing import Any

import httpx

# This legacy IIS/WCF service performs a mid-handshake TLS renegotiation and
# can take several seconds to respond (observed ~10s against a live account).
# httpx's default timeout (5s) is too short and trips a bare httpx.ReadTimeout.
_REQUEST_TIMEOUT = httpx.Timeout(30.0)

# The vendor's reporting/v1 host (Sites/Devices) has been observed to return
# intermittent 503s that clear within seconds (3 consecutive real requests:
# 503, 503, 401) — a transient blip, not a sustained outage. Retry a handful
# of times with backoff on 502/503/504 and network errors before giving up;
# do not retry other status codes (e.g. 401/404), which are not transient.
_RETRY_STATUS_CODES = {502, 503, 504}
_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_SECONDS = (0.5, 1.5)


class ContinuumError(Exception):
    def __init__(self, message: str, error_code: str | None = None):
        self.error_code = error_code
        suffix = f" ({error_code})" if error_code else ""
        super().__init__(f"ConnectWise Command API error{suffix}: {message}")


class ContinuumClient:
    """Async httpx client wrapping the ConnectWise Command (Continuum)
    ITSupport247 Reporting API.

    Auth is HTTP Basic with a blank username and the Reporting API key as
    the password (per "Getting Started with the Reporting API"). Two fixed
    hosts are used: a legacy ReportingAPIService.svc/json endpoint (POST,
    JSON body) for most resources, and a separate reporting/v1 host (GET)
    for Sites/Devices.
    """

    def __init__(self, api_key: str, legacy_base_url: str, sites_base_url: str):
        self._api_key = api_key
        self._legacy_base_url = legacy_base_url.rstrip("/")
        self._sites_base_url = sites_base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        token = base64.b64encode(f":{self._api_key}".encode()).decode()
        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }

    async def get_sites_v1(self, path: str) -> Any:
        """GET against the reporting/v1 host (Sites and Devices resources)."""
        target = f"{self._sites_base_url}{path}"
        resp = await self._request_with_retry("GET", target)
        return self._parse(resp, target)

    async def call_legacy(self, resource: str, body: dict | None = None) -> Any:
        """POST a JSON body against legacy ReportingAPIService.svc/json/{resource}."""
        target = f"{self._legacy_base_url}/{resource}"
        resp = await self._request_with_retry("POST", target, json=body or {})
        return self._parse(resp, target)

    async def _request_with_retry(self, method: str, target: str, **kwargs: Any) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
                    resp = await client.request(method, target, headers=self._headers(), **kwargs)
            except httpx.RequestError as e:
                last_error = e
            else:
                if resp.status_code not in _RETRY_STATUS_CODES:
                    return resp
                last_error = ContinuumError(f"HTTP {resp.status_code} from {target}: {resp.text[:300]}")
            if attempt < _MAX_ATTEMPTS - 1:
                await asyncio.sleep(_RETRY_BACKOFF_SECONDS[attempt])
        if isinstance(last_error, ContinuumError):
            raise last_error
        raise ContinuumError(f"Could not reach {target!r}: {last_error or type(last_error).__name__}") from None

    def _parse(self, resp: httpx.Response, target: str) -> Any:
        if resp.status_code >= 400:
            raise ContinuumError(f"HTTP {resp.status_code} from {target}: {resp.text[:300]}")
        if not resp.content:
            return None
        try:
            data = resp.json()
        except ValueError:
            return {"raw_response": resp.text}

        # Error key casing AND position are inconsistent across resources in
        # the official "Reporting API REST Resources" doc: some use "Error"
        # (capital, e.g. Agent Details), most use "error" (lowercase, e.g.
        # Antivirus Summary); check both. GET endpoints (Sites/Devices)
        # return a bare list with no error wrapper at all.
        if isinstance(data, dict):
            err = data.get("Error", data.get("error"))
            if err:
                if isinstance(err, dict):
                    raise ContinuumError(err.get("message", "Unknown error"), err.get("code"))
                raise ContinuumError(str(err))
        return data
