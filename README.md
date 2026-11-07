<div align="center">
  <img src="assets/hero-zh.jpg" alt="KATIL-skill — 通用 AI 影视创作与导演系统" width="100%">

  <h1>KATIL-skill</h1>

  <p><b>通用 AI 影视创作与导演系统</b><br/>
  不是提示词模板，是导演决策系统。</p>

  <p>
    <a href="README.en.md"><b>English</b></a> ·
    <a href="SKILL.md">技能入口</a> ·
    <a href="docs/requirement-optimizer.md">需求优化器</a> ·
    <a href="CHANGELOG.md">更新日志</a> ·
    <a href="#快速开始">快速开始</a>
  </p>

  <p>
    <a href="https://github.com/Mcz070321/katil-skill/releases"><img alt="version 3.7.5" src="https://img.shields.io/badge/version-3.7.5-2f2f2f?style=flat-square"></a>
    <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-3da639?style=flat-square">
    <a href="https://github.com/Mcz070321/katil-skill/actions/workflows/ci.yml"><img alt="checks passing" src="https://github.com/Mcz070321/katil-skill/actions/workflows/ci.yml/badge.svg"></a>
    <img alt="167 tests passed" src="https://img.shields.io/badge/tests-167%20passed-2ea44f?style=flat-square">
    <img alt="200 abilities" src="https://img.shields.io/badge/abilities-200-8957e5?style=flat-square">
    <img alt="60 styles" src="https://img.shields.io/badge/styles-60-d29922?style=flat-square">
  </p>
</div>

---

## 这是什么

KATIL-skill 是一个以 [SKILL.md](SKILL.md) 为入口的 **AI 影视导演系统**。它把一句模糊的创作需求，变成一份可执行的镜头设计，再输出中英双语、可以直接粘贴进视频生成框的提示词。

它不预设题材。动作、恐怖、爱情、广告、动画、纪录片、实验影像，都只是同一套决策流程里的可选维度——流程先判断「这次要创作什么」，再决定「该调用哪些模块、由谁主导」。

它也不绑定模型。默认交付平台无关的提示词；只有你明确指定 Seedance 2.5 时，才加载对应的执行适配。

> 一句话：**它先决定这场戏该怎么拍，再决定这段话该怎么写。**

### 它不是什么

- **不是题材模板合集。** 没有「动作片模板」「恐怖片模板」可套；模块只在命中时才加载，且同一决策域只有一个主导。
- **不是提示词美化器。** 它改的是事件、因果、观察路径与容量，不是形容词。
- **不是视频模型或剪辑器。** 它不生成视频、不做转码、不修文件。
- **不做没有证据的承诺。** 未实际生成并观看，它不会宣称成片变好了。

## 为什么需要它

| 常见做法 | KATIL 的处理 |
| --- | --- |
| 一套模板套所有题材，成片千篇一律 | 先立九维任务契约，再按决策域分配模块与主导权 |
| 中文写完再机翻英文，事实对不上 | 先定同一份事件与状态，再写等义双语；台词原句锁定 |
| 一上来堆特效、堆镜头、堆秒数 | 先核算时长与事件容量，过载与状态冲突先返修再交付 |
| 把模型参数写进创作规则 | 适配层只重组表达，不改硬要求；未指定模型不加载 |
| 用「感觉更好」宣布升级 | 文字验收与视频验收分开记录，不互相冒充 |

## 核心设计

1. **九维任务契约** —— 主导意图、题材、媒介、形式、导演模式、时长与平台、观众与用途、硬约束、成功标准。用户已给的不重复问，缺项只问真正影响结果的一处。
2. **决策域单一主导** —— 题材可以多选、模块可以同时在场（例如「恐怖＋爱情＋二维动画」），但同一个决策域只能有一个主导，避免互相打架。
3. **默认事件序，不写时间码** —— 多镜用 `分镜01`，真一镜用 `镜内阶段01`，故事板用 `第01格`。给定了时长才做容量核算；精确到秒只在音画同步、已确认剪辑窗口等必要范围使用。
4. **参考图三态** —— 无参考图 / 普通参考图 / 锁定首尾帧，三种状态的写法完全不同；不写「如有参考图」这种没有信息量的条件句。
5. **空间三模式** —— S1 屏幕坐标（默认，表演与叙事）、S2 世界坐标（建筑、产品、科学可视化）、S3 混合（复杂动作、巨物、空战）。
6. **双语独立复制块** —— 每段、每种语言各有一份完整、纯净、可直接粘贴的块；英文不是中文的缩写版，改动任何一版都要同步另一版。
7. **交付前返修** —— 容量、状态连续、手脚与支点占用、终态承载逐项核对；发现的冲突先改正文，不能只在内部写一句「注意容量」。
8. **验收分层** —— 文字验收可以现在跑；视频验收必须真实生成并观看。两者分开记录，样本不足就标「不确定」。

