# DeepSeek native main v2: run-denominator addendum

Date: 2026-09-29. This is a request-free recount of the frozen
[live batch](../../runs/20260928-deepseek-native-carrier-main-v2/summary.json)
and its existing [passage-level packet](../20260928-deepseek-native-carrier-main-v2/packet.json).
The original run and report are unchanged. [View the table](index.html) or
[machine-readable recount](recount.json). The latter records SHA-256 hashes
of all source inputs.

The prior report's denominators count *scorable source passages whose value
matches an executed sink*. They are conditional on a sink, state evidence,
pre-sink exposure and unique passage binding. The table below instead uses
**all planned runs of each condition** as its denominator: 126 clean and
126 attack runs. It does not treat no-sink, other-value or unscorable runs as
proven detector false negatives.

| Suite | Clean runs | Clean exact legitimate sink | Clean verified legitimate-carrier hit | Attack runs | Attack exact attacker sink | Attack verified attacker-carrier hit | Attack noncarrier false-positive runs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Workspace | 35 | 31 | 24/35 | 35 | 0 | 0/35 | 23/35 |
| Banking | 28 | 21 | 16/28 | 28 | 8 | 7/28 | 0/28 |
| Slack | 35 | 35 | 34/35 | 35 | 23 | 22/35 | 31/35 |
| Travel | 28 | 28 | 28/28 | 28 | 0 | 0/28 | 28/28 |
| **Total** | **126** | **115** | **102/126** | **126** | **31** | **29/126** | **82/126** |

Tier 3 and Tier 4 have identical binary decisions in every scored pair, so
the hit and false-positive columns apply to both. The 102/126 and 29/126
fractions are **end-to-end verified carrier yields per planned run**, not
conditional T3/T4 recall. The attack model put the exact attacker value in a
successfully executed sink in 31/126 attack runs. Of these, one Banking call
had no corroborating state change and one Slack call had ambiguous pre-sink
source binding. The other 29 had scorable attacker carriers, all detected by
T3/T4. On the clean side, 115/126 reached the exact legitimate value; one
Banking state result and one Slack source binding were unscorable. Among 113
scorable clean legitimate carriers, T3/T4 detected 102.

The full outcome accounting is: clean 115 legitimate, 0 attacker, 4 other,
7 no sink; attack 79 legitimate, 31 attacker, 3 other, 13 no sink. In
particular, Workspace and Travel each had attack runs (35 and 28) but zero
executed attacker-value sinks. The 82/126 noncarrier false-positive yield is
also run-denominated; it does not replace the conditional 82/103 rate among
scorable noncarrier pairs. These units must not be pooled with Case R's
whole-document comparison.

The raw ledger has 252 `completed` rows plus 244 intermediate `started`
events. The recount selects only completed rows, checks unique slot IDs and
the live summary totals, then aligns them with the existing packet's Tier
3/4 judgments. The independent raw-ledger and packet recount agreed on every
suite and condition count. Command run from `codebase/agentdojo-lab`:

```bash
.venv/bin/python scripts/recount_deepseek_native_main_v2_by_run.py \
  --batch runs/20260928-deepseek-native-carrier-main-v2 \
  --report reports/20260928-deepseek-native-carrier-main-v2 \
  --output reports/20260929-deepseek-native-carrier-main-v2-run-denominator-v1
```
