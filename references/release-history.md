# KATIL 历史发布说明归档（V3.9.3–V3.10.3）

本文件按发布时原文归档六份独立版本说明，并增加一份 V3.10.3 候选修正摘要，共七节，供审计、回溯与版本对照。`CHANGELOG.md` 只保留当前摘要，`references/fx-ab-testing.md` 只保留实验协议；两者不再重复全文。原文未改写（仅将换行统一为 LF），顺序为新→旧。文中出现的 `references/release-v*.md` 是当时包内路径；V3.10.3 已将六份文件归档到本文件，不再单独存在；V3.10.3 新节来自 `CHANGELOG.md` 与修正报告，不是原始 `release-v` 文件。来源包：`KATIL_Core_V3.10.2.zip`；V3.10.3 修正包：`KATIL_Core_V3.10.3_修正包.zip`。

---

<!-- source: V3.10.3 CHANGELOG + KATIL_Core_V3.10.3_修正报告.md -->

# KATIL Core V3.10.3 · 候选修正 · 2026-11-10

本版以 V3.10.3 原候选包为基线，完成 1 个 P1、1 个 P2、4 个 P3 的修正；发布状态仍为 candidate，修正版不覆盖原包。修正包 95 个文件、527,165 字节，SHA-256 为 `df1b9e632bfb84b51c134ac166b6c7bd8f66d68fe3cbd7a0565c8461bd1b5c7a`。

## 包体与文档

- 将 V3.9.3–V3.10.2 六份发布说明原文恢复到 `references/release-history.md`；`CHANGELOG.md` 只保留摘要与归档说明，不再声称“完整归并”。
- 移除根目录静态快照 `baseline_regression.json`；`scripts/run_regression.py` 的 `--out` 为可选，省略时只打印 stdout，需要时按需重建。
- `fx_compilation_check.py` 新增 `check_payload`，兼容单条标注对象与多用例套件，保留 `ANNOTATED_SPANS_PRESENT_REVIEW_REQUIRED` 与 `EV1_LITERAL_ONLY` 证据边界。

## 修正项

- P1：修复归档说明与实际不符；六份旧原文保留，新增归档存在性、关键词和逐条状态断言。
- P2：测试口径限定 Windows 11／PowerShell 7.6.9／Python 3.12.7：243 项中 242 通过、1 项符号链接测试跳过、0 失败；不写成全平台全部通过。
- P3：G10／G11 明确沿用 V3.10.1 vs V3.10.2，未做 V3.10.3 A/B；`tests/README.md` 修正 T61／T62／G10／G11 的版本归属与重复字样；G10 focus 补主语；回归增加逐条状态断言。

## 验证

单元测试 243 项（242 通过＋1 跳过＋0 失败）；结构回归 162 项（151 UNKNOWN＋11 PENDING_VIDEO＋0 FAIL，suite PASS）；registry、ability 240、style 60、model profile、FX CLI 通过；52 个 Markdown、265 个相对链接 0 缺失；95／95 文件 SHA-256 与清单一致。Linux 未运行。

## 证据边界

以上为 EV1 文本、结构与软件检查。没有真实成片、盲评或平台提交；G10／G11 保持 PENDING_VIDEO；V3.10.3 不改变导演规则，不能据此声称视频质量提升。

---

<!-- source: katil-skill/references/release-v3.10.2.md -->

# KATIL Core V3.10.2 · 复杂终局执行 · 2026-11-10

以本机个人技能目录的 V3.10.1 为基线，在独立工作区编制主技能及同版动作兼容入口。复杂终局在正文前核算可见状态、巨物尺度与跨段交接。触发阈值用于选读专题。默认单段、用户硬约束、既有路由类别和 FX Director 保持原有行为。

## 变更映射

| 来自案例的观察 | 实现位置 | 对应用例 |
| --- | --- | --- |
| A 终局仍见握刀手，断臂、脱刀、无臂扑击与斩首结果未形成可辨的链 | [关键状态与巨物尺度](decisive-state-and-scale.md)第 1 节，动作页补充武器可数性和尾态动词 | T61 / G10 |
| B 近景为人物拳剑与金蓝弧面，巨物形体、交点及相互侵蚀难以确认 | 新页第 2 节，特效页补充同框尺度参照和接触峰值派生 | T62 / G11 |
| 两例的必要变化集中于后段 | 新页第 3 节，主入口路由及镜头执行契约指针 | T61 / T62 |
| 外部诊断素材缺少实际提交记录及完整音画审阅 | `tests/video_regression_manifest.json` 加入已核哈希、证据范围、禁作基线标记 | G10 / G11 保持待测 |

