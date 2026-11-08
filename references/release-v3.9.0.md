# KATIL Core V3.9.0 证据等级与交付边界 · 2026-11-08

本版以 V3.8.2 为基线，新增证据等级与模型事实来源分层，为结构化验收用例补正反断言，并增加两条跨版本生成对照任务。不新建第二套创作、动作、镜头或 Seedance 规则，不改变 240 项能力库与 60 项风格库的内容边界，不把文本与结构检查写成成片结论。

## 证据等级（evidence-and-claims.md）

新增 `references/evidence-and-claims.md`，锚点 `katil-evidence`，定义四层证据：

- **EV0 设计**：已有分镜、提示词或测试卡，尚未执行；只能写“已设计”“已写稿”“待执行”。
- **EV1 文本与结构**：确定性文本检查、单元测试、schema、链接、哈希或结构回归；只能写“规则已写入”“结构可运行”“文本检查通过”，不能写模型遵循、镜头成立或成片改善。
- **EV2 生成观察**：至少一次真实生成并观看完整视频，记录模型、版本、参数与次数；只能写“本轮／该版本观察到某现象”，不能写稳定提升或跨模型成立。
- **EV3 同条件盲评**：固定变量，每版达到用例声明的 `runs_min`，证据按哈希绑定，独立盲评；只能写“在该测试集、模型、参数与样本内未再出现某类 P0／P1”，不能写普遍成功率或艺术质量已证明。

证据等级属于具体声明，不属于整个版本。没有实际生成并观看完整视频时，EV2 及以上不成立，生成用例保持 `PENDING_VIDEO`；抽帧或局部观看只支持局部观察。文字保真、提交兼容性、媒体完整性与艺术质量四类结果不互转；结构 PASS 不得改写成成片 PASS。模型事实按 official、platform_measured、unverified_assumption 分层，官方文档只支持 documented，不能单独支撑 COMPATIBLE。

## 模型适配（model-adaptation.md）

- COMPATIBLE 收紧为“平台实测或同任务真实视频观察支持当前方案且要求保留”；缺资料仍为 UNVERIFIED，硬阻塞为 UNSUPPORTED，明确损失为 DEGRADED。
- 新增来源分层段：official 只支持 documented；platform_measured 只支持具名平台、日期、版本与参数下的该任务；unverified_assumption 不得填充未知数值，也不得支撑 COMPATIBLE。
- 兼容仍不等于已上传、已生成或保证成功；无真实视频保持 PENDING_VIDEO。

## 验收与用例

- `video-acceptance-testing.md` 说明本页 P0／P1 不定义证据等级：文字验收为 EV1，单次全片观察为 EV2，同条件多次加盲评为 EV3；未观看保持 PENDING_VIDEO。
- T34–T43 与 C04 新增 `must_hold`／`must_reject` 两个非空字符串数组；`run_regression.py` 对这批结构化用例校验两字段存在、元素非空、数组内无重复、两数组无交集，缺项按结构错误退出 2。原 `criteria`／`expected` 保留。
- 新增 G05（终斩可观察性与后果连续）与 G06（高速双人交锋的阶段可读性），均为 V3.8.1 对 V3.8.2 的同任务对照，`runs_min` 为 3、要求真实视频证据；未生成并评审前保持 PENDING_VIDEO，不写成已通过。

## 注册表与版本

- 新增 EVIDENCE 1.0.0，权威文件 `references/evidence-and-claims.md`，锚点 `katil-evidence`；ADAPTER 由 1.2.0 升至 1.3.0，补来源分层与 COMPATIBLE 边界。其余 8 条规则 revision 不变。
- SKILL.md 新增 EVIDENCE 摘要并更新 ADAPTER 摘要；主技能与动作入口版本 3.9.0，revision 为 `v3.9.0-evidence-and-delivery-2026-11-08`；manifest、agents 描述、库索引标题与回归运行器同步。

## 验证范围

- `python -B -X utf8 -m unittest discover -s tests -p "test_*.py"`：184 项，OK (skipped=1)，退出 0；183 通过、1 跳过（symlinks unsupported）。
- `python -B -X utf8 scripts/run_regression.py --cases tests`：suite PASS，117 条（routing 20、execution 43、continuity 4、style 4、audio 4、generation 6、adaptation 36），111 UNKNOWN＋6 PENDING_VIDEO，0 FAIL，退出 0。
- `python -B -X utf8 scripts/rule_registry_check.py`：PASS，10 条规则；--sync 后再次检查 PASS，semantic_equivalence 仍为 UNKNOWN。
- `python -B -X utf8 scripts/ability_library.py --validate`：PASS，240 项、24 类，v2.0.0；`style_library.py --validate`：PASS，60 项、10 类，v1.9.0。
- 文件结构与链接检查在打包前执行；主包与动作入口的版本、manifest、agents 描述、库索引标题同步为 3.9.0。

以上为文本、结构与软件测试证据（EV1）。没有真实模型生成、成片观看、盲评或艺术质量评审；不得把本版写成视频效果通过或模型已遵循。
