import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_continuity_appliances(
        site_code: str, month: int, year: int
    ) -> str:
        """List Recover for Continuity backup appliances provisioned at a site.

        Source: Reports -> Executive Report -> Recover for Continuity Backup
        Data -> Appliances.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "backup/continuity247/appliances", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_continuity_backup_summary(
        site_code: str, month: int, year: int
    ) -> str:
        """Get overall percentage of Recover for Continuity backups succeeded/failed at a site.

        Source: Reports -> Executive Report -> Recover for Continuity Backup
        Data -> Backup Status -> Overview.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "backup/continuity247/status/summary", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_continuity_backup_summary_by_resource(
        site_code: str, month: int, year: int
    ) -> str:
        """Get Recover for Continuity backup results per protected resource at a site.

        Source: Reports -> Executive Report -> Recover for Continuity Backup
        Data -> Backup Status -> Per Resource.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "backup/continuity247/status/resources", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_continuity_protected_resources(
        site_code: str, month: int, year: int
    ) -> str:
        """List resources being backed up by Recover for Continuity appliances at a site.

        Source: Reports -> Executive Report -> Recover for Continuity Backup
        Data -> Protected Resources.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "backup/continuity247/resources", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
