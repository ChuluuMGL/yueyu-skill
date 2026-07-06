# Release Checklist

Use this checklist for every `yueyu-skill` release.

## 1. Prepare

- Confirm working tree is clean before release edits.
- Move `CHANGELOG.md` `Unreleased` notes into a dated version section.
- Bump the version in:
  - `skill.json`
  - `SKILL.md`
  - `README.md`
  - `README.en.md`
  - `agents/openai.yaml`
  - `.github/ISSUE_TEMPLATE/bug_report.yml` placeholder if needed
- If the live MCP server behavior changed, update the backend `serverInfo.version` and deploy it.

## 2. Verify Assets

- Check README renders the intended `social-preview.png` image.
- Confirm `assets/brand/yueyu-logo-wordmark.png` is still the correct YUEYU logo.
- Do not substitute the legacy `月瑀营销 / MONSTO MKT` mark.

## 3. Run Local QA

```bash
bash scripts/check_manifest.sh
python3 scripts/check_mcp_drift.py
bash scripts/mcp_smoke_test.sh
```

All three must pass before tagging.

## 4. Publish

```bash
git commit -m "chore: release vX.Y.Z"
git push origin main
gh run list --limit 5
gh run watch <run-id> --exit-status
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file /tmp/yueyu-release-notes.md
```

## 5. Final Checks

- GitHub Actions `CI` and `MCP Drift Check` pass on `main`.
- Release page exists and points to the correct tag.
- `README.md` and `README.en.md` show the same version.
- Live MCP `initialize` returns the expected `serverInfo.version`.
