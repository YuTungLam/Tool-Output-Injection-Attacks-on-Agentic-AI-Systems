# NeuroTaint-style 语义组件：固定协议与复现边界

## Material Passport

- Origin Skill: academic-research-suite
- Origin Mode: engineering implementation / recorded-trace analysis
- Origin Date: 2026-09-08
- Verification Status: 协议先于本轮 pilot 语义评分固定；运行验证见下方结果记录
- Version Label: nt-style-semantic-v1

## 本轮完成条件

实现论文 Tier 3 的 MiniLM 余弦比较与 Tier 4 的分块比较，接入现有历史前缀分析，保存可复核的模型、输入、分块和截断信息。读取原有 10 条 clean 轨迹，不重新调用 Groq，不改原始轨迹。代码默认仍只运行 exact/LCS；语义层必须显式启用。

本版本**对每个可见来源—参数对分别计算各组件**，没有按命中提前停止，也没有构建完整 NeuroTaint 级联。候选数量和离线总耗时都不能冒充论文级联的准确率或成本。

依据：[NeuroTaint §4.2](https://arxiv.org/html/2604.23374v1#S4.SS2)、[§5.1](https://arxiv.org/html/2604.23374v1#S5.SS1)、[MiniLM 官方模型卡](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)。论文未充分说明的细节在下面作为本地实现假设公开，不声称与作者代码逐行一致。

## 冻结配置

| 项目 | 配置 |
| --- | --- |
| 模型 | `sentence-transformers/all-MiniLM-L6-v2` |
| Revision | `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` |
| 本地模型清单 | 包内 `model_pins/minilm-v1.json`，启动逐文件验证 SHA256 |
| 上游校验 | 配置及词表核对 Hugging Face Git blob；权重核对 LFS SHA256 |
| 编码 | CPU、float32、模型原生 pooling、归一化 embedding；不更新参数 |
| 最大序列 | 256 tokens，包含特殊 token，记录原始/实际 token 数及原文编码范围 |
| 普通语义阈值 | cosine ≥ 0.60 |
| 覆盖率阈值 | ≥ 0.10 |
| 参数单位 | 当前提议的 JSON 叶值；字符串原文，非字符串标量用 JSON 表示 |
| 来源单位 | 当前实际出站请求的文本部件，沿用曝光验证与时间边界 |
| 比较范围 | user/system/developer/assistant/tool 均作为单独候选，tool 单独统计 |
| 分句假设 | `. ! ? 。 ！ ？` 后的空白，或换行；不使用语义分句模型 |
| 分块假设 | 每块 3 句，相邻重叠 1 句；保存原文 Unicode 半开区间 |
| 覆盖率假设 | 过语义阈值的块中，实际编码 token 范围的并集长度 / 原文全部码点数 |
| 资源范围 | 每输入最多 65,536 码点，每来源最多 128 块；超限显式未评分 |
| 缓存 | 固定编码器实例内按精确文本缓存；最多 1,024 条和 1,048,576 码点 |

标点缩写、没有空格的中文句子、YAML 行和长单句可能产生不理想的块。本轮不根据已有任务结果临时调整这些规则；更换规则需使用新配置/版本。

普通阈值适用于本轮单会话 clean 组件分析。尚未实现论文的 RAG/memory 与 safe-control 策略档位；不能根据评测标签自动改为 0.85 或 0.95。所选模型是英语句子/短段编码器，不应将本轮结果外推为跨语言传播能力。

## 截断与未评分

Tier 3 保留整段来源和参数的编码窗口。Tier 4 对每个块另做编码；块过长仍会截断。过阈值块只有**实际编码范围**进入覆盖率分子，重叠范围只计一次。token 范围是首末有效 token 的原文包络，包络内空白也计入长度；这不是逐 token 内容贡献度。

`status=scored` 表示能计算编码视图的相似度，不等于已完整处理原文。`truncated` 和 `complete` 描述输入处理范围，不是结论置信度。`not_applicable`、`budget_exceeded`、`encoder_error` 使用空分数和空 matched，不能当作已测负例。报告展示来源与参数的截断信息。

高相似度仍可能只是相同主题；低相似度也不能排除控制影响。参数生成原因、恶意性、用户授权和语义重合必须分开分析。

## 安装、下载与运行

```bash
UV_CACHE_DIR=.uv-cache .bootstrap/bin/uv sync --extra figures --extra semantic

HF_HOME=.model-cache/hf HF_HUB_DISABLE_IMPLICIT_TOKEN=1 HF_HUB_DISABLE_TELEMETRY=1 \
  .venv/bin/hf download sentence-transformers/all-MiniLM-L6-v2 \
  model.safetensors config.json config_sentence_transformers.json modules.json \
  sentence_bert_config.json special_tokens_map.json tokenizer.json tokenizer_config.json \
  vocab.txt 1_Pooling/config.json \
  --revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 \
  --local-dir .model-cache/all-MiniLM-L6-v2-1110a243

HF_HUB_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 \
  .venv/bin/dojo-lab provenance \
  --batch runs/20260907T025045Z-clean-pilot-b93eae95 \
  --semantic-model .model-cache/all-MiniLM-L6-v2-1110a243 \
  --semantic-revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 \
  --output reports/20260908-semantic-pilot-v1
```

输出目录须全新。模型下载与评分分开；评分只加载本地文件，禁止远程自定义代码，只使用 safetensors。模型缓存、运行日志和 HTML 结果不提交 Git；代码、模型校验清单、依赖锁与协议进入 Git。

## 开发标注

已复制 8 个教学案例到 `reports/20260908-provenance-dev-review-assistant-v1/`，填写 `assistant_draft` 与 11 处原文证据范围。助手此前已见这些案例与预测，因此**非盲、非独立、不是人工真值**。该包可辅助用户理解与核查，不用于独立测试准确率。原来的 54 条空白标注保持不变，语义分析也不读取这些草稿。

## 后续里程碑与工作量估计

以下为 2026-09-08 的粗略工程预算，不是自动后台执行计划或固定交付日期。

| 里程碑 | 验收条件 | 估计增量工程量 |
| --- | --- | --- |
| M1：词法与语义组件 | 固定模型/协议；真实本地编码；前缀分析与 HTML；测试通过 | 本轮推进 |
| M2：单会话实时归因 | 回调在动作执行前完成；独立 sidecar；超时/失败记录；正常控制验证 | 约 0.5–1 工作日 |
| M3：其余方法重实现 | 来源/敏感工具策略、完整级联、DCPG 与记忆恢复、单独 canary 条件、因果分析及隔离复核 | 约 2–3 工作日 |
| M4：迁移评测 | 独立来源标注、正常/攻击配对、重复运行、消融与归因成本 | 约 1–2 工作日，受标注与 API 配额影响 |

方法级重实现先按约 3–5 工作日量级规划，遇到跨会话适配或论文歧义可能增加。M4 不保证包含在该范围内。完整官方结果复现还要求对应公开 artifact 或足够完整的作者材料；目前未确认可用入口，不能用 AgentDojo/Groq 的结果替代原论文表格。

## 本轮结果

待最终本地评分和测试完成后记录，不提前填造结果。
