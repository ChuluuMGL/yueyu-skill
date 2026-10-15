# Changelog

yueyu-skill 版本演进。日期为首个发布该版本的提交日。

## [Unreleased]

### 修复
- 联系邮箱与官网保持一致：商务联系改为 `BD@yueyu.tech`，隐私、安全与数据删除请求改为 `Chuluu@yueyu.tech`（官网已于 2026-07-17 更换，旧地址 `chuluu@yueyutech.cn` 导致每日 MCP Drift Check 的联系方式校验失败）

### QA 与维护
- 新增 `scripts/check_assets.py`，固定校验 `social-preview.png` 与 canonical YUEYU 字标的尺寸和 SHA-256，避免 README 配图或 logo 回退
- 新增 `scripts/qa.sh` 一键本地 QA，串联 manifest、资产、严格 drift 与 MCP smoke
- `MCP Drift Check` workflow 开启 `STRICT_SERVER_ANYOF=1`，schema `anyOf` 漂移将阻断 CI
- `CI` manifest job 增加资产校验，并扩大文档 / 模板 / 安全文件的触发路径

### 文档与协作
- 新增 PR 模板、`SECURITY.md` 和 `docs/client-install.md`
- 发布清单与贡献指南改为引用一键 QA，并补充品牌图更新规则

### 隐私告知与提交确认
- `SKILL.md` 新增常驻「写入类工具的前置校验」与「个人信息告知与确认」规则，覆盖 `submit_lead` / `subscribe_reports` / `unsubscribe_reports`：调用前必须说明接收方与用途（月瑀科技商务团队，用于联系合作 / 仅用于报告推送）、复述将提交的字段，并取得用户明确确认；参数齐全不再等同于用户同意
- 最小化收集：只收姓名 + 一种联系方式；`company` / `note` 只写用户主动提供的内容；不编造、不预填联系方式；代他人提交须先确认对方知情同意并在 `note` 注明
- `subscribe_reports` 确认话术说明推送内容，以及可随时通过 `unsubscribe_reports` 取消
- `references/sales-consultation.md`「线索预筛」改为可选、仅限业务需求，并补充确认话术；`references/usage-examples.md` 的留资 / 订阅 / 退订 / 多工具编排示例改为「告知 → 复述 → 确认 → 调用」，新增用户拒绝与代他人提交示例
- `agents/openai.yaml` 新增 `data_minimization` 护栏并强化 `privacy_notice`；`skill.json` 工具描述与 `brand_prompt`、中英文 README「数据与隐私」、`SECURITY.md`、PR 模板同步提交确认要求
- 9 个 MCP 工具的名称与 inputSchema 无变化

## [0.2.6] — 2026-07-06

### QA 与发布体验
- actions/checkout 升级到 `v7`，消除 Node 20 deprecation annotation；`smoke.yml` 移除每日重复线上 smoke，保留手动完整 smoke 与 push/PR manifest，降低 live MCP 429 风险
- 新增 `assets/brand/yueyu-logo-wordmark.png` 与品牌资产说明，明确 `YUEYU` 字标为本 skill 的正确 logo，避免误用旧 `月瑀营销 / MONSTO MKT` 标识
- 新增 `docs/release-checklist.md`，固化版本、QA、tag/release、README 图和 live MCP serverInfo 的发布流程
- drift/smoke 将 live MCP `serverInfo.version` 纳入版本一致性检查，防止 package 版本与线上端点脱节
- 漂移检查补充联系方式一致性校验：线上 `get_contact_info`、README/SKILL 文档中的电话、邮箱和地址标记必须保持同步
- 漂移检查与冒烟测试新增写入类负向 smoke：`submit_lead` 缺手机号/微信、`subscribe_reports` 非法渠道、`unsubscribe_reports` 缺地址时必须被服务端拒绝
- `check_manifest.sh` 纳入英文 README 版本一致性与 `assets/mcp-config-example.json` MCP URL 校验

### 文档与安装
- 新增 `README.en.md`、`assets/mcp-config-example.json`、`.github/ISSUE_TEMPLATE/config.yml`
- 新增 `references/usage-examples.md` 与 `references/sales-consultation.md`，将长示例和销售顾问话术从常驻 `SKILL.md` 拆分为按需加载资料
- README 补齐推荐提问、兼容客户端矩阵和 references/assets 目录说明

## [0.2.5] — 2026-07-03

### 测试加固
- 冒烟测试检查「payload 内容漂移」：对 `get_company_info` / `get_service_lines` / `get_products` 的返回内容检查旧品牌/旧服务结构雷区词（大瑀/dycreative/整合营销/AI创意/达人种草/效果广告/出海营销/兔克/tktk/自研三款）
- 旧后端曾命中：`get_service_lines` 整体仍返旧「大瑀创意」服务结构、`get_products` 含 dycreative 旧域名、`get_company_info` 残留旧品牌 —— 见 #1；当前线上后端已对齐
- 漂移守卫升级为阻塞检查：旧品牌/旧服务结构再次出现在 description 或只读工具 payload 时，`scripts/mcp_smoke_test.sh` 直接失败
- 新增 `scripts/check_mcp_drift.py` 与 `MCP Drift Check` workflow：每日比对线上 MCP 工具合同、payload 可信度、版本一致性和本地 agent 元数据
- `submit_lead` 在 `skill.json` 中显式编码 `name + (phone 或 wechat)` 的机器可读 `anyOf` 合同；`check_manifest.sh` 会防止该约束回退
- README 补齐 GitHub Release 稳定版说明、Drift Check 徽章、两种接入路径和写入类工具隐私说明

## [0.2.4] — 2026-07-03

### 测试加固与清理
- 冒烟测试新增「描述漂移」非阻塞守卫：服务端工具描述若含已清理的可信度雷区词（三大子公司 / 核心数据），在 CI 日志告警（不阻断），提示后端需与 skill.json 对齐
- 删除冗余的 `assets/mcp-config-example.json`（README 内联片段与 skill.json 已覆盖），更新目录结构

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
