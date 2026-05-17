# Temu 工具平台 — 企业级 Go 开发提示词模板

**版本**: v1.0.0 | **项目**: Temu 卖家工具平台 (SaaS) | **技术栈**: Go 1.22+ / MySQL 8.0 / MCP

## 使用方式

复制对应的模板到 Trae 对话中，替换 `{{你的具体任务}}` 即可。

## 模板目录

| 模板 | ID | 用途 |
|------|-----|------|
| [核心通用模板](./core_prompt.md) | TEMU-MCP-GO-000 | 标准版通用模板，任意开发任务 |
| [Temu API 代码生成](./temu_api_codegen.md) | TEMU-MCP-GO-001 | 生成 Temu 开发者平台 API 对接代码 |
| [MCP 工具开发](./mcp_tool_dev.md) | TEMU-MCP-GO-002 | 开发企业级 MCP 工具 |
| [MySQL 只读查询](./mysql_readonly.md) | TEMU-MCP-GO-003 | 安全的数据库查询代码生成 |
| [极简一键版](./quick_start.md) | — | 最快生效，一句话启动 |

## 规范要求

- 所有提示词统一存放此目录，Git 版本管理
- 禁止在提示词中写密钥/敏感信息
- 所有 MCP 工具、API 代码必须遵循模板输出
- 禁用 Redis、禁用数据库写操作
- 全部对接 Temu 开发者平台标准接口
