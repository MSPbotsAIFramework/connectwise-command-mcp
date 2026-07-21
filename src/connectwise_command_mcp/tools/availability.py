import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_daily_server_availability(
        site_code: str, month: int, year: int
    ) -> str:
        """Get average daily availability for all servers at a site.

        Source: Reports -> Executive Report -> Server Data -> Availability
        -> Daily Averages.

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
                "availability/daily", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_server_availability_monthly(
        site_code: str, month: int, year: int
    ) -> str:
        """Get server availability monthly averages at a site.

        Source: Reports -> Executive Report -> Server Data -> Availability
        -> Monthly Averages Details.

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
                "availability/monthly", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_daily_server_utilization(
        site_code: str, month: int, year: int
    ) -> str:
        """Get daily server utilization (CPU, memory, disk IO, disk space, page file) at a site.

        Source: Reports -> Executive Report -> Server Data -> Performance By
        Server.

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
                "utilization/daily", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
