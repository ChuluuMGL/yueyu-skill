# Client Install Guide

This guide covers the common ways to connect `yueyu-skill`.

## Option A: Skill Package

Use this when your agent supports local skill packages and should receive the full YUEYU tone, guardrails, privacy notice, and fallback behavior.

```bash
git clone https://github.com/ChuluuMGL/yueyu-skill.git .claude/skills/yueyu-skill
```

Common target paths:

| Client | Target path |
|---|---|
| Claude Code | `.claude/skills/yueyu-skill/` |
| Cursor | `.cursor/skills/yueyu-skill/` |
| Codex / OpenAI agents | `.agents/skills/yueyu-skill/` |

After copying or cloning, restart the client and ask:

```text
Use yueyu-skill to introduce YUEYU TECH and its Xiaohongshu marketing services.
```

## Option B: MCP Server Only

Use this when the client supports MCP but not local skill packages, or when you only need the live tools.

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

The same configuration is available at [`../assets/mcp-config-example.json`](../assets/mcp-config-example.json).

## Verify

Ask the client:

```text
What tools does yueyu-skill expose?
```

Expected tools:

- `get_company_info`
- `get_service_lines`
- `get_methodology`
- `get_products`
- `get_latest_reports`
- `get_contact_info`
- `submit_lead`
- `subscribe_reports`
- `unsubscribe_reports`

If the client can call tools, ask:

```text
Use yueyu-skill to get YUEYU TECH contact information.
```

The response should come from the live MCP endpoint.
