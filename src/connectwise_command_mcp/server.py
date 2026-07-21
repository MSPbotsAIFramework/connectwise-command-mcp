import contextvars
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .api_client import ContinuumClient
from .config import Settings

# Per-request credential isolation via contextvars.
# GatewayTokenMiddleware sets this before the MCP handler runs.
# Python asyncio copies context per task, so concurrent SSE connections are isolated.
_gateway_key_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "connectwise_command_gateway_key", default=None
)


def get_client_from_context(settings: Settings) -> ContinuumClient | None:
    """Resolve the active ContinuumClient for the current request context."""
    api_key = _gateway_key_var.get()
    if not api_key:
        return None
    return ContinuumClient(
        api_key,
        settings.connectwise_command_legacy_base_url,
        settings.connectwise_command_sites_base_url,
    )


class GatewayTokenMiddleware:
    """ASGI middleware.

    Reads X-ConnectWise-Command-Api-Key from request headers and stores it
    in the contextvar. Unlike some other RMM vendors, ConnectWise Command's
    Reporting API hosts are fixed public endpoints (not per-tenant), so no
    server/URL override header is needed. Returns 401 if the key header is
    missing on /mcp requests.
    """

    def __init__(self, app: ASGIApp, settings: Settings):
        self.app = app
        self.settings = settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not path.startswith("/mcp"):
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        api_key = request.headers.get("x-connectwise-command-api-key")
        if not api_key:
            response = JSONResponse(
                {
                    "error": "Missing credentials",
                    "message": "This server requires the X-ConnectWise-Command-Api-Key header containing a valid Reporting API key",
                    "required_headers": ["X-ConnectWise-Command-Api-Key"],
                },
                status_code=401,
            )
            await response(scope, receive, send)
            return

        ctx_token = _gateway_key_var.set(api_key)
        try:
            await self.app(scope, receive, send)
        finally:
            _gateway_key_var.reset(ctx_token)


def create_mcp_server(settings: Settings) -> FastMCP:
    """Build the FastMCP server instance and register all ConnectWise Command tools."""
    # DNS-rebinding protection is a browser-oriented safeguard that rejects
    # non-localhost Host headers with 421. Disable it so the server works
    # correctly behind a reverse proxy or docker network.
    mcp = FastMCP(
        name="connectwise-command-mcp",
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )

    client_factory: Callable[[], ContinuumClient | None] = lambda: get_client_from_context(
        settings
    )

    from .tools import (
        agent_system,
        antivirus,
        availability,
        backup,
        misc,
        patches,
        performance,
        sites_devices,
        warranty,
    )

    sites_devices.register(mcp, client_factory)
    agent_system.register(mcp, client_factory)
    antivirus.register(mcp, client_factory)
    patches.register(mcp, client_factory)
    performance.register(mcp, client_factory)
    availability.register(mcp, client_factory)
    warranty.register(mcp, client_factory)
    backup.register(mcp, client_factory)
    misc.register(mcp, client_factory)

    return mcp
