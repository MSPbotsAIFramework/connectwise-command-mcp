from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mcp_http_port: int = 8080
    mcp_http_host: str = "0.0.0.0"

    # Both hosts are fixed, public ConnectWise Command / Continuum
    # (ITSupport247) Reporting API endpoints — not per-tenant, unlike some
    # other RMM vendors. See "Getting Started with the Reporting API".
    connectwise_command_legacy_base_url: str = (
        "https://itsapi.itsupport247.net/reportingapi/ReportingAPIService.svc/json"
    )
    connectwise_command_sites_base_url: str = "https://api.itsupport247.net"


def get_settings() -> Settings:
    return Settings()