A 在 15.88 秒附近的胸肩斩击与对照稿中段破甲相符，第一次断臂是终局最早缺乏可辨证据的必要状态，实际发生时点未知。B 在 13.50 秒附近的刃光属于中段对抗，终极巨物另查 20 秒后。B 后一组负像保留了人物左右大致轴线，回彩后仍可见类似的对峙，主要缺口是巨物及交点的识别、爆发前的侵蚀。A 测试指定双刀落地属于夹具明确条件，对照稿只明确断臂带刀飞离。尾段容量是可检验的解释，实际根因未知。

## G10／G11 实验协议

沿用[成片 A/B 记录及盲评方法](fx-ab-testing.md)的输入冻结、完整观看、盲评和哈希绑定办法。版本与执行形态分别检验。

1. **版本对照。** 固定同一用户需求、参考与绑定、视频模型、渠道、可控参数、总时长及单段交付形式。用 V3.10.1 和 V3.10.2 各自生成文本，每版每案至少生成三次独立的完整作品。记录提示词作者环境、原始提示词、参数、种子、运行次序和所有失败。
2. **交付形态对照。** 另用同一版 V3.10.2，在同一任务内比较单段 30 秒与三段交接，最终作品时长同为 30 秒，每组每案至少三次完整作品。分段的工具模式、锁帧、剪接和重试属于实验条件，逐项记录。片段数不充当完整作品次数。
3. **盲评。** 随机编号，独立评审完整音画。按 G10 的状态链或 G11 的巨物识别、交点、传播逐项记录时间。失败、无法完成与中途重试均留档，旧成片只用于定位问题。评审记录按真实视频哈希绑定。
4. **结果解释。** 单段通过时保留单段优先。分段只在相应实验中更稳定时作为该类任务的候选路径。两组都失败时，回查模型、素材和参数。单次完整观察只报告本轮现象，版本改善结论须由同条件盲评支持。

## 证据范围

两段旧片只有抽帧及关键窗口观察。对应 Word 文本是《提示词.docx》对照稿。实际提交稿、技能版本、绑定、参数和后期未核实。旧片不满足本技能 EV2 门槛。软件检查属于 EV1，G10／G11 尚未重生成，当前为 `PENDING_VIDEO`。

## 候选修正

初版候选包复查后，动作兼容入口两份重定向文件已同步 3.10.2 并从主入口定位；终局页与 T61 的主语、巨物首次建立的遮蔽条件、T62/G11 的能量巨剑输入均已显式化；单元测试子进程固定 UTF-8；README 与库标签同步 3.10.2。修正版重新打包，SHA 与初版不同。

## 候选包验证

Windows、PowerShell 7.6.9 与 Python 3.12.7（默认 cp936 控制台）下，单元测试共 239 项，238 通过，0 失败，1 项文件符号链接测试因当前环境无法创建而跳过；测试对子进程显式使用 UTF-8，不依赖控制台编码。结构回归 162 项，151 UNKNOWN、11 PENDING_VIDEO、0 FAIL。主技能和动作兼容入口格式、规则注册表、240 项能力及 60 项风格库校验通过。保留候选状态，完整发布门槛包含在支持符号链接的环境复跑及独立成片验证。

---

<!-- source: katil-skill/references/release-v3.10.1.md -->

# KATIL Core V3.10.1 · 特效保真与测试加固 · 2026-11-09

以用户提供的 V3.10.0 压缩包为基线，保留导演核心、FX Director 2.0、事件序默认、场景参考条件、结果后的尾段锁定，以及模型和证据边界。此版针对特效分类覆盖、复杂执行稿保真和可执行的成片对照计划做增量加固，不宣称已改善真实视频质量。

## 本版变更

### 1. 主导类别与用例语义

- 原 `FXT01–FXT15` 保留；新增 `FXT16–FXT21`，分别为元素、光学、变形、数字故障、动态图形、能量的独立主导案例。现在 FX01–FX15 每类均有至少一个主导案例，另保留 FXT10 的无特效对照。
- 将原空间异常用例 FXT07 的主导标签从数字故障改为空间扭曲；将风格化冲击帧 FXT14 从动态图形改为风格化；将火焰主导的 FXT15 从能量改为元素。数字故障和动态图形各有明确新用例；改正若干辅助标签和无特效案例的层级，使其对应请求中真实存在的效果。
- 运行器独立检查每类**主导**覆盖；辅助标签覆盖不能冒充主导覆盖。正反断言、六层枚举及视频证据边界仍执行。分类标签检查不能自动理解实际画面的语义，仍需人工复审。

