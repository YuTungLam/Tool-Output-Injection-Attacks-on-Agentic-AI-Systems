# Figure and table notes

Included 3 real clean runs and 1 unique evaluated tasks. Offline fixtures are excluded; every considered run and exclusion reason is in run_inventory.json.

Table 1 | Descriptive clean-run observations. R1, R2, etc. follow run_table.csv row order. Requests, tokens and wall-clock times are per run. Repeated runs are not independent tasks. Missing values remain missing. Recorded times do not measure tracing overhead.

Figure 1 | One observed clean-agent episode. Panel a follows model-response and tool-result event order; arrows and spacing do not encode causality or duration. Panel b marks tool messages included in actual outbound model requests. Repeated exposure is not an additional tool execution. The first episode with tool results in the most recent complete, audited recording is selected.

No pooled success estimate, ASR, confidence interval, significance test, or attribution-accuracy estimate is supported by this pilot. Native utility is a task-specific evaluator result.

Source data: run_table.csv, trace_nodes.csv and trace_exposure.csv when a trace is available. Source hashes and exact run/episode identity: report.json. Exports use editable SVG text, embedded TrueType PDF fonts and 300 dpi PNG previews, at 183 mm width.
