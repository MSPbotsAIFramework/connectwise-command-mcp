NO_TOKEN = "Error: No ConnectWise Command API key. Send the X-ConnectWise-Command-Api-Key header."


def body(
    site_code: str,
    month: int | None = None,
    year: int | None = None,
    resource_type: str | None = None,
    **extra,
) -> dict:
    """Build a legacy-endpoint JSON request body per the official
    "Reporting API REST Resources" doc. Field names/casing (SiteCode,
    Month, Year, ResourceType) are confirmed verbatim from that doc.
    """
    b: dict = {"SiteCode": site_code}
    if month is not None:
        b["Month"] = month
    if year is not None:
        b["Year"] = year
    if resource_type is not None:
        b["ResourceType"] = resource_type
    b.update(extra)
    return b
