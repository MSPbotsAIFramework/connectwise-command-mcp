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

41 tools — full coverage of every resource in the official "Reporting API REST Resources" doc. Most take `site_code` (get one from `connectwise_command_get_sites` first) plus `month`/`year` (int); several also take `resource_type` ("desktop" or "server", per-resource restrictions noted where the doc fixes it to one value).

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
| `connectwise_command_get_patch_summary_by_resource` | 按设备维度的补丁状态计数 | `site_code`, `month`, `year`, `resource_type` (均必填) |
| `connectwise_command_get_patch_summary_by_severity` | 按严重程度的补丁计数 | `site_code`, `month`, `year`, `resource_type` (均必填) |
| `connectwise_command_get_patch_summary_by_state` | 按状态(已装/缺失/黑名单等)的补丁总数 | `site_code`, `month`, `year`, `resource_type` (均必填) |

### Performance

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_cpu_utilization` | 服务器 CPU 月度最小/最大/平均值及每日均值 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_disk_usage` | 服务器磁盘空间月度最小/最大/平均值及每日均值 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_disk_io_utilization` | 服务器磁盘 IO 月度最小/最大/平均值及每日均值 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_memory_utilization` | 服务器内存月度最小/最大/平均值及每日均值 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_pagefile_utilization` | 服务器 PageFile 月度最小/最大/平均值及每日均值 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_disk_space_utilization` | 按设备的磁盘空间使用百分比 | `site_code`, `month`, `year`, `resource_type` (均必填) |
| `connectwise_command_get_server_utilization` | 服务器月度平均 CPU/磁盘/内存使用率 | `site_code`, `month`, `year` (均必填) |

### Availability

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_daily_server_availability` | 站点全部服务器每日平均可用性 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_server_availability_monthly` | 服务器可用性月度平均值 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_daily_server_utilization` | 每日服务器综合利用率(CPU/内存/磁盘IO/磁盘空间/PageFile) | `site_code`, `month`, `year` (均必填) |

### Warranty

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_expiring_warranties` | 已过期或即将过期保修的设备列表 | `site_code`, `month`, `year`, `resource_type` (均必填) |
| `connectwise_command_get_warranty_details` | 设备保修详情(不需要 month/year) | `site_code` (必填), `include_warranty_history?`(默认 false) |
| `connectwise_command_get_warranty_summary` | 保修状态(有效/过期/无数据)计数 | `site_code`, `month`, `year`, `resource_type` (均必填) |

### Recover for Continuity (Backup)

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_continuity_appliances` | 站点已部署的 Recover for Continuity 备份设备列表 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_continuity_backup_summary` | 备份成功/失败百分比总览 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_continuity_backup_summary_by_resource` | 按受保护资源的备份结果 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_continuity_protected_resources` | 受 Recover for Continuity 保护的资源列表 | `site_code`, `month`, `year` (均必填) |

### Misc

| Tool | 功能 | 参数 |
|---|---|---|
| `connectwise_command_get_noncompliant_mobile_devices` | 不符合企业策略的移动设备列表 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_operating_system_summary` | 操作系统分布与设备数 | `site_code`, `month`, `year`, `resource_type` (均必填) |
| `connectwise_command_get_score_summary` | 站点整体健康/风险评分(多项指标,-1 表示该站点不适用) | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_service_requests_by_month` | 近6个月工单开关数量 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_service_requests_by_week` | 近6周工单开关数量 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_snmp_devices` | 站点下 SNMP 设备(路由器/交换机等)列表 | `site_code`, `month`, `year` (均必填) |
| `connectwise_command_get_work_summary` | 技术支持工作记录汇总 | `site_code`, `month`, `year` (均必填) |

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

- **Error shape varies by resource** — some responses use `"Error"` (capital, e.g. Agent Details), most use `"error"` (lowercase, e.g. Antivirus Summary), and the position in the response varies (top, bottom, or nested per-item). `ContinuumClient._parse` checks both casings.
- **GET resources (`Sites`, `Devices`) return a bare JSON array**, not an object with an `error` key.
- **Request field name `MachineID`** (used in the request body for Antivirus Version Summary, Installed Software, System Information) differs in casing from the response field `MachineId` — both confirmed verbatim from the official doc.
- `get_site_installation_package`-equivalent functionality does not exist for this API; not applicable here (unlike N-able RMM).
