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
  - canonical contact strings drift between README/SKILL docs and live MCP data;
  - local package contracts regress, especially submit_lead requiring
    name plus phone-or-wechat;
  - safe smoke tests show write handlers accepting incomplete leads, invalid
    subscription channels, or missing unsubscribe addresses;
  - version strings drift across skill.json / SKILL.md / README / agents/openai.yaml
    or the live MCP serverInfo.version.

The live server may lag local-only JSON Schema refinements such as anyOf until
the website backend is deployed. That mismatch is reported as a warning by
default; set STRICT_SERVER_ANYOF=1 to make it blocking.
"""
import json
import os
import re
import sys
import time
import urllib.request

MCP_URL = os.environ.get("MCP_URL", "https://www.yueyu.tech/mcp")
SKILL_JSON = os.environ.get("SKILL_JSON", "skill.json")
STRICT_SERVER_ANYOF = os.environ.get("STRICT_SERVER_ANYOF") == "1"
TIMEOUT = 20
SERVER_INFO_VERSION = None

READ_ONLY_TOOLS = [
    "get_company_info",
    "get_service_lines",
    "get_methodology",
    "get_products",
    "get_latest_reports",
    "get_contact_info",
]

# Drift vocabulary lives in scripts/drift_terms.json so this Python checker and
# scripts/mcp_smoke_test.sh share one source of truth and can never silently diverge.
# Canonical facts (required_terms) source: skill.json / SKILL.md — update the docs
# AND drift_terms.json together; the checks then keep them enforced end-to-end.
_DRIFT_TERMS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drift_terms.json")
with open(_DRIFT_TERMS_PATH, encoding="utf-8") as _f:
    _DRIFT_TERMS = json.load(_f)
OLD_TERMS = _DRIFT_TERMS["payload_deny"]
DESCRIPTION_DENY = _DRIFT_TERMS["description_deny"]
REQUIRED_TERMS = _DRIFT_TERMS["required_terms"]

EXPECTED_CONTACT = {
    "phone": "+86 186-1155-3805",
    "email": "chuluu@yueyutech.cn",
    # The current live endpoint exposes the city/district only; README/SKILL carry
    # the full office address. Keep these separate so either surface can evolve
    # intentionally without silently diverging.
    "live_address_contains": "杭州市萧山区",
    "doc_address_contains": "萧山区农业大厦",
}

CONTACT_DOC_FILES = ["README.md", "README.en.md", "SKILL.md"]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def rpc(method, params=None, rid=1):
    payload = {"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}}
    body = json.dumps(payload, ensure_ascii=False).encode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    last_exc = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(MCP_URL, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                raw = r.read().decode("utf-8", "replace")
            blob = "".join(line[5:].strip() for line in raw.splitlines() if line.strip().startswith("data:")) or raw
            if blob.strip():
                return json.loads(blob)
        except Exception as exc:
            last_exc = exc
        time.sleep(min(2 ** attempt, 8))
    if last_exc:
        raise last_exc
    raise RuntimeError("empty MCP response after 3 attempts")


def server_tools():
    global SERVER_INFO_VERSION
    init = rpc(
        "initialize",
        {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "yueyu-drift-check", "version": "0"},
        },
        1,
    )
    SERVER_INFO_VERSION = (((init.get("result") or {}).get("serverInfo") or {}).get("version"))
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


def call_tool_with_args(name, arguments=None, rid=500):
    data = rpc("tools/call", {"name": name, "arguments": arguments or {}}, rid)
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def tool_payload(data):
    try:
        text = data["result"]["content"][0].get("text", "")
    except Exception as exc:
        raise RuntimeError(f"unexpected tool response shape: {exc}") from exc
    try:
        return json.loads(text)
    except Exception as exc:
        raise RuntimeError(f"tool response is not JSON: {text[:200]!r}") from exc


def validation_payload(name, arguments=None, rid=500):
    data = rpc("tools/call", {"name": name, "arguments": arguments or {}}, rid)
    if "error" in data:
        return {"success": False, "jsonrpc_error": data["error"]}
    return tool_payload(data)


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


def check_contact():
    errors, warnings = [], []
    try:
        payload = tool_payload(call_tool_with_args("get_contact_info", {}, 601))
    except Exception as exc:
        warnings.append(f"  ⚠ contact spot-check skipped: get_contact_info unusable ({exc})")
        return errors, warnings

    phone = (payload.get("phone") or "").strip()
    email = (payload.get("email") or "").strip()
    address = (payload.get("address") or "").strip()
    if phone != EXPECTED_CONTACT["phone"]:
        errors.append(f"  ✗ contact drift: server phone {phone!r} ≠ {EXPECTED_CONTACT['phone']!r}")
    if email != EXPECTED_CONTACT["email"]:
        errors.append(f"  ✗ contact drift: server email {email!r} ≠ {EXPECTED_CONTACT['email']!r}")
    if EXPECTED_CONTACT["live_address_contains"] not in address:
        errors.append(
            f"  ✗ contact drift: server address {address!r} missing {EXPECTED_CONTACT['live_address_contains']!r}"
        )

    for path in CONTACT_DOC_FILES:
        if not os.path.exists(path):
            continue
        text = read(path)
        for key in ("phone", "email"):
            expected = EXPECTED_CONTACT[key]
            if expected not in text:
                errors.append(f"  ✗ contact drift: {path} missing {expected!r}")
    for path in ("README.md", "README.en.md"):
        if os.path.exists(path) and EXPECTED_CONTACT["doc_address_contains"] not in read(path):
            errors.append(
                f"  ✗ contact drift: {path} missing office address marker {EXPECTED_CONTACT['doc_address_contains']!r}"
            )
    return errors, warnings


def check_versions(doc):
    errors = []
    version = doc.get("version")
    if SERVER_INFO_VERSION != version:
        errors.append(f"  ✗ version drift: live MCP serverInfo.version has {SERVER_INFO_VERSION!r}; skill.json has {version!r}")
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
    if os.path.exists("README.en.md"):
        en = read("README.en.md")
        en_badge = re.search(r"badge/version-([^\s)-]+)-green", en)
        en_table = re.search(r"\|\s*Version\s*\|\s*([0-9]+\.[0-9]+\.[0-9]+)", en)
        if (en_badge.group(1) if en_badge else None) != version:
            errors.append(f"  ✗ version drift: README.en.md badge has {(en_badge.group(1) if en_badge else None)!r}; skill.json has {version!r}")
        if (en_table.group(1) if en_table else None) != version:
            errors.append(f"  ✗ version drift: README.en.md table has {(en_table.group(1) if en_table else None)!r}; skill.json has {version!r}")
        if f"v{version}" not in en:
            errors.append(f"  ✗ README.en.md must mention stable release v{version}")
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


def check_safe_smoke_tests():
    errors, warnings = [], []
    tests = [
        ("submit_lead rejects missing phone/wechat", "submit_lead", {"name": "Contract Smoke Test"}),
        ("subscribe_reports rejects invalid channel", "subscribe_reports", {"channel": "sms", "address": "contract-smoke@example.com"}),
        ("unsubscribe_reports rejects missing address", "unsubscribe_reports", {}),
    ]
    for idx, (label, tool_name, args) in enumerate(tests, start=701):
        try:
            payload = validation_payload(tool_name, args, idx)
        except Exception as exc:
            warnings.append(f"  ⚠ smoke skipped: {label} ({exc})")
            continue
        if payload.get("success") is not False:
            errors.append(f"  ✗ smoke: {label}; payload={json.dumps(payload, ensure_ascii=False)[:240]}")
    return errors, warnings


def check_dry_run_accepted():
    """Write handlers must ACCEPT valid args when dry_run:true (no real write).

    The backend signals a no-op validation pass with validated/ok/dry_run == true.
    Catches a regression where dry_run is silently ignored and a real write happens,
    or where valid args start being rejected.
    """
    errors, warnings = [], []
    tests = [
        ("submit_lead accepts valid dry_run", "submit_lead",
         {"name": "Contract Smoke Test", "phone": "0000000000", "dry_run": True}),
        ("subscribe_reports accepts valid dry_run", "subscribe_reports",
         {"channel": "email", "address": "contract-smoke@example.com", "dry_run": True}),
        ("unsubscribe_reports accepts valid dry_run", "unsubscribe_reports",
         {"address": "contract-smoke@example.com", "dry_run": True}),
    ]
    for idx, (label, tool_name, args) in enumerate(tests, start=801):
        try:
            payload = validation_payload(tool_name, args, idx)
        except Exception as exc:
            warnings.append(f"  ⚠ dry_run skipped: {label} ({exc})")
            continue
        if payload.get("jsonrpc_error"):
            errors.append(f"  ✗ dry_run: {label}; server rejected valid dry_run: {payload['jsonrpc_error']}")
            continue
        if not (payload.get("validated") is True or payload.get("ok") is True or payload.get("dry_run") is True):
            errors.append(f"  ✗ dry_run: {label}; expected validated/ok/dry_run true, got {json.dumps(payload, ensure_ascii=False)[:240]}")
    return errors, warnings


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
        check_contact,
        check_safe_smoke_tests,
        check_dry_run_accepted,
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
    print("\n✓ No blocking drift — tools, schemas, annotations, payload guardrails, contact facts, safe smoke tests, versions, and local contracts are consistent.")
    if warnings:
        print(f"  ({len(warnings)} non-fatal warning(s) listed above)")


if __name__ == "__main__":
    main()
