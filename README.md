# 月瑀科技 AI Skill

> **把月瑀科技的小红书代运营服务，装进你的 AI 助手。**
> 一个开源 MCP Skill —— 接入 Claude / Cursor / 任意 MCP 客户端后，你的 AI 就能实时了解月瑀的服务、方法论，并直接帮你提交合作线索。
> *Put YUEYU TECH's Xiaohongshu marketing services into your AI assistant — a live MCP skill.*

![月瑀科技 AI Skill](social-preview.png?v=20260706-yueyu-logo)

**中文** | [English](README.en.md)

[![AI Skill](https://img.shields.io/badge/AI%20Skill-yueyu--skill-0E5E43)](https://github.com/ChuluuMGL/yueyu-skill)
[![MCP](https://img.shields.io/badge/Protocol-MCP-blue)](https://modelcontextprotocol.io/)
[![Version](https://img.shields.io/badge/version-0.2.6-green)](https://github.com/ChuluuMGL/yueyu-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](https://opensource.org/licenses/MIT)
[![Endpoint](https://img.shields.io/website?url=https%3A%2F%2Fwww.yueyu.tech%2Fmcp&label=MCP%20Endpoint)](https://www.yueyu.tech/mcp)
[![Drift Check](https://github.com/ChuluuMGL/yueyu-skill/actions/workflows/mcp-drift-check.yml/badge.svg)](https://github.com/ChuluuMGL/yueyu-skill/actions/workflows/mcp-drift-check.yml)

**国家高新技术企业 · 备案编号 `GR202533012042` · 杭州**

---

> 当前稳定版：`v0.2.6`（GitHub Release）。`main` 分支保持为最新已校验代码；每次版本号更新后同步打 tag/release，避免安装页与源码版本脱节。

## 装上能干嘛

让你的 AI 助手实时回答关于月瑀科技的问题——信息来自月瑀官网的实时接口，不是会过期的静态文档：

- 🏢 「月瑀科技是做什么的？」—— 公司介绍、团队背景
- 📋 「小红书达人投放怎么验收？」「信息流广告怎么复盘？」—— 5 大核心服务
- 🧭 「4I 营销飞轮是什么？」—— 品牌方法论
- 🤖 「你们有什么 AI 工具？」—— 品牌棱镜 / MuseWrite / REDFabric
- 📈 「最新的行业报告？」—— 趋势与学习资料
- 📞 「我想合作，帮我留个信息」—— **直接把合作线索提交到商务团队**

**适合谁装：**
- 正在找小红书代运营 / 达人投放服务商的**品牌方**
- 想快速了解月瑀服务边界与方法论的**市场负责人**
- 想在 AI 工作流里直接查询、并提交合作线索的**任何人**

---

## 30 秒试用

**第 1 步：** 把这一段加进你的 MCP 客户端配置（Claude Desktop / Cursor / Cline / Continue 等通用客户端都适用；也可直接复制 [`assets/mcp-config-example.json`](assets/mcp-config-example.json)）：

```json
{
  "mcpServers": {
    "yueyu-skill": {
      "type": "streamable-http",
      "url": "https://www.yueyu.tech/mcp"
    }
  }
}
```

**第 2 步：** 重启客户端，然后直接问你的 AI：

> **你：** 月瑀科技是做什么的？小红书达人投放怎么验收？
>
> **AI：** *（实时调用月瑀 MCP 服务）* 月瑀科技是杭州的国家高新技术企业（备案 GR202533012042），专注账号营销、小红书达人投放、信息流广告、线索转化与营销复盘。达人投放按「需求拆解 → 筛选 → Brief → 审核 → 排期 → 预算 → 结案复盘」交付，重点不在单篇爆文，而在可复盘的整条链路……

不用克隆代码、不用装依赖——它是**在线 MCP 服务**，填个网址就能用。

需要按客户端分步安装时，见 [`docs/client-install.md`](docs/client-install.md)。

---

## 推荐提问

**公司 / 服务速览**
```text
用 yueyu-skill 介绍一下月瑀科技，并说明它的小红书营销服务边界。
```

**达人投放验收**
```text
用 yueyu-skill 说明小红书达人投放应该怎么验收，不要只看发布数量。
```

**方法论**
```text
用 yueyu-skill 解释月瑀的 4I 营销飞轮，并结合账号营销举例。
```

**留资合作**
```text
我叫张三，微信 zhang-demo，想咨询小红书达人投放。用 yueyu-skill 把我的需求提交给商务团队。
```

> 提交前，AI 助手会复述将提交的姓名 / 联系方式 / 备注，说明信息仅提交给月瑀科技商务团队用于联系合作，等你确认后再调用 `submit_lead`。

---

## 9 项能力

| 能力 | 你可以这样问 | 类型 |
|---|---|---|
| 公司介绍 | 「月瑀是做什么的？」「杭州有什么营销公司？」 | 查询 |
| 服务板块 | 「小红书营销怎么做？」「达人投放怎么验收？」 | 查询 |
| 品牌方法论 | 「4I 是什么？」「品牌怎么做？」 | 查询 |
| 工具与资料 | 「有什么 AI 工具？」「BrandLens？」 | 查询 |
| 行业报告 | 「最新行业趋势？」 | 查询 |
| 联系方式 | 「怎么联系你们？」 | 查询 |
| **提交合作线索** | 「帮我留个信息」 | 写入 |
| **订阅报告** | 「有新报告通知我」 | 写入 |
| **取消订阅** | 「不要推了」 | 写入 |

---

## 为什么是月瑀

- **国家高新技术企业** · 公开备案编号 `GR202533012042`
- **公开可核验** —— 公司信息以 [官网 About](https://www.yueyu.tech/about)、[小红书营销公司服务页](https://www.yueyu.tech/services/xiaohongshu-marketing-company)、[选型指南](https://www.yueyu.tech/learning/guide-xiaohongshu-marketing-company-selection) 为准
- **团队具备小红书种草学认证讲师背景** —— 用于说明团队理解平台生态与种草链路（不代表平台背书或结果承诺）
- **独创方法论作为指导思想** —— 4I 营销飞轮（Image 品牌形象 → Impression 品牌印象 → Interaction 品牌互动 → Increasing 品牌增长），核心公式：品牌增长 = 形象 × 印象 × 互动

> 月瑀不写未经公开核验的客户数量、行业比例或效果承诺。不知道的就说明不知道。

---

## 核心服务

| 服务 | 说明 | 覆盖平台 |
|---|---|---|
| 账号营销 | 账号定位、内容栏目、节奏与运营复盘 | 小红书、抖音、微信生态 |
| 小红书达人投放 | 达人筛选、Brief、内容审核、排期、结案复盘 | 小红书 |
| 信息流广告 | 素材测试、预算拆分、投放承接、效果复盘 | 小红书聚光、巨量引擎、腾讯广告 |
| 线索转化 | 咨询入口、线索质量、销售承接、表单复盘 | 官网、私域、表单、客服 |
| 营销复盘 | 账号 / 达人 / 广告 / 线索放同一张表复盘 | 全链路 |

---

## 接入与联系

> **两种路径，能力不同：**
> - **方式 A = 安装 Skill 包**：AI 助手获得 9 个工具 + 月瑀品牌调性、盲区红线、隐私告知和降级策略。
> - **方式 B = 仅连接 MCP server**：AI 助手只获得 9 个查询/写入工具，适合只想接数据接口的场景。

| 你的客户端 | 接入方式 |
|---|---|
| Claude Code | `.claude/skills/yueyu-skill/`（安装 Skill 包） |
| Cursor | `.cursor/skills/yueyu-skill/` 或 MCP 配置 |
| Cline / Continue | MCP 配置 |
| Codex / OpenAI | `.agents/skills/yueyu-skill/`（配合 `agents/openai.yaml`） |
| 通用 MCP 客户端 | 用上面的 `mcpServers` URL 配置，**无需克隆** |

```bash
git clone https://github.com/ChuluuMGL/yueyu-skill.git \
  .claude/skills/yueyu-skill
```

**商务**：+86 186-1155-3805（微信同号 178 8790 0622）· BD@yueyu.tech · 杭州萧山区农业大厦 1 座 2005 室
**关注月瑀**：[小红书](https://www.xiaohongshu.com/user/profile/6706447e000000001d031a68) · [抖音](https://www.douyin.com/user/MS4wLjABAAAAEHnj91dHGmeatPJBSawvaS0PSwaaesRqkUyPGj37GnA) · [官网](https://www.yueyu.tech/)

---

## 数据与隐私

本 Skill 通过远程 MCP 端点提供实时数据。使用写入类工具时请注意：

- **提交前确认**：AI 助手在调用写入类工具前，会先说明信息的接收方与用途、复述将提交的内容，并在你明确确认后才提交；不会编造或自动填入你的联系方式。
- **提交合作线索（`submit_lead`）**：姓名、电话/微信、公司、需求备注会提交给月瑀科技商务团队（飞书 + CRM），仅用于商务跟进联系。
- **订阅报告（`subscribe_reports`）**：邮箱、微信号或 Webhook URL 仅用于推送新报告通知，可随时通过 `unsubscribe_reports` 取消。
- **查询类工具**：公司介绍、服务、方法论、报告、联系方式查询不需要用户个人信息。

---

## 常见问答

**这要钱吗？** Skill 完全免费、开源（MIT）。它让 AI 实时查月瑀的服务信息，不收任何费用。

**它和别的代运营有啥不同？** 月瑀把账号内容、达人表达、信息流广告、咨询线索放在**同一套可复盘链路**里，而不是只看发布数量；并保有独创的 4I 方法论作为指导思想。

**AI 会乱编案例和数据吗？** 不会。月瑀明确禁止编造案例、客户数量、效果承诺；未经公开核验的信息会如实说明，或引导联系商务。

**怎么联系 / 合作？** 直接让 AI 帮你提交合作线索（留姓名 + 手机/微信），或拨打 +86 186-1155-3805。

**服务怎么收费？** 咨询式报价，按行业、范围、周期定制。联系商务获取针对性报价。

---

## 技术规格

| 项目 | 说明 |
|---|---|
| 协议 | MCP (Model Context Protocol) |
| 传输 | Streamable HTTP |
| 端点 | `POST https://www.yueyu.tech/mcp` |
| 部署 | 阿里云 ECS（杭州） |
| 后端 | Express.js（复用官网 API） |
| 版本 | 0.2.6 |
| 契约校验 | [drift-check CI](https://github.com/ChuluuMGL/yueyu-skill/actions/workflows/mcp-drift-check.yml)：工具名/schema/annotations、payload 关键事实、联系方式、写入类负向 smoke、版本一致性 |

## 目录结构

```
yueyu-skill/
├── SKILL.md                    # 元数据 + Agent 指令
├── skill.json                  # 机器可读配置（工具定义 / 品牌调性）
├── README.md / README.en.md    # 中英文公开文档
├── references/                 # 工具调用样例 + 销售顾问话术
├── assets/                     # MCP 配置示例 + 品牌资产
├── docs/                       # 客户端安装说明 + 发布检查清单
├── scripts/mcp_smoke_test.sh   # MCP 冒烟测试
├── scripts/check_manifest.sh   # 清单自检（版本一致 + 工具字段）
├── scripts/check_mcp_drift.py  # live MCP / skill 包漂移检查
├── scripts/check_assets.py     # README / 社交预览 / logo 资产校验
├── scripts/qa.sh               # 一键本地 QA
├── agents/openai.yaml          # OpenAI / Codex agent 元数据
├── .github/workflows/          # smoke + drift-check CI
├── CHANGELOG.md · CONTRIBUTING.md · SECURITY.md · LICENSE
```

## 相关 Skill

- [proposal-ppt-skill](https://github.com/ChuluuMGL/proposal-ppt-skill) — 生成商业提案 PPT 与逐字稿
- [business-website-skill](https://github.com/ChuluuMGL/business-website-skill) — 构建客户级企业 / 品牌 / 营销网站

## License

MIT

---

> 觉得有用？给个 ⭐ 让更多人发现它 · 有问题或建议？[提个 issue](https://github.com/ChuluuMGL/yueyu-skill/issues)
