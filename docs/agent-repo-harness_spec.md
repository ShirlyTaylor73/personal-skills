# agent-repo-harness 规格

## 目标

新建 skill `agent-repo-harness`，指导 agent 参照 DeepSeek Harness（DSH）的做法，把一个目标仓库整理成便于 agent 工作的仓库：分层 `AGENTS.md`、描述当前事实的 `docs/`、记录决策依据的 Agent Notes，以及可选的可执行检查脚本和 CI 接入。

## 已澄清的需求

1. **职责划分**：skill 负责一次性的调查、设计和搭建；后续日常维护所需的规则必须写进目标仓库自身（根 / 子树 `AGENTS.md`、`docs/AGENTS.md`、notes 规则、检查命令），不依赖再次调用 skill。skill 不设“增量维护模式”。
2. **覆盖范围**：skill 必须同时包含文档体系、检查脚本、CI 三部分的说明与指导。
3. **自动化程度由用户选择**：agent 在调查后向用户说明收益与改动，并提供三档选择：仅文档体系；文档体系 + 本地检查脚本；文档体系 + 检查脚本 + CI。
4. **检查脚本是可运行代码**：检查相对链接、notes 状态与目录一致性及必要结构、文档长度预算、归档 notes 冻结；错误输出指明文件和原因，失败返回非零退出码。
5. **CI**：复用目标仓库已有平台与运行环境，调用与本地相同的命令。
6. **验证**：既验证正常文档通过，也用临时错误样例确认脚本能发现问题，结束后恢复。
7. **不照搬 DSH 细节**：已实施 notes 随代码更新事实、只有归档 notes 冻结；预算只覆盖清单中的文件；规模按目标仓库裁剪。

## 结构

- `SKILL.md`：目的、边界、主流程、询问节点、reference 路由。
- `references/layering.md`：分层规则与需写入目标仓库的维护规则。
- `references/agent-notes.md`：notes 生命周期、格式、取代与归档。
- `references/checks.md`：检查脚本设计、适配与验证。
- `references/ci.md`：CI 接入指导。
- `assets/check_agent_docs.py`：可复制到目标仓库并按需调整的 Python 标准库检查脚本。

## 放置

遵循本仓库规定：`plugins/personal-skills/skills/agent-repo-harness/`，并在 `README.md` 的 skill 表格与安装命令中登记。
