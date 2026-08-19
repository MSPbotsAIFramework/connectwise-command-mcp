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
    async def connectwise_command_get_sites() -> str:
        """List all active sites for the authenticated partner.

        Site codes returned here are required by nearly every other tool
        in this server.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get_sites_v1("/reporting/v1/sites")
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_devices(
        site_code: Annotated[str, Field(description="Site code, from connectwise_command_get_sites.")],
        machine_id: Annotated[
            str | None, Field(description="Optional device ID to fetch a single device.")
        ] = None,
    ) -> str:
        """List devices for a site, optionally scoped to one device."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        path = f"/reporting/v1/sites/{site_code}/devices"
        if machine_id is not None:
            path += f"/{machine_id}"
        try:
            result = await client.get_sites_v1(path)
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_site_summary(
        site_code: Annotated[str, Field(description="Site code, from connectwise_command_get_sites.")],
        month: Annotated[int, Field(description="Requested month (1-12).")],
        year: Annotated[int, Field(description="Requested year.")],
    ) -> str:
        """Get asset and service request summary for a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("summary/site", body(site_code, month, year))
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()
