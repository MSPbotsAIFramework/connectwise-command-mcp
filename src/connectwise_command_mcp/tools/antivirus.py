import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_antivirus_ages(site_code: str, month: int, year: int) -> str:
        """Get the age (in days) of antivirus definitions on desktop machines at a site.

        Source: Reports -> Executive Report -> Desktop Data -> Antivirus
        Definitions -> Ages. Desktop machines only (this resource does not
        support servers).

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
                "antivirus/ages", body(site_code, month, year, "desktop")
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_antivirus_summary(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """Get counts of machines by antivirus protection state (Updated/Outdated/Not
        Installed/Information Unavailable) at a site.

        Source: Reports -> Executive Report -> Desktop Data / Server Data ->
        Antivirus Definitions -> Monthly Status.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
            resource_type: "Desktop" or "server".
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "antivirus/summary", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_antivirus_version_summary(
        site_code: str, machine_id: int | None = None
    ) -> str:
        """Get currently detected antivirus product/version per device at a site.

        Source: Reports -> Preventive Maintenance -> Antivirus Version Report.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            machine_id: Optional Machine ID (from connectwise_command_get_agent_details)
                to scope results to a single device.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        req: dict = {"SiteCode": site_code}
        if machine_id is not None:
            req["MachineID"] = machine_id
        try:
            result = await client.call_legacy("antivirus/versions", req)
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_daily_antivirus_status(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """Get daily antivirus status per machine for each day of a month.

        Source: Reports -> Executive Report -> Desktop Data / Server Data ->
        Antivirus Definitions -> Daily Status.

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
                "antivirus/daily", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_missing_antivirus(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """List devices missing antivirus software at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Antivirus Definitions -> Missing.

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
                "antivirus/missing", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_outdated_antivirus(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """List devices with outdated antivirus definitions at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Antivirus Definitions -> Outdated.

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
                "antivirus/outdated", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_unsupported_antivirus(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """List devices running an unsupported antivirus product at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Antivirus Definitions -> Unsupported.

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
                "antivirus/unsupported", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
