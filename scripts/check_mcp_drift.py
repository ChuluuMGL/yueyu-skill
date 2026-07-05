#!/usr/bin/env python3
"""
Check yueyu-skill against the live MCP endpoint.

Hard-fails when:
  - skill.json and the live server expose different tool names;
  - required fields, parameter keys, enum values, or MCP annotations drift;
  - old brand/service terms reappear in tool descriptions or read-only payloads;
  - canonical facts go missing from read-only payloads (e.g. the high-tech
    enterprise record number, the 5 service-line names, product names) — i.e.
    the server must return correct content, not merely non-banned content;
  - local package contracts regress, especially submit_lead requiring
    name plus phone-or-wechat;
  - version strings drift across skill.json / SKILL.md / README / agents/openai.yaml.

The live server may lag local-only JSON Schema refinements such as anyOf until
the website backend is deployed. That mismatch is reported as a warning by
default; set STRICT_SERVER_ANYOF=1 to make it blocking.
"""
import json
import os
import re
import sys
import urllib.request

MCP_URL = os.environ.get("MCP_URL", "https://www.yueyu.tech/mcp")
SKILL_JSON = os.environ.get("SKILL_JSON", "skill.json")
STRICT_SERVER_ANYOF = os.environ.get("STRICT_SERVER_ANYOF") == "1"
TIMEOUT = 20

READ_ONLY_TOOLS = [
    "get_company_info",
    "get_service_lines",
    "get_methodology",
    "get_products",
    "get_latest_reports",
    "get_contact_info",
]

OLD_TERMS = {
    "get_company_info": ["大瑀", "dycreative", "三大子公司", "核心数据", "整合营销", "AI创意"],
    "get_service_lines": ["大瑀", "dycreative", "整合营销", "AI创意", "达人种草", "效果广告", "出海营销", "兔克", "tktk"],
    "get_products": ["dycreative", "自研三款", "自研的"],
}

DESCRIPTION_DENY = ["大瑀", "dycreative", "三大子公司", "核心数据", "兔克", "tktk"]

# Canonical facts each read-only payload MUST contain (positive correctness).
# Source of truth: skill.json / SKILL.md. If a canonical fact changes, update
# the skill docs AND this table together — the check then keeps it enforced
# end-to-end and catches the backend silently dropping or altering it.
REQUIRED_TERMS = {
    "get_company_info": ["月瑀科技", "GR202533012042", "186-1155-3805"],
    "get_service_lines": ["账号营销", "小红书达人投放", "信息流广告", "线索转化", "营销复盘"],
    "get_methodology": ["3Insights", "4I", "5D"],
    "get_products": ["BrandLens", "MuseWrite", "REDFabric"],
    "get_contact_info": ["chuluu@yueyutech.cn", "186-1155-3805"],
    "get_latest_reports": ["reports"],
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def rpc(method, params=None, rid=1):
    payload = {"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}}
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload, ensure_ascii=False).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read().decode("utf-8", "replace")
    blob = "".join(line[5:].strip() for line in raw.splitlines() if line.strip().startswith("data:")) or raw
    return json.loads(blob)


def server_tools():
    rpc(
        "initialize",
        {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "yueyu-drift-check", "version": "0"},
        },
        1,
    )
    data = rpc("tools/list", {}, 2)
    if "error" in data:
        sys.exit(f"FATAL: tools/list returned an error: {data['error']}")
    return {t["name"]: t for t in data["result"]["tools"]}


def local_doc():
    doc = json.load(open(SKILL_JSON, encoding="utf-8"))
    return doc, {t["name"]: t for t in doc.get("tools", [])}


def enum_by_property(schema):
    out = {}
    for name, prop in (schema.get("properties") or {}).items():
        if isinstance(prop, dict) and "enum" in prop:
            out[name] = tuple(prop.get("enum") or [])
    return out


def required_sets(items):
    return {frozenset(item.get("required", [])) for item in items if isinstance(item, dict)}


