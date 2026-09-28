# Audience 第二轮审计摘要

数据：`data/00-ready-to-use-data/sf-tech-week-events-master-slim.json`，1721 场。八个标签可叠加，数量不可相加为活动总数。

| 标签 | 当前场数 |
| --- | ---: |
| Founder | 1378 |
| Investor | 945 |
| Engineer | 858 |
| Marketing | 140 |
| Sales | 163 |
| HR | 156 |
| Creator | 215 |
| PM | 63 |

- 空 audience：107 场，见 `missing.json`（`audience-unlabeled.json` 为兼容副本）。其中 Open to Work 的泛求职者和 Finance Leaders Dinner 的财务负责人没有对应的八类职业标签，继续留空；intent 已对原先 40 场空值统一补上兜底 `Networking`，因此单独的 `intent-missing.json` 是空数组。
- 对全部 1721 场独立生成了逐标签证据，见 `audience-evidence-audit.json`。第一批写回 22 场明确新增及校正，随后又逐场核实并补标 17 场空值活动。`audience-manual-overrides.json` 现记录 34 场逐场校正。
- 已修正的典型例子：Demoscene 的人工确认标签；NEXA 的多身份相关性；Product Leader Dinner 的误加 Founder；CPO & Talent AMA 中 CPO 是 People 职能；Founders' Coffee 的误加 Investor。The (We)ekly Reset 原先人工清空职业标签，后按新的 `Fundraising / Investing` theme 统一映射补为 Founder、Investor；这场尤其值得人工复核。
- `audience-review-queue.json` 还有 508 场需复核，其中 371 场高优先级。清单包含 107 场未人工锁定的空标签活动、227 场存在仅由宽泛旧规则支持的标签，以及 5 个以上标签或缺少公开描述的活动；各组有重叠。298 场存在候选删标，但未做未经核对的批量删除；84 场存在正文角色词带来的候选新增，也未自动写回。

`HR / Hiring` theme 的 90 场现全部有 HR audience，但 HR 总计 156 场，因为标题、描述等还可独立命中。类似地，`Fundraising / Investing` theme 的 362 场现全部有 Funding intent，而 Funding 总计 490 场。主题数量与 audience/intent 总数不必相等。

第二轮脚本：`python3 scripts/audit_event_audiences.py` 只更新审计清单；加 `--apply` 仅写回明确新增与逐场人工校正。不要重跑第一轮的追加式脚本覆盖校正。后续审查时，优先核对原文中的邀请对象、活动安排、嘉宾与赞助商介绍，并把确认结果写入 `audience-manual-overrides.json`，再执行 `--apply` 和 `python3 web/build_data.py`。
