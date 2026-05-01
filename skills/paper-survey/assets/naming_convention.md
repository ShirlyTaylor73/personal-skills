# PDF 命名规范

paper-survey skill 在阶段 1 下载 PDF 后必须立即按本规范重命名。reviewer 在阶段 1 末尾用本规范的正则验证。

## 格式

`YYYY_{venue}_{method}[_{author}].pdf`

## 字段规则

| 字段 | 规则 | 示例 |
|---|---|---|
| YYYY | 录用年优先；仅 preprint → arXiv 首版年 | 2025_ICLR_MoA |
| venue | 主流缩写：ICLR/NeurIPS/CVPR/ICCV/ECCV/ICML/EMNLP/ACL/NAACL/AAAI/IJCAI/KDD/WWW/SIGGRAPH/TPAMI/TMLR/JMLR；未发表/拒稿/纯 arXiv → `arXiv`；期刊扩展版用期刊缩写；workshop 加 `W` 后缀（`ICLRW`） | 2025_arXiv_SelfMoA |
| method | 优先论文官方简称；连字符去掉（`DeepSeek-R1`→`DeepSeekR1`）；驼峰保留（`SelfMoA`）；无简称→首作者姓氏+关键词（`Liu2024Diffusion`） | 2024_ICLR_MoA |
| author（可选） | 仅同名消歧时加首作者姓氏 | 2024_NAACL_RAG_Lewis vs 2025_arXiv_RAG_Chen |

## 衍生约定

- arXiv 多版本（v1/v2/v3）：默认下最高版本，文件名不带 v 后缀
- 同方法多年迭代（如 RAP 2023 → RAP-Pro 2024）：`2023_arXiv_RAP` / `2024_EMNLP_RAPPro`
- Spotlight/Oral/Best Paper 不进文件名（记录在 spec.md 备注）
- 中文论文：venue 用拼音/英文缩写（如 `计算机学报` → `JoC`），method 用英文简称
- 文件名只用 ASCII（避免 Windows 中文路径在 npm/docx 工具链里偶发的 GBK 问题）

## 验证正则

阶段 1 reviewer 用：

```python
import re
pattern = r'^\d{4}_[A-Za-z]+W?_[A-Za-z0-9]+(_[A-Za-z]+)?\.pdf$'
```

## 阶段 1 reviewer 验证清单

1. 全部文件名匹配上述正则
2. spec.md 论文清单里每条都对应一个 PDF（无遗漏）
3. 每个 PDF 都在 spec.md 清单里（无多余下载）
4. arXiv ID 唯一（去重）
5. 同名 method（如多个 RAG）全部加了 author 后缀

## 常见错误命名纠错对照表

| 错误命名 | 错在哪 | 正确命名 |
|---|---|---|
| `2024_ICLR_混合智能体.pdf` | method 含中文，违反 ASCII-only 约定 | `2024_ICLR_HybridAgent.pdf` |
| `2024_ICLR_DeepSeek-R1.pdf` | method 含连字符，正则不匹配 | `2024_ICLR_DeepSeekR1.pdf` |
| `2024 ICLR MoA.pdf` | 含空格，正则不匹配且路径易碎 | `2024_ICLR_MoA.pdf` |
| `2024_arXiv_MoA_v2.pdf` | v 后缀不进文件名，始终下最高版本即可 | `2024_arXiv_MoA.pdf` |
| `2024_arXiv_MoA.pdf`（实际录用 ICLR'25） | arXiv 首版年 + 预印平台；已有正式录用应更新 | `2025_ICLR_MoA.pdf` |
| `2024_International_Conference_on_Learning_Representations_MoA.pdf` | venue 用全名，超出正则允许的简洁范围且可读性差 | `2024_ICLR_MoA.pdf` |
| `2024_NAACL_RAG.pdf`（存在两篇同名） | 同名 method 未消歧，无法区分来源 | `2024_NAACL_RAG_Lewis.pdf` / `2024_NAACL_RAG_Guu.pdf` |
| `2024_ICLR_Method.pdf`（实际投稿于 ICLR Workshop） | 缺 `W` 后缀，误将 workshop 论文标记为主会 | `2024_ICLRW_Method.pdf` |
| `2023_arXiv_Method.pdf`（实际已发表于 TPAMI） | 已有正式期刊版本应用期刊缩写，不再用 arXiv | `2023_TPAMI_Method.pdf` |
| `2024_Neurips_MoA.pdf` | venue 大小写不统一（NeurIPS 非 Neurips） | `2024_NeurIPS_MoA.pdf` |

## 正则各分组解释

验证正则：`^\d{4}_[A-Za-z]+W?_[A-Za-z0-9]+(_[A-Za-z]+)?\.pdf$`

- `^` → 字符串起始锚点，防止前缀垃圾字符
- `\d{4}` → **YYYY**，四位数字年份（如 `2024`）
- `_` → 第一个分隔下划线，连接年份与 venue
- `[A-Za-z]+` → **venue 主体**，纯字母缩写（如 `ICLR`、`NeurIPS`、`arXiv`）
- `W?` → **workshop 可选后缀**，`W` 出现 0 或 1 次；`ICLRW` 中的 `W` 由此匹配
- `_` → 第二个分隔下划线，连接 venue 与 method
- `[A-Za-z0-9]+` → **method**，字母+数字组合（允许驼峰如 `DeepSeekR1`，不允许连字符/空格/中文）
- `(_[A-Za-z]+)?` → **author 可选后缀**，整体为可选组；若出现则以 `_` 开头后接纯字母姓氏（如 `_Lewis`）；不允许数字，防止混入版本号
- `\.pdf$` → 固定 `.pdf` 扩展名并锚定字符串末尾，`.` 需转义避免匹配任意字符
