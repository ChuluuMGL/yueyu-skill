#!/usr/bin/env bash
# yueyu-skill 清单静态自检（不联网、无副作用）
# 校验：1) skill.json / SKILL.md / README 徽章与表格 版本号一致；
#       2) 每个工具具备 name/description/inputSchema 及 4 个 MCP 注解，且工具名不重复。
# 用法： bash scripts/check_manifest.sh
# 退出码：0 通过；非 0 有失败。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${SCRIPT_DIR}/.."

python3 - "$ROOT" <<'PY'
import json, os, re, sys
root = sys.argv[1]
errors = []

skill = json.load(open(os.path.join(root, "skill.json"), encoding="utf-8"))
v_json = skill.get("version")

# 1) 版本号跨文件一致
v_skill = None
with open(os.path.join(root, "SKILL.md"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("version:"):
            v_skill = line.split()[1] if len(line.split()) > 1 else None
            break
readme = open(os.path.join(root, "README.md"), encoding="utf-8").read()
m_badge = re.search(r"badge/version-(\d+\.\d+\.\d+)", readme)
m_table = re.search(r"\|\s*版本\s*\|\s*(\d+\.\d+\.\d+)", readme)
v_badge = m_badge.group(1) if m_badge else None
v_table = m_table.group(1) if m_table else None

print("版本：skill.json=%s | SKILL.md=%s | README徽章=%s | README表格=%s"
      % (v_json, v_skill, v_badge, v_table))
for label, v in [("SKILL.md", v_skill), ("README徽章", v_badge), ("README表格", v_table)]:
    if v is None:
        errors.append("读不到 %s 的版本号" % label)
    elif v != v_json:
        errors.append("版本不一致：%s=%s ≠ skill.json=%s" % (label, v, v_json))

# 2) 工具字段 / 注解齐全
HINTS = ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"]
tools = skill.get("tools", [])
if not isinstance(tools, list) or not tools:
    errors.append("skill.json.tools 为空或非数组")
    names = []
else:
    names = []
    for t in tools:
        name = t.get("name") or "<无名>"
        if name in names:
            errors.append("重复工具名：%s" % name)
        names.append(name)
        if not (t.get("description") or "").strip():
            errors.append("%s：缺少 description" % name)
        sch = t.get("inputSchema")
        if not isinstance(sch, dict) or sch.get("type") != "object" or "properties" not in sch:
            errors.append("%s：inputSchema 不是 object 或缺 properties" % name)
        ann = t.get("annotations") or {}
        miss = [h for h in HINTS if h not in ann]
        if miss:
            errors.append("%s：annotations 缺 %s" % (name, ",".join(miss)))

print("工具数：%d" % len(names))
if errors:
    print("\n✗ 清单自检失败：")
    for e in errors:
        print("  - %s" % e)
    sys.exit(1)
print("\n✓ 清单自检通过：版本一致，%d 个工具字段/注解齐全" % len(names))
PY
