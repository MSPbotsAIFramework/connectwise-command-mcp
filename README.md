# connectwise-command-mcp

**ConnectWise Command** MCP server — exposes the ConnectWise Command (Continuum) ITSupport247 Reporting API as MCP tools.

> **Naming note:** app.mspbots.ai calls this integration **"ConnectWise Command (continuum)"** (`sys_integration.subject_code = CONTINUUM`). ConnectWise acquired Continuum and rebranded its RMM product as "ConnectWise Command"; the underlying API is still hosted on the legacy **ITSupport247** domain (`itsupport247.net`) and documented as the "Reporting API". This server wraps that Reporting API only — it is unrelated to ConnectWise Manage (PSA) or ConnectWise Automate.

## Overview

This server implements the [Model Context Protocol](https://modelcontextprotocol.io/) (Streamable HTTP/SSE transport) and wraps the ConnectWise Command / Continuum Reporting API. It follows the MSPbots **Vendor MCP Service SOP**: stateless, no stored credentials, per-request header authentication.

The underlying API authenticates via HTTP Basic Auth (blank username, API key as password) and returns JSON. This server never stores the key — the caller passes it per-request via a header.

## Quick Start

### Docker (recommended)

```bash
docker compose up --build
```

The server starts on `http://localhost:8080`.

### Local (uv)

```bash
uv sync
python -m connectwise_command_mcp
```

## Health Check

```bash
curl http://localhost:8080/health
# {"status": "ok", "service": "connectwise-command-mcp", "transport": "http"}
```

No token is required for the health endpoint.

## 授权参数说明 (Authentication)

Every request to `/mcp` must include a valid Reporting API key:

```
X-ConnectWise-Command-Api-Key: <api_key>
```

Generate the key in the ITSupport247 portal: **Admin > Integration > Reporting API > Regenerate Key**. Internally, this server encodes it as HTTP Basic Auth with a **blank username**:

```
Authorization: Basic base64(":" + api_key)
```

Unlike some other RMM vendors (e.g. N-able), ConnectWise Command's Reporting API hosts are **fixed public endpoints, not per-tenant** — there is no "URL" field to configure, matching the single "API Key" field on the app.mspbots.ai integration form. Missing `X-ConnectWise-Command-Api-Key` returns `401 Unauthorized`.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MCP_HTTP_PORT` | `8080` | Listening port |
| `MCP_HTTP_HOST` | `0.0.0.0` | Listening host |
| `CONNECTWISE_COMMAND_LEGACY_BASE_URL` | `https://itsapi.itsupport247.net/reportingapi/ReportingAPIService.svc/json` | Legacy report endpoints (POST) |
| `CONNECTWISE_COMMAND_SITES_BASE_URL` | `https://api.itsupport247.net` | Sites/Devices endpoints (GET) |

## MCP Endpoint

```
POST http://localhost:8080/mcp
```

Connect your MCP client with:
- Transport: `http` (Streamable HTTP / SSE)
- Header: `X-ConnectWise-Command-Api-Key: <api_key>`

## Tool List

20 tools, matching the interfaces already configured for this integration in app.mspbots.ai (`data_api_manage` rows under `integration_id = 1424565871921713153`). Most tools require a `site_code` — get one from `connectwise_command_get_sites` first.

### Sites & Devices

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_sites` | 列出该 API key 可见的所有站点 | 无参数 |
| `connectwise_command_get_devices` | 列出站点下的设备 | `site_code` (必填) |

### Antivirus

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_antivirus_summary` | 站点防病毒防护概况 | `site_code` (必填) |
| `connectwise_command_get_antivirus_ages` | 病毒库更新时长统计 | `site_code` (必填) |
| `connectwise_command_get_antivirus_version_summary` | 防病毒产品/版本汇总,可选定位到单设备 | `site_code` (必填), `machine_id?` |
| `connectwise_command_get_daily_antivirus_status` | 每日防病毒状态汇总 | `site_code` (必填) |
| `connectwise_command_get_missing_antivirus` | 缺失防病毒防护的设备列表 | `site_code` (必填) |
| `connectwise_command_get_outdated_antivirus` | 病毒库过期的设备列表 | `site_code` (必填) |
| `connectwise_command_get_unsupported_antivirus` | 使用不受支持防病毒产品的设备列表 | `site_code` (必填) |

### Patches

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_missing_patches` | 缺失补丁列表 | `site_code` (必填) |
| `connectwise_command_get_patch_summary_by_resource` | 按设备维度的补丁状态汇总 | `site_code` (必填) |
| `connectwise_command_get_patch_summary_by_severity` | 按严重程度的补丁状态汇总 | `site_code` (必填) |
| `connectwise_command_get_patch_summary_by_state` | 按补丁状态(已装/待装/失败等)汇总 | `site_code` (必填) |

### Reports

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_agent_details` | 站点内所有设备的监控代理详情(也用于获取 machine_id) | `site_code` (必填) |
| `connectwise_command_get_installed_software` | 已安装软件列表,可选定位到单设备 | `site_code` (必填), `machine_id?` |
| `connectwise_command_get_system_information` | 系统/硬件信息,可选定位到单设备 | `site_code` (必填), `machine_id?` |
| `connectwise_command_get_score_summary` | 站点整体健康/风险评分 | `site_code` (必填) |
| `connectwise_command_get_warranty_details` | 设备保修详情 | `site_code` (必填) |
| `connectwise_command_get_warranty_expiring` | 即将到期的设备保修列表 | `site_code` (必填) |
| `connectwise_command_get_warranty_summary` | 设备保修状态汇总 | `site_code` (必填) |

## 测试示例 (Test Example)

List all sites, then get devices for one:

```json
{
  "method": "tools/call",
  "params": { "name": "connectwise_command_get_sites", "arguments": {} }
}
```

Equivalent `curl` against the running server (streamable HTTP MCP endpoint):

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "X-ConnectWise-Command-Api-Key: <api_key>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": { "name": "connectwise_command_get_sites", "arguments": {} }
  }'
```

## API Reference

- Official doc: "Getting Started with the Reporting API" (ConnectWise Command / ITSupport247 portal, Admin > Integration > Reporting API)

## Known Gaps / Unverified

- **Legacy endpoint JSON body field names are unconfirmed.** The official doc confirms every legacy resource takes a Site Code (and some optionally a Machine ID) but does not publish the exact JSON field names. This server sends `{"SiteCode": ..., "MachineId": ...}` (PascalCase, typical for WCF/.svc JSON services) as a best-effort guess — **verify against a live account and adjust `_body()` in `tools/antivirus.py` / `tools/reports.py` and the inline dicts in `tools/patches.py` if the real API rejects this shape.**
- No self-test against a live account has been performed yet (pending a real Reporting API key).