## 快速开始

### 1. 获取

```bash
git clone https://github.com/Mcz070321/katil-skill.git
```

### 2. 安装到 Agent 的技能目录

把整个目录放进运行时的 skills 路径，目录名保持 `katil-skill`：

```bash
# Claude Code
mv katil-skill ~/.claude/skills/katil-skill

# 其他兼容 Agent Skills / SKILL.md 的运行时
mv katil-skill ~/.agents/skills/katil-skill
```

技能入口是 [SKILL.md](SKILL.md)；[manifest.yaml](manifest.yaml) 声明版本、兼容范围与验证边界；[agents/openai.yaml](agents/openai.yaml) 供支持该清单的运行时读取显示名与默认提示。

### 3. 触发

在对话里说 **KATIL**、**提示词 skill**，或直接描述影视创作任务。

### 4. 一个最小任务

> 用 KATIL 写一场 30 秒的雨夜便利店戏：刚下夜班的女孩发现店员是她多年未见的同学。要克制，不要配乐。

正常会得到：任务契约确认 → 必要的追问（最多一处）→ 角色图 / 场景图 / 视频提示词 → 中文复制块 + 等义英文复制块 → 块外的交付前自检说明。

## 配套工具：需求指令优化器

KATIL 的上限，一半由你的需求决定。如果你手里只有一句想法、一堆零散要求、一份旧提示词、一段原著，或一次成片反馈，可以先用配套的**需求指令优化器**把需求整理成 KATIL 能直接执行的指令。

- 中文版：[docs/requirement-optimizer.md](docs/requirement-optimizer.md)
- 英文版：[docs/requirement-optimizer.en.md](docs/requirement-optimizer.en.md)

用法只有三步：

1. 把这份文件的内容交给任意一个能读文本的 AI，作为它本轮的工作规则；支持上传文件的对话可以直接上传。
2. 说出你的原始想法。有原文、参考图、旧提示词或生成结果时，把实际内容一并给出。
3. 把它输出的一段代码块原样发给正在运行 KATIL-skill 的助手，附件再附一次。

它处理的是技能**之前**那一层——「我说不清要什么」：把含糊诉求拆成目标与体验、必须保留、重点解决、可设计范围、交付范围，同时把硬约束、偏好与未定信息分开；不替你写分镜、不加你没说过的剧情、不锁定你没指定的时长与画幅。

两条边界要讲清楚：优化器产出的是**给 KATIL 的需求稿**，不是最终视频提示词；它也不传递附件、不安装 KATIL。文件自身注明基于 V3.7.2 的工作方式整理——如果你的 KATIL 已更新，以运行中技能的当时规则和你的当轮要求为准。

## 交付长什么样

下面是**格式示意**，用于展示事件序、正向描述与中英对应关系，不代表效果承诺：

**中文复制块**

```text
分镜01 雨夜，便利店的自动门在女孩身后合拢，把街上的雨声压成一条细线。她停在关东煮的热气前，手指还捏着工牌挂绳。
分镜02 收银台后的店员抬头，目光在她工牌上停住；他手里的扫码枪垂下，红光落在台面上。女孩顺着他的视线低头，把工牌翻了过去。
分镜03 两人隔着热气对视，谁都没有先开口。冰柜压缩机启动，灯光轻轻一颤；女孩把伞靠在门边，伞尖的水在瓷砖上摊开一小片。
```

**English copy block**

