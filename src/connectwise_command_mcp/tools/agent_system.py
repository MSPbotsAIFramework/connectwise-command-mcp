from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_agent_details(
        site_code: Annotated[str, Field(description="Site code, from connectwise_command_get_sites.")],
    ) -> str:
        """Get monitoring agent details for all devices at a site.

        Also the way to discover Machine IDs for tools that accept one.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("agent/details", {"SiteCode": site_code})
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_system_information(
        site_code: Annotated[str, Field(description="Site code, from connectwise_command_get_sites.")],
        machine_id: Annotated[
            int | None,
            Field(
                description=(
                    "Optional Machine ID (from connectwise_command_get_agent_details) "
                    "to scope results to a single device."
                )
            ),
        ] = None,
    ) -> str:
        """Get system information (hardware/OS/BIOS details) for devices at a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        req: dict = {"SiteCode": site_code}
        if machine_id is not None:
            req["MachineID"] = machine_id
        try:
            result = await client.call_legacy("systeminformation", req)
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_installed_software(
        site_code: Annotated[str, Field(description="Site code, from connectwise_command_get_sites.")],
        machine_id: Annotated[
            int | None,
            Field(
                description=(
                    "Optional Machine ID (from connectwise_command_get_agent_details) "
                    "to scope results to a single device."
                )
            ),
        ] = None,
    ) -> str:
        """List installed software (publisher, version, install date) for devices at a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        req: dict = {"SiteCode": site_code}
        if machine_id is not None:
            req["MachineID"] = machine_id
        try:
            result = await client.call_legacy("software/installed", req)
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()
