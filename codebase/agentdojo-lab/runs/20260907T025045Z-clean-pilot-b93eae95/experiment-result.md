# Clean pilot v1 paced：首轮结果

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-09-07
- Verification Status: VERIFIED（首轮本地记录与内部一致性审计）
- Version Label: 20260907T025045Z-clean-pilot-b93eae95-round1

本批次 30 个预定槽位中，首轮 10 个不同任务均已完成且通过原生效用评估；10 份记录完整、审计有效，后两轮 20 次尚未开始。运行对象为 AgentDojo workspace v1.2.2 的正常任务，模型为 Groq openai/gpt-oss-120b；工具操作均在本地模拟环境中进行。

首轮共 31 次 SDK 请求，API 报告输入 65,277、输出 2,896 tokens。保存 260 个事件、21 次工具执行、35 次工具结果曝光、8 次环境变化，覆盖 12 种工具。task 0 和 task 33 各出现一次工具错误并自行恢复，主批次无 HTTP 错误。没有单响应提出多个工具调用的真实案例。所有观测仅代表本清单，不是整个 benchmark 的效用或防御效果估计。

各 run elapsed 合计 1,898.745 秒，其中配额等待合计 1,872.016 秒。这些数值不能测量 tracer 开销或服务端推理时间；事件日志总计 3,766,920 字节。两条固定响应离线轨迹的另行对照、时钟控制、噪声与计时排除项见完整结果记录。

主执行命令：`.venv/bin/dojo-lab pilot --config configs/pilot_clean.toml --through-repeat 1`。实现内容对应 `226d7bdae512c4724409606190d5e5c4f3dfa255`，Python 与依赖锁哈希匹配本批次冻结计划，详见 `code-state.json`。此前未节流批次 `20260907T024217Z-clean-pilot-3d075ef1` 的 6 次 HTTP 429 故障另行保留，未合并统计。

- [交互总览](index.html)
- [完整逐槽位 CSV](trials.csv)
- [详细结果、命令与解释边界](../../pilot-results.md)
- [首轮表格 PDF](../../reports/clean-pilot-v1-round1/table_runs.pdf)
- [离线回放对照](../../reports/pilot-replay-cost-clock-controlled/report.html)

下一步按冻结条件完成预定重复，再独立标注参数来源、歧义与未知。本轮尚未实现来源匹配或自适应防御。