### 2. 内部设计与执行稿保真

- 按需路由至 `fx-compilation-and-fidelity.md`：内部梳理用户硬约束、事件先后、持续状态及同事件反馈，再编成可复制的外部执行稿；先消除重复、合并相容反馈，不擅自删改用户锁定的速度、强度、画面覆盖、结局、镜头或素材职责。
- 新增 3 组手工设计的完整稿／精简稿以及字面证据检查；负向测试包括全屏效果遗漏、手别变化、尾态丢失和事件顺序颠倒。字面工具对否定、同义、漏标等情况有已知局限：即使片段齐全，状态仍为 `ANNOTATED_SPANS_PRESENT_REVIEW_REQUIRED`，需要人工语义复核；没有长度合格阈值，也不将文字测试当作视频质量。
- 复审时发现一组示例原先只保留物件位置“连续”，未表达“可看清”；已补成“连续且可辨”，并单列对应检查点。这个示例是人工编写的文本夹具，不是模型独立生成结果。

### 3. 三组成片 A/B 方案

- `tests/generation_cases.json` 增加 G07 高速近战／冲击帧、G08 重力领域／大范围破坏、G09 非战斗流体／光学。比较版本为 V3.9.5 与 V3.10.1，每版每组建议至少 3 次，实际须先确认平台和预算。
- `fx-ab-testing.md` 给出冻结同一需求与素材、分别生成版本提示词、控制可用模型设置、记录失败、平衡顺序、遮盲观看、按五项观察指标记录，以及小样本结论限制。
- 这些只是**待执行实验**；没有新生成的视频、实际 Seedance 平台提交、成片观看或独立盲评。G07–G09 的视频状态维持 `PENDING_VIDEO`。

## 实际软件检查

- 在本次 Linux 运行环境中执行 `python -m unittest discover -s tests -p 'test_*.py'`：按本压缩包的分发文件集合执行 **237 项全部通过，0 失败，0 跳过**。原个人安装保留了 12 项更早版本的历史测试，保留它们后完整运行 **249 项全部通过**；这些旧文件不包含在以 V3.10.0 原包为基线的分发压缩包中。其中的媒体校验使用合成夹具，不是成片证据。
- 执行 `python scripts/run_regression.py --cases tests`：结构套件 PASS，共 158 项；没有外部响应时为 **149 UNKNOWN、9 PENDING_VIDEO、0 FAIL**。结构套件 PASS 只说明输入与断言的字段、范围及内在结构通过。
- 执行 `python scripts/rule_registry_check.py`：15 条已登记规则的结构与摘要校验 PASS，语义等价仍为 UNKNOWN。技能格式基础校验通过。
- 能力库 `abilities.json` 与风格库 `styles.json` 分别与 V3.10.0 原包逐字节一致；对应校验为 **240/240** 和 **60/60**。
- 历史 V3.10.0 的测试结果保留在其原发布说明中，不当作本版执行结果。独立成片评审、用户实际素材适配和平台提交均未执行。

## 兼容与使用

`katil-skill/` 是主技能。压缩包另含同套 `direct-cinematic-fights/` 兼容转接入口；若使用环境已存在同名独立技能，不覆盖、不自动合并该独立技能。兼容入口应指向同套 3.10.1 主技能，缺失时明确提示，而不是退回旧模板。

现存可确定性检查无法保证模型遵守事件顺序、特效演化、画面信息或音画同步。实际效果须使用同任务视频和适当的盲评进行判断。

---

<!-- source: katil-skill/references/release-v3.10.0.md -->

# KATIL Core V3.10.0 · FX Director 2.0 · 2026-11-09

本版以 V3.9.5 为基线，把“特效”从单篇 effects-and-damage 扩展为按需加载的特效导演层：先判断任务与世界机制，再选主导类别、分层、生命周期、摄影观察与声音同步。它是增量扩展，不推翻导演核心，不改变事件序默认、240 项能力库、60 项风格库、连续性硬约束与 EV0–EV3 证据边界。

## 核心更新

### 1. 五个新权威专题

