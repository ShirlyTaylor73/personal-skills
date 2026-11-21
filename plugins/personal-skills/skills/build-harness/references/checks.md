# 文档检查脚本

检查脚本是目标仓库里的可运行代码，把文档规则中可机械判断的部分变成命令：通过时退出码 0，发现问题时逐条输出“文件:行号: 原因”并返回非零退出码，CI 据此标记失败。脚本不判断内容是否真实、结构是否合理，那部分仍由 agent 对照证据审核。

## 检查什么

按目标仓库选用的文档体系启用，未使用的机制不检查：

| 检查 | 规则 | 何时启用 |
| --- | --- | --- |
| `links` | Markdown 相对链接的目标必须存在。只识别真正的链接标签（未转义的 `[...]` 紧跟 `(`），按反斜杠转义和 `%20` 编码还原文件名；支持 `<带空格路径>`、路径中成对括号和引用式定义；跳过外部 URL、纯锚点、行内代码、围栏代码块和归档 notes；不校验锚点是否存在 | 几乎总是 |
| `notes` | notes 根目录必须有规则文件且只放规则文件（`.gitkeep` 等占位文件处处忽略）；路径为 `{lifecycle}/{class}/YYYY-MM-DD-topic.md`；分类属于封闭集合；`Status:` 与所在目录一致；按生命周期要求必需节；implemented 禁止提案期节；备选方案节必需 | 采用 [agent-notes.md](agent-notes.md) 的 Agent Notes 布局时；沿用已有 ADR 时移除或按其约定改写 |
| `budgets` | 只检查清单中列出的常驻文档；超限、清单中文件缺失、上限非法均失败 | 决定为常驻文档设预算时 |
| `archive` | 已登记的归档文件哈希不变、不被删除；新归档文件须有 `Archived:` 行并显式登记 | 使用 Agent Notes 的 `archived/` 时 |

`links` 的范围是有意收窄的：只检查写在单行内的行内链接、图片和引用式定义所指向的本地文件或目录。跨行的链接文字或目标、HTML `<a>` / `<img>`、自动链接、外部 URL 可达性和锚点是否存在都不检查。目标仓库需要这些时，复用仓库已有或成熟的链接检查工具，不要把这个脚本扩展成完整的 Markdown 解析器；两者并存时在 `docs/AGENTS.md` 中写明各自负责的范围。

按需可以追加的检查：锚点存在性、生成文档是否最新（重新生成后比对）、`CLAUDE.md` 是否仍指向 `AGENTS.md`、文档中的代码块能否编译。只有目标仓库确实存在相应规则时才加。

## 使用附带的实现

[../assets/check_agent_docs.py](../assets/check_agent_docs.py) 是只依赖 Python 标准库的参考实现，覆盖上表四项。

1. 复制到目标仓库（默认 `scripts/check_agent_docs.py`，脚本以自身上一级目录为仓库根，也可用 `--root` 指定）。
2. 修改文件顶部“配置”区，使其与写入目标仓库的规则一致：排除目录、notes 位置、分类集合（空集合表示不分类）、节名（默认中文，可换成英文）、允许的规则文件名、预算清单和归档登记文件路径。规则文字与脚本配置必须一致，改一处时同步另一处。
3. 不使用的检查从文件底部的 `CHECKS` 中移除，而不是保留一个必然失败的检查。例如不设预算就移除 `budgets`，也不需要建清单。
4. 设预算时，用初始化命令按当前用量加约 10% 余量生成清单（清单已存在时拒绝覆盖）：

   ```bash
   python3 scripts/check_agent_docs.py budgets --init AGENTS.md docs/AGENTS.md
   python3 scripts/check_agent_docs.py budgets --list
   ```

   只列根 `AGENTS.md`、`docs/AGENTS.md` 等常驻文档。计数规则是每个 CJK 字符计 1、其他按空白分词计 1；改用其他计数方式时在 `docs/AGENTS.md` 中写明。之后调整上限直接编辑清单。
5. 已有归档 notes 时运行一次 `archive --write` 登记初始哈希；之后每次归档新 note 后再运行。

