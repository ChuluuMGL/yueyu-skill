# Changelog

yueyu-skill 版本演进。日期为首个发布该版本的提交日。

## [0.2.3] — 2026-07-03

### 工具链与文档
- 新增静态清单自检 `scripts/check_manifest.sh`：校验 skill.json / SKILL.md / README 版本号一致，且每个工具字段与 MCP 注解齐全；接入 CI（`manifest` job）
- `get_latest_reports` 的 `type`（report/learning）/ `since` / `limit` / `offset` 参数在 SKILL.md 触发表与示例中显式暴露，便于 Agent 主动调用

## [0.2.2] — 2026-07-03

### 可维护性与可信度收尾
- 新增每日定时 MCP 冒烟工作流（`.github/workflows/smoke.yml`）：端点不可达 / serverInfo 版本漂移 / 工具集与 skill.json 不符 / 服务端数据未同步转型时，GitHub 邮件告警
- 冒烟测试由「工具数 ≥ 9」升级为「与 `skill.json` 精确比对工具集合」，工具名单一来源为 `skill.json`
- 补齐市场 / Codex 收录元数据：`skill.json` 的 `homepage` / `website` / `bugs`、`agents/openai.yaml`
- 修复 `SKILL.md` 中残留的旧品牌域名 `brandlens.dycreative.tech`，AI 工具访问地址统一以官网为准
- `.gitignore` 补充 `.claude/`，避免本地权限配置误提交

## [0.2.1] — 2026-06-13

### 转型与可信度
- 服务定位整体转向「账号营销 / 小红书达人投放 / 信息流广告 / 线索转化 / 营销复盘」
- 移除未经公开核验的客户数据（200+/91%/25% 等），改为以公开事实源为准
- 新增「公开事实源」一节；补充高新技术企业备案编号 `GR202533012042`
- 软化 AI 产品表述（「自研三款」→「相关工具包括」）
- 团队「小红书种草学认证讲师」背景加注：仅说明团队理解平台生态，不代表平台背书

## [0.2.0] — 2026-06-08

### 功能
- 新增 `subscribe_reports` / `unsubscribe_reports` 订阅与退订工具
- 修复订阅 / 线索收集的参数校验与追问逻辑
- 补全地址及团队背景，扩充核心触发词

## [0.1.0] — 2026-04-24

- 初始版本：MCP 营销服务查询，9 项工具
