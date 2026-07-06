# YUEYU TECH AI Skill

> **Put YUEYU TECH's Xiaohongshu marketing services into your AI assistant.**
> An open-source MCP Skill that lets Claude, Cursor, Codex, and other MCP-compatible clients query YUEYU's services, methodology, reports, and contact paths in real time.

![YUEYU TECH AI Skill](social-preview.png?v=20260706-yueyu-logo)

[中文](README.md) | **English**

[![AI Skill](https://img.shields.io/badge/AI%20Skill-yueyu--skill-0E5E43)](https://github.com/ChuluuMGL/yueyu-skill)
[![MCP](https://img.shields.io/badge/Protocol-MCP-blue)](https://modelcontextprotocol.io/)
[![Version](https://img.shields.io/badge/version-0.2.5-green)](https://github.com/ChuluuMGL/yueyu-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](https://opensource.org/licenses/MIT)
[![Endpoint](https://img.shields.io/website?url=https%3A%2F%2Fwww.yueyu.tech%2Fmcp&label=MCP%20Endpoint)](https://www.yueyu.tech/mcp)
[![Drift Check](https://github.com/ChuluuMGL/yueyu-skill/actions/workflows/mcp-drift-check.yml/badge.svg)](https://github.com/ChuluuMGL/yueyu-skill/actions/workflows/mcp-drift-check.yml)

---

> Current stable version: `v0.2.5` (GitHub Release). The `main` branch tracks the latest validated package; each version bump should be tagged and released so source and install pages stay aligned.

## What This Skill Does

Once installed, an AI assistant can answer questions about YUEYU TECH's account marketing services through **9 live MCP tools**:

| Capability | Example questions | Type |
|---|---|---|
| Company info | "What does YUEYU TECH do?" "Any marketing agency in Hangzhou?" | Query |
| Service lines | "How does Xiaohongshu influencer placement work?" "What services do you offer?" | Query |
| Brand methodology | "What is the 4I growth wheel?" "How do you plan brand growth?" | Query |
| AI tools | "What AI tools do you have?" "BrandLens? MuseWrite?" | Query |
| Reports and learning | "Any latest marketing reports?" | Query |
| Contact details | "How do I reach you?" | Query |
| **Submit lead** | "Take my info for a consultation" | Write |
| **Subscribe to reports** | "Notify me when new reports are published" | Write |
| **Unsubscribe** | "Stop the report notifications" | Write |

All query answers come from the live MCP endpoint, not a static README cache.

---

## Install

### Path A: install the Skill package

This gives the AI assistant the 9 tools plus YUEYU's tone, guardrails, privacy notice, and fallback behavior.

| Agent / IDE | Skill directory | Status |
|---|---|---|
| Claude Code | `.claude/skills/yueyu-skill/` | Expected compatible |
| Cursor | `.cursor/skills/yueyu-skill/` | Expected compatible |
| Cline / Continue | MCP config | Expected compatible |
| Codex / OpenAI | `.agents/skills/yueyu-skill/` with `agents/openai.yaml` | Expected compatible |
| Generic MCP client | MCP config | Expected compatible |

```bash
git clone https://github.com/ChuluuMGL/yueyu-skill.git \
  .claude/skills/yueyu-skill
```

### Path B: connect the MCP server only

Use this when you only want the tools, without the Skill package's brand behavior. Copy [`assets/mcp-config-example.json`](assets/mcp-config-example.json):

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

---

## Recommended Prompts

**Company and services overview**
```text
Use $yueyu-skill to introduce YUEYU TECH and explain its Xiaohongshu marketing services.
```

**Influencer placement acceptance**
```text
Use $yueyu-skill to explain how YUEYU evaluates Xiaohongshu influencer placement beyond post count.
```

**Methodology**
```text
Use $yueyu-skill to explain the 4I marketing growth wheel and how it applies to account marketing.
```

**Lead submission**
```text
My name is Alex. My WeChat is alex-demo. I want to discuss Xiaohongshu influencer placement. Use $yueyu-skill to submit my request to the business team.
```

---

## Why YUEYU

- **National High-Tech Enterprise** with public filing number `GR202533012042`.
- **Publicly verifiable facts**: company and service information should be checked through the official website and live MCP tools.
- **Xiaohongshu seeding-certified lecturer background**: this only indicates platform/ecosystem understanding; it does not imply platform endorsement, preferred partnership, or guaranteed results.
- **Structured methodology**: 3Insights, 4I Wheels, and 5D Model for account marketing, content, media, lead conversion, and review loops.

YUEYU does not fabricate case studies, client counts, rankings, or performance promises. Unknown or non-public information should be stated as unknown.

---

## Contact

- Business phone: +86 186-1155-3805
- Backup phone / WeChat: 178 8790 0622
- Email: chuluu@yueyutech.cn
- Office: Room 2005, Building 1, Nongye Tower (萧山区农业大厦), Xiaoshan District, Hangzhou, Zhejiang, China
- Website: [www.yueyu.tech](https://www.yueyu.tech/)

---

## Data And Privacy

This Skill uses a remote MCP endpoint. For write tools:

- `submit_lead`: name, phone/WeChat, company, and notes are sent to YUEYU's business team via Feishu + CRM and used only for business follow-up.
- `subscribe_reports`: email, WeChat, or Webhook URL is used only for new-report notifications.
- `unsubscribe_reports`: cancels report notifications for the provided address.
- Query tools do not require personal information.

Before collecting contact details, the assistant must tell the user that the information is submitted only to YUEYU TECH's business team for cooperation follow-up.

---

## Technical Spec

| Item | Value |
|---|---|
| Protocol | MCP (Model Context Protocol) |
| Transport | Streamable HTTP |
| Endpoint | `POST https://www.yueyu.tech/mcp` |
| Version | 0.2.5 |
| Tools | 9 |
| Contract check | [drift-check CI](https://github.com/ChuluuMGL/yueyu-skill/actions/workflows/mcp-drift-check.yml): tools, schemas, annotations, canonical payload terms, contact facts, safe write-tool smoke tests, and versions |

## Repository Layout

```text
yueyu-skill/
├── SKILL.md                    # Agent instructions and routing
├── skill.json                  # Machine-readable tool definitions
├── README.md / README.en.md    # Public docs
├── references/                 # Usage examples and sales consultation guidance
├── assets/mcp-config-example.json
├── scripts/                    # Manifest, smoke, and drift checks
├── agents/openai.yaml          # OpenAI / Codex metadata
└── .github/                    # CI workflows and issue templates
```

## License

MIT
