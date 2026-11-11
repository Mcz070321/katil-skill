# V3.10.5 · 2026-11-11

- **冲击帧**：全画幅或抽象效果可短暂遮住交点，恢复后承接同一次接触及受力相位。明确指定的换机位与尺度按可追踪的交点或轴线衔接。
- **成片评审**：G10／G11 为每条完整视频核对必要判据标识。按用例同步盲评最少样本数、结构回归数量及填写说明。
- **证据边界**：G10／G11 的版本对照仍为 V3.10.1 vs V3.10.2，视频保持 `PENDING_VIDEO`。V3.10.5 本地安装采用候选包。

# V3.10.4 · 2026-11-10

- **证据与工程收口（不改变导演规则）**：活跃版本标记统一为 3.10.4；`references/release-history.md` 增加 V3.10.3 第七节，标题改为 V3.9.3–V3.10.3，并说明该节来自 CHANGELOG 与修正报告，不是被删除的 `release-v` 文件。包内仍为 95 个文件（主技能 90＋动作入口 5），不新增 `release-v` 或 `baseline_regression.json`。
- **历史归档哈希门禁**：`tests/test_fx_director.py` 按 source 注释切分六份旧原文，统一 LF、`rstrip()` 后比对预置 SHA-256；V3.10.3 新节只做存在性、顺序与关键词检查，不冒充原始发布说明哈希。
- **跨平台口径**：Windows 11／PowerShell 7.6.9／Python 3.12.7 全量单元测试 243 项（242 通过、1 跳过、0 失败）；结构回归 162 项（151 UNKNOWN＋11 PENDING_VIDEO、0 FAIL）。本机无 WSL／bash，Linux 记为 `NOT_RUN`；`tests/README.md` 增加验证矩阵与复跑命令。跳过项为 `test_video_evidence.VideoEvidenceTests.test_symlink_alias_is_rejected`。
- **证据边界**：本轮为 EV1 文本、结构与软件检查；未新增真实视频、盲评或平台提交。G10／G11 继续沿用 V3.10.1 vs V3.10.2，V3.10.3／V3.10.4 均未新增终局 A/B，所有视频项保持 `PENDING_VIDEO`；发布状态保持 candidate，未安装十端。

# V3.10.3 · 2026-11-10

- **包体收敛与历史发布文档归档**：将 `references/release-v3.9.3.md` 至 `references/release-v3.10.2.md`（共 6 份独立版本说明）按发布时原文归档到 `references/release-history.md`；`CHANGELOG.md` 与 `references/fx-ab-testing.md` 只保留当前摘要与实验协议，不再重复全文。移除根目录静态快照 `baseline_regression.json`（可由 `scripts/run_regression.py --out` 按需重建；默认只打印 stdout）。主技能 `katil-skill` 文件数为 **90 个**，双技能合包总文件数为 **95 个**（V3.10.2 为 96／101；本版删除 7 份旧文件并新增 1 份归档），保持在 100 文件红线以内。
- **终局实验协议统一收口**：将 `G10`（《竹海·斩鬼》不可逆状态链）与 `G11`（《拳镇山河·剑断天穹》巨物尺度梯）的版本对照与单段／三段交付形态对照协议并入 `references/fx-ab-testing.md`，并将 `tests/generation_cases.json` 中 `G10／G11` 的 `protocol` 统一指向 `references/fx-ab-testing.md`。
- **执行稿编译检查器 CLI 协议增强**：`scripts/fx_compilation_check.py` 新增 `check_payload`，同时兼容单条标注对象与多用例套件（如直接运行 `python3 scripts/fx_compilation_check.py tests/fx_compilation_cases.json`），保持 `ANNOTATED_SPANS_PRESENT_REVIEW_REQUIRED` 与 `EV1_LITERAL_ONLY` 证据边界。
- **验证范围（EV1）**：Windows 11／PowerShell 7.6.9／Python 3.12.7 下，全量单元测试 **243 项（242 通过、1 跳过、0 失败）**；跳过项为 `test_video_evidence.VideoEvidenceTests.test_symlink_alias_is_rejected`（当前环境不能创建测试所需符号链接）。结构回归 **162 项**（151 UNKNOWN＋11 PENDING_VIDEO，0 FAIL），规则注册表 15 条 PASS，能力库 240 项与风格库 60 项 PASS，Markdown 内部链接 0 断链。无新增真实视频或独立盲评，所有生成项保持 `PENDING_VIDEO`；未在 Linux 复跑。

# V3.10.2 · 2026-11-10

- **复杂终局预编排（`references/decisive-state-and-scale.md`）**：针对复杂终局后段高密度变化，在动笔前核算**不可逆状态链（S0→Sn）**、**巨物尺度梯（分别成形→会合接触→峰值恢复→传播拉远）**与**单段承载／可选分段交接**；动作专题补充双持／多件武器可数性与尾态动词，特效专题补充巨物同框尺度锚与接触峰值派生。
- **外部诊断样本归档与回归扩充**：`tests/execution_cases.json` 新增 `T61`（《竹海·斩鬼》两次断臂、无臂前扑、头身分离与崩解）、`T62`（《拳镇山河·剑断天穹》巨拳巨剑成形、交点侵蚀与云墙至星球拉远）；`tests/generation_cases.json` 新增 `G10／G11`；`tests/video_regression_manifest.json` 记入两条 2026-11-10 外部抽帧诊断视频哈希与观察边界（明确标记 `usable_as_baseline: false`，不满足 EV2 门槛）。
- **候选修正**：动作兼容入口 references 同步 3.10.2；T61／T62 主语与能量巨剑输入显式化；巨物首次建立允许经授权的剪影／局部锚；测试子进程固定 UTF-8；README 与库标签同步。

