## Summary

- 

## QA

- [ ] `bash scripts/check_manifest.sh`
- [ ] `python3 scripts/check_assets.py`
- [ ] `STRICT_SERVER_ANYOF=1 python3 scripts/check_mcp_drift.py`
- [ ] `bash scripts/mcp_smoke_test.sh`

## Release / Docs Checks

- [ ] Version surfaces are intentionally unchanged, or `skill.json`, `SKILL.md`, `README.md`, `README.en.md`, `agents/openai.yaml`, and issue-template placeholders are all bumped together.
- [ ] README social preview still renders the approved YUEYU logo.
- [ ] No fabricated client counts, case data, rankings, ROI, platform endorsement, or performance guarantees were added.
- [ ] Write tools still require required contact fields and include privacy notice + explicit user confirmation guidance.
- [ ] If live MCP behavior changed, the website backend was deployed and `serverInfo.version` was checked.