- `references/fx-director.md`（FX_DIRECTOR@1.0.0）：区分制作领域／技术门类、15 类视觉特效与六层调度；提供 A–H 决策流程、主导 1 类＋辅助 0–3 类、三档预算、事件级六项、术语 Level 0–3 与 P0/P1/P2 检查。权威范围为特效分类与调度，不裁决能力、伤势、动作结果、摄影锁定或声音授权。
- `references/procedural-fx-grammar.md`（FX_PROCEDURAL@1.0.0）：Niagara-inspired 的设计语法，不是真实 Niagara。生命周期为 Trigger → Spawn/Formation → Initial State → Motion → Interaction → Event Response → Decay → Residue；覆盖发射源、形态、分布、尺度层级、初速度、寿命、运动场、碰撞五问、残留与跨镜状态。
- `references/engine-fx-visual-mapping.md`（FX_ENGINE@1.0.0）：把 Niagara、Niagara Fluids、Chaos、Material/Shader、Lumen、Compositing/Composure、Motion Graphics、Camera/Lens FX 翻译成画面语言；明确 Niagara 不是特效类别、Lumen 不生成粒子或破坏、Compositing 不是 Niagara 模块；除非实际使用对应软件，不得声称 AI 模型调用引擎。
- `references/optical-and-compositing-grammar.md`（FX_OPTICAL@1.0.0）：Bloom/Glow、Lens Flare、Refraction、Chromatic Aberration、Reflection、Volumetric Lighting、Exposure/Clipping、Depth of Field、Heat Haze、Motion Blur 十项光学语法；每项要求光源、介质、摄影动机、触发与恢复，并检查前中后景、透明轮廓、遮挡与主体分离。
- `references/fx-synchronization.md`（FX_SYNC@1.0.0）：以事件为单位组织 Action／Primary FX／Secondary FX／Impact／Environment／Optical／Camera／Audio 八轨；规定接触簇、环境响应前沿、摄影机不制造未发生位移、声音与材质／距离／相位相符，以及特效消散不等于伤势或破坏恢复。

### 2. 分类、分层与预算

- 15 类为 FX01 粒子、FX02 流体、FX03 大气环境、FX04 能量、FX05 元素、FX06 破坏、FX07 光学、FX08 空间扭曲、FX09 冲击、FX10 风格化、FX11 变形、FX12 运动、FX13 环境交互、FX14 动态图形、FX15 故障。分类是创作标签，可多标签但必须指定主导类别；声音不放入 15 类，由 SOUND 管理。
- 六层为 Primary、Secondary、Impact、Environment、Optical/Compositing、Audio；Stylized 贯穿各层，不是第七层。
- 预算分简单、中等、复杂三档；简单效果不写满六项，复杂高潮也要主次、顺序、观察与尾态清楚。不要求每镜凑类别，不默认最大亮度、粒子量、破坏或闪白。

### 3. 入口与旧专题衔接

- `SKILL.md` 增加 5 个按需路由与 5 个规则摘要块：复杂特效分类／六层／预算→fx-director；粒子流体火焰破坏的完整生命周期→procedural；UE5／Niagara／Chaos／Lumen／Shader 术语→engine；光晕耀斑折射色散景深曝光合成→optical；特效与动作环境光学摄影声音同步→fx-sync。简单光效、自然现象与产品微距仍可直接走能力卡或 effects-and-damage，无特效／纯文戏不加载 FX。
- effects-and-damage 继续裁决机制、受力、破坏、伤害与结果；visual-material-grammar 继续裁决材质与媒介；camera-direction 继续裁决机位、焦点、运动与剪辑；sound-and-rhythm 继续裁决声音授权、层次、音乐与静默；model-adaptation 与 seedance-2.5 的模型边界与证据边界不变。
- 能力库标题更新为 KATIL 3.10.0，240 张卡与 A001–A240 未改写；风格库仍为 60 项、v1.9.0。

## 测试与验证

