import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_agent_details(site_code: str) -> str:
        """Get monitoring agent details for all devices at a site.

        Also used to discover Machine IDs for tools that accept one.
        Source: Reports -> Agent Report.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("agent/details", {"SiteCode": site_code})
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_system_information(
        site_code: str, machine_id: int | None = None
    ) -> str:
        """Get system information (hardware/OS/BIOS details) for devices at a site.

        Source: Reports -> Technical Details -> System Information Report.

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
            result = await client.call_legacy("systeminformation", req)
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_installed_software(
        site_code: str, machine_id: int | None = None
    ) -> str:
        """List installed software (publisher, version, install date) for devices at a site.

        Source: Reports -> Technical Details -> Installed Software Report.

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
            result = await client.call_legacy("software/installed", req)
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
