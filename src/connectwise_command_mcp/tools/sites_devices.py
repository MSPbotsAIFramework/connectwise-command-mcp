import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_sites() -> str:
        """List all active sites for the authenticated partner.

        Source: Reports -> (n/a, top-level resource). Site codes returned
        here are required by nearly every other tool in this server.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get_sites_v1("/reporting/v1/sites")
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_devices(site_code: str, machine_id: str | None = None) -> str:
        """List devices for a site, optionally scoped to one device.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            machine_id: Optional device ID to fetch a single device.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        path = f"/reporting/v1/sites/{site_code}/devices"
        if machine_id is not None:
            path += f"/{machine_id}"
        try:
            result = await client.get_sites_v1(path)
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_site_summary(site_code: str, month: int, year: int) -> str:
        """Get asset and service request summary for a site.

        Source: Reports -> Executive Report -> Summary -> Site Summary.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("summary/site", body(site_code, month, year))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
