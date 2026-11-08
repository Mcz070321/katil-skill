---
name: katil-skill
description: Use when 用户说“提示词skill／提示词 skill／KATIL”，指定Seedance 2.5影视提示词，或需要通用 AI 影视创作与导演：电影分镜、剧情短片、文戏表演、动作战斗、恐怖悬疑、爱情、科幻奇幻、现实主义、广告、动画、故事板、长视频及配套角色／场景图提示词。纯转码、压缩和文件修复不触发影视创作。
metadata:
  integration-version: "3.9.0"
  integration-revision: "v3.9.0-evidence-and-delivery-2026-11-08"
  display-name: "KATIL-skill"
  user-alias: "提示词skill"
  ability-count: "240"
  style-count: "60"
  ability-library-version: "2.0.0"
  style-library-version: "1.9.0"
---

# KATIL-skill V3.9.0 · 通用导演核心与 Seedance 2.5 按需适配

KATIL 是**通用 AI 影视创作与导演系统**，不是动作、高速战斗或某一种画风的专用模板。它先理解这次要创作什么，再按维度给模块分配决策权；不预设题材、画风、速度、特效强度或镜头语言。动作、恐怖、爱情、广告、动画都只是可选维度；通用核心负责理解、编排、裁决与验收，专业模块负责深度。

默认先建立多维任务契约，再按决策域加载模块；不把 4～6 秒、180 度轴线、真实物理、最大特效写成所有类型的通用法律。题材可以多选，模块可以多个同时在场；但同一决策域只能有一个主导。用户要安静告别时，不自动打起来；用户要写实拳击时，不套恐怖氛围；用户要产品广告时，不把产品当武器。

## 统一流程

