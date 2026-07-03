#!/usr/bin/env bash
# yueyu-skill MCP 冒烟测试
# 验证：端点可达、initialize 成功、tools/list 工具集合与 skill.json 完全一致、各只读工具返回非错误。
# 顺带打印 serverInfo.version 与工具集合，便于发现「服务端版本漂移」「工具集与 skill.json 不符」「服务端数据与 skill 文档不一致」。
# 用法： bash scripts/mcp_smoke_test.sh [endpoint]
# 退出码：0 全过；非 0 有失败。
#
# 实现说明：只把「不含花括号的值」（id、工具名）作为变量插进 body；body 里的花括号全是
# 双引号字符串里的字面量，避免在 bash 下把含 { , } 的 JSON 当函数参数传递时被拆碎。
# tools/list 比对依赖 python3（GitHub Actions ubuntu-latest 与 macOS 均自带）。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_JSON="${SCRIPT_DIR}/../skill.json"
ENDPOINT="${1:-https://www.yueyu.tech/mcp}"
PASS=0; FAIL=0; ID=0
HEADERS="$(mktemp)"; LIST_FILE="$(mktemp)"
trap 'rm -f "$HEADERS" "$LIST_FILE"' EXIT

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

scan_drift () {  # scan_drift <tool> <body-file> —— payload 内容漂移扫描（非阻塞）
  python3 - "$1" "$2" <<'PY'
import sys
tool, path = sys.argv[1], sys.argv[2]
DENY = {
    "get_company_info": ["大瑀", "dycreative", "三大子公司", "核心数据", "整合营销", "AI创意"],
    "get_service_lines": ["大瑀", "dycreative", "整合营销", "AI创意", "达人种草", "效果广告", "出海营销", "兔克", "tktk"],
    "get_products": ["dycreative", "自研三款", "自研的"],
}
deny = DENY.get(tool)
if not deny:
    sys.exit(0)
txt = open(path, encoding="utf-8").read()
hits = [w for w in deny if w in txt]
if hits:
    print("  ⚠ 内容漂移（非阻塞）%s：含 %s" % (tool, "、".join(hits)))
    print("    后端未与 skill.json 对齐，需重新部署（见 issue #1）")
PY
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

# 2) tools/list —— 与 skill.json 精确比对工具集合（工具名单一来源：skill.json）
printf '[2/3] tools/list\n'
LIST=$(rpc tools/list)
ok "tools/list" "$LIST"
printf '%s' "$LIST" > "$LIST_FILE"
if python3 - "$SKILL_JSON" "$LIST_FILE" <<'PY'; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
import json, re, sys
expected = {t["name"] for t in json.load(open(sys.argv[1])).get("tools", [])}
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
# 描述漂移守卫（非阻塞）：服务端描述不得含已清理的可信度雷区词
DENY = ["三大子公司", "核心数据"]
hits = [(n, w) for n, d in descs.items() for w in DENY if w in d]
if hits:
    print("  ⚠ 描述漂移（非阻塞，后端未与 skill.json 可信度清理对齐）：")
    for n, w in hits:
        print("    - %s：描述含「%s」" % (n, w))
    print("  · 修复：重新部署 www.yueyu.tech 后端，使工具描述与 skill.json 一致")
PY

# 3) 只读工具逐个（顺带做 payload 内容漂移扫描，非阻塞）
printf '[3/3] 只读工具\n'
for t in get_company_info get_service_lines get_methodology get_products get_latest_reports get_contact_info; do
  BODY="$(call_tool "$t")"
  ok "$t" "$BODY"
  printf '%s' "$BODY" > "$LIST_FILE"
  scan_drift "$t" "$LIST_FILE"
done

printf '\n结果：%s 通过，%s 失败\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
