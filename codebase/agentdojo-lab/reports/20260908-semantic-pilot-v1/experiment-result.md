# MiniLM 语义组件：本地前缀分析结果

## Material Passport

- Origin Skill: academic-research-suite
- Origin Mode: recorded-trace analysis
- Origin Date: 2026-09-08
- Verification Status: 工程运行与重复性通过；无独立人工真值
- Version Label: nt-style-semantic-v1

本轮对原有10条clean运行的21个提议、54个参数做离线分析，没有增加Groq调用。214次来源—参数比较均成功，Tier3工具候选出现在2个字段，Tier4出现在12个字段；22个Tier3比较存在截断，Tier4无截断。

各组件独立评分，不是完整NeuroTaint级联。候选数不代表准确率、恶意性或因果影响；没有进行攻击评测。8条助手开发草稿非盲、非独立，未用于算法或准确率计算。

模型revision、10个输入文件SHA256、完整方法假设和源码/锁文件哈希见analysis.json。重新加载模型并完整重放的214个分数与全部前缀输出逐值一致，见reproducibility.json。

原30个日志文件不变，54条空白标注与旧包逐字节相同。HTML链接/结构检查通过，未做浏览器视觉验收。第一轮与单元测试并行，墙钟只作诊断，不是在线开销测量。

[打开交互证据报告](index.html) · [完整数据](analysis.json) · [重复性验证](reproducibility.json) · [原始文件及HTML检查](artifact-checks.json)