```text
Shot 01 Rainy night. The automatic door closes behind the girl, narrowing the street noise to a thin line. She stops in front of the steam from the oden pot, still holding the lanyard of her work badge.
Shot 02 The clerk behind the counter looks up; his gaze catches on her badge. The scanner lowers in his hand, its red light pooling on the counter. She follows his look and turns the badge face-down.
Shot 03 They hold each other's gaze through the steam, neither speaking first. The freezer compressor kicks in; the light trembles slightly. She leans her umbrella by the door, and the water at its tip spreads across the tiles.
```

注意几个刻意的选择：没有时间码，没有形容词堆砌，没有「不要什么」的解释句，每个镜头都落在一个可见的变化上，中英两版是同一批事件。

## 能力库与风格库

- **200 张角色能力卡（C01–C20）** —— 覆盖现实、科幻、奇幻三类世界，每张按「机制与用途 / 动作与应答 / 特效描写 / 限制与反制 / 镜头与声音 / 残留与连续性」组织，避免把能力写成没有代价的万能招。
- **60 张视觉风格配方（F01–F10）** —— 从真人纪实到日式二维、传统绘画、定格与实验混合媒介；每张含角色图、场景图、视频三种风格片段的**中英双语**写法。
- **9 条权威规则** —— 带 SHA-256 溯源与摘要块，见 [rules/rule-registry.yaml](rules/rule-registry.yaml)。

两个库都是只读检索，不需要打开整份 JSON：

```bash
python scripts/ability_library.py --query "冰" --limit 2
python scripts/style_library.py --list-families
python scripts/style_library.py --family F06 --limit 2
```

<details>
<summary>输出示例（节选）</summary>

```text
## A131 冰楔错步
适用：奇幻｜冰水与流体｜控制、进攻
- 机制与用途：霜契者抽取附近水洼的水并耗去寒纹，在对手前脚落点形成浅冰楔，
  以突变坡度打乱重心而非冻结整个人。
- 限制与反制：需要近处有水且落点可见，寒纹用尽便不能成冰；
  砂砾铺面、提前跳跨或重踏破楔都能反制。
```

```text
F06 日式二维动画: S031-S036
匹配6项，显示2项；风格片段需融入实际设计。
```

</details>

## 仓库结构

```text
katil-skill/
├─ SKILL.md                技能入口：9 步统一流程与「按任务读取」路由表
├─ manifest.yaml           版本、兼容范围、验证边界（机器可读）
├─ CHANGELOG.md            版本记录（当前 3.7.5）
├─ agents/openai.yaml      运行时清单：显示名、简介、默认提示
├─ references/             37 个专题文档 + 3 个数据目录
│  ├─ general-creative-core.md      多维契约、模块决策权、TIME 规则
│  ├─ action-and-shot-compiler.md   动作编排与关键因果
│  ├─ narrative-and-performance.md  文戏、对白、人物关系
│  ├─ horror-and-suspense.md        恐怖、悬疑、心理压迫
│  ├─ camera-direction.md           运镜
│  ├─ spatial-coordinate-system.md  S1／S2／S3 空间
│  ├─ sound-and-rhythm.md           声音四层与节奏
│  ├─ prompt-delivery-and-language.md  复制块、双语、台词锁死
│  ├─ general-acceptance.md / video-acceptance-testing.md  两级验收
│  ├─ ability-library/abilities.json    200 张能力卡
│  ├─ style-library/styles.json         60 张风格卡
│  └─ model-capabilities/seedance-2.5.json
├─ rules/rule-registry.yaml  9 条权威规则与摘要哈希
├─ scripts/                 7 个校验 / 检索脚本
├─ tests/                   167 项软件测试、100 条回归用例与样本
├─ docs/                    配套工具：需求指令优化器（中英双语）
└─ assets/                  图标与中英横幅
```

## 质量与验证

这个仓库做了它能做的检查，并且明确写出哪些检查做不了。

```bash
python -m pytest tests -q
python scripts/rule_registry_check.py
python scripts/model_profile_check.py
python scripts/ability_library.py --validate
python scripts/style_library.py --validate
python scripts/run_regression.py --cases tests --out regression_result.json
```

当前状态（2026-11-07；Windows 11 / Python 3.12.7 / pytest 7.4.4 本地运行，GitHub Actions 上另有 Linux + Python 3.12 的同套检查）：

