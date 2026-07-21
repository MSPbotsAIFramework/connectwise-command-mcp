import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_noncompliant_mobile_devices(
        site_code: str, month: int, year: int
    ) -> str:
        """List mobile devices not in compliance with corporate policy at a site.

        Source: Reports -> Executive Report -> Mobile Device Data ->
        Noncompliant Devices.

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
                "mobiledevices/noncompliant", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_operating_system_summary(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """Get a summary of operating systems in use and machine counts at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Operating Systems -> Number of Machines.

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
                "operatingsystems/summary", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

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

    @mcp.tool()
    async def connectwise_command_get_service_requests_by_month(
        site_code: str, month: int, year: int
    ) -> str:
        """Get counts of service requests opened/closed over the last 6 months at a site.

        Source: Reports -> Executive Report -> Service Request Data -> Open /
        Closed -> By Month.

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
                "servicerequests/monthly", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_service_requests_by_week(
        site_code: str, month: int, year: int
    ) -> str:
        """Get counts of service requests opened/closed over the previous 6 weeks at a site.

        Source: Reports -> Executive Report -> Service Request Data -> Open /
        Closed -> By Week.

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
                "servicerequests/weekly", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_snmp_devices(site_code: str, month: int, year: int) -> str:
        """List SNMP devices (routers, switches, etc.) at a site.

        Source: Reports -> Executive Report -> SNMP Monitoring -> Device
        Details.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("snmp/devices", body(site_code, month, year))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_work_summary(site_code: str, month: int, year: int) -> str:
        """Get a summary of technician work performed on desktops/servers at a site.

        Source: Reports -> Executive Report -> Work Status -> Summary of
        Work.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("worksummary", body(site_code, month, year))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
