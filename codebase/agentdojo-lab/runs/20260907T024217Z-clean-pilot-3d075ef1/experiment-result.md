## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-09-07
- Verification Status: UNVERIFIED（接入诊断）
- Version Label: unpaced-diagnostic

## 执行结果

此批次原计划30个trial，本轮尝试执行前10个；在第8个结束后停止派发。已完成8个，其中2个原生评估通过、6个因HTTP429无法评估；8份记录均完整。后22个预定槽位未运行，不记作失败。

Groq明确返回该模型每分钟8000 tokens限额。本批次仅用于接入诊断，不与后续节流批次合并统计；原配置和原始日志保持不变。后续调整请求节奏，并在独立目录20260907T025045Z-clean-pilot-b93eae95重做固定任务首轮。

执行命令：`.venv/bin/dojo-lab pilot --config configs/pilot_clean.toml --through-repeat 1`（配置以本目录冻结副本为准）。
