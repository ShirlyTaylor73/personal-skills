# paper-survey skill 常见失败模式与对策

## 1. Windows 中文路径 GBK 问题

**症状**：subagent 输出含中文时偶发 `'gbk' codec can't decode` 错误，特别在 Python `print` / docx XML 校验时。

**对策**：

- 工作目录 slug 优先用拼音/英文（`AgenticRL` 优于 `智能体强化学习`）
- 所有 Bash 命令用绝对路径（避免 `cd` 中文目录）
- pdf_extraction.py / validation.py 文件读写一律 `encoding='utf-8'`
- pdf_extraction.py / validation.py 入口必须 `sys.stdout.reconfigure(encoding='utf-8')`
- subagent prompt 禁止 `print()` 长中文，改用 Write 写文件 + Read 读文件

## 2. Semantic Scholar 限流

**症状**：`Rate limited (429). Waiting 4 seconds before retry`，后续检索失败。

**对策**：

- 默认源用 `arxiv,crossref,openreview,doaj`（不含 semantic）
- 单次会话 ≤30 次 search 调用，超出时分批跑
- 0c 阶段补全 arxiv_id 时，先按默认源查，找不到才 fallback 加 semantic

## 4. PDF 抽取失败

**症状**：`pdfplumber` 抽某些 PDF 返回空字符串（图像型 / 加密 / 损坏）。

**对策**：

- 阶段 1 reviewer 在下载后立即调 `pdf_extraction.py extract_page <pdf> 1` 验证非空
- 抽取失败的论文自动加入 spec.md `## 待手动获取` 段，不阻塞其他论文
- 用户出口同阶段 1 失败回退（提供 PDF URL / 本地 PDF / 移出清单）

## 5. subagent 输出格式不规整

**症状**：implementor 输出字段缺引文括号、N/A 写错（如 `不适用` 而非 `N/A-源文本未覆盖`）、章节缩进错位。

**对策**：

- subagent prompt 末尾必须有 "**输出契约**" 段落，给 1 个完整正例 + 1 个反例
- reviewer 第一项检查就是格式合规（regex 扫引文括号 / N/A 字面量）
- 格式 FAIL → 主 Claude γ 修复（直接 sed/Edit 改格式，不重派 subagent）

## 6. 阶段 5 核查 FAIL 反复触发

**症状**：修复一项另一项又 FAIL，达到上限 3 次。

**对策**：

- 升级用户时一次性给出全部 FAIL 项 + 修复历史 + 当前 md 路径
- 用户可选：手动修 md / 重跑该阶段 / 接受当前结果（spec.md 加备注 "已知缺陷"）

## 7. outline.md fenced JSON block 解析失败

**症状**：阶段 4 跑 `python assemble_md.py` 报错 `JSON.parse: ...`，无法组装 md。

**对策**：

- outline_writer 完成后立即在 prompt 中要求 dry-run JSON 解析验证
- fenced JSON 内禁止注释（`//` 或 `/* */`）和 trailing comma
- 若解析失败，主 Claude 直接 Edit outline.md 修 JSON，不重派 outline_writer
- 若整段 fenced 残缺，触发降级路径（第 7 章用定性段落代替）

## 9. ProcessPoolExecutor 在 Windows 上启动失败

**症状**：`pdf_extraction.py verify_quotes_batch` 报 `freeze_support` 或 `RuntimeError`。

**对策**：

- pdf_extraction.py 入口必须 `if __name__ == '__main__': main()` 保护
- Windows 默认 spawn 启动子进程，每个 worker 重新 import 模块；确保模块顶层无副作用
- worker 数 > PDF 数时自动收敛到 PDF 数（已在 verify_quotes_batch 中实现）

## md 时代常见失败模式

### LaTeX `$` 配对错误（validation #17 FAIL）

- 现象：`validation.py` 报「行内 $ 配对失败（N 个）」N 为奇数
- 原因：subagent 漏写闭合 `$`（如 `$x = 1` 而非 `$x = 1$`），或行间 `$$` 内含未转义 `$`
- 排查：`grep -c '\$' <md>` 检查总数；`grep -E '\$\$.*\$\$' <md>` 检查行间是否成对
- 修复：主 Claude Edit 修补漏闭合的 `$`

### fenced JSON 未展开（assemble_md 报错）

- 现象：assemble_md.py 输出 `{"status": "error", "msg": "第 5 章子节 X fenced JSON 解析失败: ..."}`
- 原因：outline_writer 写 papers JSON 时含 trailing comma / 单引号 / 注释
- 排查：用 `python -c` 取出 outline.md 中的 fenced JSON 段（三反引号 + json 起始、三反引号 结束）做 `json.loads`
- 修复：主 Claude Edit outline.md 修 JSON 严格语法

### markdown pipe table 列对齐错位

- 现象：`validation.py` 第 7 章 PASS 但渲染后表格断裂
- 原因：第 7 章 fenced JSON 数组中某行字段含 `|` 字符（如 metric 名「val|test」）
- 修复：转义 `\|` 或用全角 `｜`

### 中文紧邻 `$` 渲染失败

- 现象：md 在 GitHub iOS App / 部分版本 Typora 中公式不渲染
- 原因：行内公式与中文紧邻无空格（如「方程为$E=mc^2$，其中」）
- 修复：subagent prompt 已强制空格规则；如已生成可批量 `sed 's/\([一-鿿]\)\$/\1 $/g'`
