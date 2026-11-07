# V3.7.5 回归样本与脚本边界

本版以现用 V3.7.3 为基线，原88项输入和预期保留，新增 T22–T33 共12项。结构回归共100项，无响应时96 UNKNOWN和4 PENDING_VIDEO；定向完整提示词回归另存实际回答及逐案评审。当前版本证据见 `results/v3.7.4`。

新增可选字段 `timing_mode` 接受 `event_driven`、`timecoded`、`local_anchor`。回归运行器仅对显式 `event_driven` 用例启用镜头时间标签检查；既有未标记用例沿原检查行为。授权时点位置、全片覆盖、容量及双语等义须结合实际回答审查。

`python scripts/block_lint.py prompt.md --timing-policy forbid` 在复制块内警示明确的镜头／阶段时间标签，包括编号后的区间、时点和单镜时长。存在围栏时只对围栏内做此检查，无围栏时检查纯文本提示词。默认 `auto` 沿用原区间检查。总长、剧情延迟、距离、表盘读数及块外技术说明按各自用途处理。未识别标签或没有警示的结果仍需语义核对。

下文为 V3.7.3 及更早版本的验收沿革，计数和结论按各自版本理解。

# V3.7.3 回归样本与脚本边界

本轮新增 T14–T21 关键事件、终态、冲击帧与反例共8条，原80项输入与预期不改；现有套件共88项。下文 V3.7.2／3.7.1 的数量与结果属于历史阶段。新样本结构可校验，但未执行的创作输出仍为 UNKNOWN，真实视频仍为 PENDING_VIDEO。当前结果见 `results/v3.7.3`。

回归工程沿革自 V3.6.4，当前包为 V3.7.3；历史结果与本次软件复跑分别记录。V3.7.0 的 40 条文字任务已有非盲文本执行记录，结果见 `results/text_regression_report.json` 和 `results/forward_outputs.md`；4 条历史视频对照仍待实际验证。这里的“待执行”描述固定用例本身，不覆盖上述历史执行记录，也不代表后续修改已重跑创作回归。

`routing_cases.json` 的前12条保留V3.5.2实际输入及路由预期，第13–16条为概念档位（约束／约束／极简／作者）；第14项固定原文同时见本页所述样本文件与 `../references/routing-regression.md`；`execution_cases.json` 的 T05 为近义改写，不能与固定原文混作逐字相同的输入。`execution_cases.json` 保留 T01–T08，新增 T09–T13：祭庙战容量返修、锁定动作边界、强效果高速正向对照、巨物多人联动与恐怖文戏留白。T09 的输入节选见 `fixtures/temple_battle_excerpt.md`；它明确哪些事件锁定、哪些战术补全可重编，不冒充完整原稿。`continuity_cases.json` 与 `style_cases.json` 提供连续性、风格边界；`audio_cases.json` 的 A01–A04 检查声音目的判断。它们是待执行测试任务与预期，不代表模型或技能已经通过。请让独立执行者只看输入和技能，给出实际路由或提示词，再用预期审查。路由与完整创作质量分开。

G01–G03 保留 V3.6.1 对 V3.6.2 的历史生成任务；新增 G04 为 V3.6.2 对 V3.6.3 的祭庙战新生成对照，不改写历史版本。回归运行器接受任意两个不同三段版本号，并按该用例版本核对证据分组。新增用例不是已执行结果，关键词或字段齐全不能证明容量、支点、媒介或成片质量通过。

`video_regression_manifest.json` 按用户口述记录旧样本归属：1000034265.mp4＝用户第二版提示词，1000034266.mp4＝DeepSeek 与用户融合的提示词。文件、原始提示词和生成参数均未取得，故不记录原片观察或虚构结果；旧成片不能证明新版提升。需要同任务、同模型版本与尽量相同参数进行多次 A/B 新生成并实际观看后才可评价，且小样本不能推断统计显著性。`generation_cases.json` 要求每个用例至少 3 次生成，G03 为正向对照，防止新规则把动作压得过慢、过平。

另新增 `1000034429.mp4` 诊断记录：本次会话已取得视频和用户提供的对应提示词，观察证据为抽帧与关键段密集抽帧；原速、音画同步、角色图及生成参数仍未知。视频不随包分发，只保存带范围声明的文字节选。它不能代替 G04 同条件新生成的 V3.6.2 基线；G04 同时检查是否为简化编排而牺牲用户指定强度与异变。

