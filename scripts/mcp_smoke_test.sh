#!/usr/bin/env bash
# yueyu-skill MCP 冒烟测试
# 验证：端点可达、initialize 成功、tools/list 工具集合与 skill.json 完全一致、各只读工具返回非错误、
#       写入类工具拒绝缺失/非法参数。
# 同时阻断旧品牌/旧服务结构回流，避免 CI 绿灯但日志里藏着漂移告警。
# 漂移词表来自 scripts/drift_terms.json（与 check_mcp_drift.py 共用单一源）。
# 用法： bash scripts/mcp_smoke_test.sh [endpoint]
# 退出码：0 全过；非 0 有失败。
#
# 实现说明：只把「不含花括号的值」（id、工具名）作为变量插进 body；body 里的花括号全是
# 双引号字符串里的字面量，避免在 bash 下把含 { , } 的 JSON 当函数参数传递时被拆碎。
# tools/list 比对依赖 python3（GitHub Actions ubuntu-latest 与 macOS 均自带）。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_JSON="${SCRIPT_DIR}/../skill.json"
DRIFT_TERMS_JSON="${SCRIPT_DIR}/drift_terms.json"
EXPECTED_VERSION="$(python3 - "$SKILL_JSON" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8")).get("version", ""))
PY
)"
ENDPOINT="${1:-https://www.yueyu.tech/mcp}"
PASS=0; FAIL=0; ID=0
HEADERS="$(mktemp)"; LIST_FILE="$(mktemp)"
trap 'rm -f "$HEADERS" "$LIST_FILE"' EXIT

raw () {  # raw <body> —— POST 一个完整 body 字符串；线上偶发空响应时重试最多 3 次，避免假失败
  local body="$1" resp i
  for i in 1 2 3; do
    resp="$(curl -s -m 20 -X POST "$ENDPOINT" \
      -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
      --data-raw "$body")"
    [ -n "$resp" ] && { printf '%s' "$resp"; return 0; }
    sleep 1
  done
  printf '%s' "$resp"
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

call_tool_args () {  # call_tool_args <tool-name> <json-args> —— json-args 必须是完整 JSON object
  ID=$((ID+1))
  raw "{\"jsonrpc\":\"2.0\",\"id\":${ID},\"method\":\"tools/call\",\"params\":{\"name\":\"$1\",\"arguments\":$2}}"
}

scan_drift () {  # scan_drift <tool> <body-file> —— payload 内容漂移扫描（阻塞）；词表来自 drift_terms.json
  python3 - "$1" "$2" "$DRIFT_TERMS_JSON" <<'PY'
import json, sys
tool, path, terms_path = sys.argv[1], sys.argv[2], sys.argv[3]
deny = json.load(open(terms_path, encoding="utf-8"))["payload_deny"].get(tool)
if not deny:
    sys.exit(0)
txt = open(path, encoding="utf-8").read()
hits = [w for w in deny if w in txt]
if hits:
    print("  ✗ 内容漂移 %s：含 %s" % (tool, "、".join(hits)))
    print("    后端未与 skill.json 对齐，需重新部署")
    sys.exit(1)
PY
}

assert_rejected () {  # assert_rejected <label> <body> —— success:false 或 JSON-RPC error 都算正确拒绝
  local label="$1" body="$2"
  printf '%s' "$body" > "$LIST_FILE"
  if python3 - "$label" "$LIST_FILE" <<'PY'; then
import json, sys
label, path = sys.argv[1], sys.argv[2]
raw = open(path, encoding="utf-8").read()
blob = "".join(line[5:].strip() for line in raw.splitlines() if line.strip().startswith("data:")) or raw
try:
    data = json.loads(blob)
except Exception as exc:
    print(f"  ✗ {label}: cannot parse response: {exc}")
    sys.exit(1)
if "error" in data:
    sys.exit(0)
try:
    text = data["result"]["content"][0].get("text", "")
    payload = json.loads(text)
except Exception as exc:
    print(f"  ✗ {label}: unexpected response shape: {exc}")
    sys.exit(1)
if payload.get("success") is False:
    sys.exit(0)
print(f"  ✗ {label}: expected rejection, got {json.dumps(payload, ensure_ascii=False)[:240]}")
sys.exit(1)
PY
    printf '  ✓ %s\n' "$label"; PASS=$((PASS+1))
  else
    printf '    %s\n' "$(printf '%s' "$body" | tr -d '\n' | head -c 300)"
    FAIL=$((FAIL+1))
  fi
}

printf 'Endpoint: %s\n' "$ENDPOINT"

