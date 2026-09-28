# Audience 与 Intent 活动标注标准

本标准用于根据活动的 `name`、`themes`、`formats`、`tracks`、`primary_host` 和 `partiful_description`，给 SF Tech Week 活动标注地图筛选所需的 audience 与 intent。目标是让参加者从不同入口找到同一场相关活动，因此两个字段都允许多标签，不设固定标签数量上限。

## 两个字段分别回答什么

- `audience_inferred`：**以某种身份参加，这场活动与我有关吗？** 明确受邀、能听到相关内容、遇到相关人物或获得相关机会，都可以成为标签依据。某个身份不必是主办方唯一指定的受众。
- `intent_inferred`：**参加这场活动可能实现什么目标？** 包括活动的主要目的，以及文案明确承诺或举例说明的机会；不要求每个目标都是活动的主标题。

例如，介绍服务说“你可能认识下一位投资人、客户或员工”，可同时标记 Funding、Consumer、Hiring 和 Networking。对 audience，这也可能使 Founder、Investor、Sales、HR 等身份觉得活动相关；结合活动形式和上下文逐项判断，无须等待“专为某类人举办”的措辞。

## 最终类别

| 页面标签 | `audience_inferred` 值 | 判定依据 |
| --- | --- | --- |
| Founder | `Founder` | 创业、融资、找客户、招人、结识投资人等内容或机会与创始人相关。 |
| Investor | `Investor` | 投资话题、投资人嘉宾、投资人交流或认识投资人的机会，使投资人这一身份与活动相关。 |
| Engineer | `Engineer` | 技术开发、工具、演示、动手实践或工程师社群与工程师相关。 |
| Marketing | `Marketing` | 市场、品牌、传播、公关或内容推广的内容或机会与其相关。 |
| Sales | `Sales` | 获客、销售、GTM、商务合作或认识潜在客户的机会与其相关。 |
| HR | `HR` | 招聘、人才对接、职场与团队建设的内容或机会与 HR 相关。 |
| Creator | `Creator` | 创作、媒体制作、创作者社群或创作工具与其相关。 |
| PM | `PM` | 产品经理、产品负责人、CPO、产品策略与产品团队相关内容或机会。 |

产品经理和产品负责人归 PM。AI 高管按具体职责及活动内容判断，可同时与 PM、Engineer、Founder 等类别相关；仅有“AI 高管”这一称呼时不强行归类。

| 页面标签 | `intent_inferred` 值 | 判定依据 |
| --- | --- | --- |
| Funding | `Funding` | 融资、投资人对接、募资指导、明确可能认识投资人，或 `tracks` 含 `Fundraising & Investing`、`themes` 含 `Fundraising / Investing`；仅有投资人主办不自动算。 |
| Networking | `Networking` | 活动安排介绍、配对、交流或 mingling；`formats` 含 `Breakfast, Brunch or Lunch` 时直接标记。 |
| Building | `Building` | 参加者有动手开发、原型制作、共创、hackathon 等实际实践机会。谈论“如何 build”本身不算。 |
| Learning | `Learning` | 讲座、演示、课程、panel、Q&A、知识分享等有明确学习内容的环节。 |
| Consumer | `Consumer` | `themes` 含 `B2C / Consumer`，或明确有寻找客户、买家、销售线索、试点合作、认识潜在客户的机会；仅讨论市场或 GTM 不自动算。原 `Customer` 并入此类。 |
| Hiring | `Hiring` | 招聘、求职、人才对接，或明确可能认识未来员工。 |
| Entertainment | `Entertainment` | `themes` 含完整标签 `Media / Entertainment`、`Gaming` 或 `AR / VR`，或参加者观看、参与 Karaoke、喜剧、DJ/舞会、Murder Mystery、Mahjong、电影放映、游戏等娱乐环节。 |

同一场 workshop 可以同时是 Building 和 Learning：既有讲解，也有参加者动手实践。Breakfast、Brunch、Lunch 也可以是 Networking，尤其当活动以相识、交流、配对或结识同行为目的时；即使 `formats` 没有同时标记 Networking，也应结合标题和描述判断。餐叙中有讲座、招聘或融资交流时，还可以叠加其他 intent。

