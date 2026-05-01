# paper-search 命令速查（paper-survey skill 内引用）

paper-survey 通过 paper-search CLI 完成所有检索/下载/抽取。

## CLI 路径

```bash
uv run --directory d:/skills/paper-search-mcp paper-search <command> [args]
```

## 默认源策略

paper-search 多源选择按风险/收益排序：

| 优先级 | 源组合 | 何时用 |
|---|---|---|
| **默认** | `arxiv,crossref,openreview,doaj` | 所有阶段缺省 — 不含 semantic（429 限流频繁，无 API key 时近不可用） |
| fallback | `arxiv,crossref,openreview,doaj,semantic` | 默认源返 0 结果时再加 semantic |
| broad | `all` | 仅在 fallback 仍 0 结果时（小众主题），耗时长 |

## 阶段 0b 预调研：搜综述

```bash
uv run --directory d:/skills/paper-search-mcp paper-search search "{topic} survey OR review OR tutorial" -n 5 -s arxiv,crossref,openreview,doaj
```

返回 JSON 含候选综述。挑选 1-3 篇下载到 `pdfs/_pre/`。

## 阶段 0c 写 spec：补全 arxiv ID

```bash
uv run --directory d:/skills/paper-search-mcp paper-search search "{paper_simple_name} {first_author} {year}" -n 5 -s arxiv,crossref,openreview,doaj
```

按 fuzzy ≥ 80% 直采，否则 AskUserQuestion。

## 阶段 1 检索下载（按 spec 清单）

按 arxiv ID 直接下载（无需关键词检索）：

```bash
uv run --directory d:/skills/paper-search-mcp paper-search download arxiv {arxiv_id} -o {workdir}/pdfs/
```

## 阶段 1 下载后校验（自动重试）

每篇 PDF 下载后必做 3 项校验：

```bash
# 1. 文件大小 > 30 KB
test $(stat -c %s "{pdf}") -gt 30000 || echo "FAIL: file too small"
# 2. 第一页可抽取（非空，非加密图像型）
python /c/Users/Administrator/.agents/skills/paper-survey/assets/pdf_extraction.py extract_page "{pdf}" 1 | head -c 100
# 3. 标题/第一作者 fuzzy ≥ 80% 匹配 spec 清单
# （由 paper_search_reviewer subagent 验证）
```

任一项失败 → 自动重试下载 ≤ 2 次（不同源轮换），仍失败 → 走用户出口。

下载校验通过后立即按 naming_convention.md 重命名：

```bash
mv {workdir}/pdfs/{arxiv_id}.pdf {workdir}/pdfs/{YYYY}_{venue}_{method}.pdf
```

## 多源失败回退

```bash
# fallback：加 semantic
uv run --directory d:/skills/paper-search-mcp paper-search search "{query}" -s arxiv,crossref,openreview,doaj,semantic

# broad：全源（仅小众主题）
uv run --directory d:/skills/paper-search-mcp paper-search search "{query}" -s all
```

仍失败 → 三个用户出口（见 SKILL.md 阶段 1 流程）：

1. 用户提供 PDF URL → WebFetch 下载到 `pdfs/`
2. 用户提供本地 PDF 绝对路径 → Bash cp
3. 用户决定移出清单 → 写入 spec.md `## 已剔除论文` 段

## 元数据查询（不下载，不用 jq）

```bash
uv run --directory d:/skills/paper-search-mcp paper-search search "{query}" -n 1 -s arxiv | python -c "import json,sys; p=json.load(sys.stdin)['papers'][0]; print(json.dumps({k:p[k] for k in ['paper_id','title','authors','published_date','pdf_url']}, ensure_ascii=False))"
```

用于阶段 0c 验证 arxiv_id 真实可下载（dry-run 等价物）。**不使用 jq**（Windows 默认未装）。

## 已知问题

- Semantic Scholar 无 API key 时频繁 429 限流：默认不用，仅 fallback
- 中文路径偶发 GBK 问题：所有命令用绝对路径 + `-o` 而非 `cd` 切目录
- arXiv 多版本：默认下载最新版（不指定 v 后缀）
