import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError

_NO_TOKEN = "Error: No ConnectWise Command API key. Send the X-ConnectWise-Command-Api-Key header."


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_missing_patches(site_code: str) -> str:
        """List missing patches across devices at a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("patches/missing", {"SiteCode": site_code})
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_patch_summary_by_resource(site_code: str) -> str:
        """Get patch status summary grouped by device (resource) for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("patches/resources", {"SiteCode": site_code})
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_patch_summary_by_severity(site_code: str) -> str:
        """Get patch status summary grouped by severity for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("patches/severity", {"SiteCode": site_code})
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_patch_summary_by_state(site_code: str) -> str:
        """Get patch status summary grouped by patch state (e.g. installed/pending/failed) for a site.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.call_legacy("patches/state", {"SiteCode": site_code})
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
