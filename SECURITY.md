# Security Policy

## Reporting Security Issues

Please do not open public GitHub issues for vulnerabilities, leaked secrets, or personal-data exposure.

Email: chuluu@yueyutech.cn

Include:

- A short description of the issue
- Steps to reproduce, if safe to share
- Affected file, endpoint, or MCP tool
- Any logs or response snippets with secrets and personal data removed

## Personal Data And Write Tools

This skill exposes write tools that may collect contact details for business follow-up:

- `submit_lead`: name plus phone or WeChat, with optional company and notes
- `subscribe_reports`: email, WeChat, or webhook URL
- `unsubscribe_reports`: subscription address

Agents must tell users before collecting contact details that the information is submitted only to YUEYU TECH's business team for cooperation follow-up or report notifications, read back the fields to be sent, and call a write tool only after the user's explicit confirmation. Agents collect only the name plus one contact method (or channel plus address for subscriptions), never fabricate or prefill contact details, and do not submit a third party's details without confirming that person's consent.

For deletion, correction, or unsubscribe requests, contact chuluu@yueyutech.cn or use `unsubscribe_reports` where applicable.

## Scope

In scope:

- `skill.json`, `SKILL.md`, README files, and public package metadata
- MCP tool schema or validation drift
- Public docs that could cause unsafe collection or exposure of personal data
- CI scripts and checks in this repository

Out of scope:

- Business consultation, pricing, or service-fit requests
- Spam reports unrelated to repository security
- Attacks requiring compromised user devices or credentials