# V3.10.1 · 2026-11-09

- **分类主导覆盖**：新增 FXT16–FXT21，修正 FXT07／14／15 主导与若干辅助分类；运行器现在要求 15 类分别有主导案例，不允许仅凭辅助覆盖。FXT10 保持无特效对照。
- **双层执行稿与保真**：新增按需指南，内部整理关键事实、事件因果与状态，再将并发反馈编成可复制稿；三组人工夹具与字面标注检查覆盖遗漏、顺序与否定局限，任何自动结果仍需人工语义复核。
- **成片对照准备**：新增 G07–G09 和实验方案，覆盖高速近战、重力领域及非战斗流体光学；相同任务和素材、预先记录控制变量、盲评与失败，所有真实视频仍为待执行。
- **复审结果**：本环境分发集合单元测试 237 项通过，保留历史测试的个人安装完整运行 249 项通过；158 项结构回归为 149 UNKNOWN＋9 PENDING_VIDEO，0 FAIL；注册表、技能基础格式及 240／60 库校验通过。未生成真实视频或声称模型效果提升。

# V3.10.0 · 2026-11-09

- **FX Director 2.0 总入口（`FX_DIRECTOR@1.0.0`）**：新增 `references/fx-director.md`，区分制作领域／技术门类、15 类视觉特效与六层调度；提供 A–H 决策流程、主导 1 类＋辅助 0–3 类、三档预算、事件级六项、术语 Level 0–3 与 P0/P1/P2 检查。权威范围为特效分类与调度，不越权改写能力、伤势、动作结果、摄影锁定或声音授权。
- **程序化生命周期（`FX_PROCEDURAL@1.0.0`）**：新增 `references/procedural-fx-grammar.md`，以 Niagara-inspired 设计语法（非真实 Niagara）规定 Trigger→Spawn/Formation→Initial State→Motion→Interaction→Event Response→Decay→Residue，覆盖发射源、分布、尺度、初速度、寿命、运动场、碰撞响应、残留与跨镜状态。
- **引擎视觉转译（`FX_ENGINE@1.0.0`）**：新增 `references/engine-fx-visual-mapping.md`，把 Niagara、Niagara Fluids、Chaos、Material/Shader、Lumen、Compositing/Composure、Motion Graphics、Camera/Lens FX 翻译成画面语言；明确 Niagara 不是特效类别、Lumen 不生成粒子或破坏、Compositing 不是 Niagara 模块，不得把术语写成真实引擎调用。
- **光学与合成（`FX_OPTICAL@1.0.0`）**：新增 `references/optical-and-compositing-grammar.md`，覆盖 Bloom/Glow、Lens Flare、Refraction、Chromatic Aberration、Reflection、Volumetric Lighting、Exposure/Clipping、Depth of Field、Heat Haze、Motion Blur；每项要求光源、介质、摄影动机、触发与恢复，并检查前中后景、遮挡与主体分离。
- **事件级同步（`FX_SYNC@1.0.0`）**：新增 `references/fx-synchronization.md`，以事件为单位组织 Action／Primary／Secondary／Impact／Environment／Optical／Camera／Audio 八轨，规定接触簇、环境响应前沿、摄影机不制造未发生位移、声音与材质／距离／相位相符，以及特效消散不等于伤势或破坏恢复。
- **入口与旧专题衔接**：`SKILL.md` 增加 5 个按需路由与 5 个规则摘要块；effects-and-damage、visual-material-grammar、camera-direction、sound-and-rhythm、model-adaptation、seedance-2.5 增加交叉引用并保留各自权威边界；ability-library 标题更新为 3.10.0，240 张卡未改写。
- **FX 用例与运行器**：新增 `tests/fx_cases.json` 15 条 FXT01–FXT15，覆盖 FX01–FX15 与六层；FXT10 为无特效写实、primary_fx=NONE。`scripts/run_regression.py` 增至 149 项（fx 15），校验主导／辅助类别、六层、正反断言与 PENDING_VIDEO 边界；143 UNKNOWN＋6 PENDING_VIDEO，0 FAIL。
- **测试**：单元测试 225 项（224 通过、1 跳过，Windows 符号链接不支持）；新增 `tests/test_fx_director.py` 15 项，覆盖 15 类／六层、5 个权威锚点、registry 依赖、SKILL 路由与版本同步、失败注入。注册表 15 条 PASS。
- **验证范围**：文本、结构与软件测试为 EV1；没有真实 Seedance 生成、成片观看、独立盲评或实际提交；FXT01–FXT15 全部 PENDING_VIDEO。

# V3.9.5 · 2026-11-09

