import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_missing_patches(site_code: str, month: int, year: int) -> str:
        """Get a summary of desktop machines missing patches at a site.

        Source: Reports -> Executive Report -> Desktop Data -> Patch
        Updates -> Missing.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("patches/missing", body(site_code, month, year))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_patch_summary_by_resource(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """Get patch counts by state (Installed/Missing/Blacklisted/etc.) per device at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Patch Updates -> By State Per Server / By State Per Desktop.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
            resource_type: "desktop" or "server".
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "patches/resources", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_patch_summary_by_severity(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """Get installed/missing patch counts by severity class (Critical/Important/etc.) at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Patch Updates -> By Severity.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
            resource_type: "desktop" or "server".
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "patches/severity", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_patch_summary_by_state(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """Get total patch counts by state (Installed/Missing/Blacklisted/etc.) at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Patch Updates -> By State.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
            resource_type: "desktop" or "server".
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "patches/state", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