## 回归运行器

```powershell
python -X utf8 scripts/run_regression.py --cases tests --out regression_result.json
python -X utf8 scripts/run_regression.py --cases tests --responses responses.json --prompts prompts
```

运行器检查用例结构、字段、音频预期、媒体完整性、证据重复与外部评审记录的对应关系，不自动判断动作、美术或艺术质量。V3.7.2 延续验收工程、规则注册表与按需模型适配检查；G01–G04 的历史比较版本与待执行状态保持不变。

生成用例请求汇总 `video: PASS` 时，响应须给出比较版本各自的完整证据列表、模型与参数、生成次数，以及另存的逐条评审 JSON 路径。旧的 `reviewed=true` 单独存在不再有效：

```json
{
  "G01": {
    "video": "PASS",
    "model": "目标视频模型",
    "model_version": "实际版本号",
    "parameters": "实际时长、画幅、帧率、种子和参考绑定等设置",
    "runs": {"3.6.1": 3, "3.6.2": 3},
    "evidence": {
      "3.6.1": ["videos/a1.mp4", "videos/a2.mp4", "videos/a3.mp4"],
      "3.6.2": ["videos/b1.mp4", "videos/b2.mp4", "videos/b3.mp4"]
    },
    "review_file": "reviews/G01.json"
  }
}
```

证据与评审路径都相对 `--responses` 文件目录解析，也支持绝对本地路径。`ffprobe` 须可从 PATH 调用；运行器限制探测协议为本地 file／pipe，以30秒为单文件探测超时，读取多帧并检查视频流、尺寸和有限正时长。不是只看扩展名。无工具或超时保持 `PENDING_VIDEO`，已确认无效的媒体判 `FAIL`；ffprobe 的非致命 stderr 不单独否决，记入 `probe_warnings`，只有非零退出或媒体流／帧结构不可解析才判 `FAIL`。

媒体证据须满足：各版数量与声明次数一致且不低于 `runs_min`，路径解析、文件实体和 SHA-256 在整个用例的组内及跨版本均不重复。复制改名也不能多算一次。哈希不能识别所有重编码、剪辑或视觉近似重复，更不能认证生成来源；模型设置和生成次数仍需来源记录支持。

独立存放的评审文件格式如下。示例只展示第一条；实际 `clips` 必须覆盖两版每条证据。`index` 从1起，与该版 evidence 顺序对应，`sha256` 必须填当前视频的真实完整哈希，不能填示例文字：

```json
{
  "case_id": "G01",
  "reviewer": {"id": "实际评审者标识", "kind": "human"},
  "reviewed_at": "2026-11-05T16:00:00+08:00",
  "clips": [
    {
      "version": "3.6.1", "index": 1,
      "sha256": "此处填写真实64位SHA-256",
      "viewing": "full_video", "verdict": "PASS",
      "observations": [
        {"criterion": "关键接触", "time_seconds": 5.2, "observation": "填写实际看见的交点、偏转和受力结果"}
      ]
    }
  ]
}
```

`reviewer.kind` 为 `human` 或 `model`；`reviewed_at` 为带时区 ISO 时间；`viewing` 为 `full_video`、`frames` 或 `partial_video`。评审者应对照用例 focus、硬要求及适用 P0/P1 逐项记录；抽帧与局部观看不足以证明全片通过，音画同步另需对应音轨证据。

- `evidence_status`：只报告媒体、唯一性、次数及参数记录检查。通过不代表成片好，也不证明独立生成。
- `review_status`：外部逐条评审的汇总，缺记录或观看范围不足保持 `PENDING_VIDEO`；无效、错用例、漏条目、重复条目或错哈希不能通过。
- `quality_verdict_source`：指出是否导入外部评审。程序不认证评审者身份、独立性或实际观看行为；伪造评审文件仍不能被视作可信认证。
- 外部评审含 `FAIL` 则汇总失败；含 `WARN` 且全片评审齐全则汇总警示；全部符合且全片评审均为 `PASS` 才导入该结论。程序没有自行给艺术质量打分。
- 无响应时76条文本项仍为 `UNKNOWN`、4条视频项仍为 `PENDING_VIDEO`；不能由结构检查制造执行结果。
- 结构错误退出2，证据或评审失败退出1，其余退出0。返回0也可能全部尚未验证。