- **结果发生后的尾段锁定（`WITNESS@1.3.0`）**：`shot-execution-contract.md` 新增锚点 `katil-outcome-lock`，规定决定性结果成立后，尾段只承接直接余波、承受、环境沉降、站位呼吸、视线声音余响或用户已要求的下一阶段；不得新开独立攻击／召唤／领域／增援／追逐／第二结局，不得用新巨物、新战场或新增支线替换已分出胜负的双人主体。反转／诈死／二次觉醒须有用户明确要求、前置触发和可见因果；无触发追加翻盘仍按新开事件处理。
- **执行与验收同步**：`high-speed-combat-generation.md` 的终点段与 `video-acceptance-testing.md` 的尾段检查加入同一可检查项；`SKILL.md` 的 WITNESS 摘要升至 1.3.0，并保留结果发生前的多线并发、交叉剪辑、必要反击与用户指定的开放式结尾。
- **新增 T60 回归**：九节点过载版对六节点终态链，覆盖结果后继续开事件、巨物替换双人主体、破灯／胜负／余波不可辨与无触发反转；execution 59→60，结构回归总 133→134，UNKNOWN 127→128，PENDING_VIDEO 保持 6，0 FAIL。`STRUCTURED_IDS` 覆盖 T34–T60＋C04。
- **测试**：单元测试 210 项（209 通过、1 跳过，Windows 符号链接不支持）。新增 `test_v395_outcome_lock.py` 5 项，覆盖 T60 字段、过载／收束对照、权威文档锚点与条件化反转、验收引用、WITNESS 1.3.0 摘要。注册表 10 条 PASS。
- **验证范围**：文本、结构与软件测试为 EV1；没有真实 Seedance 生成、成片观看、独立盲评或实际提交；T60 尚无文本执行输出，所有视频项保持 PENDING_VIDEO。

# V3.9.4 · 2026-11-09

- **场景参考与摄影决策一致性修复（`REF@1.4.0`、`SEEDANCE@1.5.0`）**：在 `reference-and-task-handling.md` 建立四维独立判断（素材用途、摄影目标、叙事任务、场景证据 K／I／U）与 SR-A–E；局部起幅、换视角、真实位移、锁帧后脱框全部改为四条件同时满足时才建议，不再强制前景滑出、不再要求相邻镜头必换角度景别，也不把静态画面本身判为锁死。
- **执行摘要条件化**：`camera-direction.md` 的相邻镜头与 Dolly 段改为条件规则；`seedance-2.5.md` 的 SD25-05／SD25-06 只保留执行表达；`SKILL.md` 的 REF／SEEDANCE 摘要同步为条件化表述，不再保留旧强制句。
- **结构化用例扩充**：T44／T45 改为条件化；新增 T46–T57（对应 S01–S12）与 T58（普通参考→锁首帧）、T59（Dolly→Zoom）两个变形测试；execution 45→59，结构回归总 119→133，UNKNOWN 113→127，PENDING_VIDEO 保持 6，0 FAIL。`STRUCTURED_IDS` 覆盖 T34–T59＋C04。
- **测试**：单元测试 205 项（204 通过、1 跳过，Windows 符号链接不支持）。新增 `test_v394_scene_decisions.py`，含旧强制句反例、条件化正向断言、T44–T59 覆盖、T58／T59 变形边界与失败注入（缺字段、重复断言、互相矛盾）。注册表 `REF@1.4.0`／`SEEDANCE@1.5.0`，10 条 PASS。
- **G2 文本实测**：`review/v394_g2/` 保存 T46–T59 共 16 条中文提示词输出与逐条 must_hold／must_reject 审查记录；全部 EV1、PENDING_VIDEO，不是 Seedance 成片证据。
- **验证范围**：文本、结构与软件测试为 EV1；没有真实模型生成、成片观看、独立盲评或实际提交，不声称破框能力已提升。

# V3.9.3 · 2026-11-09

- **场景参考图“一减三留”与三维破框（`REF@1.3.0`、`SEEDANCE@1.4.0`）**：在 `reference-and-task-handling.md`、`seedance-2.5.md`、`camera-direction.md` 就地合入场景图防锁死规则——删减已知静态外观复述，只留方位锚点、物理光影反馈与画外延伸；提供**首镜局部起幅破框**、**前景滑出画外强制 3D 视差（防 2D 照片放大）**与**首帧锁死（I2V）动态脱框**三套解法。
- **盲评样本量联动加固**：`scripts/video_evidence.py` 在 `review_mode == 'blind'` 时校验 `sample_size >= max(2, case['runs_min'])`，确保 EV3 盲评样本量不低于用例声明的最低生成次数。
- **回归与契约扩充**：新增 `T44`、`T45`（含 `must_hold`／`must_reject` 正反断言）及 V3.9.3 契约与盲评边界测试；结构回归共 **119 项**（113 UNKNOWN＋6 PENDING_VIDEO），单元测试 **194 项**。
- **历史发布文件归并瘦身**：归并 `release-v3.8.0.md`～`release-v3.9.2.md` 至本日志，包内仅保留当前 `references/release-v3.9.3.md`，主包文件数由 78 降至 **73 个文件**。
- **验证范围**：文本、结构与软件测试为 EV1；没有真实视频、盲评或实际提交，不声称成片通过。