- **单元测试**：`python -X utf8 -m unittest discover -s tests -p "test_*.py"` → 225 项，224 通过、1 跳过（Windows 符号链接不支持）；0 FAIL／ERROR。新增 `tests/test_fx_director.py` 15 项。
- **结构回归**：`python -X utf8 scripts/run_regression.py --cases tests` → suite PASS，149 项（routing 20、execution 60、continuity 4、style 4、audio 4、generation 6、adaptation 36、fx 15），143 UNKNOWN＋6 PENDING_VIDEO，0 FAIL。`baseline_regression.json` 已按 3.10.0 重生成。
- **FX 用例**：FXT01–FXT15 覆盖 15 类与六层；FXT10 为无特效写实，primary_fx=NONE，secondary 为空。所有 FX 项只做结构、分类与设计断言，evidence_boundary=PENDING_VIDEO。
- **注册表**：`python scripts/rule_registry_check.py --sync` 后复跑 → PASS，15 条规则；新增 5 条均为 1.0.0、reviewed、2026-11-09，依赖无循环，authority／summary SHA-256 双向一致。
- **兼容回归**：T34–T60／C04 的正反字段校验、WITNESS@1.3.0 尾段锁定、REF@1.4.0、SEEDANCE@1.5.0 与 V3.9.x 历史用例继续运行，未改写旧结论。

## 证据边界

以上均为文本、结构与软件测试（EV1）。没有真实 Seedance 生成、成片观看、独立盲评或实际提交证据；FXT01–FXT15 的结构 PASS 只表示用例字段、分类覆盖与断言布局有效，不表示模型会遵循 FX 生命周期、光学语法或声画同步，也不表示特效质量已提升。所有视频项保持 PENDING_VIDEO；不得把本版写成成片验证通过、引擎实测或平台提交通过。

## 版本与文件

- 主技能：3.10.0；动作入口：3.10.0；revision：v3.10.0-fx-director-2.0。
- 规则注册表：FX_DIRECTOR／FX_PROCEDURAL／FX_ENGINE／FX_OPTICAL／FX_SYNC 各 1.0.0；旧 10 条版本不变。
- 新增：5 个 FX 权威专题、`tests/fx_cases.json`、`tests/test_fx_director.py`、`references/release-v3.10.0.md`。
- 文件数：主技能 86、动作入口 5，合计 91；保留 `references/release-v3.9.5.md` 及更早发布记录，不改写旧版本号。

---

<!-- source: katil-skill/references/release-v3.9.5.md -->

# KATIL Core V3.9.5 结果发生后的尾段锁定 · 2026-11-09

本版以 V3.9.4 为基线，只处理一个已暴露的问题：双人决斗的决定性结果已经成立，尾段仍继续追加新攻击、召唤、领域或第二结局，导致破灯、胜负与余波不可辨。V3.9.4 已有“从终态倒推”和“尾段检查”，缺的是一条明确的结果后锁定，而不是七条并列新规则。

不改变 240 项能力与视效库、60 项风格库、通用导演核心、事件序默认、连续性规则与 EV0–EV3 证据边界。

## 核心更新

### 1. 结果发生后的尾段锁定（WITNESS@1.3.0）

`references/shot-execution-contract.md` 新增 `<a id="katil-outcome-lock"></a>` 与“结果发生后的尾段锁定”一节：

- **结果点与实际结尾分开**：结果成立后，尾段只承接直接余波、承受、环境沉降、站位与呼吸、视线或声音余响，或用户已明确要求的下一阶段。
- **禁止尾段再开事件**：不得新开独立攻击、召唤、领域、增援、追逐目标或第二结局；不得用新巨物、新战场或新增支线替换已经分出胜负的双人主体。分镜节点更多、总长仍有余量，都不是重写尾段的理由。
- **反转条件化**：用户明确要求诈死、反杀、二次觉醒、幕后新敌或续章钩子时，须有前置触发、可见因果与新状态；没有前置触发、只靠尾段追加翻盘，仍按新开事件处理。
- **多线例外**：已建立的其他未解决威胁可以继续，但不得切回已经结束的双人决斗再开一轮；群像收束要能指出哪条线仍在进行、哪条线已经结束。
- **交付前检查**：从结果发生点追到实际结尾，查新独立事件、主体替换与第二结局；胜负、直接后果与余波至少各有一项可辨，但不要求每项独立成镜。
- **范围限制**：本条只约束结果成立后的尾段，不限制结果发生前的多线并发、交叉剪辑、必要反击，也不限制用户指定的开放式结尾。

### 2. 执行与验收同步

- `references/high-speed-combat-generation.md`：终点段增加“决定性结果成立后，尾段只承接直接余波、存亡与状态沉降，不再开新回合、换新巨物或补第二结局；用户明确要求的反转须有前置触发”，并链接 `shot-execution-contract.md#katil-outcome-lock`。
- `references/video-acceptance-testing.md`：尾段检查增加“结果成立后是否又新开独立攻击、召唤、领域、增援、追逐或第二结局，或用新巨物／新战场替换已分出胜负的主体”，用户明确要求且有前置触发、可见因果的反转／诈死／二次觉醒除外。
- `SKILL.md`：WITNESS 摘要升至 1.3.0，加入结果后尾段锁定句；结果发生前的多线、必要反击与开放式结尾仍按原规则处理。

