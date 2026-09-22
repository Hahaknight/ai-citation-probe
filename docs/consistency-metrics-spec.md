# 跨采样与跨引擎一致性评分 — 公开公式规范 v0.1

Owner 槽位: Hermes(Phase 2 方法论即产品)。度量分层采纳 codex_PM 2026-09-21 的三层定义,
本文档把它转成**公开发布**的公式规范(闭源工具只给分数不给公式, 我们反着来)。
实现归属 codex_PM(M1-M2); 实现与本规范冲突时, 以 PR 讨论为准, 两者必须同步改。

设计立场: **不设单一总分**。一个总分掩盖分歧来源, 正是闭源工具测量危机的一部分。
所有一致性输出都是分层的、可回溯到原始响应的。

## 0. 符号

- 问题 q, provider p, 第 i 次采样 run_i (i = 1..n, n >= 2)
- v_i ∈ {cited, not_cited}: 第 i 次采样中品牌引用判定(判定规则: 证据层输出, 非人工)
- U_i: 第 i 次采样提取的来源 URL 集合
- e_i ∈ E: 证据可比性类别(见第 3 节)

## 1. 采样稳定性(provider 内, intra-provider)

1.1 引用判定一致率 (verdict agreement rate)
    A(q,p) = max(k, n-k) / n, 其中 k = |{i : v_i = cited}|
    即多数派占比。解读: A=1 稳定可见/稳定不可见(结合多数派方向), A=0.5 偶发出现。
    报告必须同时给多数派方向, 禁止只报 A。

1.2 URL 集合相似度 (Jaccard, 成对平均)
    J(q,p) = (2 / (n(n-1))) * Σ_{i<j} |U_i ∩ U_j| / |U_i ∪ U_j|
    约束: v_i = not_cited 的采样**不参与** Jaccard(空集无意义), 单独计数报告;
    若可参与计算的成对数 < 1, 输出 not_comparable, 不硬造分。

## 2. 跨引擎一致性(仅对 q.comparable_providers 声明可比的题计算)

2.1 引用状态混淆矩阵: 对 provider 对 (p_a, p_b), 2x2 矩阵
    M[x][y] = #{q : v(p_a)=x, v(p_b)=y}, x,y ∈ {cited, not_cited}
    报告给矩阵 + 派生指标: 双引率, 单引率(分歧率), 双不引率。

2.2 跨引擎 URL Jaccard: 与 1.2 同式, 集合取各自 provider 的多次采样**并集**。
    口径声明: 并集 = "乐观覆盖"语义 — 若 provider 每次引不同源, 并集虚大、J 偏低,
    反映的是来源池稳定性而非单次质量。故报告**双报** J_union(并集) 与 J_intersect
    (逐采样对直接跨 provider 配对, 同 1.2 成对式), 并在图注写明两者语义差异。
    (2026-09-21 采纳 Claude_engineer review 可选1)

2.3 分歧清单(divergence list): 同一问题 A 引用 B 不引用的逐题对照表,
    附双方原始证据片段 — 这是 hero 功能的核心输出, 解释分歧而不是只报数字。

## 3. 证据可比性(解释层, 四分类)

每 (q, p, i) 输出一个类别:
  - brand_mentioned: 品牌被提及(无论有无引用 URL)
  - brand_with_citation: 品牌被提及且伴随来源 URL
  - citation_only: 有来源 URL 但未提品牌
  - refused_or_unsearchable: 模型拒绝回答 / 声明无法搜索
refused 单独标记, 不参与 1/2 节任何相似度计算。

## 4. 口径标注(随每份报告输出)

- search_mode: none / native_search / web_grounding / unknown (per provider)
- consumer_surface_equivalence: direct / partial / proxy / no
- 裸 ChatGPT API(不开 search)的报告章节必须标注"模型能力测量",
  不得与"真实 AI 搜索可见度"混排同一张对比图。

## 5. 最少披露(每份报告 header)

probe-set version + canonical_hash / 模型版本 / temperature / 采样次数 /
时间窗 / provider profile hash / 成本合计 — 与 run manifest 一一对应, 可点击回溯。

## 6. 跨版本对比规则

跨 probe-set 版本对比时, **只允许按共同 question id 子集计算**:
两次运行的问题集取 id 交集, 所有第 1/2 节指标仅在该子集上重算;
新增或删除的题不得进入均值(防 minor bump 后均值被稀释或抬升)。
(2026-09-21 采纳 Claude_engineer review 可选2)
