# Markdown LaTeX 公式约定

paper-survey skill 全链路（paper_extractor / outline_writer / 最终 md / validation）共用的公式表达契约。

## 分隔符（GFM 风格）

| 类型 | 分隔符 | 示例 |
|---|---|---|
| 行内公式 | `$...$` | 损失函数 $\mathcal{L}_\theta = \mathbb{E}_{x \sim p}[-\log p_\theta(x)]$ 是负对数似然 |
| 行间公式 | `$$...$$`（独占一行，前后空行） | `\n\n$$\dot{x}_t = v_\theta(x_t, t)$$\n\n` |

## 中文紧邻空格规则（**强制**）

GFM 渲染器在中文与 `$` 紧邻时部分失败（如 Typora、GitHub iOS App）。**行内公式前后必须用半角空格隔开中文**：

| 写法 | 渲染 |
|---|---|
| `方程为 $E = mc^2$ ，其中 $m$ 为质量` | ✅ 正确 |
| `方程为$E = mc^2$，其中$m$为质量` | ❌ 部分渲染器无法识别 |

行间公式 `$$...$$` 必须**前后各空一行**，确保被识别为 block 而非 inline：

```markdown
策略目标如下：

$$
J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_t r_t\right]
$$

其中 $\tau$ 是轨迹。
```

## 常用命令清单（subagent 写作参考）

| 命令 | 含义 | 示例 |
|---|---|---|
| `\mathcal{L}` | 花体 L（损失） | $\mathcal{L}$ |
| `\mathbb{E}` | 期望符 | $\mathbb{E}$ |
| `\mathbb{R}^d` | d 维实空间 | $\mathbb{R}^d$ |
| `\theta, \pi, \phi, \nabla` | 希腊字母 / 梯度 | $\theta, \pi, \phi, \nabla$ |
| `\frac{a}{b}` | 分式 | $\frac{a}{b}$ |
| `\sum_{i=1}^N` | 求和 | $\sum_{i=1}^N$ |
| `\int_0^T` | 积分 | $\int_0^T$ |
| `\dot{x}, \hat{y}` | 点导/估计 | $\dot{x}, \hat{y}$ |
| `\| \cdot \|` | 范数符 | $\| \cdot \|$ |
| `a^{(t)}, x_t` | 上下标 | $a^{(t)}, x_t$ |
| `\arg\min, \arg\max` | 优化算子 | $\arg\min, \arg\max$ |

## 公式必含位置（按 skill 阶段强制级别）

| 阶段产物 | 强制级 | 规则 |
|---|---|---|
| paper_extractor 的 extract.md | **鼓励** | 能从 PDF 文本/图说明确定的核心公式用 LaTeX；不能确定时用文字描述并标 `〔p.X 处含公式 N，本 extract 用文字〕` |
| outline_writer 的 outline.md 第 4 章「相关概念与基础理论」 | **强制** | 每个 H3 子节（2.1/2.2/...）至少含 1 个核心定义/损失公式 |
| outline_writer 的 outline.md 第 5 章 papers 描述 | **鼓励** | 各论文核心损失/架构公式如能确定就 LaTeX；不强制 |
| 第 7 章性能对比表 | 不适用 | 数值表用 markdown pipe table，不需要公式 |
| validation 第 4 章 `$` 出现次数 | **≥ 2** | 所有第 4 章子节累计至少 2 处 `$`（行内或行间） |

## 反例（subagent 禁止）

```markdown
❌ 编造未在 PDF 中出现的公式
   写法：$\mathcal{L}_{\text{flow}} = \mathbb{E}[\| v_\theta - u \|^2]$
   原文：仅文字描述「flow matching 损失为 conditional vector field 的均方误差」
   禁止理由：违反反幻觉契约 B（每字段附引文）

❌ 公式与中文紧邻不空格
   写法：$E=mc^2$中E是能量
   禁止理由：渲染失败

❌ 行间公式不空行
   写法：策略：$$\pi_\theta(a|s)$$，其中
   禁止理由：被识别为行内，渲染错乱

❌ $ 配对漏闭合（孤儿 $）
   写法：损失函数 $\mathcal{L}_\theta = \mathbb{E}[-\log p]
   禁止理由：validation #17 latex_formula_well_formed 会 FAIL
```

## validation #17 抽查规则

`validation.py` 第 17 项 `latex_formula_well_formed`：

1. `$` 出现次数为偶数（行内配对）
2. `$$` 出现次数为偶数（行间配对）
3. 第 4 章「相关概念与基础理论」段中 `$` 出现 ≥ 2
4. 抽样 5 处 `$...$` / `$$...$$` 内容，检查是否含已知 LaTeX 命令（`\frac` `\sum` `\theta` `\pi` `\nabla` `\mathbb` `\mathcal` `\dot` `\hat` `\arg` `\int` `_` `^` 等任一），无则警告（疑似空 `$$`）