## 证据使用规则

1. 优先阅读活动具体内容。`name` 和 `partiful_description` 中的邀请对象、嘉宾、活动安排、预期收获是主要证据；时间表中的 talks、Q&A、open building、mingling 等动作尤其明确。
2. `formats` 用于补充或核对。例如 Hackathon 支持 Building，Panel / Fireside Chat 支持 Learning，Matchmaking 支持 Networking。`tracks` 若可用，也作辅助线索。形式本身通常无法排除其他 audience。
3. `themes` 提供相关性线索，但不总是直接等同于职业或参加目的。完整标签 `Creators`、`Engineering`、`Fundraising / Investing`、`HR / Hiring`、`Media / Entertainment`、`Gaming`、`AR / VR`、`B2C / Consumer` 按本页的指定映射批量补标；其他主题仍需结合活动内容判断。
4. “可能遇到下一位客户 / 员工 / 投资人”属于明确举出的参加机会，可以给相应 intent 多标签，也可以支持相关身份的 audience 标签。投资人嘉宾、招聘机会等同样可以使 Investor、HR 等身份与活动相关。关键是该人物或机会是否构成参加理由；无关的名单或随手提及不计入。
5. 排除统一的 `#SFTechWeek` 页脚，例如“a week of events hosted by VCs and startups”。这段话不能给每场活动加 Founder、Investor 或 Funding。
6. 如果描述不公开、只有通用页脚，或没有命中已指定的规则，相关字段可留空并标记待人工核查。人工确认的标签优先于自动规则，并记录确认来源。下文 `company`、`brand`、`Building` 等宽泛规则是已指定的批量映射，命中后仍建议复核具体语境。

旧版 `audience_inferred`、`intent_inferred` 和 `_v2` 可以用于发现差异，但不能当成新一轮标注的事实依据。新标注应根据上述原始内容独立判断。

## 已执行的 Intent 规则

运行 `python3 scripts/infer_event_intents.py`，根据标题、公开描述、`themes`、`tracks` 与活动形式重算七个目标标签；`--dry-run` 只预览数量。多标签用 `; ` 分隔，顺序固定为 Funding、Networking、Building、Learning、Consumer、Hiring、Entertainment。统一的 Tech Week 页脚会从描述中移除，即使正文写在页脚后面也保留。`Fundraising & Investing` track 或 `Fundraising / Investing` theme 直接支持 Funding；`Breakfast, Brunch or Lunch` 格式直接支持 Networking，和 Networking、Matchmaking、Happy Hour、Dinner 一样。Panel / Fireside Chat、Roundtable / Workshop、Pitch Event / Demo Day 支持 Learning，Hackathon 支持 Building。`Media / Entertainment`、`Gaming`、`AR / VR` theme 直接支持 Entertainment；`B2C / Consumer` theme 或明确的客户对接线索支持 Consumer。`Customer` 不再是独立标签。Hiring 仍须有较具体的活动文案或对接线索，不能只从主办方推导。Entertainment 也可由标题或正文中具体的表演/游戏线索触发，但不从 `Experiential` 形式单独推导。**若 Funding、Networking、Building、Learning、Hiring 均未命中，输出时仍默认保留 `Networking`**，即使同时命中 Entertainment 或 Consumer；这是兜底标签，不表示文案明确承诺社交机会。关键词批量标注仍有上下文误判风险，应抽样复核，尤其是赞助商介绍、否定句和宽泛的融资/获客讨论。运行 `python3 scripts/export_missing_intent.py` 可同步空 intent 清单（目前应为空数组）。

## 已执行的 Audience 规则

以下五步记录第一轮追加式规则，**不应再直接重跑它们覆盖第二轮结果**。其中 `company/brand -> Founder`、`VP -> Investor`、`Ventures -> Founder+Investor`、`Pitch Event / Demo Day -> 三类` 是待复核的宽泛旧线索，不再单凭它们新增标签。第二轮 `scripts/audit_event_audiences.py` 另将 `HR / Hiring` theme 直接补为 `HR`；这并不证明每场活动只面向 HR，建议抽样复核。

