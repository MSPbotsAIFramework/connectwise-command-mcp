from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:
    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_score_summary(
        site_code: Annotated[str, Field(description="Site code, from connectwise_command_get_sites.")],
        month: Annotated[int, Field(description="Requested month (1-12).")],
        year: Annotated[int, Field(description="Requested year.")],
    ) -> str:
        """Get overall health/risk scoring metrics (antivirus, patch, disk space, etc.)
        for a site.

        A value of -1 for any metric means it's not applicable at that site
        (e.g. server metrics at a site with no servers).
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("summary/score", body(site_code, month, year))
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()
