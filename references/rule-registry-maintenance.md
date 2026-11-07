# 规则注册表维护

仅在规则维护、冲突审查或发布检查时读取；普通创作不加载注册表。

`rules/rule-registry.yaml` 为沿用的文件名，内容只接受严格 JSON 子集，由标准库 `json.loads` 解析；不支持 YAML 注释、锚点或其他 YAML 专用语法。合同版本保持 1.0.0。

每条规则必须有至少一项 `summary_refs`。每项记录路径、marker、rule_revision 和 `summary_sha256`；对应文件中用唯一的 `<!-- SUMMARY of ID@revision -->` 与 `<!-- END SUMMARY of ID@revision -->` 包围独立的非空正文，不将多个规则的marker堆在同一条摘要前。

摘要哈希的输入为两标记之间的正文：先将 CRLF／CR 统一成 LF，再去除正文首尾空白，按 UTF-8 编码计算 SHA-256；不改正文内部空白。权威专题的 `authority_sha256` 仍按原始文件字节计算。

修改摘要或权威专题后，先人工对照两者的实际含义、用户优先级和适用边界，再更新相应哈希与审查记录；不要为消除报错而盲目刷新哈希。重复摘要块、空摘要、正文被删／改、修订不匹配或路径错误都不能通过 `python scripts/rule_registry_check.py`。

检查器验证定位、修订与内容完整性，无法认证摘要与权威专题语义等价、审查者身份或视频效果；`semantic_equivalence` 仍为 `UNKNOWN`。发布时分别保存软件测试、人工／模型文字审查和真实媒体证据。

## 自动同步哈希

修改权威文件或 `SKILL.md` 摘要正文后，可直接运行 `python scripts/rule_registry_check.py --sync` 自动重算并写回 `authority_sha256` 与 `summary_sha256`，随后脚本会自动执行完整性校验。