1. **建立多维任务契约。** 确认主导意图、题材（可多选）、媒介、形式、导演模式、时长、观众、硬约束与成功标准；用户已给的不重复问，缺项只问真正影响结果的一处。无秒数不估总长；不再要求先定一个主类型。完整字段、模块决策权与冲突裁决见[通用创作核心](references/general-creative-core.md)，媒介／形式默认值见[默认矩阵](references/defaults-and-medium.md)。
2. **判断导演概念。** 有原创表达空间或需要重新组织主题时，按需读[原创概念](references/creative-concept-engine.md)，区分作者型、约束型与极简型（三档定义见该页）；原著、纪实与产品事实边界优先，极简任务不强加母题。
3. **按决策域加载模块。** 不再只选一个主模式；按题材、媒介、形式与导演模式拆开，给每个决策域指定唯一主导，其他模块只能约束或建议。只读当前任务真正需要的专题，不遍历整库。动作是模块，不是默认；文戏里的一个动作节拍不等于整段动作化。混合任务可同时加载多个模块，例如“恐怖＋爱情＋二维动画”可同时读恐怖、叙事、动画、声音与运镜；禁止的是同一域两个主导，不是多个模块。
4. **按题材、媒介与形式做创作设计。** 动作读[动作编排](references/action-and-shot-compiler.md)，需要奇观／受创再读[特效与受创](references/effects-and-damage.md)，极高速／人海才读[高速与多人](references/high-speed-combat-generation.md)；文戏／爱情读[叙事与表演](references/narrative-and-performance.md)；恐怖／悬疑读[恐怖与悬疑](references/horror-and-suspense.md)；现实主义／广告读[现实主义与广告](references/realism-and-advertising.md)；动画／故事板／长视频读[动画与故事板](references/animation-and-storyboard.md)。先定作品自己的物理与能力规则：写实要承重，超现实要自洽，特效强度不默认最大化。
<!-- SUMMARY of WITNESS@1.2.0 -->
5. **核对关键事件与终态承载。** 对重要动作或叙事变化按需读[镜头执行契约](references/shot-execution-contract.md)，确定观看目标、变化依据和下一状态；已要求明确终态时从结果倒推必要条件与观察机会，冲击帧恢复后逐项承接结果。无时间码稿同样核对串行变化与结果容量。非动作不强塞威胁／接触，开放结尾和不揭示按作品要求。
<!-- END SUMMARY of WITNESS@1.2.0 -->
6. **定时间、事件容量、空间意图、媒介材质与声音。**
<!-- SUMMARY of TIME@1.0.0 -->
   - **总长约束与事件编排。** 默认采用无时间码事件序，多镜用 `分镜01` / `Shot 01`，真一镜用 `镜内阶段01` / `Phase 01`，静态故事板用 `第01格` / `Panel 01`。给定全片及分段时长写入相应视频块并核容量，未给总长按事件推进。精确时间按用户或母稿锁定要求、精确音画同步、已确认 Edit 窗口、技术重叠换算或含时间字段导出的必要范围使用；局部授权只作用于局部。总长、快节奏和模型名沿用默认事件序。局部返修保留已定时序，明确去时码则重编并核容量。完整规则见[通用创作核心](references/general-creative-core.md#katil-time)。
<!-- END SUMMARY of TIME@1.0.0 -->
   - **自适应提示词预算。** 根据故事和场面复杂度组织信息，保留人物／武器约束、能力、台词、运镜与尾态，去除重复与空话。通过观看任务与详略组织节奏，工具限制另列适配。
   - **空间模式与战术意图锁定：** 空间先选 S1 屏幕坐标（默认，表演／动作／普通叙事）、S2 世界坐标（建筑／产品／科学可视化，可用尺寸与方位）、S3 混合（复杂动作／巨物／空战，内部世界图＋屏幕投影）；180 度轴线是 S1／S3 保持方向感的基线，支持有可见证据的动态越轴，实验／梦境／蒙太奇可以有意打破。动作交锋中**锁定角色的战术意图与敌我相对参照**（明确区分“迎敌前压、后撤卸力、诱敌拉扯、绕背换位、转身撤离”并保留可见对手／地标参照，避免“同一瞬间进退混写”或“无参照迎面空跑”造成像逃跑又像进攻的误导）。
   - **视觉材质：** 指定水墨、流体、手绘、定格或混合媒介时按需读[视觉材质与媒介语法](references/visual-material-grammar.md)，核对形态、演化和互动；不把风格名当作效果本身。
   - **声音与节奏：** 声音分对白、环境、动作／Foley、音乐四层；声音目的（音乐主导／声音设计主导／信息主导／未指定）与文字按[默认矩阵](references/defaults-and-medium.md)判断。运镜、空间与声音分别读[导演运镜](references/camera-direction.md)、[空间描述三模式](references/spatial-coordinate-system.md)、[声音与节奏](references/sound-and-rhythm.md)。
7. **按通用标准验收，冲突先返修再交付。** 成稿前执行[镜头执行契约](references/shot-execution-contract.md)的“容量与交付前返修”；动作加查[动作编排](references/action-and-shot-compiler.md)的关键因果、手脚与支点占用，多种强效果并存按[特效与受创](references/effects-and-damage.md)组织主次。保留用户指定速度、强度、材质与必经事件，先优化技能自行补全的编排；已发现的过载或状态冲突不能原样交付。日常创作执行跨类型轻量质量自检（核对契约完整性、意图、叙事、人物、空间、风格、时长承载、声音、可执行性与动作方向／接触／尾态）；需要做系统性验收、版本横向评测、同条件 A/B 或路由抽检时，分别读取[通用验收](references/general-acceptance.md)、[动作视频验收](references/video-acceptance-testing.md)与[路由回归](references/routing-regression.md)；抽检时用 `tests/routing_cases.json` 的固定样本作输入，样本只提供输入与预期，不代表已通过。文字验收与视频验收分开；未实际生成并观看，不宣称成片改善。需要写发布结论、版本对比或跨模型证据声明时，按[证据等级与声明边界](references/evidence-and-claims.md)标注 EV0–EV3，不把结构 PASS 写成成片 PASS。按下一步判断是否需要模型执行适配，再按[完整复制块](references/prompt-delivery-and-language.md)编交付正文；推演与自检留块外。
8. **按需模型适配。** 已明确目标模型时按下方适配路由选择内置模块；未指定模型不加载。适配在导演设计后重组执行表达，保护母稿与用户硬要求，不把渠道参数变成全类型默认。
9. **按需反馈修订。** 用户提供成片、抽帧、音轨或具体反馈时，按[成片故障诊断](references/video-failure-diagnostics.md)区分观察、推断与不确定，定位最小失败接点；未提供结果不自动进行此步，不虚报重测。

## 按任务读取

| 当前任务 | 专题 |
| --- | --- |
| 原创作品需要导演概念、主题回收或受限表达设计 | [原创概念](references/creative-concept-engine.md) |
| 关键事件的因果和可观察性、终幕能否读懂 | [镜头执行契约](references/shot-execution-contract.md) |
| 水墨、流体、手绘、定格与混合媒介材质 | [视觉材质与媒介语法](references/visual-material-grammar.md) |
| 成片、抽帧、音轨或具体用户反馈的失败定位 | [成片故障诊断](references/video-failure-diagnostics.md) |
| 多维任务契约、模块决策权、冲突裁决、通用导演决策 | [通用创作核心](references/general-creative-core.md) |
| 媒介／形式／BGM／字幕／画幅默认值 | [默认矩阵](references/defaults-and-medium.md) |
| 文戏、对白、人物关系、爱情、情绪转折、表演、环境叙事 | [叙事与表演](references/narrative-and-performance.md)（混合剧情与空间锚点可参看[电影叙事](references/cinematic-storytelling.md)） |
| 恐怖、悬疑、心理压迫、未知威胁、怪谈 | [恐怖与悬疑](references/horror-and-suspense.md) |
| 攻防、追逃、身体／能力交锋与实质返修 | [动作编排](references/action-and-shot-compiler.md) |
| 极高速、全程动作、多人／敌海、站桩重复返修 | [高速与多人](references/high-speed-combat-generation.md) |
| 战斗稿视觉增强、画面过弱；原创战斗明确需姿态节拍／夸张透视／打击感 | [视觉精修](references/combat-visual-refinement.md) |
| 设计奇观、复杂效果、材料破坏与受创 | [特效与受创](references/effects-and-damage.md) |
| 运镜、空间防迷向、移焦、复杂跟拍或互斥摄影修订 | [导演运镜](references/camera-direction.md) |
| 复杂空间、巨物／空战、双人换位、主动越轴或 S1／S2／S3 选择 | [空间描述三模式](references/spatial-coordinate-system.md) |
| 严格POV、真一镜、混合摄影、跨段／续段 | [视点与连续](references/viewpoint-and-continuity.md) |
| 现实主义、纪录片、社会题材、自然光（导演模式） | [现实主义与广告](references/realism-and-advertising.md) |
| 产品、品牌、广告、宣传片（形式／用途） | [现实主义与广告](references/realism-and-advertising.md) |
| 二维／三维／定格／国漫／日漫（媒介） | [动画与故事板](references/animation-and-storyboard.md) |
| 故事板、长视频、系列、预告（形式） | [动画与故事板](references/animation-and-storyboard.md)＋[视点与连续](references/viewpoint-and-continuity.md) |
| 实验、梦境、超现实、意识流、纯氛围 | [通用创作核心](references/general-creative-core.md)＋[叙事与表演](references/narrative-and-performance.md)＋[声音与节奏](references/sound-and-rhythm.md) |
| 对白、环境声、Foley、音乐、静默与节奏 | [声音与节奏](references/sound-and-rhythm.md) |
| 小说／章节忠实转化 | **先读**[原著约束](references/novel-faithful-adaptation.md) |
| 角色、场景、故事板图或用户本轮另要的图片提示词 | [资产与故事板](references/asset-prompts.md) |
| 明确Seedance 2.5，或同一作品已确认该模型的续段 | [通用适配](references/model-adaptation.md)＋[2.5执行适配](references/seedance-2.5.md)；参数核对时才读能力档案 |
| 素材职责、锁帧、编辑或延长 | [参考与任务处理](references/reference-and-task-handling.md) |
| 用户回传失败结果、局部修订 | [反馈修订](references/feedback-repair.md) |
| 通用文字验收、类型专项检查、版本横向比较 | [通用验收](references/general-acceptance.md) |
| 发布结论、证据等级、跨模型能力来源声明 | [证据等级与声明边界](references/evidence-and-claims.md) |
| 实际动作视频验收、版本 A/B、失败复现与回归 | [动作视频验收](references/video-acceptance-testing.md) |
| 跨类型路由回归、版本升级抽检 | [路由回归](references/routing-regression.md) |
| 风格转换、新能力或非战斗视效（微距／天象／转场／怪谈）设计 | [60种风格](references/style-library.md)／[240种能力与全类型视效](references/ability-library.md)，只检索相关卡 |
| 需要动作具体写法对比 | [局部示例](references/combat-writing-examples.md)，只在动作任务读 |

普通任务从通用核心、多维任务契约与交付开始；条件命中再加专题，不遍历整库。内部兼容模块共用本技能规则。

## 可选制片能力与规则治理

普通创作只用本入口与命中的专题，交付自然语言提示词。跨集正典、API工程适配、结构化导出或实验评价明确命中时，读取[扩展边界](references/production-boundary.md)；已登记模型的自然语言适配由Core完成。普通任务不探测扩展、注册表或历史账本；扩展缺失不阻止Core创作。

<!-- SUMMARY of ADAPTER@1.3.0 -->
已有母稿时保留来源并派生执行稿；首轮只要执行稿时先整理契约、事件链、观察点与首尾态，再直接编写并核对。模型适配只重组表达，不静默改动硬要求；默认按指定语言和范围交付事件序执行稿，精确时间范围沿用 TIME 规则。素材、母稿、渠道或模式变化后重核受影响项；文字保真、提交兼容性与真实视频证据分别记录。模型事实分官方文档、平台实测与未验证假设；官方文档不能单独支撑 COMPATIBLE，兼容需实测或同任务观察。
<!-- END SUMMARY of ADAPTER@1.3.0 -->
<!-- SUMMARY of EVIDENCE@1.0.0 -->
发布、验收与模型来源声明按 EV0–EV3 标注：EV0 设计、EV1 文本与结构、EV2 单次生成观察、EV3 同条件多次加独立盲评。EV1 不得写成视频或模型通过；无视频保持 PENDING_VIDEO；模型事实分 official、platform_measured、unverified_assumption，官方文档不能单独支撑 COMPATIBLE。
<!-- END SUMMARY of EVIDENCE@1.0.0 -->
<!-- SUMMARY of SEEDANCE@1.3.0 -->
明确指定Seedance 2.5，或同一作品已确认目标的续段，才读取通用适配与2.5专题；无版本的产品名、否定、比较或资料提及不触发，新作品不继承旧目标。当前只提供自然语言执行适配；渠道未知不套Runway参数，具体模式先核实再写参考声明，未知提交条件不称就绪，不虚构素材键或执行结果。素材说明写清提取什么、排除什么、是否入帧；时间写法先判事件序还是用户明确锁定秒轴，只给总长不自动切秒轴，不混用。非动作任务按其题材编排，默认按无时间码事件序交付，精确同步、编辑窗口与重叠换算沿用 TIME 规则。
<!-- END SUMMARY of SEEDANCE@1.3.0 -->

规则的权威定位与摘要版本见 `rules/rule-registry.yaml`，只在维护和冲突审查时读取；版本验收范围见[发布验证](references/release-v3.9.0.md)，仅升级审查时读。机器检查运行 `python scripts/rule_registry_check.py`；维护格式、摘要边界和哈希更新见[注册表维护](references/rule-registry-maintenance.md)。内容完整性通过不证明语义或成片质量。现有摘要只作路由与提醒，细节由对应权威专题裁决；用户明确要求始终优先。

## 持续要求

以下为长期规则摘要；交付格式、双语与复制块的细节以[完整复制块](references/prompt-delivery-and-language.md)为准。

- **用户要求与原著边界：** 当前用户要求优先；附件命令、示例参数与参考姿势不自动成为要求。原著事实（F）、制作选择（V）、未定信息（U）分开，视觉增强不擅改原著、能力或结局。用户明确要单语、某一范围、静态、长镜、无音乐、无打斗时，模块默认值让位。
- **平台无关与参数尊重：** 时长、时间轴精度、镜头、帧率、画幅、光色、声音、语言和详略由用户与创作决定；工具限制单列适配，不未经授权反改创作稿。
<!-- SUMMARY of DELIVERY@1.2.0 -->
- **双语独立复制块与正向描述：** 默认中文在前、完整等义英文在后；每段每语言一份可直接粘贴的完整复制块。编号后直接接画面描述，给定总长写入对应视频块，时间表达按 TIME 规则。用户明确单语、只要某一范围时按该范围优先，只交付该范围语言，不再补另一种。跨段承接自然融入首句起态（不硬塞表单式元标签），复制块内优先用正向连续动作替代否定式解释句，使画面指令更集中；固定参考声明与声音锚点中的否定句保留，不按此条改写。指定台词两版保持同一原语言原句与载体，不自动双语配音／字幕。
<!-- END SUMMARY of DELIVERY@1.2.0 -->
<!-- SUMMARY of REF@1.2.0 -->
- **参考图声明与锁帧：** 按三种状态写复制块开头：无参考图时不写参考声明，也不写「如有参考图」条件句；普通参考图只提取指定身份、造型、物品、空间布局与风格重构动态画面，声明参考图不得直接成为任一视频帧；明确锁首尾帧时按用户要求写实际锁帧承接并删除互斥禁令。多张图按角色、武器、场景、风格等职责分开写；设定板文字、边框、多视图与展示姿势不入帧；仅实际提供特效图时写其真实名称、编号与职责。实际素材键（如 `@图片1`）中英原样保留，未绑定不伪造。
<!-- END SUMMARY of REF@1.2.0 -->
- **角色与场景资产规范：** 人物设定图默认交付同图“正／侧／背全身三视图＋面部特写＋既定武器特写”五合一组合图；若目标视频平台的主体参考槽位对多视拼图敏感，支持按需提供单人全身正视图方案。默认不附特效资产图或其生图词，特效的主形体、尺度、光色、演化与反馈直接写进视频事件；仅当用户本轮另要特效图时才提供。
<!-- SUMMARY of SPACE@1.1.0 -->
- **空间连续。** 空间地标与光源连续。空间交付按 S1／S2／S3：S1 屏幕坐标（画面左／右、前景／中景／远景）与具象地标，不写罗盘方位与抽象米数；S2 世界坐标用于建筑、产品、科学可视化，可按用户要求写尺寸、坐标、楼层与方位；S3 复杂动作／巨物／空战用内部世界图＋屏幕投影，必要时加一句尺度说明。叙事默认保持空间可读；180 度轴线是工具，实验／梦境／蒙太奇可以有意打破，但要让观众感到这是选择而非事故。动作任务中，远程攻防优先前后景同框锚定。
<!-- END SUMMARY of SPACE@1.1.0 -->
<!-- SUMMARY of CONTINUITY@1.2.0 -->
- **身份、持物与视点连续：** 身份、物品数量与受创连续。持物可按剧情换手／收放，先有过程再更新；既定手别优先。严格人眼 POV 不外拍自己；真一镜写清起幅观察状态、主体锁点、转向／航点、环境变化作证，沿连续机位路径分阶段组织；跨段由准确尾态进入下一动作，局部时间表达沿用 TIME 规则；遮挡保留关键因果的观察依据。
<!-- END SUMMARY of CONTINUITY@1.2.0 -->
<!-- SUMMARY of SOUND@1.0.0 -->
- **声音与文字：** 声音与文字按[默认矩阵](references/defaults-and-medium.md)：未经要求不擅自加入音乐、字幕、画面文字与额外旁白，音乐主导、声音设计主导与信息主导任务按目的判断；用户明确指定或原著必要内心声／叙述按原载体保留。
<!-- END SUMMARY of SOUND@1.0.0 -->
- **物理、特效与运镜：** 写实要承重、惯性、材料与伤口可信；科幻／奇幻／武侠／动画先立本片规则，再让后果自洽；超现实可以违反现实物理，但不能违反自己刚建立的规则。特效强度不默认最大化，克制与爆发都是工具。固定、手持、长镜、快切、环绕、POV、蒙太奇、长焦、广角是平等工具，按任务选择，不默认动态高于静态。
- **文字验收与视频验收分开：** 未实际生成并观看，只报告文字设计或用户反馈，不宣称规则升级已改善成片；通用检查按[通用验收](references/general-acceptance.md)，动作专项按[动作视频验收](references/video-acceptance-testing.md)，记录 P0／P1、生成次数与模型设置，样本不足标“不确定”。