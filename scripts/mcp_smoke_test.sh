#!/usr/bin/env bash
# yueyu-skill MCP 冒烟测试
# 验证：端点可达、initialize 成功、tools/list 工具齐全、各只读工具返回非错误。
# 顺带打印 serverInfo.version 与工具数，便于发现「服务端版本漂移」「工具数与文档不符」「服务端数据与 skill 文档不一致」。
# 用法： bash scripts/mcp_smoke_test.sh [endpoint]
# 退出码：0 全过；非 0 有失败。
#
# 实现说明：只把「不含花括号的值」（id、工具名）作为变量插进 body；body 里的花括号全是
# 双引号字符串里的字面量，避免在 bash 下把含 { , } 的 JSON 当函数参数传递时被拆碎。
set -uo pipefail

ENDPOINT="${1:-https://www.yueyu.tech/mcp}"
PASS=0; FAIL=0; ID=0
HEADERS="$(mktemp)"; trap 'rm -f "$HEADERS"' EXIT

raw () {  # raw <body> —— 直接 POST 一个完整 body 字符串
  curl -s -m 20 -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
    --data-raw "$1"
}

ok () {  # ok <label> <body> —— 兼容 JSON 与 SSE（data: 行里同样含 "result"）
  local label="$1" body="$2"
  if printf '%s' "$body" | grep -q '"result"' && ! printf '%s' "$body" | grep -q '"error"'; then
    printf '  ✓ %s\n' "$label"; PASS=$((PASS+1))
  else
    printf '  ✗ %s\n' "$label"
    printf '    %s\n' "$(printf '%s' "$body" | tr -d '\n' | head -c 300)"
    FAIL=$((FAIL+1))
  fi
}

rpc () {  # rpc <method> —— 无参方法（tools/list 等）
  ID=$((ID+1))
  raw "{\"jsonrpc\":\"2.0\",\"id\":${ID},\"method\":\"$1\",\"params\":{}}"
}

call_tool () {  # call_tool <tool-name> —— 只传工具名，body 花括号全是字面量
  ID=$((ID+1))
  raw "{\"jsonrpc\":\"2.0\",\"id\":${ID},\"method\":\"tools/call\",\"params\":{\"name\":\"$1\",\"arguments\":{}}}"
}

printf 'Endpoint: %s\n' "$ENDPOINT"

# 1) initialize（-D 抓 Mcp-Session-Id）
printf '[1/3] initialize\n'
INIT=$(curl -s -m 20 -D "$HEADERS" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  --data-raw '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"smoke","version":"0.0.1"}}}')
ID=1
ok "initialize" "$INIT"
SESSION="$(grep -i '^mcp-session-id:' "$HEADERS" | tail -1 | tr -d '\r' | awk '{print $2}')"
SVRVER="$(printf '%s' "$INIT" | grep -o '"version":"[^"]*"' | head -1)"
printf '  · session=%s  serverInfo=%s\n' "${SESSION:-（无）}" "${SVRVER:-?}"

# 2) tools/list
printf '[2/3] tools/list\n'
LIST=$(rpc tools/list)
ok "tools/list" "$LIST"
COUNT="$(printf '%s' "$LIST" | grep -o '"name"[[:space:]]*:' | wc -l | tr -d ' ')"
printf '  · 服务端工具数 %s（skill.json 文档化 9 个）\n' "${COUNT:-0}"
if [ "${COUNT:-0}" -ge 9 ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi

# 3) 只读工具逐个
printf '[3/3] 只读工具\n'
for t in get_company_info get_service_lines get_methodology get_products get_latest_reports get_contact_info; do
  ok "$t" "$(call_tool "$t")"
done

printf '\n结果：%s 通过，%s 失败\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