### 3. 新增 T60 回归

`tests/execution_cases.json` 新增 T60：同一 30 秒双人决斗做九节点过载版与六节点终态链两版，人物、兵器、场景、总长和最终胜负相同，只允许结果发生后的尾段事件容量不同。must_hold 覆盖结果点分离、尾段只承接余波、破灯／胜负／余波可辨、反转前置触发与多线例外；must_reject 覆盖结果后再开独立事件、巨物／新战场替换双人主体、第二结局、终态不可辨、无触发反转，以及把结果前必要反击误判为尾段新开事件。

## 测试与验证

- **单元测试**：`python -X utf8 -m unittest discover -s tests -p "test_*.py"` → 210 项，209 通过、1 跳过（Windows 符号链接不支持）；0 FAIL／ERROR。
- **结构回归**：`python -X utf8 scripts/run_regression.py --cases tests` → suite PASS，134 项（routing 20、execution 60、continuity 4、style 4、audio 4、generation 6、adaptation 36），128 UNKNOWN＋6 PENDING_VIDEO，0 FAIL。`baseline_regression.json` 已按 3.9.5 重生成。
- **结构化用例**：`STRUCTURED_IDS` 为 T34–T60＋C04；T60 的正反断言非空、无重复、无交集。T60 结构可校验，但没有新增文本执行输出，仍为 UNKNOWN。
- **注册表**：`python scripts/rule_registry_check.py --sync` 后复跑 → PASS，10 条规则，WITNESS@1.3.0 的 authority／summary 双向 SHA-256 一致；其余 9 条版本不变。
- **测试文件**：新增 `tests/test_v395_outcome_lock.py` 5 项，覆盖 T60 字段、过载与收束对照、权威文档锚点与条件化反转、验收与高速文档引用、WITNESS 1.3.0 摘要。V3.9.4 的 G2 16 条记录是历史文本证据，不是 3.9.5 新执行，也不导入本版。

## 证据边界

以上均为文本、结构与软件测试（EV1）。没有真实 Seedance 生成、成片观看、独立盲评或实际提交证据；T60 的结构 PASS 只表示用例字段与断言布局有效，不表示模型会遵循结果锁，也不表示外部案例的尾段问题已经修复。外部真实案例仍按 BASELINE_OBSERVED_PARTIAL 记录，所有视频项保持 PENDING_VIDEO；不得把本版写成成片验证通过或破框／收束能力已提升。

## 版本与文件

- 主技能：3.9.5；动作入口：3.9.5。
- 规则注册表：WITNESS@1.3.0；REF@1.4.0、SEEDANCE@1.5.0，其余 7 条版本不变。
- 新增：`references/release-v3.9.5.md`、`tests/test_v395_outcome_lock.py`。
- 文件数：主技能 78、动作入口 5，合计 83；保留 `references/release-v3.9.4.md` 与 `release-v3.9.3.md` 作为历史发布记录，不改写旧版本号。

---

<!-- source: katil-skill/references/release-v3.9.4.md -->

# KATIL Core V3.9.4 场景参考与摄影决策一致性修复 · 2026-11-09

本版以 V3.9.3 为基线，修复旧版把“防锁死”写成局部起幅、前景滑出、立即脱框和相邻镜头强制变化的问题。目标不是更强破框，而是让场景参考、用户指定摄影目标、叙事观察任务与画面空间证据共同决定镜头，不再用一条通用强制规则反改用户已经确定的构图、机位与运动。

不改变 240 项能力与视效库、60 项风格库、通用导演核心、AW／CAM／VFX／SD25 模块、事件序默认、连续性规则与 EV0–EV3 证据边界。

## 核心更新

### 1. 四维判断与证据分级（REF@1.4.0）

`references/reference-and-task-handling.md` 新增四个可同时成立的维度：

- **A 素材用途**：无参考、语义场景参考、强制首帧、首尾帧、视频延长／编辑。
- **B 摄影目标**：固定机位、Zoom、Dolly／Tracking、旋转／摇镜、分镜切换、真一镜。
- **C 叙事任务**：宏观尺度、空间关系、人物行动、细节、情绪、悬念、产品信息。
- **D 场景证据**：K 已知（图中可见）、I 合理推断（须标明设计）、U 未知（无依据不锁死）。

