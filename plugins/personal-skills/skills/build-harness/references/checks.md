# 文档检查脚本

检查脚本是目标仓库里的可运行代码，把文档规则中可机械判断的部分变成命令：通过时退出码 0，发现问题时逐条输出“文件:行号: 原因”并返回非零退出码，CI 据此标记失败。脚本不判断内容是否真实、结构是否合理，那部分仍由 agent 对照证据审核。

## 检查什么

按目标仓库选用的文档体系启用，未使用的机制不检查：

| 检查 | 规则 | DSH 对应 |
| --- | --- | --- |
| 相对链接 | Markdown 中的相对链接目标必须存在；跳过外部 URL、行内代码、围栏代码块和归档 notes | `verify-md-links` |
| notes 结构 | 路径为 `{lifecycle}/{class}/YYYY-MM-DD-topic.md`；分类属于封闭集合；`Status:` 与所在目录一致；按生命周期要求必需节；implemented 禁止提案期节；备选方案节必需 | `verify-agent-note-classification`、`verify-agent-note-format` |
| 文档预算 | 只检查清单中列出的常驻文档；超限、清单中文件缺失、上限非法均失败；`--list` 显示用量 | `verify-doc-budgets` |
| 归档冻结 | 已登记的归档文件哈希不变、不被删除；新归档文件须有 `Archived:` 行并显式登记 | `verify-archived-agent-notes` |

按需可以追加的检查：锚点存在性、生成文档是否最新（重新生成后比对）、`CLAUDE.md` 是否仍指向 `AGENTS.md`、文档中的代码块能否编译。只有目标仓库确实存在相应规则时才加。

## 使用附带的实现

[../assets/check_agent_docs.py](../assets/check_agent_docs.py) 是只依赖 Python 标准库的参考实现，覆盖上表四项。

1. 复制到目标仓库（默认 `scripts/check_agent_docs.py`，脚本以自身上一级目录为仓库根）。
2. 修改文件顶部“配置”区，使其与写入目标仓库的规则一致：排除目录、notes 位置、分类集合（空集合表示不分类）、节名（默认中文，可换成英文）、预算清单和归档登记文件路径。规则文字与脚本配置必须一致，改一处时同步另一处。
3. 不使用的检查从默认列表 `CHECKS` 中移除，而不是保留一个必然失败的检查。
4. 建立预算清单 `scripts/doc-budgets.json`：先用 `budgets --list` 测出当前用量，上限取当前用量加约 5%～10% 余量；只列根 `AGENTS.md`、`docs/AGENTS.md` 等常驻文档。计数规则是每个 CJK 字符计 1、其他按空白分词计 1；如果改用其他计数方式，在 `docs/AGENTS.md` 中写明。
5. 已有归档 notes 时运行一次 `archive --write` 登记初始哈希。

目标仓库的主要工具链不是 Python（例如 Node 项目且 CI 中没有 Python）时，可以按同样的规则用仓库语言重写，DSH 就用 TypeScript 实现。重写时保持相同的输出格式和退出码约定。

## 接入仓库

- 提供一个聚合入口命令，与仓库现有命令风格一致：`package.json` 的 `"check:docs"`、`Makefile` 的 `check-docs`、`justfile` 等；没有任务运行器时直接使用 `python3 scripts/check_agent_docs.py`。
- 把该命令写进根 `AGENTS.md` 的命令列表和“完成前检查”规则；在 `docs/AGENTS.md` 中写明各项检查对应哪条规则，以及失败时的处理方式（如预算超限：先迁移，再压缩，最后才在说明理由后提高上限）。
- 仓库已有 pre-commit / lefthook 等钩子时，可询问用户是否加入；不要擅自新增钩子框架。

## 验证

1. 在整理好的目标仓库上运行全部检查，必须通过。
2. 对每项启用的检查构造一个最小错误样例，确认命令失败且输出指向正确的文件和原因。例如：添加一个指向不存在文件的链接；把一个 implemented note 的 Status 改成 proposed；把预算上限改到低于当前用量；修改一个已登记的归档文件。
3. 恢复所有样例（`git checkout` / `git clean` 或手工撤销），再次运行确认通过，并检查 `git status` 没有残留。
4. 在交付报告中列出实际运行过的命令和结果。
