import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_expiring_warranties(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """List devices with expired warranties or warranties expiring soon at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Warranty -> Expired / Expiring.

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
                "warranty/expiring", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_warranty_details(
        site_code: str, include_warranty_history: bool = False
    ) -> str:
        """Get device warranty details for a site.

        Source: Reports -> Technical Details -> Warranty Report. Note: this
        resource takes no Month/Year — only SiteCode and
        IncludeWarrantyHistory.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            include_warranty_history: Whether to include past warranty history.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy(
                "warranty/details",
                {
                    "IncludeWarrantyHistory": "1" if include_warranty_history else "0",
                    "SiteCode": site_code,
                },
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_warranty_summary(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """Get counts of devices with active/expired/unavailable warranty data at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Warranty -> Status.

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
                "warranty/summary", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
