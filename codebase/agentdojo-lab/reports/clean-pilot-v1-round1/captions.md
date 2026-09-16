# Figure and table notes

Included 10 real clean runs and 10 unique evaluated tasks. Offline fixtures are excluded; every considered run and exclusion reason is in run_inventory.json.

Table 1 | Descriptive clean-run observations. R1, R2, etc. follow run_table.csv row order. Requests, tokens and elapsed times are per run. Repeated runs are not independent tasks. Missing values remain missing. Elapsed times include client quota waiting, reported separately as pacing_wait_seconds in the batch trials.csv. Recorded times and elapsed minus waiting do not measure tracing overhead or server inference latency.

Figure 1 | One observed clean-agent episode: r01-user_task_9, episode:00000002. Panel a follows model-response and tool-result event order; arrows and spacing do not encode causality or duration. Panel b marks tool messages included in actual outbound model requests. Repeated exposure is not an additional tool execution. Selection searches complete, audited recordings in reverse run-directory-name order, then takes the first episode with tool results; directory-name order is not chronological trial order in this batch.

No pooled success estimate, ASR, confidence interval, significance test, or attribution-accuracy estimate is supported by this pilot. Native utility is a task-specific evaluator result.

Source data: run_table.csv, trace_nodes.csv and trace_exposure.csv when a trace is available. Source hashes and exact run/episode identity: report.json. Exports use editable SVG text, embedded TrueType PDF fonts and 300 dpi PNG previews, at 183 mm width.
