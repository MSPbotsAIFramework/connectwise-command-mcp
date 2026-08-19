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
_MACHINE_ID = Annotated[
    int | None,
    Field(
        description=(
            "Optional Machine ID (from connectwise_command_get_agent_details) to "
            "scope results to a single device."
        )
    ),
]


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_antivirus_ages(
        site_code: _SITE_CODE, month: _MONTH, year: _YEAR
    ) -> str:
        """Get antivirus definition age (in days) for desktop machines at a site.

        Desktop machines only; this resource does not support servers.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "antivirus/ages", body(site_code, month, year, "desktop")
            )
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_antivirus_summary(
        site_code: _SITE_CODE, month: _MONTH, year: _YEAR, resource_type: _RESOURCE_TYPE
    ) -> str:
        """Get counts of machines by antivirus protection state (updated/outdated/not
        installed/information unavailable) at a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "antivirus/summary", body(site_code, month, year, resource_type)
            )
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_antivirus_version_summary(
        site_code: _SITE_CODE, machine_id: _MACHINE_ID = None
    ) -> str:
        """Get currently detected antivirus product/version per device at a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        req: dict = {"SiteCode": site_code}
        if machine_id is not None:
            req["MachineID"] = machine_id
        try:
            result = await client.call_legacy("antivirus/versions", req)
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_daily_antivirus_status(
        site_code: _SITE_CODE, month: _MONTH, year: _YEAR, resource_type: _RESOURCE_TYPE
    ) -> str:
        """Get daily antivirus status per machine for each day of a month."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "antivirus/daily", body(site_code, month, year, resource_type)
            )
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_missing_antivirus(
        site_code: _SITE_CODE, month: _MONTH, year: _YEAR, resource_type: _RESOURCE_TYPE
    ) -> str:
        """List devices missing antivirus software at a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "antivirus/missing", body(site_code, month, year, resource_type)
            )
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_outdated_antivirus(
        site_code: _SITE_CODE, month: _MONTH, year: _YEAR, resource_type: _RESOURCE_TYPE
    ) -> str:
        """List devices with outdated antivirus definitions at a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "antivirus/outdated", body(site_code, month, year, resource_type)
            )
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def connectwise_command_get_unsupported_antivirus(
        site_code: _SITE_CODE, month: _MONTH, year: _YEAR, resource_type: _RESOURCE_TYPE
    ) -> str:
        """List devices running an unsupported antivirus product at a site."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "antivirus/unsupported", body(site_code, month, year, resource_type)
            )
            return dump_json_capped(result)
        except ContinuumError as e:
            return e.to_envelope()
