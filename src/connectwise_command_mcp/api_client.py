import asyncio
import base64
from typing import Any

import httpx

from ._json import error_envelope

# This legacy IIS/WCF service performs a mid-handshake TLS renegotiation and
# can take several seconds to respond (observed ~10s against a live account).
# httpx's default read timeout (5s) is too short and trips a bare
# httpx.ReadTimeout, so read is set well above that observed figure.
_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)

# The vendor's reporting/v1 host (Sites/Devices) has been observed to return
# intermittent 503s that clear within seconds (3 consecutive real requests:
# 503, 503, 401) — a transient blip, not a sustained outage. Retry a handful
# of times with backoff on 429/5xx and network errors before giving up; do
# not retry other status codes (e.g. 401/404), which are not transient.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_MAX_RETRIES = 3
_MAX_BACKOFF_SECONDS = 20.0

# One shared connection pool for the process lifetime. No credentials are
# ever stored on it — the API key is passed per-request via headers built
# fresh from the per-request ContinuumClient instance, so sharing this pool
# across tenants/requests is safe (see server.py's contextvar-based
# credential isolation, which is what actually keeps tenants apart).
_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True)
    return _http_client


# status_code -> (error code, retryable), per the SOP's fixed error-code
# vocabulary. status_code 0 means a network/connection-level failure (no
# response at all). Body-level errors that arrive on an HTTP 200 (this
# vendor sometimes wraps a business error in a 200 response — see _parse)
# fall through the `>= 500` / default branches below like any other
# unlisted status.
_STATUS_TO_CODE: dict[int, tuple[str, bool]] = {
    0: ("upstream_error", True),
    400: ("invalid_argument", False),
    401: ("unauthorized", False),
    403: ("unauthorized", False),
    404: ("not_found", False),
    422: ("invalid_argument", False),
    429: ("rate_limited", True),
}


def _classify(status_code: int) -> tuple[str, bool]:
    if status_code in _STATUS_TO_CODE:
        return _STATUS_TO_CODE[status_code]
    if status_code >= 500:
        return "upstream_error", True
    return "invalid_argument", False


class ContinuumError(Exception):
    def __init__(self, status_code: int, message: str, error_code: str | None = None):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        suffix = f" ({error_code})" if error_code else ""
        super().__init__(f"ConnectWise Command API error{suffix}: {message}")

    def to_envelope(self) -> str:
        code, retryable = _classify(self.status_code)
        return error_envelope(code, self.message, retryable)


class ContinuumClient:
    """Async httpx client wrapping the ConnectWise Command (Continuum)
    ITSupport247 Reporting API.

    Auth is HTTP Basic with a blank username and the Reporting API key as
    the password (per "Getting Started with the Reporting API"). Two fixed
    hosts are used: a legacy ReportingAPIService.svc/json endpoint (POST,
    JSON body) for most resources, and a separate reporting/v1 host (GET)
    for Sites/Devices. Reuses the module-level connection pool (see
    _get_http_client) across every call made through this instance, rather
    than opening a new connection per request.
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
        client = _get_http_client()
        headers = self._headers()

        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = await client.request(method, target, headers=headers, **kwargs)
            except httpx.RequestError as e:
                last_exc = e
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(min(2**attempt, _MAX_BACKOFF_SECONDS))
                    continue
                raise ContinuumError(0, f"{e or type(e).__name__} (url={target})") from e

            if resp.status_code in _RETRYABLE_STATUS and attempt < _MAX_RETRIES:
                await asyncio.sleep(self._retry_delay(resp, attempt))
                continue

            return resp

        # Unreachable in practice (loop always returns or raises above), but
        # keeps type checkers happy and guards against future edits.
        if last_exc:
            raise ContinuumError(0, f"{last_exc}") from last_exc
        raise ContinuumError(0, "request failed with no response")

    def _retry_delay(self, resp: httpx.Response, attempt: int) -> float:
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), _MAX_BACKOFF_SECONDS)
            except ValueError:
                pass
        return min(2**attempt, _MAX_BACKOFF_SECONDS)

    def _parse(self, resp: httpx.Response, target: str) -> Any:
        if resp.status_code >= 400:
            try:
                detail = resp.json()
                if isinstance(detail, dict):
                    msg = detail.get("message") or detail.get("error") or str(detail)[:300]
                else:
                    msg = str(detail)[:300]
            except ValueError:
                msg = resp.text[:300]
            raise ContinuumError(resp.status_code, msg)

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
        # return a bare list with no error wrapper at all. These body-level
        # errors are commonly returned with an HTTP 200 status, so the
        # ContinuumError raised here still carries resp.status_code (usually
        # 200) for consistent SOP error-code classification (see _classify).
        if isinstance(data, dict):
            err = data.get("Error", data.get("error"))
            if err:
                if isinstance(err, dict):
                    raise ContinuumError(
                        resp.status_code, err.get("message", "Unknown error"), err.get("code")
                    )
                raise ContinuumError(resp.status_code, str(err))
        return data