四维不是四选一状态机。只有同时满足“有相关场景参考、任务确需换视角／探索空间／真实机位位移、素材模式允许、画面有可描述空间依据”时，才建议换视角、局部起幅或真实位移；否则保持用户构图。用户指定固定机位、纯 Zoom、真一镜或锁首帧时，防锁死建议不得反改。

### 2. SR-A–E 条件化

- **SR-A 首镜与起幅**：首镜由用户锁定条件与叙事任务决定，可大全景、全景、中景、局部近景或特写；不把原图静态机位默认为全片唯一视角。只有任务确需探索且无锁帧限制、变化有依据时，才局部起幅、换角度或穿行。
- **SR-B 真实位移**：Dolly／Tracking 优先写遮挡顺序、相对角度、近远景视差、地面透视、主体与地标距离、逐渐显露；不要求每个镜头都有前景，不强制前景滑出；缺纵深可保留简洁路径并说明可观察性有限，不凭空添加柱子、树木或建筑；纯 Zoom、固定机位、二维平面运动不改写成三维平移。
- **SR-C 锁帧承接**：锁首帧时首帧按图承接，删除只针对该图的互斥禁入声明；之后可保持固定构图完成表演、光影或氛围变化，也可在适合的动作节点移动、改变景别或切镜；不强制立即移动、立即硬切或大幅遮挡。
- **SR-D 相邻镜头**：有场景图的多镜保持必要空间一致，但不要求每相邻两镜都换角度和景别；只有切镜服务新观察任务时才变化；反应、强调、静态对话、对称、重复构图、长镜内部推进可保留相同地标／景别；禁止无叙事目的地复制，也禁止为变镜破坏轴线、连续性与空间关系。
- **SR-E 锁死判定**：锁死指用户需要动态探索或视角变化、成片没有兑现；不以静态画面本身判失败。静态构图在悬疑、情绪、产品展示、远景尺度、用户指定固定机位中可以是正确结果。

### 3. 执行层同步

- `references/camera-direction.md`：相邻镜头段与 Dolly 段改为条件规则，删除“每相邻镜头必变角度景别”“附场景图 Dolly 必须前景滑出”。
- `references/seedance-2.5.md`：SD25-05 改为按四维判断与一减三留执行，SD25-06 改为锁帧承接后由用户与事件决定去留，不强制立即脱框。
- `SKILL.md`：REF@1.4.0、SEEDANCE@1.5.0 摘要同步为条件化表述，版本与 revision 更新为 3.9.4／`v3.9.4-scene-decision-consistency-2026-11-09`。

## 测试与验证

- **单元测试**：`python -X utf8 -m unittest discover -s tests -p "test_*.py"` → 205 项，204 通过、1 跳过（Windows 符号链接不支持）；0 FAIL／ERROR。
- **结构回归**：`python -X utf8 scripts/run_regression.py --cases tests` → suite PASS，133 项（routing 20、execution 59、continuity 4、style 4、audio 4、generation 6、adaptation 36），127 UNKNOWN＋6 PENDING_VIDEO，0 FAIL。
- **结构化用例**：T44／T45 条件化；T46–T57 覆盖 S01–S12；T58／T59 覆盖两个变形。`STRUCTURED_IDS` 为 T34–T59＋C04，失败注入覆盖缺字段、重复断言、互相矛盾三类。
- **注册表**：`python scripts/rule_registry_check.py --sync` → PASS，10 条规则，REF@1.4.0、SEEDANCE@1.5.0 双向 SHA-256 一致。
- **G2 文本实测**：`review/v394_g2/` 保存 T46–T59 共 16 条中文提示词与 16 份逐条审查记录；全部 EV1、PENDING_VIDEO。

## 证据边界

以上均为文本、结构与软件测试（EV1）。没有真实 Seedance 生成、成片观看、独立盲评或实际提交证据；G2 的 PASS 只表示提示词文本逐条符合本轮场景决策预期，不表示 Seedance 已遵循，也不表示破框能力或成片质量提升。T58／T59 未指定秒数，按镜头数与事件容量对齐，不擅自估算总长。

## 版本与文件