# V3.9.2 · 2026-11-08

- **证据来源类型加固**：run_regression.py 对 submission_evidence.source 先判断字符串，再执行来源枚举；数组、对象、数字与 null 不再触发 TypeError: unhashable type，改为结构错误、该条 FAIL、兼容性回退 UNVERIFIED。
- **回归**：新增 test_compatible_evidence_source_wrong_type_returns_structured_error，覆盖 list、dict、int、None；修复前已复现无结构化 JSON，修复后均退出 2 并给出报告。
- **验证**：单元测试 193 项（192 通过、1 跳过），结构回归 117 项（111 UNKNOWN＋6 PENDING_VIDEO），注册表与库校验沿用 3.9.1 结果。
- **版本同步**：主技能与动作入口 3.9.2，revision 为 v3.9.2-evidence-type-hardening-2026-11-08；manifest、agents 描述、库索引标题、注册表摘要与哈希同步。
- **验证范围**：文本、结构与软件测试为 EV1；没有真实视频、盲评、实际提交或艺术质量评审，不声称成片通过。

# V3.9.1 · 2026-11-08

- **COMPATIBLE 证据门槛**：run_regression.py 要求声明 COMPATIBLE 时附 submission_evidence，source 限 platform_measured／ev2_observation／ev3_observation，reference 非空；缺失或非法判结构错误、该条 FAIL，兼容性回退 UNVERIFIED，不再无证据通过。
- **documented／submission_ready 边界**：documented 只描述官方文档能力，不是 submission_compatibility 取值；3.9.x 的 submission_ready 恒为 false，取得提交证据也只记录，不改字段或升级文字套件。
- **EV1 范围**：明确 EV1 含确定性检查与按验收条目的语义文字评审；后者仍是文本层，不是 EV2，不能升级为模型遵循或成片通过。
- **EV3 盲评字段**：评审记录新增 review_mode／independence／blind_protocol／sample_size；blind 需 protocol、样本量至少 2、independence=independent；审计标记 ev3_supported，但仍不认证实际盲法执行。
- **结构化断言与单条状态**：T42、C04 的 must_hold 去掉被修掉的否定式并改为正向；adaptation 非法值与 COMPATIBLE 缺证据时该条直接 FAIL；tests/README.md 修正版本、标题与空格。
- **历史格式说明**：rules/rule-registry.yaml 继续沿用 .yaml 扩展名（内容为 JSON），本版不改名、不迁移，避免影响既有工具链。
- **回归与契约**：新增 COMPATIBLE 证据、documented、非法 adaptation、盲评字段等测试；单元测试 192 项（191 通过、1 跳过），结构回归 117 项（111 UNKNOWN＋6 PENDING_VIDEO）。
- **版本同步**：主技能与动作入口 3.9.1，revision 为 v3.9.1-evidence-hardening-2026-11-08；manifest、agents 描述、库索引标题、注册表摘要与哈希同步。
- **验证范围**：文本、结构与软件测试为 EV1；没有真实视频、盲评、实际提交或艺术质量评审，不声称成片通过。

# V3.9.0 · 2026-11-08

- **证据等级（EV0–EV3）**：新增 references/evidence-and-claims.md，区分设计与文本/结构、单次生成观察、同条件盲评；每句结论必须写等级、对象与范围，EV1 不得写成视频或模型通过，结构 PASS 不得改成成片 PASS，无视频保持 PENDING_VIDEO。
- **模型事实来源分层**：model-adaptation.md 写入 official／platform_measured／unverified_assumption；官方文档只支持 documented，不能单独判 COMPATIBLE；兼容需平台实测或同任务 EV2／EV3，未知数值与未注明来源不得填充。
- **验收边界**：video-acceptance-testing.md 说明文字验收 EV1、单次全片观察 EV2、同条件多次加盲评 EV3；P0／P1 不定义证据等级。
- **结构化断言**：T34–T43 与 C04 增加 must_hold／must_reject，run_regression.py 校验两数组非空、无重复、无交集，缺项退出 2。
- **跨版本对照**：新增 G05（终斩可观察性与后果连续）、G06（高速双人交锋阶段可读性），均为 V3.8.1 对 V3.8.2、runs_min 3，未评审前 PENDING_VIDEO。
- **注册表**：新增 EVIDENCE 1.0.0，ADAPTER 1.2.0→1.3.0；其余 8 条不变，SKILL.md 摘要、registry 标记与哈希同步。
- **回归与契约**：新增 tests/test_v390_evidence.py 6 个测试；结构回归117项（111 UNKNOWN＋6 PENDING_VIDEO），单元测试184项（183通过、1跳过）。
- **版本同步**：主技能与动作入口 3.9.0，revision 为 v3.9.0-evidence-and-delivery-2026-11-08；manifest、agents 描述、库索引标题、回归运行器同步。
- **验证范围**：文本、结构与软件测试为 EV1；没有真实视频、盲评或艺术质量评审，不声称成片通过。

# V3.8.2 · 2026-11-08

