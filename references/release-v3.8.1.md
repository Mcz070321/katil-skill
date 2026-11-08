# KATIL Core V3.8.1 修复范围 · 2026-11-08

本版以 V3.8.0 为基线，只做卡名、文档口径与回归覆盖的维修，不新增创作框架、不改变 240 项能力库与 60 项风格库的内容边界。

## 修复

- **A224 卡名统一为「走廊重力翻转」**：修正 `references/ability-library/abilities.json` 与 `references/ability-library/index.md` 中的「走廊重力折翻转」，并在 `tests/test_run_regression.py` 增加 `test_v381_a224_name_is_canonical_in_card_and_index`，同时断言卡名与索引行。
- **C23 发布说明对齐实际卡名**：`references/release-v3.8.0.md` 的「镜廊延迟错位／雨滴悬停倒流／油画融化入实」改为「镜廊慢拍错位／雨滴悬停升空／画布融化入实」。
- **回归文档计数与路径修正**：`tests/README.md` 的无响应文本项由 76 改为 96；删除包内不存在的 `results/release_manifest.json` 指向；把 80 项／76 UNKNOWN 明确标为 V3.7.2 历史口径，当前为 100 项／96 UNKNOWN＋4 PENDING_VIDEO。
- **测试口径如实记录**：V3.8.0 的 168 项测试实际为 167 通过、1 跳过（`symlinks unsupported`）；V3.8.1 新增 1 项回归测试后共 169 项，168 通过、1 跳过。跳过不是通过。
- **版本同步**：主技能与动作兼容入口的 `integration-version` 均为 3.8.1，revision 为 `v3.8.1-card-name-and-evidence-doc-fix-2026-11-08`；manifest、agents 描述、库索引标题与回归运行器版本同步。

## 验证范围

- `python -X utf8 -m unittest discover -s tests -p 'test_*.py'`：169 项，`OK (skipped=1)`，退出 0；168 通过、1 跳过。
- `python -X utf8 scripts/ability_library.py --validate`：PASS，240 项、24 类、每类 10 项，v2.0.0。
- `python -X utf8 scripts/style_library.py --validate`：PASS，60 项、10 类，v1.9.0。
- `python -X utf8 scripts/rule_registry_check.py`：PASS，9 条规则；`model_profile_check.py`：PASS，6 份档案。
- `python -X utf8 scripts/run_regression.py --cases tests`：suite PASS，100 条，96 UNKNOWN＋4 PENDING_VIDEO，0 FAIL，退出 0。
- 文件结构：主包 71 个文件，含 `direct-cinematic-fights` 共 76 个文件。

以上为文本、结构与软件测试证据；没有真实模型生成、成片观看或艺术质量评审，不能据此声称视频效果通过。