- 主技能：3.9.4；动作入口：3.9.4。
- 规则注册表：REF@1.4.0、SEEDANCE@1.5.0，其余 8 条版本不变。
- 新增：`references/release-v3.9.4.md`、`tests/test_v394_scene_decisions.py`、G2 审查目录（包外交付）。
- 保留：`references/release-v3.9.3.md` 作为历史发布记录，不改写。

---

<!-- source: katil-skill/references/release-v3.9.3.md -->

# KATIL Core V3.9.3 场景参考图防锁死与三维空间解绑 · 2026-11-09

本版以 V3.9.2 为基线，在既有权威专题中就地合入“场景参考图一减三留”与“三套三维破框语法”，收口盲评 `sample_size` 与用例 `runs_min` 的联动校验，并将前序小版本的散落发布文件归并入 `CHANGELOG.md`。不新建第二套模块文档，不改变 240 项能力与视效库、60 项风格库的内容边界。

## 核心更新

### 1. 场景参考图“一减三留”与空间破框（`REF@1.3.0`、`SEEDANCE@1.4.0`）

- **SR-1 一减三留（`reference-and-task-handling.md`）**：已附场景参考图时，删减对画面已知静态建筑雕花、墙壁颜色、远山形态等静态外观的重复堆砌（避免抢占动作/运镜权重或诱导模型生成微动壁纸）；只保留**方位与轴线锚点**、**物理与光影反馈**、**画外与纵深延伸**三类三维交互信息。
- **SR-2 三套破框语法（`reference-and-task-handling.md`、`seedance-2.5.md`）**：
  - **策略 A（首镜局部起幅破框）**：多镜任务显式声明提取空间布局与光色材质、不锁定原图静态机位与全景画幅，`分镜01` 优先从场景内部的局部中近景或具体地标旁起幅。
  - **策略 B（前景滑出画外强制 3D 视差）**：单镜或真一镜穿行进入场景图内部时，写明前景地标向画框两侧或下方滑出画外、中后景拉开立体视差，防止退化为 2D 照片数码放大（2D Zoom）。
  - **策略 C（首帧锁死 I2V 动态脱框）**：强制首帧锁死模式下删除“不入帧”互斥句，起幅承接首帧构图后立即借主体跨前景大幅位移遮挡、带视差跟移或共有地标硬切脱离初始静态视角。
- **SR-3 运镜视差与视角转换（`camera-direction.md`）**：补充附带场景图时的 `dolly in/out` 前景出画视差要求与同场景相邻镜头的地标观察角度/景别变换要求。

### 2. 工程加固与包体瘦身（SR-4）

- **盲评 `sample_size` 与 `runs_min` 联动校验（`scripts/video_evidence.py`）**：`review_mode == 'blind'` 时，强制校验 `sample_size >= max(2, case['runs_min'])`，消除 `sample_size` 小于用例最低生成次数仍获 `ev3_supported: true` 的边界缺口。
- **结构化回归扩充至 119 项**：`tests/execution_cases.json` 新增 `T44`（附场景图多镜破框与静态减法）、`T45`（附场景图 3D 视差推进防 2D 放大），均带非空无交集的 `must_hold` 与 `must_reject` 断言。
- **历史发布说明归并瘦身**：将 V3.8.0–V3.9.2 的历史说明统一保留在 `CHANGELOG.md`，包内仅保留当前版 `references/release-v3.9.3.md`，主技能包文件数由 78 个精简至 **73 个文件**（含 `direct-cinematic-fights` 共 78 个文件）。

## 验证范围（EV1）

- `python3 -m unittest discover -s tests -p "test_*.py"`：194 项测试全部通过（Linux 环境下符号链接测试亦正常执行，Windows 环境下为 193 通过、1 跳过）。
- `python3 scripts/rule_registry_check.py --sync`：PASS，10 条核心规则（含 `REF@1.3.0`、`SEEDANCE@1.4.0`）双向 SHA-256 一致。
- `python3 scripts/run_regression.py --cases tests`：suite PASS，119 条（routing 20、execution 45、continuity 4、style 4、audio 4、generation 6、adaptation 36），113 UNKNOWN＋6 PENDING_VIDEO，0 FAIL。
- `python3 scripts/ability_library.py --validate`：PASS，240 项、24 类，v2.0.0；`style_library.py --validate`：PASS，60 项、10 类，v1.9.0；`model_profile_check.py`：PASS。

以上为文本、结构与软件测试证据（EV1）。没有真实模型生成、成片观看、独立盲评或实际提交证据；不得把本版写成视频效果通过或模型已遵循。