### Audience 第一步：标题直接命中

先只看 `name`，以不区分大小写的完整词匹配身份，并把命中的类别**追加**到 `audience_inferred`（已有标签保留，可多标签）。`Founder/Founders` -> `Founder`，`Investor/Investors` -> `Investor`，`Engineer/Engineers` -> `Engineer`，`PM`、`Product Manager`、`Product Leader`、`CPO` 及其复数 -> `PM`，`Marketing` -> `Marketing`，`Sales` -> `Sales`，`HR` -> `HR`，`Creator/Creators` -> `Creator`。页面上的 `Marketing/Sales` 同时匹配两个数据标签。

这只是标题证据的第一轮；未命中保持空值，留待 themes、formats、description 等后续步骤补充。可用 `python3 scripts/infer_audience_from_name.py` 重新运行这一轮。

### Audience 第二步：Creators 主题

若 `themes` 中包含完整标签 `Creators`，就在已有 `audience_inferred` 后追加 `Creator`；不替换其他身份，也不重复添加。仅对这一主题应用此规则，其他 themes 留待逐项讨论。可用 `python3 scripts/add_creator_audience_from_theme.py` 重跑。

### Audience 第三步：description 中的身份词

先移除 Partiful description 末尾的统一 `#SFTechWeek` 宣传文案和 URL，再查找活动自身文案中的身份词并追加标签。明确提到的嘉宾、可能结识的人或相关机会也可以构成相关性，不要求活动只面向该身份。

| 文字线索（含单复数等变体） | 追加标签 |
| --- | --- |
| founder、co-founder、startup、entrepreneur | `Founder` |
| investor、VC、venture capitalist、angel investor | `Investor` |
| engineer、developer、builder | `Engineer` |
| product manager、product leader、chief product officer、CPO | `PM` |
| marketing、marketer、communications、public relations | `Marketing` |
| sales、business development、GTM、go-to-market | `Sales` |
| HR、recruiter、recruiting、hiring、talent acquisition、people ops | `HR` |
| creator、artist、filmmaker、musician、creative professional | `Creator` |

这些是第一轮字词证据，允许一场活动命中多个身份。`builder` 也会命中 Engineer，即使活动本身是跑步、早餐等社交形式；这类宽泛用法值得后续复核。仅有宽泛主题、词语歧义或缺失 description 的活动仍需后续复核。运行 `python3 scripts/add_audience_from_description.py` 可在前两轮结果上追加标签；`--dry-run` 只预览数量。

### Audience 第四步：明确指向身份的 tracks

| 完整 track 标签 | 追加的 audience |
| --- | --- |
| `Global Founders` | `Founder` |
| `Fundraising & Investing` | `Founder; Investor` |
| `Developer Tools` | `Engineer` |
| `Hackathons and Demos` | `Engineer` |
| `Consumer & Creative AI` | `Creator` |

这些映射参考了官方 track 描述中明确提到的创始人、投资人、工程师或创意从业者。`Enterprise AI`、`Deep Tech` 等可能同时涉及多种职业，目前不凭 track 名称直接添加身份。运行 `python3 scripts/add_audience_from_tracks.py` 追加标签，`--dry-run` 可先预览。

### Audience 第五步：指定的跨字段关键词

| 字段 | 匹配内容 | 追加的 audience |
| --- | --- | --- |
| description | company/companies、brand/brands、CFO/CFOs | `Founder` |
| description | VP/VPs | `Investor` |
| description | Engineering | `Engineer` |
| name | Building、Builder/Builders | `Engineer` |
| name | CTO/CTOs | `Founder; Engineer` |
| themes | 完整标签 `Engineering` | `Engineer` |
| themes | 完整标签 `Fundraising / Investing` | `Founder; Investor` |
| primary_host | Ventures | `Founder; Investor` |
| formats | 完整标签 `Pitch Event / Demo Day` | `Founder; Investor; Engineer` |
| formats | 完整标签 `Hackathon` | `Engineer` |

