import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:
    @mcp.tool()
    async def connectwise_command_get_score_summary(site_code: str, month: int, year: int) -> str:
        """Get overall health/risk scoring metrics (antivirus, patch, disk space, etc.) for a site.

        Source: Reports -> Executive Report -> Summary -> Overall Score.
        A value of -1 for any metric means it's not applicable at that site
        (e.g. server metrics at a site with no servers).

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("summary/score", body(site_code, month, year))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

