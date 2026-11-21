# 决策记录

决策记录保存代码、测试和现有文档无法承载的“为什么”和“放弃了什么”。先判断目标仓库属于哪种情况：

- **已有成熟的 ADR / RFC 约定**（例如平铺的 `docs/adr/0001-use-postgres.md`，配有 `docs/adr/README.md` 索引，状态写在文件内，用 `Superseded by` 链接标记取代）：沿用它的目录、编号、索引、状态写法、归档方式、格式和可变性规则（例如“采纳后不可修改，只能由新 ADR 取代”时就不套用下文“implemented 保持事实最新”的规则）。只补齐缺失的规则（何时写、事实如何保持最新、取代如何处理），写进该目录的 README 或 `AGENTS.md`。不迁移到下面的布局；附带脚本的 `notes` 和 `archive` 检查是为下面的布局设计的，应从检查列表移除，或按该约定改写后再启用。
- **没有约定或约定已废弃**：采用下面的 Agent Notes 布局。

## Agent Notes 布局

默认放在 `.agents/notes/`。路径同时编码生命周期和分类：

```text
.agents/notes/
  README.md                       # 规则（必需）
  AGENTS.md                       # 给 agent 的常驻规则（可选）
  implemented/architecture/2026-01-15-use-sqlite.md
  proposed/process/2026-03-01-docs-check-in-ci.md
```

- **lifecycle**：`proposed/`（待评审、未实施）、`implemented/`（已上线）、`rejected/`（已否决），以及 `archived/`。状态变化即移动文件。
- **class**：封闭集合，例如 `feature`、`bug-fix`、`simplification`、`architecture`、`process`、`testing`。小仓库可以减少分类或不分类（路径变为 `{lifecycle}/YYYY-MM-DD-topic.md`）；增删分类要同时更新规则文件和检查脚本中的集合。
- 生命周期和分类目录在第一份对应 note 出现时再建，不需要预建空目录或占位文件。没有值得记录的决策时只写规则文件，不为示范编造 note。仓库中已有的 `.gitkeep` / `.keep` 占位文件不必删除，附带脚本会忽略它们。
- notes 根目录只放规则文件，note 一律放在生命周期目录下。
- 日期是首次提出的日期。note 之间用相对 Markdown 链接互相引用，便于机械检查。
- 这一布局不建集中索引：目录树就是索引，集中索引会重复路径信息并造成提交冲突。（沿用的 ADR 约定若有索引，照常维护它。）

## 何时写

只在有持久的决策理由、且代码 / 测试 / 现有文档无法解释时才写；与代码改动同一提交。已有记录覆盖该决策时更新它，不建重复记录。机械性、局部修改（包括局部 UI 调整）不写。

## 文件格式

前三行固定，便于脚本检查。第 3 行按所在目录取以下一种，逐字一致：

```markdown
Status: proposed
Status: implemented
Status: rejected — 维护成本高于收益
```

只有 `rejected` 带理由（`— ` 后接一行理由）；`proposed` 和 `implemented` 不带日期、括注或理由。完整的 implemented 示例：

```markdown
# Agent Note: 使用 SQLite 存储会话

Status: implemented

## 问题
## 决策
## 备选方案
## 影响
```

正文以“问题”节开头，之后按生命周期要求不同的节：

| lifecycle | 必需节 | 说明 |
| --- | --- | --- |
| `proposed` | 问题、方案、备选方案、验收标准、风险 | 方案可以用将来时 |
| `implemented` | 问题、决策、备选方案、影响 | 用现在时描述已上线的现实；禁止出现方案 / 计划 / 迁移计划 / 验收标准等提案期节 |
| `rejected` | 问题、方案、备选方案 | 冻结的提案，结论写在 Status 行 |

**备选方案节是强制的**：每个真实的备选及其落选原因。只记录真实考虑过的备选，不虚构。节名可以用目标仓库的语言，但规则文件和检查脚本中必须一致。

## 生命周期规则

- **proposed → implemented**：Status 行改为 `Status: implemented`，把“方案”改写为现在时的“决策”，把验收标准和风险并入“影响”或现在时的“测试”节，删除计划。
- **proposed → rejected**：Status 行改为 `Status: rejected — <理由>`，其余内容冻结。
- **implemented 保持与现实一致**：代码移动文件、重命名、改默认值时，在同一改动中更新 note 中的事实（路径、名称、结构），直接改写，不追加变更历史。
- **不改写决策本身**：推翻决策或理由时新建 note 并互相链接。
- **取代检查**：每新建一个 note，搜索覆盖同一决策或机制的旧 note。完全取代的旧 note 可以在把其独特理由、备选和后果保留到新 note 后删除，并修复入站链接；部分取代则两者都保留并互相链接。
- **删除**：只描述机械或小型 UI 调整的 implemented note 可以删除；被否决的 note 只在能防止一个可信的错误时保留。

## 归档与冻结

- 只有 implemented note 能归档：决策已完整上线、理由不太可能指导未来工作、但仍有历史价值时，移动到 `archived/{class}/`，保留 `Status: implemented`，并在其下一行插入 `Archived: YYYY-MM-DD`：

  ```markdown
  # Agent Note: 使用 SQLite 存储会话

  Status: implemented
  Archived: 2026-11-01
  ```

  这是归档时唯一允许的内容修改。
- 仍有用的备选方案、所有权边界、否定性保证、持久化或协议语义、安全规则、重新引入条件时，保持活跃，不归档。
- 归档后永久冻结：不编辑、不重排、不翻译、不移动，也不作为当前行为的依据。文档检查跳过归档文件（包括其外链）；活跃文档仍可链接到归档 note 作为历史引用。
- 不以字数、年龄或配额决定归档。

## 写入目标仓库的文件

- `.agents/notes/README.md`：上述布局、分类表、何时写、格式、生命周期与归档规则。
- `.agents/notes/AGENTS.md`（或并入 README）：每新建 note 触发取代检查；`archived/` 冻结；implemented 保持事实最新但不改写决策。
- 根 `AGENTS.md`：一行创建条件和一行冻结规则，链接到 README。

沿用已有 ADR 时，把对应规则写进该 ADR 目录的 README 或 `AGENTS.md`，根 `AGENTS.md` 链接到那里。