文本匹配不区分大小写，按完整词或列出的单复数匹配；description 仍先排除统一页脚和 URL。上述是用户指定的相关性规则，尤其 `company`、`brand`、`Building` 和 `Pitch Event / Demo Day` 会覆盖较广，之后可结合活动内容复核。运行 `python3 scripts/add_audience_from_requested_fields.py` 追加标签；`--dry-run` 只预览。

## 讨论过的示例

| 活动 | Audience | Intent | 关键判断 |
| --- | --- | --- | --- |
| `79a58346-8a61-45f8-84ce-cb86b877a7eb`，NEXA “ur +1 is a stranger” | `Founder; Investor; Sales; HR` | `Funding; Networking; Consumer; Hiring` | 文案明确写可能认识下一位投资人、客户或员工；这些机会对相应身份有用，服务本身是介绍与见面。 |
| `ae7919f8-941c-47aa-a4db-cb3e4cd03c19`，Bria x fal x LTX | `Engineer; Creator; PM` | `Networking; Building; Learning` | 明确邀请 builders、developers、product managers；生成式媒体内容支持 Creator，但证据较弱。安排了 talks、Q&A、open building 和 mingling。 |
| `ccab76c7-0dba-4288-b9f5-0269e2d62b4c`，Product Leader Dinner | `PM` | `Networking` | 晚餐面向 CPO，描述明确提到与同行交流；嘉宾曾是 co-founder 不等于整场活动必然面向 Founder。 |
| `dfc52c14-600b-465e-a4d1-f2d2f43979fe`，Demoscene | `Founder; Investor; Creator`，人工确认 | 仅凭公开描述无法可靠确认 | 公开描述只有活动名及通用页脚；三项 audience 来自人工校正，不应由页脚推广到其他活动。 |

## 输出与复核

第二轮用 `python3 scripts/audit_event_audiences.py` 从原始标题、描述、主题、track 和形式独立生成候选证据，不依赖旧标签推导新标签。证据区分 high（标题明确角色）、medium（描述或指定主题/track/形式）、weak（上述宽泛旧线索）；结果在 `audience-evidence-audit.json`，待核项按风险排序在 `audience-review-queue.json`。`--apply` **只追加标题/指定主题/track/Hackathon 的明确标签，并执行 `audience-manual-overrides.json` 中逐场确认的完整替换**；其余新增和删标均留待人工核查。运行 `python3 scripts/export_missing_audience.py` 把空 audience 同步写入 `missing.json` 和兼容文件 `audience-unlabeled.json`；空 intent 则另存于 `intent-missing.json`。人工校正不会被第二轮脚本覆盖。

第二轮特别处理 `PM` 的时间歧义（如 `6 PM` 不代表产品经理）及多种 `#SFTechWeek` 通用页脚写法。`CPO` 也有 Chief Product Officer / Chief People Officer 的歧义，须结合上下文判定；已人工校正的 “CPO & Talent AMA” 属于 HR。

对剩余空值做逐场复核时，明确的职业/职能或明显服务的工作内容可以补标，例如 AI/XR builders -> Engineer、People Leaders -> HR、museum designers -> Creator、企业 AI 买卖双方中的供应商 -> Sales。仅有泛化身份不能强行映射：Open to Work 的求职者不等于 Engineer；Finance Leaders Dinner 的财务负责人不等于 Founder。这两场在当前八类体系下继续留空。`intent_inferred` 的兜底 Networking 也不能反推出任何 audience。

- `audience_inferred` 使用上表中的八个显示名称，顺序固定为 `Founder; Investor; Engineer; Marketing; Sales; HR; Creator; PM`；`intent_inferred` 使用上表中的七个显示名称。两个字段均以 `; ` 分隔多标签；audience 无可靠标签时为空字符串，intent 按上述规则兜底。
- 每个标签最好同时保存触发它的具体证据、证据来源（标题、描述、形式、人工确认）和信心等级；不能用旧 `_v2` 的 reason 或 confidence 解释新标签。
- 优先人工复核：描述缺失、仅有通用页脚、规则之间冲突、标签特别多，以及新旧结果差异较大的活动。
- 人工复核后的结论回写到独立的人工校正记录，保证再次运行时不会被自动规则覆盖。
