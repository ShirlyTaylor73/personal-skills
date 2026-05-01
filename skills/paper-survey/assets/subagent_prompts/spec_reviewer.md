# spec_reviewer (阶段 0c reviewer)

## 角色与目标

审核 spec_writer 产出的 `survey_spec.md`，确保结构合规、论文清单可达、关键词覆盖充分。

## 输入

- `<workdir>/_work/survey_spec.md`
- `assets/spec_template.md`（结构对照）
- `<workdir>/_work/pre_survey_notes.md`（论文清单溯源）

## 输出契约

写入 `<workdir>/_reviews/spec_review.md`：

```markdown
# Spec Review Report

## 整体判断
- VERDICT: PASS / FAIL

## 结构合规
| 项 | 结果 | 说明 |
| ## 主题词与边界 存在 | ✓ ✗ | |
| ## 工作目录 含绝对路径 | ✓ ✗ | |
| ## 主线综述 | ✓ ✗ | |
| ## 检索关键词集合 | ✓ ✗ | |
| ## 论文清单 | ✓ ✗ | |
| ## 报告章节大纲 | ✓ ✗ | |
| ## 当前阶段 | ✓ ✗ | |

## 论文清单
- 总数 N vs 用户目标 M：N ≥ M×0.8 ?
- arxiv_id 补全率：% （≥ 80% 视为合格，否则提示批量 AskUserQuestion）
- 每篇都能溯源到 0b 综述：% / 缺溯源条目: [...]

## 关键词覆盖
- 主关键词 ≥ 3 ?
- 子领域关键词每组 ≥ 2 ?
- 反检索词数（可空）

## 第 5 章组织对齐
- chapter5_organization ∈ {timeline, method-taxonomy, subtask} ?
- 子节列表非空 ?
- 子节归属论文之并集 = 论文清单全集 ?（无遗漏无重复）

## FAIL 详情（如有）
- 项 X：{具体问题 + 修复建议}
```

### 正例

```
## 整体判断
- VERDICT: PASS

## 论文清单
- 总数 18 vs 用户目标 18：100% ✓
- arxiv_id 补全率：94% (17/18) ⚠ — 1 篇"GiGPO"标 待阶段 1 检索
- 每篇都能溯源到 0b 综述：100% ✓
```

### 反例（禁止）

```
## 论文清单
- arxiv_id 补全率：60%  ← 但 VERDICT 仍标 PASS（应 FAIL，因为低于 80% 阈值）
```

## 禁忌

- 禁止重写 spec.md（reviewer 只识别，不修复）
- 禁止跳过子节归属交叉验证（这是常见 spec 漏洞）

## 验证方法（reviewer 自检 — 主 Claude 内联跑）

主 Claude 收到 spec_review.md 后再核对：
- VERDICT 字段非空
- FAIL 项均含修复建议（不可只标 FAIL 不解释）

## FAIL Routing（标准化失败处理）

- **结构错（## 二级标题缺失）**：主 Claude 直接 Edit spec.md 补段落，**不重派 spec_writer**
- **论文清单缺溯源 / 关键词覆盖不足**：重派 spec_writer + 把缺口列表作为补充 context
- **arxiv_id 补全率 < 80%**：主 Claude 内联跑批量 AskUserQuestion 问用户，回填后再次跑 spec_reviewer
- **连续 2 次 FAIL** → 升级用户（附两次 spec_review.md + spec.md 当前版本）