| 检查 | 结果 |
| --- | --- |
| `pytest tests` | **167 passed**（Linux CI，含符号链接用例）；**166 passed, 1 skipped**（Windows 本地） |
| `rule_registry_check.py` | PASS，9 条规则；语义等价性 UNKNOWN（需人工复核） |
| `model_profile_check.py` | PASS（仅结构与来源链接）；semantic_support 始终 UNKNOWN |
| `ability_library.py --validate` | PASS，200 项，C01–C20 |
| `style_library.py --validate` | PASS，60 项，F01–F10 |
| `run_regression.py` | 100 条用例结构检查：96 UNKNOWN + 4 PENDING_VIDEO |

**边界，写在最前面：** 以上全部是文本层与软件层的验证。[manifest.yaml](manifest.yaml) 里的 `validation_scope` 写得很直白——`E1: fixed text tasks and software tests; no real-model/video claim`。本仓库没有附带真实模型生成与成片评审证据，也不把「结构检查通过」当成「画面变好了」。历史证据目录（`tests/README.md` 中提到的 `results/v3.x`）属于发布时的离线记录，未随技能包分发。

## 版本与兼容

- 当前版本 **3.7.5**（2026-11-07），发布通道 `stable`
- 兼容范围 `compatible_core: ">=3.7.0,<4.0.0"`
- 能力库 1.8.0 / 风格库 1.9.0
- 变更记录见 [CHANGELOG.md](CHANGELOG.md)；本版发布范围见 [references/release-v3.7.5.md](references/release-v3.7.5.md)
- 规则治理与哈希同步见 [references/rule-registry-maintenance.md](references/rule-registry-maintenance.md)

## 常见问题

<details>
<summary><b>必须用 Seedance 2.5 吗？</b></summary>

不必。默认交付平台无关的提示词；只有明确指定 Seedance 2.5（或同一作品已确认该模型）时才加载 2.5 执行适配，而且适配只重组表达，不改你的硬要求、台词、时序与结局。
</details>

<details>
<summary><b>会自动加 BGM、字幕或旁白吗？</b></summary>

不会。未经要求不擅自加入音乐、字幕、画面文字与额外旁白。你明确说「静音」「无配乐」「只要环境声」时，模块默认值让位。
</details>

<details>
<summary><b>一次能做多长？有固定镜长吗？</b></summary>

没有固定的镜长、镜数、回合数或「每秒几个动作」公式。你给总时长，它就核算事件容量；内容装不下时，会先列出冲突并给出分段、缩小范围或调整时长的实际选项，而不是硬塞。
</details>

<details>
<summary><b>能做动画、广告、纪录片吗？</b></summary>

能。媒介（真人／二维／三维／定格／混合）和形式（短片／故事板／长视频／系列／预告）是契约里的维度，不是附加功能。广告会保护产品事实边界，纪录片会先立事实与观察规则。
</details>

<details>
<summary><b>可以直接商用吗？</b></summary>

代码与文档是 MIT，见 [LICENSE](LICENSE)。你用它生成的画面、角色与素材，版权与商用条件取决于你使用的模型和平台条款，不由此仓库授予。
</details>

<details>
<summary><b>为什么 README 不放「使用前后对比」？</b></summary>

因为没做同条件、同模型版本、多次生成并实际观看的对照。放一张精选成片当证据，恰恰是这个项目反对的做法。要评估请按 [references/video-acceptance-testing.md](references/video-acceptance-testing.md) 自己跑 A/B，并接受小样本不能推断统计显著性。
</details>

## 参与贡献

欢迎 issue 与 PR：新的能力卡、风格卡、回归用例、文档修订、脚本健壮性。

改动规则时请同步 [rules/rule-registry.yaml](rules/rule-registry.yaml) 的摘要与哈希：

```bash
python scripts/rule_registry_check.py --sync
python -m pytest tests -q
```

提交前请至少跑通上面「质量与验证」里的六条命令。涉及语义的改动，请在 PR 里说明你实际改了什么、为什么，以及哪些结论仍需人工复核。

## 许可

[MIT](LICENSE) © 2026 Mcz070321

第三方视觉与特效研究来源见 [references/style-study-sources.md](references/style-study-sources.md) 与 [references/vfx-study-sources.md](references/vfx-study-sources.md)。

---

<div align="center">
  <sub>KATIL-skill · V3.7.5 · 写给人看的分镜，也写给模型看的指令。</sub>
</div>
