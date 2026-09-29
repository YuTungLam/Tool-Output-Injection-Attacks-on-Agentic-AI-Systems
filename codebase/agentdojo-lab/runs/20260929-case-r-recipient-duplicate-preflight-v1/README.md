# Duplicate-address control preflight — 2026-09-29

This directory preserves the first zero-request two-cell packet. Its source
texts, T3/T4 scores and labels are identical to the verified packet. Its
automated interpretation only noted that the full-source binary labels stayed
separated. Inspection of the saved chunks showed that the John hit comes from
a **non-target-containing name-only chunk**, while neither correction chunk
containing the target email matches. The verified report explicitly records
that distinction:
[`reports/20260929-case-r-recipient-duplicate-control-offline-v1/`](../../reports/20260929-case-r-recipient-duplicate-control-offline-v1/).
No API or live agent request was made for either packet.
