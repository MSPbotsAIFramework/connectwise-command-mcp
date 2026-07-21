import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import ContinuumClient, ContinuumError
from ._common import NO_TOKEN, body


def register(mcp: FastMCP, client_factory: Callable[[], ContinuumClient | None]) -> None:

    @mcp.tool()
    async def connectwise_command_get_cpu_utilization(site_code: str, month: int, year: int) -> str:
        """Get monthly min/max/average CPU utilization, plus daily averages, per server at a site.

        Source: Reports -> Executive Report -> Server Data -> Performance
        Analysis -> CPU Utilization.

        Args:
            site_code: Site code, from connectwise_command_get_sites.
            month: Requested month (1-12).
            year: Requested year.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.call_legacy("performance/cpu", body(site_code, month, year))
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_disk_usage(site_code: str, month: int, year: int) -> str:
        """Get monthly min/max/average disk space utilization, plus daily averages, per server.

        Source: Reports -> Executive Report -> Server Data -> Performance
        Analysis -> Disk Usage.

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
                "performance/diskusage", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_disk_io_utilization(site_code: str, month: int, year: int) -> str:
        """Get monthly min/max/average disk IO utilization, plus daily averages, per server.

        Source: Reports -> Executive Report -> Server Data -> Performance
        Analysis -> Disk Utilization.

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
                "performance/diskutilization", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_memory_utilization(site_code: str, month: int, year: int) -> str:
        """Get monthly min/max/average memory utilization, plus daily averages, per server.

        Source: Reports -> Executive Report -> Server Data -> Performance
        Analysis -> Memory Utilization.

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
                "performance/memory", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_pagefile_utilization(site_code: str, month: int, year: int) -> str:
        """Get monthly min/max/average pagefile utilization, plus daily averages, per server.

        Source: Reports -> Executive Report -> Server Data -> Performance
        Analysis -> Page File (Swap).

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
                "performance/pagefile", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_disk_space_utilization(
        site_code: str, month: int, year: int, resource_type: str
    ) -> str:
        """Get per-device disk space utilization percentage at a site.

        Source: Reports -> Executive Report -> Server Data / Desktop Data ->
        Utilization -> Disk Space Per Volume.

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
                "utilization/diskspace", body(site_code, month, year, resource_type)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def connectwise_command_get_server_utilization(site_code: str, month: int, year: int) -> str:
        """Get average server CPU/disk-space/memory utilization for a month.

        Source: Reports -> Executive Report -> Server Data -> Utilization ->
        Per Server.

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
                "utilization/server", body(site_code, month, year)
            )
            return json.dumps(result, indent=2)
        except ContinuumError as e:
            return f"Error: {e}"