- **特效规则（E1–E5）**：把源头、路径、兑现点，爆炸三层，峰值身份锚，环境承接写入 effects-and-damage.md；把特效层与实体层的附着边界写入 visual-material-grammar.md。无源全屏光斑、先烟花后补环、峰值丢失主体、只有角色光边均判无效。
- **动作规则（A1–A4）**：对手按可达状态应答（闪／格／受），命中承认分流、不默认震屏，点名落点决定局部材料与功能，可见打击至少带动一种当场介质；写入 action-and-shot-compiler.md。
- **镜头与连续（C1–C3）**：每次切镜换观看任务，跨尺度允许硬切并保留共有地标，真一镜写清起幅、主体锁点、航点与环境作证；C1／C2 写入 camera-direction.md，C3 写入 viewpoint-and-continuity.md。
- **Seedance（S1–S2）**：素材说明写清提取、排除、是否入帧；时间写法在事件序与用户锁定秒轴之间二选一，不混用；写入 seedance-2.5.md。
- **注册表**：CONTINUITY 1.1.0→1.2.0，SEEDANCE 1.2.0→1.3.0；其余 7 条不变，SKILL.md 摘要与 registry 标记、哈希同步。
- **回归与契约**：新增 R17–R20、T34–T43、C04 共15条；新增 tests/test_v382_contract.py 8 个契约测试；当前结构回归115项（111 UNKNOWN＋4 PENDING_VIDEO），单元测试177项（176通过、1跳过）。
- **版本同步**：主技能与动作入口 3.8.2，revision 为 v3.8.2-camera-action-vfx-contracts-2026-11-08；manifest、agents 描述、库索引标题、回归运行器同步。主包与动作入口文件数见发布报告。
- **验证范围**：文本、结构与软件测试为 E1；没有真实视频、盲评或艺术质量评审，不声称成片通过。

# V3.8.1 · 2026-11-08

- **卡名与发布说明对齐**：A224 在 `abilities.json` 与 `ability-library/index.md` 统一为「走廊重力翻转」；`release-v3.8.0.md` 的 C23 描述改为实际卡名「镜廊慢拍错位／雨滴悬停升空／画布融化入实」。
- **回归文档校正**：`tests/README.md` 的无响应文本项由 76 改为 96；删除包内不存在的 `results/release_manifest.json` 指向；80 项／76 UNKNOWN 明确标为 V3.7.2 历史口径。
- **测试覆盖**：新增 A224 规范名回归测试；全量 169 项中 168 通过、1 跳过（`symlinks unsupported`），不再写成全部通过。
- **版本同步**：主技能与动作兼容入口均为 3.8.1，manifest、agents 描述、库索引标题与回归运行器版本同步；主包 71 个文件，含动作入口共 76 个文件。

# V3.8.0 · 2026-11-08

- **全类型影视视效库扩充（`v2.0.0`，200 → 240 项）**：在保留原有 `C01–C20`（200 项动作、科幻、奇幻角色技能）的基础上，于单文件 `references/ability-library/abilities.json` 中新增 4 类共 40 项**非战斗全类型影视视效卡（`C21–C24`，`A201–A240`）**：
  - `C21 商业微距与产品视效`（`A201–A210`：水油乳化、冰块入水冠冕、精密悬浮拆解、风洞流线、丝绸流波、液态汞珠、香氛焦斑、纳米脉冲、日晷光影、油脂拉花）；
  - `C22 自然天象与宏观奇观`（`A211–A220`：极光折卷、深海荧光涡流、双月潮汐、穹顶圣光、四季延时枯荣、雷暴云墙、灰幕日食、荒原蜃景、星环流火、云海雾瀑）；
  - `C23 心理梦境与超现实转场`（`A221–A230`：空间碎镜剥落、地面液化深潜、镜廊慢拍错位、走廊重力翻转、胶片烧穿闪回、轮廓风化散沙、雨滴悬停升空、瞳孔缩入换景、室内拉伸荒原、画布融化入实）；
  - `C24 怪谈异变与诡异氛围`（`A231–A240`：烛火转绿逆影、纸人渗墨转睛、墙面潮痕漫延、红绸逆风悬铃、雪花屏显背影、井水倒影脱节、长廊逐灭逼近、石像裂纹渗泪、门缝黑水漫入、冥纸旋风空巷）。
- **跨专题自动补全联动**：当用户只提供想象画面与视频类型而未写特效细节时，广告、文戏、超现实转场、宏观空镜与中式怪谈可直接按需检索 `C21–C24` 视觉母形，无需借用战斗爆炸词条。
- **零文件膨胀与全量验证**：得益于 V3.7.5 单文件库架构，新增 40 张视效卡后主技能包仍保持 **70 个文件**；`ability_library.py --validate`（240 项、24 类）、`style_library.py --validate`（60 项）、`rule_registry_check.py --sync`（9 条规则双向哈希）与 **168 项单元测试**（167 项通过、1 项跳过，跳过原因为 `symlinks unsupported`）。

# V3.7.5 · 2026-11-07

