import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError

_NO_TOKEN = "Error: No ConnectWise Command API key. Send the X-ConnectWise-Command-Api-Key header."


def _body(site_code: str, machine_id: str | None = None) -> dict:
    body: dict = {"SiteCode": site_code}
    if machine_id is not None:
        body["MachineId"] = machine_id
    return body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_agent_details(site_code: str) -> str:
        """Get monitoring agent details for all devices at a site.

        Also used to discover Machine IDs for tools that accept one.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("agent/details", _body(site_code))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_installed_software(
        site_code: str, machine_id: str | None = None
    ) -> str:
        """List installed software across a site, optionally scoped to one device.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            machine_id: Optional device ID to scope to a single machine.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("software/installed", _body(site_code, machine_id))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_system_information(
        site_code: str, machine_id: str | None = None
    ) -> str:
        """Get system information (hardware/OS details) for a site, optionally scoped to one device.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            machine_id: Optional device ID to scope to a single machine.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("systeminformation", _body(site_code, machine_id))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_score_summary(site_code: str) -> str:
        """Get the overall health/risk score summary for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("summary/score", {"SiteCode": site_code})
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_warranty_details(site_code: str) -> str:
        """Get device warranty details for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("warranty/details", {"SiteCode": site_code})
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_warranty_expiring(site_code: str) -> str:
        """List devices with warranties expiring soon at a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("warranty/expiring", {"SiteCode": site_code})
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_warranty_summary(site_code: str) -> str:
        """Get device warranty status summary for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("warranty/summary", {"SiteCode": site_code})
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
