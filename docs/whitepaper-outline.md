# 白皮书大纲 v0.1 —《为什么各家 AI 可见度数字打架》

Owner 槽位: Hermes(Phase 2 首发)。定位: 接住 Forbes / Search Engine Land 对行业的批评势能,
把"测量危机"变成项目的入口叙事。发布形态: 英文为主 + 中文版, 独立站 + 仓库 docs 双挂。
代码仓库: https://github.com/Hahaknight/ai-citation-probe (2026-09-22 M1 建成, public/MIT/main)

## 0. 摘要(一页)
各家 AI 可见度工具数字互相打架, 不是优化失效, 是仪器失灵。本文分解波动来源,
给出可信测量的最低标准清单。

## 1. 现象: 数字打架的证据
- Forbes 2026-08-17: AI Visibility Numbers Are Unreliable — 各工具数字互相矛盾,
  8% 到 X% 的跳变更像工具噪声而非真实变化
- Search Engine Land 2026-01: 7 条硬真相 — 没有任何工具能真正把你弄进 AI 回答;
  没人知道真实问答量
- 现状生态: 卖铲子的在跑(agency 30 天报告 / SaaS 仪表盘), 品牌方没跑出成绩

## 2. 波动来源分解(理论 + 实证)
2.1 理论清单: 模型版本 / 地域 / 采样次数 / prompt 口径 / search_mode 差异
2.2 关键口径: 裸 ChatGPT API 不开 search = 测"模型能力", 不是测"消费者侧 AI 搜索可见度"
    (引 provider 矩阵: search_mode + consumer_surface_equivalence, 见 consistency-metrics-spec 4 节)
2.3 实证(数据钩子, 排期挂 M2 后, 依赖 M1/M2 产出):
    - 同题同引擎两次采样的 verdict agreement rate 分布
    - 同题跨引擎 confusion matrix 实例
    - 一条真实分歧清单样例(带原始证据)
    [HOOK: 需要至少 2 个 provider x 20 题 x 3 采样 的 M2 数据]

## 3. 为什么闭源工具解决不了
方法不透明 -> 数字无法归因 -> 预算不敢加 -> 行业没人跑出成绩(商业闭环卡死的根子)。
只给分数不给公式, 用户无法区分"真实变化"与"工具噪声"。

## 4. 开源也没解决(竞品勘误, 2026-09-21 实测)
- geo-optimizer-skill (859 star) / GEORank (474) / GetCito (418) / geo-checker (8):
  全部是 audit + optimize + track 打法
- 没有一家把"可复现方法论 + 跨引擎一致性评分"当核心卖点
- 结论: 竞品验证了需求, 且留出了"唯一可复现的那一个"的定位空位

## 5. 可信测量的最低标准清单(白皮书的可执行产出)
1. run manifest 可追溯(模型版本/参数/时间窗/问题集 version+hash 成对)
2. 原始响应 - 证据 - 评分三层分离, 可点击回溯
3. not_comparable 显式输出, 不硬造分
4. 一致性公式公开(引用 consistency-metrics-spec)
5. 探针集协议化: semver + PR 流程 + 每份报告标注版本
6. 成本作为一等字段

## 6. 结论
优化手法已被证明有效(Princeton GEO, KDD 2024: 可见度提升最高 40%),
卡住行业的是测量与归因。仪器先于优化 — 引向工具 + 探针集开放共建。

## 附录
A. 探针集协议(probe-set.yaml 规范)
B. 一致性公式全文
C. provider 能力矩阵(含 search_mode / consumer_surface_equivalence)

## 待办 / 依赖
- [ ] M2 数据到位后填 2.3 实证节
- [x] 命名定稿: ai-citation-probe(2026-09-22 owner DM 拍板), 文档占位名已替换
- [ ] 英文版翻译排期(MVP 上线前后)
