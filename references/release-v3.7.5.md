# KATIL Core V3.7.5 发布范围 · 2026-11-07

本版以 V3.7.4 为基线，实施非内容扩充型的**工程瘦身、跨专题去重与维护工具链升级**，完整保留 9 大权威规则、200 项能力库、60 项风格库、Seedance 2.5 按需适配及 100 项固定回归用例。

## 主要改动

- **数据卡单文件合并与发布包瘦身**：`references/ability-library/abilities.json` 单文件承载全部 200 项能力卡与分类元数据，`references/style-library/styles.json` 单文件承载全部 60 项风格卡与分类元数据；`ability_library.py` 与 `style_library.py` 优先读取合并文件并向下兼容旧分片。移除离线 `tests/results/` 历史日志、旧版单次发布说明及主包内重复嵌套的 `compatibility/` 目录（顶层 `direct-cinematic-fights` 独立保留），将主技能包文件数从 340 个压缩至 **68 个**（无 `.log` / `.ps1` 等平台禁用后缀）。
- **复制块纯净度门禁收口（`block_lint.py`）**：新增 `copy_block_purity_findings()`，集中检查「如有参考图」条件句、全局「默认无BGM」、块内 `SD25-` 维护编号、表单式转场标题与无时间码自解释赘语，并在 `run_regression.py` 中直接复用。
- **注册表哈希自动同步（`rule_registry_check.py --sync`）**：支持一键重算并回写 9 条规则的权威文件 `SHA-256` 与 `SKILL.md` 闭合摘要块 `SHA-256`。
- **跨专题去重**：清理子专题中重复的通用时间与免责复述，统一指向 `TIME@1.0.0`、`DELIVERY@1.2.0` 与 `REF@1.2.0` 权威锚点。

## 验证范围

- **单元测试**：整合为 4 个测试模块（`test_block_lint.py`、`test_run_regression.py`、`test_model_profile_check.py`、`test_video_evidence.py`），共 **168 项测试全部通过（0 失败）**，新增 `--sync` 自动哈希同步与复制块纯净度门禁专项单测。
- **静态与回归检查**：`rule_registry_check.py`（9 条规则）、`model_profile_check.py`（6 份档案）、`ability_library.py --validate`（200 项）、`style_library.py --validate`（60 项）及 `run_regression.py`（100 项用例结构检查：`96 UNKNOWN + 4 PENDING_VIDEO`）全部 `PASS`，全包 Markdown 内部链接 0 死链。
