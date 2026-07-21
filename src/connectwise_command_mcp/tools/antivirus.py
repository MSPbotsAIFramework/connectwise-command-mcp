import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError

_NO_TOKEN = "Error: No ConnectWise Command API key. Send the X-ConnectWise-Command-Api-Key header."

# NOTE: The official "Getting Started with the Reporting API" doc confirms
# every legacy resource takes a Site Code (and some optionally a Machine
# ID), but does not publish the exact JSON body field names. Body keys here
# ("SiteCode"/"MachineId") are a best-effort guess based on typical WCF/.svc
# JSON service conventions and are UNVERIFIED against a live account.


def _body(site_code: str, machine_id: str | None = None) -> dict:
    body: dict = {"SiteCode": site_code}
    if machine_id is not None:
        body["MachineId"] = machine_id
    return body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_antivirus_summary(site_code: str) -> str:
        """Get antivirus protection summary for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("antivirus/summary", _body(site_code))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_antivirus_ages(site_code: str) -> str:
        """Get antivirus definition age summary for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("antivirus/ages", _body(site_code))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_antivirus_version_summary(
        site_code: str, machine_id: str | None = None
    ) -> str:
        """Get antivirus product/version summary for a site, optionally scoped to one device.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            machine_id: Optional device ID to scope to a single machine.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("antivirus/versions", _body(site_code, machine_id))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_daily_antivirus_status(site_code: str) -> str:
        """Get the daily antivirus status summary for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("antivirus/daily", _body(site_code))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_missing_antivirus(site_code: str) -> str:
        """List devices with missing antivirus protection at a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("antivirus/missing", _body(site_code))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_outdated_antivirus(site_code: str) -> str:
        """List devices with outdated antivirus definitions at a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("antivirus/outdated", _body(site_code))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_unsupported_antivirus(site_code: str) -> str:
        """List devices running an unsupported antivirus product at a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("antivirus/unsupported", _body(site_code))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
