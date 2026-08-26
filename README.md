# connectwise-command-mcp

**ConnectWise Command** MCP server — exposes the ConnectWise Command (Continuum) ITSupport247 Reporting API as MCP tools.

> **Naming note:** app.mspbots.ai calls this integration **"ConnectWise Command (continuum)"** (`sys_integration.subject_code = CONTINUUM`). ConnectWise acquired Continuum and rebranded its RMM product as "ConnectWise Command"; the underlying API is still hosted on the legacy **ITSupport247** domain (`itsupport247.net`) and documented as the "Reporting API". This server wraps that Reporting API only — it is unrelated to ConnectWise Manage (PSA) or ConnectWise Automate.

## Overview

This server implements the [Model Context Protocol](https://modelcontextprotocol.io/) (Streamable HTTP/SSE transport) and wraps every resource in the official **"Reporting API REST Resources"** reference for ConnectWise Command / Continuum. It follows the MSPbots **Vendor MCP Service SOP**: stateless, no stored credentials, per-request header authentication.

The underlying API authenticates via HTTP Basic Auth (blank username, API key as password) and returns JSON. This server never stores the key — the caller passes it per-request via a header. All request/response field names below are transcribed verbatim from the official reference doc, not guessed.

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
# {"status": "ok"}
```

No token is required for the health endpoint.

## 授权参数说明 (Authentication)

Every request to `/mcp` must include the following HTTP header:

| Header | 类型 | 是否必填 | 默认值 | 枚举值 | 字段描述 | Example |
|---|---|---|---|---|---|---|
| `X-ConnectWise-Command-Api-Key` | string | 必填 | 无 | 无(自由文本) | ConnectWise Command (Continuum) Reporting API key,在 ITSupport247 门户 **Admin > Integration > Reporting API > Regenerate Key** 生成。服务端收到后转换为 HTTP Basic Auth(用户名留空,该 key 作为密码)发往上游 API,不做任何存储。 | `X-ConnectWise-Command-Api-Key: <your_reporting_api_key>` |

Internally, this server encodes the key as:

```
Authorization: Basic base64(":" + api_key)
```

Unlike some other RMM vendors (e.g. N-able), ConnectWise Command's Reporting API hosts are **fixed public endpoints, not per-tenant** — there is no "URL" field/header to configure, matching the single "API Key" field on the app.mspbots.ai integration form. Missing `X-ConnectWise-Command-Api-Key` returns `401 Unauthorized`.

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

**19 tools.** Trimmed from an original 41-tool full-API build (2026-08-04) down to 21 tools matching MSPbots' actually-configured 19 endpoints, then a further 2026-08-26 trim removed `connectwise_command_get_patch_summary_by_resource` and `connectwise_command_get_patch_summary_by_state` — an intent-matching test pass found their descriptions were near-duplicates of each other ("Get [total] patch counts by state... [per device]", differing only by a few trailing words), a real misfire risk since a mixup silently swaps a per-device breakdown for a site-wide aggregate on the same underlying data. Rather than patch the wording, both were removed; `connectwise_command_get_patch_summary_by_severity` and `connectwise_command_get_missing_patches` still cover patch reporting without that ambiguity. If either removed tool is needed later, the official "Reporting API REST Resources" doc (linked below) still documents it and it can be re-added; git history has both implementations verbatim.

Everything else from the original 41-tool build — Performance (7), Availability (3), Recover for Continuity/Backup (4), and 6 of 7 Misc tools (noncompliant mobile devices, OS summary, service requests by month/week, SNMP devices, work summary) — was removed on 2026-08-04 as unused by MSPbots.

Most kept tools take `site_code` (get one from `connectwise_command_get_sites` first) plus `month`/`year` (int); several also take `resource_type` ("desktop" or "server", per-resource restrictions noted where the doc fixes it to one value).

### Sites, Devices & Summary

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_sites` | 列出该 API key 可见的所有活跃站点 | 无参数 |
| `connectwise_command_get_devices` | 列出站点下的设备,可选定位到单设备 | `site_code` (必填), `machine_id?` |
| `connectwise_command_get_site_summary` | 站点资产与工单概况 | `site_code`, `month`, `year` (均必填) |

### Agent / System / Software

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_agent_details` | 站点内所有设备的监控代理详情(也用于获取 Machine ID) | `site_code` (必填) |
| `connectwise_command_get_system_information` | 系统硬件/OS/BIOS 信息,可选定位到单设备 | `site_code` (必填), `machine_id?` |
| `connectwise_command_get_installed_software` | 已安装软件列表,可选定位到单设备 | `site_code` (必填), `machine_id?` |

### Antivirus

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_antivirus_ages` | 桌面机防病毒库更新时长(天),仅支持 desktop | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_antivirus_summary` | 防病毒防护状态计数汇总 | `site_code`, `month`, `year`, `resource_type` (均必填,"Desktop"/"server") |
| `connectwise_command_get_antivirus_version_summary` | 防病毒产品/版本,可选定位到单设备 | `site_code` (必填), `machine_id?` |
| `connectwise_command_get_daily_antivirus_status` | 每日防病毒状态 | `site_code`, `month`, `year`, `resource_type` (均必填) |
| `connectwise_command_get_missing_antivirus` | 缺失防病毒防护的设备列表 | `site_code`, `month`, `year`, `resource_type` (均必填) |
| `connectwise_command_get_outdated_antivirus` | 病毒库过期的设备列表 | `site_code`, `month`, `year`, `resource_type` (均必填) |
| `connectwise_command_get_unsupported_antivirus` | 使用不受支持防病毒产品的设备列表 | `site_code`, `month`, `year`, `resource_type` (均必填) |

### Patches

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_missing_patches` | 桌面机缺失补丁汇总 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_patch_summary_by_severity` | 按严重程度的补丁计数 | `site_code`, `month`, `year`, `resource_type` (均必填) |

### Warranty

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_expiring_warranties` | 已过期或即将过期保修的设备列表 | `site_code`, `month`, `year`, `resource_type` (均必填) |
| `connectwise_command_get_warranty_details` | 设备保修详情(不需要 month/year) | `site_code` (必填), `include_warranty_history?`(默认 false) |
| `connectwise_command_get_warranty_summary` | 保修状态(有效/过期/无数据)计数 | `site_code`, `month`, `year`, `resource_type` (均必填) |

### Misc

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_score_summary` | 站点整体健康/风险评分(多项指标,-1 表示该站点不适用) | `site_code`, `month`, `year` (均必填) |

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

A month/year-based resource:

```json
{
  "method": "tools/call",
  "params": {
    "name": "connectwise_command_get_cpu_utilization",
    "arguments": { "site_code": "AGTSolutions", "month": 4, "year": 2015 }
  }
}
```

## API Reference

- Official docs (ITSupport247 portal, Admin > Integration > Reporting API):
  - "Getting Started with the Reporting API"
  - "Reporting API REST Resources" (full per-resource request/response schemas — source of every field name in this server)

## Implementation Notes

- **Trimmed twice**: 41 tools (full API) → 21 tools on 2026-08-04 (MSPbots'
  actually-configured 19 endpoints plus the small always-kept Sites/Devices/
  Agent/System categories) → **19 tools on 2026-08-26** (removed
  `get_patch_summary_by_resource`/`get_patch_summary_by_state` — see Tool
  List above for why). See the Tool List section for the full rationale
  each time. If a removed tool is needed later, the official Reporting API
  doc (linked below) still documents it and it can be re-added the same
  way the kept tools were generated; git history has every removed tool's
  implementation verbatim.
- **Error shape varies by resource** — some responses use `"Error"` (capital, e.g. Agent Details), most use `"error"` (lowercase, e.g. Antivirus Summary), and the position in the response varies (top, bottom, or nested per-item). `ContinuumClient._parse` checks both casings.
- **GET resources (`Sites`, `Devices`) return a bare JSON array**, not an object with an `error` key.
- **Request field name `MachineID`** (used in the request body for Antivirus Version Summary, Installed Software, System Information) differs in casing from the response field `MachineId` — both confirmed verbatim from the official doc.
- `get_site_installation_package`-equivalent functionality does not exist for this API; not applicable here (unlike N-able RMM).
