import base64
from typing import Any

import httpx

# This legacy IIS/WCF service performs a mid-handshake TLS renegotiation and
# can take several seconds to respond (observed ~10s against a live account).
# httpx's default timeout (5s) is too short and trips a bare httpx.ReadTimeout.
_REQUEST_TIMEOUT = httpx.Timeout(30.0)


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
        try:
            async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
                resp = await client.get(target, headers=self._headers())
        except httpx.RequestError as e:
            raise ContinuumError(f"Could not reach {target!r}: {e or type(e).__name__}") from None
        return self._parse(resp, target)

    async def call_legacy(self, resource: str, body: dict | None = None) -> Any:
        """POST a JSON body against legacy ReportingAPIService.svc/json/{resource}."""
        target = f"{self._legacy_base_url}/{resource}"
        try:
            async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
                resp = await client.post(target, headers=self._headers(), json=body or {})
        except httpx.RequestError as e:
            raise ContinuumError(f"Could not reach {target!r}: {e or type(e).__name__}") from None
        return self._parse(resp, target)

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
