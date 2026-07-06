# Contributing

感谢你关注月瑀科技 AI Skill。本仓库包含 Skill 定义文件、文档和校验脚本；远程 MCP 服务端由月瑀科技维护，服务端源码不一定与本仓库同一发布节奏。

## 可以贡献什么

- 文档改进：`README.md`、`README.en.md`、`SKILL.md`、`references/` 示例、安装说明。
- 工具合同对齐：发现 `skill.json` 与线上 `tools/list` 的工具名、参数、enum、annotations 不一致时，可提交修正。
- 兼容性补充：更多 IDE / agent 的安装路径和实测结果。
- 配置示例：`assets/mcp-config-example.json` 与 MCP 客户端安装说明。
- 脚本与 CI：`scripts/check_manifest.sh`、`scripts/mcp_smoke_test.sh`、`scripts/check_mcp_drift.py` 和 workflow 增强。

## 提交前请确认

1. 改动工具定义、README、品牌图、CI 或发布材料时，先跑：

   ```bash
   bash scripts/qa.sh
   ```

2. 不要编造案例、客户数量、排名、效果承诺、合同条款或未经公开核验的数据。
3. 写入类工具必须保留前置校验：`submit_lead` 需要姓名加电话或微信；订阅/退订需要明确接收地址。负向 smoke 必须确认缺失/非法参数不会被服务端接受。
4. 如果版本号变化，必须同步 `skill.json`、`SKILL.md`、`README.md`、`README.en.md`、`agents/openai.yaml`，并在合并后同步 tag/release。
5. 如果硬编码联系方式、办公地址、MCP URL 或公开关键事实发生变化，必须同步 README/SKILL/agents 元数据，并更新 `scripts/check_mcp_drift.py` 里的对应常量。
6. 如果更新 `social-preview.png` 或 `assets/brand/yueyu-logo-wordmark.png`，必须先目视确认 logo 正确，再更新 `scripts/check_assets.py` 里的尺寸/哈希。
7. 安全问题、个人信息暴露或密钥泄露不要开公开 issue，按 `SECURITY.md` 处理。

## 不接受的范围

- 商务咨询类 issue：请访问官网或使用 `submit_lead` 留资。
- 远程 MCP 服务端部署请求：可以报告 drift，但实际部署由维护者处理。
- 虚假营销材料、不可核验数据或夸大式效果承诺。

## 流程

1. Fork 或新建分支。
2. 修改并完成本地校验。
3. 提 PR，说明改动动机和测试结果。
4. CI 通过后等待维护者 review。
