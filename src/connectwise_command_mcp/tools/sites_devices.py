import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError

_NO_TOKEN = "Error: No ConnectWise Command API key. Send the X-ConnectWise-Command-Api-Key header."


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_sites() -> str:
        """List all sites visible to this Reporting API key.

        Site codes returned here are required by nearly every other tool in
        this server.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get_sites_v1("/reporting/v1/Sites")
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_devices(site_code: str) -> str:
        """List devices (with top-level asset info) for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get_sites_v1(f"/reporting/v1/sites/{site_code}/devices")
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
