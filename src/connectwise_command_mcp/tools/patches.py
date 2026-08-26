from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body

_SITE_CODE = Annotated[str, Field(description="Site code, from connectwise_command_get_sites.")]
_MONTH = Annotated[int, Field(description="Requested month (1-12).")]
_YEAR = Annotated[int, Field(description="Requested year.")]
_RESOURCE_TYPE = Annotated[str, Field(description='"desktop" or "server".')]


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_missing_patches(
        site_code: _SITE_CODE, month: _MONTH, year: _YEAR
    ) -> str:
        """Get a summary of desktop machines missing patches at a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("patches/missing", body(site_code, month, year))
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_patch_summary_by_severity(
        site_code: _SITE_CODE, month: _MONTH, year: _YEAR, resource_type: _RESOURCE_TYPE
    ) -> str:
        """Get installed/missing patch counts by severity class (critical/important/etc.)
        at a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "patches/severity", body(site_code, month, year, resource_type)
            )
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()
