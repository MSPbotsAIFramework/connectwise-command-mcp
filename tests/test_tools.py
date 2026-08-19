"""tools/list snapshot + error-envelope mapping tests.

No network calls: tool enumeration goes through FastMCP's in-process
list_tools(), and the error-code mapping is tested directly against
ContinuumError, independent of any real HTTP request.
"""

import pytest

from connectwise_command_mcp.api_client import ContinuumError
from connectwise_command_mcp.config import Settings
from connectwise_command_mcp.server import create_mcp_server

EXPECTED_TOOLS = {
    # sites_devices
    "connectwise_command_get_sites": set(),
    "connectwise_command_get_devices": {"site_code"},
    "connectwise_command_get_site_summary": {"site_code", "month", "year"},
    # agent_system
    "connectwise_command_get_agent_details": {"site_code"},
    "connectwise_command_get_system_information": {"site_code"},
    "connectwise_command_get_installed_software": {"site_code"},
    # antivirus
    "connectwise_command_get_antivirus_ages": {"site_code", "month", "year"},
    "connectwise_command_get_antivirus_summary": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    "connectwise_command_get_antivirus_version_summary": {"site_code"},
    "connectwise_command_get_daily_antivirus_status": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    "connectwise_command_get_missing_antivirus": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    "connectwise_command_get_outdated_antivirus": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    "connectwise_command_get_unsupported_antivirus": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    # patches
    "connectwise_command_get_missing_patches": {"site_code", "month", "year"},
    "connectwise_command_get_patch_summary_by_resource": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    "connectwise_command_get_patch_summary_by_severity": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    "connectwise_command_get_patch_summary_by_state": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    # warranty
    "connectwise_command_get_expiring_warranties": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    "connectwise_command_get_warranty_details": {"site_code"},
    "connectwise_command_get_warranty_summary": {
        "site_code",
        "month",
        "year",
        "resource_type",
    },
    # misc
    "connectwise_command_get_score_summary": {"site_code", "month", "year"},
}


@pytest.mark.asyncio
async def test_tools_list_snapshot():
    mcp = create_mcp_server(Settings())
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert names == set(EXPECTED_TOOLS), f"unexpected tool set: {names}"

    by_name = {t.name: t for t in tools}
    for name, expected_required in EXPECTED_TOOLS.items():
        tool = by_name[name]
        required = set(tool.inputSchema.get("required", []))
        assert required == expected_required, f"{name}: required={required}"
        assert tool.annotations is not None and tool.annotations.readOnlyHint is True

        description = tool.description or ""
        assert len(description) <= 500, f"{name}: description too long ({len(description)})"
        first_line = description.strip().splitlines()[0] if description.strip() else ""
        assert len(first_line) <= 100, f"{name}: first line too long: {first_line!r}"
        assert "API:" not in description, f"{name}: leaked implementation detail"
        assert "GET /" not in description and "POST /" not in description, (
            f"{name}: leaked implementation detail"
        )


@pytest.mark.asyncio
async def test_service_instructions_present_and_bounded():
    mcp = create_mcp_server(Settings())
    assert mcp.instructions
    assert len(mcp.instructions) <= 1500


@pytest.mark.parametrize(
    "status_code,expected_code,expected_retryable",
    [
        (0, "upstream_error", True),
        (200, "invalid_argument", False),  # body-level error on an HTTP 200 response
        (400, "invalid_argument", False),
        (401, "unauthorized", False),
        (403, "unauthorized", False),
        (404, "not_found", False),
        (422, "invalid_argument", False),
        (429, "rate_limited", True),
        (500, "upstream_error", True),
        (503, "upstream_error", True),
    ],
)
def test_error_envelope_mapping(status_code, expected_code, expected_retryable):
    import json

    err = ContinuumError(status_code, "boom")
    envelope = json.loads(err.to_envelope())
    assert envelope["error"]["code"] == expected_code
    assert envelope["error"]["retryable"] is expected_retryable
    assert envelope["error"]["message"] == "boom"