- **结构瘦身与单文件库合并**：将 `C01–C20.json` 与 `catalog.json` 合并为单文件 `references/ability-library/abilities.json`（200项），将 `F01–F10.json` 与 `catalog.json` 合并为单文件 `references/style-library/styles.json`（60项），检索脚本同时兼容单文件与旧分片；剥离离线历史日志与冗余副本，使技能包总文件数降至 68 个，完全适配各平台 100 文件上限与 MIME 门禁。
- **复制块纯净度门禁统一收口**：`scripts/block_lint.py` 新增 `copy_block_purity_findings`，统一拦截「如有参考图」条件句、全局「默认无BGM」、复制块内泄露的 `SD25-` 维护编号、表单式转场头及无时间码写作方式自解释赘语，由 `run_regression.py` 直接复用。
- **规则注册表一键同步**：`scripts/rule_registry_check.py` 新增 `--sync` 参数，自动计算并写回 9 条核心规则的 `authority_sha256` 与 `summary_sha256`。
- **跨专题去重脱水**：精简次级专题中的重复通用规则复述，统一回指权威锚点。版本与兼容入口对齐 V3.7.5。

# V3.7.4 · 2026-11-07

- 默认按无时间码事件序编排，总长约束容量，精确时间在明确要求或任务必需范围使用。TIME@1.0.0 为权威规则，各专题按职责应用。
- 多镜、真一镜、故事板分别用分镜、镜内阶段和格号，编号后直接写画面；局部返修保留来源时序，明确去时码则重编并核容量。
- block_lint 新增可选 timing-policy，回归运行器对显式 event_driven 用例调用共用检查；旧调用沿现有行为。
- 新增 T22–T33，套件共100项。版本、注册表与两级兼容入口同步，发布范围及实际证据见 `references/release-v3.7.4.md`。

# V3.7.3 · 2026-11-06

- 在既有权威专题补强终态倒推、关键变化观察关系、状态来源与承接、冲击帧后的结果兑现；保留开放结尾、用户强度与时序，不新增第二套流程。
- 模型适配沿用通用规则；成片诊断与验收逐项记录指定终态，尾段检查从决定性事件追到结尾。
- 修正恐怖专题固定2～5秒余波建议与用户参数优先的冲突。
- 新增T14–T21共8条回归输入及预期；历史证据不冒充本轮实测。软件与文字评审分开记录，真实视频待复测。
-。

# V3.7.2 · 2026-11-05

- 维护版：不新增大型创作框架，不改变44个原任务、36个适配任务的输入与预期，不把3.7.1继承的文字结论改写成3.7.2重跑。
- 修复3.7.1证据文档的26处构建机绝对链接，改为包内相对路径；`baseline-forward`保留的绝对路径是当时构建机审计记录。
- `video_evidence.inspect_video`仅在ffprobe非零退出或媒体流／帧结构不合格时判FAIL，非致命stderr记入`probe_warnings`，并新增回归测试。
- CR-01状态回写closed并关联`retake-review.json`；初始质量审查文档保留并标注已关闭。
- 清理`routing_cases.json`两处重复标点；16条请求、预期、字段与顺序不变，字节数与3.7.1基线不同已在manifest说明。
- 发布清单补充外部计划不可包内复核的注记，修正current字段措辞，说明`repair_case_ids`空数组语义；3.7.1发布说明明确34案按SHA-256继承、M31／M34定向复读。
- 版本与兼容入口元数据同步到3.7.2；Core 155项执行、154通过、1跳过，无响应回归80项为76 UNKNOWN＋4 PENDING_VIDEO；未做真实视频、模型投递或盲评。
- 3.7.1历史证据保留在`tests/results/v3.7.1`。

# V3.7.1 · 2026-11-05

- 基于已完成同版复核修复的3.7.0，新增Core内置Seedance2.5自然语言按需适配；不将无版本产品名、比较或新作品误作继承，不依赖Production。
- 母稿转译与首轮直接执行稿分开，保留硬要求、微时间线和指定强度；不将2～6秒例子固化为镜长，不以分段冒充原生一镜。
- 新增公开模型、Runway四模式和即梦未知参数档案；Runway Edit时长/画幅随源，Extend画幅随源且只返回新增片段。档案结构检查不证明实际提交或成片表现。
- 注册表增至8条；DELIVERY/REF修订1.1.0，独立起止标记、摘要正文与权威文件哈希同步维护。
- 原44任务和16路由不变；新增M01–M36及独立评审标准，文字、提交声明与视频状态分开。软件和文字实测结果见本版发布范围及结果文件，历史日志不冒充本版重跑。
- 同步本套兼容入口与元数据至3.7.1；能力/风格JSON数据卡及Production0.1.0-preview文件不变，无真实视频生成。

# V3.7.0 · 2026-11-05

- 以指定V3.6.4源码为基线；保留200能力/60风格库、全部16路由和44任务，不将旧视频比较版本改写为新版本。
- Core继续直接自然语言创作；Production按需单独启用，不增加普通任务默认加载。
- 新增六类权威规则的定位、摘要修订和摘要/来源校验；同版复核后要求独立非空摘要块及正文SHA-256，检查空引用、空正文、篡改、重复、断锚、错版、循环和越界路径，语义仍需人工复核。
- 修复通用核心“特效仅随动作启用”与非战斗奇幻路由的已确认冲突。
- 跨集正典与单段内部规划区分，兼容入口与UI版本对齐3.7.0；独立安装的同名战斗技能保持自身身份。
- Production V0.1.0预览单独维护源绑定IR、SQLite候选/批准账本、四态证据分类、人工语义复核门槛、只读确定性导出与备份恢复。
- 真实两个模型配置未提供；无真实生成或盲评，不能据此宣称视频提升。高级合并/剧情回滚/迁移不开放。