当前软件测试的运行环境、执行/通过/跳过数和跳过原因见 `results/release_manifest.json`；历史日志不作为后续修改已复跑的证据。

测试中的短视频与评审 JSON 均为临时合成的软件测试夹具，用于验证分支；不是实际生成案例或艺术评审。媒体集成测试需 ffmpeg／ffprobe，缺工具时对应测试跳过，必须报告跳过数。

## 静态检查

```powershell
python -X utf8 scripts/block_lint.py prompt.txt --duration 30 --language zh --task-type action --reference-mode none
python -X utf8 -m unittest discover -s tests -p 'test_*.py'
```

可选 `--previous-state state.txt` 只读取并记录是否提供，无法进行语义对照；`--allow-overlap` 表示用户明确接受同轨重叠。文本可以混合使用语言标题下的纯文本与独立代码块，也可以用 `[track:camera]`、`[track:sound]` 分轨；每块、每轨的区间分开比较。支持行首 0—2秒、0.5–1.5 s、00:01–00:02 及 00:00:01.250–00:00:02.500 等。单点、帧范围、行内未解析的疑似时间段、过大的非有限数值、未识别格式、未提供目标时长均不能证明时间校验通过；对于带明确距离单位的数字区间尽量不当作时间，但模糊数字仍可能需要人工确认。重叠与间隙可为有意选择，因此只警示。

脚本仅对**识别出的时间区间**检查顺序、时长、缺口和同轨重叠。人工需要检查身份、持物及换手、图像绑定、单双语和台词、参考模式、跨段承接、声音、文本重复、内部术语、事件/风格和生成结果；这些语义项一律 UNKNOWN 或在显式标签冲突时 WARN，不能因为程序返回而视为通过。整体 PASS 不作为视频生成、动作正确或成片效果的依据。

报告的 `timing` 仅说明已识别区间的有限检查，`coverage` 单独标记为 UNKNOWN：未声明需要完整覆盖时，不能推断片首、片尾或留白是否有意。含围栏与带语言标签的非围栏内容会分别检查，普通说明文字不自动视为复制块。JSON 禁止 NaN/Infinity。

## Seedance 2.5适配文字回归

`model_adaptation_cases.json` 保存M01–M36的完整请求、独立前文和实际素材条件；评审标准单独存于 `model_adaptation_expectations.json`。执行者只读技能及输入，不看预期，逐案保存实际回答，再由评审者对照。真实图像/原片不可见时，文字职责和状态处理可以复核，图像身份、尾帧和接缝仍为UNKNOWN。M23实际源文本超过渠道字符上限，M36要求调用旧Production只读导出；承诺、伪输出或手写CSV不能冒充工具执行。

80项为原44项加36项适配；原16条路由的请求、预期与顺序不变（3.7.2仅清理两处重复标点）；M编号与A01–A04声音用例分开。未提供响应时76 UNKNOWN＋4 PENDING_VIDEO，不制造文字PASS。当前结果与历史结果分期，旧35 PASS／5 WARN不移植为3.7.2结果。

适配响应使用 `adaptation`（PASS／WARN／FAIL／UNKNOWN）和可选 `text_review_status`；`submission_compatibility` 独立取UNVERIFIED／UNSUPPORTED／DEGRADED／COMPATIBLE，缺省UNVERIFIED。运行器只导入外部声明，不自行认证来源或配置就绪。适配文字套件的 `video` 保持PENDING_VIDEO，拒绝从这里导入视频PASS；视频证据仍走生成用例专用校验。

```json
{
  "M21": {
    "adaptation": "PASS",
    "text_review_status": "PASS",
    "submission_compatibility": "UNVERIFIED",
    "video": "PENDING_VIDEO",
    "notes": ["文字保留要求；实际渠道参数与素材提交尚未核验"]
  }
}
```

`python scripts/model_profile_check.py` 默认检查内置自然语言能力档案，也支持 `--profile PATH`；标准库实现，返回结构错误位置和0/1退出码。它不接受Production API profile替代，也不认证网页声明、UI当前状态、实际生成或作品语义。单元测试中的合成值仅检验检查器分支，不是新增官方能力。