目标仓库的主要工具链不是 Python（例如 Node 项目且 CI 中没有 Python）时，可以按同样的规则用仓库语言重写，保持相同的输出格式和退出码约定。

## 接入仓库

- 提供一个聚合入口命令，与仓库现有命令风格一致：`package.json` 的 `"check:docs"`、`Makefile` 的 `check-docs`、`justfile` 等；没有任务运行器时直接使用 `python3 scripts/check_agent_docs.py`。
- 把该命令写进根 `AGENTS.md` 的命令列表和“完成前检查”规则；在 `docs/AGENTS.md` 中写明各项检查对应哪条规则，以及失败时的处理方式（如预算超限：先迁移，再压缩，最后才在说明理由后提高上限）。
- 仓库已有 pre-commit / lefthook 等钩子时，可询问用户是否加入；不要擅自新增钩子框架。

## 验证

负例只在隔离的临时副本中构造，不在目标仓库的工作树里改动再还原：工作树里可能有用户未提交的改动和刚搭建、尚未提交的文件，`git checkout` / `git clean` 会把它们一起抹掉。

1. 在目标仓库上运行全部已启用检查，必须通过。
2. 用 bash 运行下面的脚本。它在仓库外新建临时目录，复制当前工作树（含未提交文件，不含 `.git`），任一步（包括复制管道两端）失败即停止，结束时删除副本，并确认目标仓库的 `git status` 未变。
   - 错误样例只写进副本中的**普通文件**：坏链接写进副本里新建、事先确认不存在的 `.md` 文件；其他样例（把 implemented note 的 Status 改成 `Status: proposed`、把预算上限改到低于当前用量、修改已登记的归档文件）先用 `[ -f "$f" ] && [ ! -L "$f" ]` 确认目标不是符号链接再改。tar 会原样保留符号链接，改写一个指向副本外的链接会改到真实文件。
   - 脚本区分两类失败：检查以退出码 1 报出预期的样例诊断才算负例成立；退出码 0 表示漏报，2 表示配置 / 参数错误或脚本无法打开，其他值表示复制或执行失败，都不能当作负例通过。

   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   repo=$(git rev-parse --show-toplevel)
   tmp=$(mktemp -d "${TMPDIR:-/tmp}/harness-neg.XXXXXX")
   [ -n "$tmp" ] && [ -d "$tmp" ] || { echo "临时目录创建失败" >&2; exit 1; }
   trap 'rm -rf -- "$tmp"' EXIT
   case "$tmp/" in "$repo"/*) echo "临时目录位于仓库内：$tmp" >&2; exit 1 ;; esac
   before=$(git -C "$repo" status --short)
   (cd "$repo" && tar --exclude=./.git --exclude=./node_modules -cf - .) | (cd "$tmp" && tar -xf -)

   # 错误样例：只写副本中的普通文件
   sample="$tmp/harness-negative-sample.md"
   [ ! -e "$sample" ] && [ ! -L "$sample" ] || { echo "样例文件已存在：$sample" >&2; exit 1; }
   printf '[坏链接](does-not-exist.md)\n' > "$sample"
   expected="harness-negative-sample.md:1: 链接目标不存在"

   set +e
   out=$(python3 "$repo/scripts/check_agent_docs.py" --root "$tmp" 2>&1)
   code=$?
   set -e
   printf '%s\n' "$out"
   case "$code" in
     1) ;;
     0) echo "漏报：检查通过了，负例未被发现" >&2; exit 1 ;;
     2) echo "配置、参数错误或脚本无法打开（退出码 2），不是样例诊断" >&2; exit 1 ;;
     *) echo "检查执行失败（退出码 $code），不是样例诊断" >&2; exit 1 ;;
   esac
   case "$out" in *"$expected"*) ;; *) echo "未出现预期诊断：$expected" >&2; exit 1 ;; esac
   [ "$before" = "$(git -C "$repo" status --short)" ] || { echo "目标仓库状态被改变" >&2; exit 1; }
   echo "负例验证通过"
   ```

3. 逐条核对输出：每个样例都被报出，且指向正确的文件和原因。
4. 再次对目标仓库运行检查，仍应通过。
5. 在交付报告中列出实际运行过的命令和结果。