同版复核修复（不改版本号）：修正嵌套兼容入口及转接路径，恢复入口metadata，统一当前库标题与测试说明；条件路由单独记录，旧证据分期，当前Windows测试/跳过原因和各文档字节数另存。Core 81项执行、80通过、1符号链接测试跳过；Production 54项通过。真实模型与视频仍未执行。

以下为保留的历史记录。

# KATIL-skill 版本记录

## V3.6.4 · 2026-11-05

验收工程维护，不改变 V3.6.3 导演编排规则，也不实施 V3.7.0 架构改造。

- **修复已复现漏洞**：旧运行器将写着 `NOT A VIDEO` 的文本文件重复填入两版各三次仍返回 PASS。新增 `scripts/video_evidence.py`，使用 ffprobe 检查视频流、帧读取、尺寸与有限正时长；伪视频、纯音频、单帧与读取错误不能通过。缺工具或探测超时保持待验证。
- **证据去重**：按规范路径、文件实体与 SHA-256 检查组内和跨版本重复，复制改名不能冒充独立次数；证据条数须与声明次数一致。字节哈希不保证识别重编码或视觉近似重复，也不认证生成来源。
- **评审与媒体分开**：新增 `evidence_status`、`review_status` 与质量结论来源记录。`reviewed=true` 不足以通过；须另存逐条评审 JSON，并匹配用例、版本、序号、当前哈希、观看范围、带时区时间及具体观察。全片质量结论来自外部评审，程序不认证评审身份、实际观看或艺术质量。
- **文档与复现边界**：更新运行器使用格式，补全祭庙节选缺失条件说明；原始角色图、完整可分发原稿及生成参数仍未补齐，不伪造可复现条件或 A/B 结果。补记下方 V3.6.3 历史记录。
- **验证范围**：58项脚本单元测试通过，包含真实短媒体合成夹具与负向证据测试；夹具不代表实际生成或艺术评审。44条任务仅结构合法，仍为40 UNKNOWN＋4 PENDING_VIDEO。真实版本视频 A/B 尚未执行。

## V3.6.3 · 2026-11-05（补记）

- **交付前返修**：将顺序动作、并发反馈与必要线索分开检查；发现容量或状态冲突后先修改正文，保留用户指定速度、强度、材质与必经事件。
- **动作约束**：检查关键因果依赖、手脚任务、承重、卡械与支点转换；超现实能力按本片规则成立。
- **强效果组织**：区分随动作的材质、接触峰值冲击帧与场景异变；持续剑气不自动等于冲击帧，不以降强度作为通用修法。
- **证据与回归**：补充要求和实际观察对应表；新增 T09–T13、G04 与祭庙战输入节选，保留原能力库、风格库与历史比较任务。
- **当时验证**：41项脚本单元测试通过，44条任务结构合法但40 UNKNOWN＋4 PENDING_VIDEO；未执行真实视频 A/B。该版媒体检查与重复计数存在漏洞，不能将当时的证据形式 PASS 解释为媒体真实性或艺术质量已通过；由 V3.6.4 修复。

## V3.6.2 · 2026-11-04

主题：通用性修复 · 执行稳定性 · 真实回归。不新增能力库、风格库或固定创作模板，不改事件容量上限。

