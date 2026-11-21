# CI 接入

CI 的作用是在推送或 PR 时自动运行与本地完全相同的文档检查命令，让规则在 agent 或人忘记运行时仍然生效。CI 只调用检查命令，不复制检查逻辑。

## 原则

- **复用现有平台和环境。** 仓库已有 GitHub Actions / GitLab CI / 其他 CI 时，在现有工作流中加一个 job 或 step，沿用其 checkout、运行时版本和缓存方式；没有 CI 时，先向用户确认平台再新建。
- **调用同一个入口命令。** 例如 `pnpm run check:docs`、`make check-docs` 或 `python3 scripts/check_agent_docs.py`，保证本地与 CI 结果一致。
- **触发范围合理。** 文档检查很快，通常在所有 push 和 PR 上运行即可。如果用路径过滤，必须覆盖所有会影响结果的路径：Markdown 文件、notes 目录、检查脚本自身、预算清单和归档登记文件、CI 配置文件。链接检查的结果也取决于被链接的非 Markdown 文件，代码文件被删除或移动同样可能产生坏链接，因此路径过滤通常弊大于利。
- **最小权限。** 文档检查只需要读取仓库，不需要密钥、写权限或网络访问（安装依赖除外）。
- **不设为可忽略。** 不使用 `continue-on-error` 之类的方式让失败变成警告；需要暂缓某条规则时，在脚本配置中显式移除该检查，并在规则文档中说明。

## GitHub Actions 示例

只在仓库没有可复用的工作流时作为起点；有现有工作流时把 step 加进去即可。

```yaml
name: Docs

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python3 scripts/check_agent_docs.py
```

Action 的主版本以目标仓库现有工作流使用的版本为准；新建时查一下当前推荐的主版本。

## 验证

- 本地运行 CI 中的同一条命令并通过。
- 能在不影响共享分支的前提下验证时（例如用户同意推送到临时分支或开 PR），确认 CI job 实际运行并通过；否则在交付报告中说明 CI 配置尚未在远端运行过。推送和开 PR 属于对外操作，需用户授权。
- 在根 `AGENTS.md` 或 `docs/development.md` 中写一句 CI 运行哪些文档检查，链接到入口命令，而不是逐条复述检查内容。
