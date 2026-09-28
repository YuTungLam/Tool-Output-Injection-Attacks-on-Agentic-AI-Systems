# Case R Diksha offline preflight — 2026-09-29

This directory preserves the first request-free packet from the frozen Case R
recipient/context diagnostic. It used the correct saved full-source inputs and
fixed MiniLM. Its T3/T4 scores, exact-string results and all 46 + 4 + 8 evaluated
text pairs match the final packet numerically.

The preflight packet's free-text interpretation incorrectly says there were
four unique original carrier input pairs. The verified recount is **two**
legitimate and **three** attacker carrier input pairs. The preflight also had
not yet performed the explicit raw exposure, executed-action and native sent
state assertions added before the verified rebuild. Its bytes are retained
here for audit; cite the verified
[`reports/20260929-case-r-diksha-crossover-offline-v1/packet.json`](../../reports/20260929-case-r-diksha-crossover-offline-v1/packet.json)
for findings. Neither build made an API or live agent request.