- **声音默认改为按目的判断（A）**：默认矩阵不再对全类型写死「无 BGM」。音乐主导（MV／音乐视觉化／卡点同步）把音乐当叙事与剪辑结构；声音设计主导（恐怖／动作／拟音）按用户意图取舍环境音、效果音、音乐或静默；信息主导（演示／教学／纪录片）按信息清晰度决定配乐；未指定时仍不擅自加入与目标冲突的音乐、旁白和台词。字幕与画面文字同规则：默认不加，但用户明确要求的标题、产品信息、说明文字必须保留。同步修改 SKILL.md、defaults-and-medium.md、sound-and-rhythm.md、general-creative-core.md、general-acceptance.md、cinematic-storytelling.md、prompt-delivery-and-language.md 与两份 agents/openai.yaml。
- **参考图恢复三态（B/C）**：无参考图不生成任何参考声明（删除「如有参考图…」条件句）；普通参考图只提取指定内容，默认不得原样成为任一视频帧；明确锁定首尾帧时按用户要求承接并删除互斥禁令。多图按角色、武器、场景、风格分职责；设定板文字、边框、多视图不入动态画面；切镜不复原武器服装战损，非主要人物不无故复用同一面孔。
- **路由与样本清理（D/E/F）**：第9条二维动画故事板区分「只表现追逐路线与情绪」与「明确搏斗、碰撞、格挡或复杂交锋」；第11、13条 BGM 措辞改为「未经要求不加」；第14条删除与故事无关的「拆信内容」；连续性 C01 写明持灯手、断剑残刃、断尖位置与下一镜拾取关系，断尖是同一柄剑的断裂部件而非第二把武器。
- **关键事件可观察性（G）**：shot-execution-contract.md 新增时长不足时的五级优先（威胁来源→关键攻防→决定性接触或状态变化→直接后果→必要收束），装饰特写与重复奇观可压缩，镜头数不与质量挂钩；用户明确要求最终一击时，不得只有能量爆发而缺少决定性依据，不强制特写，大范围破坏继承同一次打击，余波服务目标。
- **有效运动与尾段（H）**：video-acceptance-testing.md 明确像素变化不等于交锋，列出六类有效运动与可成立的短暂静止；高速连续打斗逐阶段检查「主动目标→行动→对手反应→战局变化」，只有摆姿势、绕行、特效扩散记「可能的无效运动阶段」；最后20%单独检查漏攻击、过早胜利姿态、无依据重复构图、运动未完成与声音不一致。
- **故障记录（I）**：video-failure-diagnostics.md 统一 8 字段（时间位置、预期、实际、差异、证据等级、可能来源、最小修复、复测结果）；未复测只能写「尚未复测」，不另建修复体系，复用 feedback-repair.md。
- **回归可运行化（J/K）**：新增 scripts/run_regression.py 与 tests/test_run_regression.py；新增 tests/audio_cases.json（A01–A04）与 tests/generation_cases.json（G01–G03，含正向对照）。运行器只做确定性结构检查，未执行项输出 UNKNOWN／PENDING_VIDEO，不允许把文本通过写成成片通过。
- **证据校验补丁（同日，不改版本号）**：run_regression.py 不再只检查 evidence 是否非空。视频 PASS 现在必须按 3.6.1／3.6.2 分组，证据文件真实存在、非空且可读，每版达到 runs_min 且证据数不少于声明次数，并记录模型、模型版本、生成参数与 reviewed=true；文件存在但未评审保持 PENDING_VIDEO。单一路径、缺任一版本或伪造路径判 FAIL。旧样本归属写入 generation_cases.json 与 video_regression_manifest.json：1000034265＝用户第二版提示词，1000034266＝DeepSeek 与用户融合的提示词；原始提示词与参数未取得，不冒充基线。
- **版本同步（L）**：两个入口、重定向说明、两份 openai.yaml、能力库与风格库标题统一为 3.6.2；revision 为 v3.6.2-stability-and-regression-2026-11-04。
- **验证范围**：39 项静态单元测试通过，38 条用例结构检查通过（35 UNKNOWN＋3 PENDING_VIDEO）。真实视频 A/B、四个音频判断样本、三组生成对照均未执行，不能据此声称成片质量提升。

## V3.6.1 · 2026-11-04

一致性修订，不新增创作能力，只把 V3.6.0 里互相矛盾的文本收口：

- **概念档位统一为「作者型／约束型／极简型」**：SKILL.md、通用创作核心、原创概念引擎三处旧称（受事实约束型／极简功能型／原创表达／既定内容的表达／功能性表达）加括号别名，路由表与 JSON 的 `concept_mode` 只取这三值；`expected_load` 里虚构的「创意概念引擎」全部改为「原创概念」。
- **路由回归表修复**：删除第 12 行与第 13 行之间导致表格断裂的空行；「应加载」列只写模块名，概念档位写成「原创概念（约束型）」；新增第 16 条作者型用例，三处「15 条」同步改为「16 条」。
- **第 14 项固定原文统一**为阿岚版（门外两下敲击／铜钥匙／「等等」），`routing_cases.json`、`execution_cases.json` T05 与路由文档三处同句；T05 判据同步改为「原话与开放终点」。
- **通用验收 P0 加限定**：参考图入帧一条补上「在禁止参考图直接入帧的任务中」与「明确锁定首尾帧时按用户要求判定」，与 SKILL.md、prompt-delivery、reference-and-task-handling、video-acceptance-testing 的锁帧例外对齐。
- **测试样本补齐字段**：第 13–16 项补 intent／genre／medium／form／director_mode，与 1–12 同构；SKILL.md 第 7 步加一句指向 `tests/routing_cases.json`，样本不再是不可达资产。
- **口径清理**：「九维」契约删去 SKILL.md 多列的「故事」（并入主导意图）；通用验收「BGM 与文字按形式矩阵」改为「按默认矩阵（默认无）」；SKILL.md「長镜头」改「长镜头」；tests/README 的「后 3 条／另外两份文件」改为「第 13–16 条／另外三份文件」。
- 已知缺口：作者型只有一条路由样本，未做多场景覆盖；`tests/` 仍无自动校验脚本，字段与原文一致性靠人工核对。

## V3.6.0 · 2026-11-04

- 在保留九维任务契约、多维决策域、S1/S2/S3 与原能力／风格库的基础上，按需加入原创导演概念、镜头执行、材质语法和成片故障诊断。
- 强化决定性事件观察、动态双方对抗、状态承接、事件容量、媒介一致性、终幕及反馈处理；尊重原著与有意留白。
- 扩展路由和固定回归样本，新增用于文本检查的辅助脚本；脚本与文字验收不能证明模型能力或实际成片改善。
- 恢复用户指定的参考图声明、默认无 BGM／字幕／画面文字／额外旁白；删除缺乏依据的时间与字数区间。
- 成片同条件 A/B、实际视频诊断以真实素材与实际执行结果为准，不由版本号自动代表已通过。