def call_tool(name):
    data = rpc("tools/call", {"name": name, "arguments": {}}, 100 + READ_ONLY_TOOLS.index(name))
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def check_schema(local_tools, remote_tools):
    errors, warnings = [], []
    local_names = set(local_tools)
    remote_names = set(remote_tools)
    for name in sorted(local_names - remote_names):
        errors.append(f"  ✗ '{name}' is documented in skill.json but not exposed by the server")
    for name in sorted(remote_names - local_names):
        warnings.append(f"  ⚠ '{name}' is exposed by the server but not documented in skill.json")

    for name in sorted(local_names & remote_names):
        local = local_tools[name]
        remote = remote_tools[name]
        l_schema = local.get("inputSchema") or {}
        r_schema = remote.get("inputSchema") or {}
        l_props = set((l_schema.get("properties") or {}).keys())
        r_props = set((r_schema.get("properties") or {}).keys())
        if l_props != r_props:
            errors.append(f"  ✗ '{name}': params drift — doc={sorted(l_props)} server={sorted(r_props)}")
        l_required = set(l_schema.get("required") or [])
        r_required = set(r_schema.get("required") or [])
        if l_required != r_required:
            errors.append(f"  ✗ '{name}': required drift — doc={sorted(l_required)} server={sorted(r_required)}")
        l_enums = enum_by_property(l_schema)
        r_enums = enum_by_property(r_schema)
        for prop, values in l_enums.items():
            if set(values) != set(r_enums.get(prop) or []):
                errors.append(
                    f"  ✗ '{name}.{prop}': enum drift — doc={list(values)} server={list(r_enums.get(prop) or [])}"
                )
        l_anyof = required_sets(l_schema.get("anyOf", []))
        r_anyof = required_sets(r_schema.get("anyOf", []))
        if l_anyof != r_anyof:
            msg = f"  {'✗' if STRICT_SERVER_ANYOF else '⚠'} '{name}': anyOf drift — doc={sorted(map(sorted, l_anyof))} server={sorted(map(sorted, r_anyof))}"
            (errors if STRICT_SERVER_ANYOF else warnings).append(msg)
        if (local.get("annotations") or {}) != (remote.get("annotations") or {}):
            errors.append(f"  ✗ '{name}': annotations drift")

        desc = remote.get("description") or ""
        hits = [term for term in DESCRIPTION_DENY if term in desc]
        if hits:
            errors.append(f"  ✗ '{name}': live description contains blocked terms: {', '.join(hits)}")

    return errors, warnings


def check_payloads():
    errors, warnings = [], []
    for name in READ_ONLY_TOOLS:
        try:
            data = call_tool(name)
        except Exception as exc:
            errors.append(f"  ✗ '{name}': call failed: {exc}")
            continue
        raw = json.dumps(data, ensure_ascii=False)
        hits = [term for term in OLD_TERMS.get(name, []) if term in raw]
        if hits:
            errors.append(f"  ✗ '{name}': payload contains blocked terms: {', '.join(hits)}")
        missing = [term for term in REQUIRED_TERMS.get(name, []) if term not in raw]
        if missing:
            errors.append(f"  ✗ '{name}': payload missing canonical terms: {', '.join(missing)}")
    return errors, warnings


def check_versions(doc):
    errors = []
    version = doc.get("version")
    checks = [
        ("SKILL.md", r"(?m)^version:\s*([^\s]+)"),
        ("README.md badge", r"badge/version-([^\s)-]+)-green"),
        ("README.md table", r"\|\s*版本\s*\|\s*([0-9]+\.[0-9]+\.[0-9]+)"),
        ("agents/openai.yaml", r"(?m)^version:\s*([^\s]+)"),
    ]
    for label, pattern in checks:
        path = label.split()[0]
        text = read(path)
        match = re.search(pattern, text)
        found = match.group(1) if match else None
        if found != version:
            errors.append(f"  ✗ version drift: {label} has {found!r}; skill.json has {version!r}")
    if f"v{version}" not in read("README.md"):
        errors.append(f"  ✗ README.md must mention stable release v{version}")
    return errors


def check_local_contracts(local_tools):
    errors = []
    submit_schema = (local_tools.get("submit_lead") or {}).get("inputSchema") or {}
    if set(submit_schema.get("required") or []) != {"name"}:
        errors.append("  ✗ local contract: submit_lead must require name")
    if required_sets(submit_schema.get("anyOf", [])) != {frozenset({"phone"}), frozenset({"wechat"})}:
        errors.append("  ✗ local contract: submit_lead must require phone or wechat via anyOf")

    subscribe_schema = (local_tools.get("subscribe_reports") or {}).get("inputSchema") or {}
    channel = ((subscribe_schema.get("properties") or {}).get("channel") or {})
    if set(channel.get("enum") or []) != {"email", "wechat", "webhook"}:
        errors.append("  ✗ local contract: subscribe_reports channel enum must be email/wechat/webhook")

    agent = read("agents/openai.yaml")
    for name in local_tools:
        if f"- name: {name}" not in agent:
            errors.append(f"  ✗ agents/openai.yaml missing tool entry: {name}")
    return errors


def main():
    print(f"Comparing {SKILL_JSON} against {MCP_URL} ...")
    try:
        remote = server_tools()
    except Exception as exc:
        sys.exit(f"FATAL: cannot reach MCP server: {exc}")
    doc, local = local_doc()

    errors, warnings = [], []
    for fn in (
        lambda: check_schema(local, remote),
        check_payloads,
    ):
        e, w = fn()
        errors += e
        warnings += w
    errors += check_versions(doc)
    errors += check_local_contracts(local)

    print(f"\nDocumented tools: {len(local)} | Server tools: {len(remote)}")
    for warning in warnings:
        print(warning)
    if errors:
        print("\nDRIFT DETECTED:")
        for error in errors:
            print(error)
        print("\nFix: update skill.json/SKILL.md/README/agents metadata or deploy the website MCP backend to match.")
        sys.exit(1)
    print("\n✓ No blocking drift — tools, schemas, annotations, payload guardrails (blocked + canonical terms), versions, and local contracts are consistent.")
    if warnings:
        print(f"  ({len(warnings)} non-fatal warning(s) listed above)")


if __name__ == "__main__":
    main()
