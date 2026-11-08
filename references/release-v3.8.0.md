# KATIL Core V3.8.0 发布范围 · 2026-11-08

本版以 V3.7.5（单文件库与工程瘦身版）为基线，将能力与视效库由 200 项（`C01—C20`，`v1.8.0`）升级至 **240 项（`C01—C24`，`v2.0.0`）**，补齐非战斗影视创作的四大视效象限。

## 主要改动

- **新增 `C21—C24` 共 40 项非战斗影视视效卡（`A201—A240`）**：
  - `C21 商业微距与产品视效`（10 项）：覆盖护肤品乳化、饮品高速入水冠冕、硬件同轴悬浮拆解、汽车风洞流线、织物微距、液态金属成形、香氛散景、芯片脉冲、日晷光影与咖啡油脂拉花。
  - `C22 自然天象与宏观奇观`（10 项）：覆盖极光折卷、深海荧光涡流、双月潮汐、穹顶丁达尔圣光、四季延时枯荣、雷暴云墙、灰幕日食、荒原蜃景、硬科幻星环流火与高山云瀑日晕。
  - `C23 心理梦境与超现实转场`（10 项）：覆盖空间碎镜剥落、地面液化深潜、镜廊慢拍错位、走廊重力翻转、胶片烧穿闪回、人物轮廓风化散沙、雨滴悬停升空、瞳孔缩入换景、室内拉伸荒原与画布融化入实。
  - `C24 怪谈异变与诡异氛围`（10 项）：覆盖烛火转绿逆影、纸人渗墨转睛、墙面潮痕漫延、红绸逆风悬铃、CRT雪花屏显背影、井水倒影脱节、长廊逐盏断电逼近、石像裂纹渗泪、门缝黑水漫入与冥纸旋风空巷。
- **专题路由打通**：在 `SKILL.md`、`realism-and-advertising.md`、`narrative-and-performance.md`、`horror-and-suspense.md` 中接入 `C21—C24` 按需检索指引，使用户仅提供“想象画面＋视频类型”时也能获得精准的非战斗视效补全。
- **保持 70 文件轻量结构**：全部 240 张卡统一封装于 `references/ability-library/abilities.json`，文件总数零增加（主包 70 个文件，含 `direct-cinematic-fights` 共 75 个文件）。

## 验证范围

- `python scripts/ability_library.py --validate`：240 项、24 类（每类 10 项）、ID 连续性与四段式 `signature` 唯一性校验 `PASS`。
- `python scripts/style_library.py --validate`：60 项、10 类校验 `PASS`。
- `python scripts/rule_registry_check.py --sync`：9 条权威规则双向 `SHA-256` 校验 `PASS`。
- `python scripts/model_profile_check.py`：6 份 Seedance 2.5 模型与渠道能力档案校验 `PASS`。
- `python -m unittest discover -s tests`：168 项中 167 项通过、1 项跳过（`symlinks unsupported`）；跳过不是通过。
