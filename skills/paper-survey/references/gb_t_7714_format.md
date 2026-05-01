# GB/T 7714 参考文献格式

paper-survey skill 阶段 2 paper_extractor 输出每篇论文的 GB/T 7714 条目时，按本文档字段顺序拼装；阶段 5 validation.py 用本文档正则验证完整性。

## 通用规则

- 西文作者：姓 + 空格 + 名缩写；3 个以上作者用 `et al.`
- 中文作者：姓名全名，多作者用逗号分隔，3 个以上 `等`
- 期刊名/会议名英文部分用斜体（markdown 中用 `*期刊名*` 渲染为 italic）
- 文献类型标识：[J] 期刊 / [C] 会议 / [D] 学位论文 / [M] 专著 / [EB/OL] 电子资源；arXiv preprint 用 [J] 加 arXiv 标注
- 出版年与卷期号：期刊为 `年, 卷(期): 页`；会议为 `出版地: 出版者, 年: 页`

## 1. 期刊论文 [J]

字段顺序：`作者. 题名[J]. 期刊名, 出版年, 卷号(期号): 起始页码-结束页码.`

英文样例：
```
LECUN Y, BENGIO Y, HINTON G. Deep learning[J]. Nature, 2015, 521(7553): 436-444.
```

中文样例：
```
张三, 李四, 王五. 深度学习综述[J]. 计算机学报, 2018, 41(7): 1543-1560.
```

## 2. 会议论文 [C]

字段顺序：`作者. 题名[C]//会议论文集名. 出版地: 出版者, 出版年: 起始页-结束页.`

样例：
```
WANG G, ZHU Y, ANANDKUMAR A, et al. Voyager: An open-ended embodied agent with large language models[C]//Proceedings of the International Conference on Learning Representations. 2024.
```

## 3. arXiv preprint [J]

字段顺序：`作者. 题名[J]. arXiv preprint arXiv:{ID}, 出版年.`

> 注：`{ID}` 不带版本后缀（如 `2502.00674`，不写 `2502.00674v2`），下载默认取最新版本（参见 naming_convention.md）。

样例：
```
LI W, LIN Y, XIA M, et al. Rethinking Mixture-of-Agents: Is Mixing Different Large Language Models Beneficial?[J]. arXiv preprint arXiv:2502.00674, 2025.
```

## 4. 学位论文 [D]

字段顺序：`作者. 题名[D]. 学校所在地: 学校名, 出版年.`

样例：
```
张三. 某领域 XXX 算法的研究[D]. 北京: 北京理工大学, 2024.
```

## 5. 专著 [M]

字段顺序：`作者. 书名[M]. 版本（第 1 版可省略）. 出版地: 出版者, 出版年: 起始页-结束页.`

样例：
```
GOODFELLOW I, BENGIO Y, COURVILLE A. Deep Learning[M]. Cambridge: MIT Press, 2016: 100-150.
```

## 6. 电子资源 [EB/OL]

字段顺序：`作者. 题名[EB/OL]. (发布日期)[访问日期]. 网址.`

样例：
```
ANTHROPIC. Claude API Documentation[EB/OL]. (2024-06-01)[2026-05-01]. https://docs.anthropic.com.
```

## skill 内使用规则

- 阶段 2 paper_extractor 输出每篇论文时附 GB/T 7714 条目（按 venue 类型选模板）
- 阶段 4 assemble_md.py 的 `collect_references` 从 extracts/*.md 抽取这些条目，按引用顺序排序、不重复、按 [N] 编号装配第 11 章
- 阶段 5 validation.py 用以下正则验证完整性：

```python
# 期刊论文
pattern_J = r'^[^.]+\. [^.]+\[J\]\. .+, \d{4}.*$'
# 会议论文
pattern_C = r'^[^.]+\. [^.]+\[C\]\/\/.+\. .+, \d{4}.*$'
# 通用文献类型标识检查
pattern_type = r'\[(J|C|D|M|EB/OL)\]'
```

## 常见错误对照

| 错误 | 正确 |
|---|---|
| 缺文献类型标识 `WANG G. Voyager. 2024.` | `WANG G. Voyager[C]//Proc. ICLR. 2024.` |
| 多作者未用 et al. | `WANG G, ZHU Y, ANANDKUMAR A, et al.` |
| 期刊名没斜体 | markdown 中 期刊名用 *italic*（GFM `*期刊名*` 渲染为斜体；assemble_md.py 直接透传 extract 中的 GB/T 7714 字面量） |
| arXiv 写成 \[arXiv\] | 应写 \[J\]. arXiv preprint arXiv:{ID} |
