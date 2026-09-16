## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-09-07
- Verification Status: VERIFIED（仅固定响应回放的工程一致性）
- Version Label: pilot-replay-cost-clock-controlled

## 结果

两个来源任务各 5 组配对，另各 1 组预热。每对的出站请求、episode 最终环境/对话和原生效用均一致；开启采集的日志均通过审计。

- user_task_0: paired delta median 4.408 ms.
- user_task_7: paired delta median 6.971 ms.

这是离线固定响应、固定邮件时钟的工程对照，不是新的真实模型重复，也不证明真实部署中的普遍非干扰或端到端开销。完整时钟控制与计时边界见 plan.json。此前未控制邮件系统时钟的回放在环境哈希处发现差异，保留于相邻 pilot-replay-cost-v1 目录，不纳入本报告。

原始配对差值包括负值（task7 最小约 -31.13 ms），保留在 pairs.csv 中；少量本机回放存在调度噪声，因此这些中位数不是精确或稳定的普遍开销估计。