# 1) initialize（-D 抓 Mcp-Session-Id；空响应重试）
printf '[1/4] initialize\n'
for _ in 1 2 3; do
  INIT="$(curl -s -m 20 -D "$HEADERS" -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
    --data-raw '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"smoke","version":"0.0.1"}}}')"
  [ -n "$INIT" ] && break
  sleep 1
done
ID=1
ok "initialize" "$INIT"
SESSION="$(grep -i '^mcp-session-id:' "$HEADERS" | tail -1 | tr -d '\r' | awk '{print $2}')"
SVRVER="$(printf '%s' "$INIT" | grep -o '"version":"[^"]*"' | head -1 | sed 's/^"version":"//;s/"$//')"
printf '  · session=%s  serverInfo=%s\n' "${SESSION:-（无）}" "${SVRVER:-?}"
if [ "$SVRVER" = "$EXPECTED_VERSION" ]; then
  printf '  ✓ serverInfo.version matches skill.json (%s)\n' "$EXPECTED_VERSION"; PASS=$((PASS+1))
else
  printf '  ✗ serverInfo.version drift: server=%s skill.json=%s\n' "${SVRVER:-?}" "$EXPECTED_VERSION"; FAIL=$((FAIL+1))
fi

# 2) tools/list —— 与 skill.json 精确比对工具集合（工具名单一来源：skill.json）
printf '[2/4] tools/list\n'
LIST=$(rpc tools/list)
ok "tools/list" "$LIST"
printf '%s' "$LIST" > "$LIST_FILE"
if python3 - "$SKILL_JSON" "$LIST_FILE" "$DRIFT_TERMS_JSON" <<'PY'; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
import json, re, sys
expected = {t["name"] for t in json.load(open(sys.argv[1]))["tools"]}
raw = open(sys.argv[2]).read()
blob = ""
for line in raw.splitlines():
    s = line.strip()
    if s.startswith("data:"):
        blob += s[5:].strip()
    elif s[:1] == "{":
        blob += s
actual = set()
descs = {}
try:
    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("tools"), list):
                for t in o["tools"]:
                    if isinstance(t, dict) and "name" in t:
                        actual.add(t["name"])
                        if isinstance(t.get("description"), str):
                            descs[t["name"]] = t["description"]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(json.loads(blob))
except Exception:
    actual = set(re.findall(r'"name"\s*:\s*"([^"]+)"', raw))
print("  · skill.json %d 个 / 服务端 %d 个" % (len(expected), len(actual)))
if expected != actual:
    miss = sorted(expected - actual)
    extra = sorted(actual - expected)
    if miss:
        print("  ✗ 服务端缺失：" + ", ".join(miss))
    if extra:
        print("  ✗ 服务端多出：" + ", ".join(extra))
    sys.exit(1)
print("  ✓ 工具集合与 skill.json 完全一致")
# 描述漂移守卫：服务端描述不得含已清理的可信度/旧品牌雷区词（词表来自 drift_terms.json）
DENY = json.load(open(sys.argv[3], encoding="utf-8"))["description_deny"]
hits = [(n, w) for n, d in descs.items() for w in DENY if w in d]
if hits:
    print("  ✗ 描述漂移（后端未与 skill.json 可信度清理对齐）：")
    for n, w in hits:
        print("    - %s：描述含「%s」" % (n, w))
    print("  · 修复：重新部署 www.yueyu.tech 后端，使工具描述与 skill.json 一致")
    sys.exit(1)
PY

# 3) 只读工具逐个（顺带做 payload 内容漂移扫描，发现旧内容即失败）
printf '[3/4] 只读工具\n'
for t in get_company_info get_service_lines get_methodology get_products get_latest_reports get_contact_info; do
  BODY="$(call_tool "$t")"
  ok "$t" "$BODY"
  printf '%s' "$BODY" > "$LIST_FILE"
  if scan_drift "$t" "$LIST_FILE"; then
    :
  else
    FAIL=$((FAIL+1))
  fi
done

printf '[4/4] 写入参数拒绝\n'
BODY="$(call_tool_args submit_lead '{"name":"Contract Smoke Test"}')"
assert_rejected "submit_lead rejects missing phone/wechat" "$BODY"
BODY="$(call_tool_args subscribe_reports '{"channel":"sms","address":"contract-smoke@example.com"}')"
assert_rejected "subscribe_reports rejects invalid channel" "$BODY"
BODY="$(call_tool_args unsubscribe_reports '{}')"
assert_rejected "unsubscribe_reports rejects missing address" "$BODY"

printf '\n结果：%s 通过，%s 失败\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
