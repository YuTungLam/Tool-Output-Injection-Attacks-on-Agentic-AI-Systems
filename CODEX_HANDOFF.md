# Codex Handoff: Research Proposal, Literature Triage, and Zotero State

Last updated: 2026-07-02, Pacific/Auckland.

## Purpose

This repository supports a one-year Master's research proposal on tool-output injection / prompt-injection risks in agentic AI systems, with emphasis on LLM agents, tool use, MCP security, long-horizon attacks, and evaluation/defence methods.

The immediate work has been:

- Build a ~15-slide proposal/scoping presentation.
- Extract references from the proposal README and Zotero.
- Use Scite citation-context signals where available.
- Classify papers into practical Zotero tiers.
- Keep generated CSV/MD/PPTX artifacts available across devices.

Do not include individual supervisor names in file names or generated documents.

## Current Git Hygiene

`.gitignore` should ignore only scratch/cache outputs, not final artifacts:

- Ignored: `outputs/_deck_work/`
- Ignored: `outputs/*.inspect.ndjson`
- Tracked/available for commit: `outputs/*.csv`, `outputs/*.md`, `outputs/*.pptx`

This is intentional because CSV/MD/PPTX files are needed across devices.

## Important Artifacts

Primary presentation:

- `outputs/research_proposal_supervisor_deck.pptx`
- `outputs/scoping_meeting_deck.pptx`

Primary literature and Zotero outputs:

- `outputs/zotero_tier_split_for_classification.csv`
- `outputs/zotero_tier_split_for_classification.md`
- `outputs/zotero_markdown_actionable_inconsistencies.csv`
- `outputs/zotero_markdown_actionable_inconsistencies.md`
- `outputs/zotero_markdown_inconsistencies.csv`
- `outputs/zotero_markdown_inconsistencies.md`
- `outputs/zotero_paper_inventory.csv`
- `outputs/expanded_literature_scite_matrix.csv`
- `outputs/zotero_classification_markdown_table.md`

Older or supporting outputs:

- `outputs/scite_reference_citation_contexts.csv`
- `outputs/scite_claim_evidence_matrix.csv`
- `outputs/scite_query_log.csv`
- `outputs/expanded_scite_query_log.csv`
- `outputs/reference_inventory.csv`
- `outputs/literature_quality_inventory.csv`

## Zotero Access Notes

The local Zotero API was enabled at:

- `http://localhost:23119/api`

In this environment, the most reliable read-only extraction has been direct SQLite read:

- `C:\Users\Administrator\Zotero\zotero.sqlite`
- SQLite URI used by scripts: `file:C:/Users/Administrator/Zotero/zotero.sqlite?mode=ro&immutable=1`

If continuing on another device, do not trust stale `outputs/zotero_paper_inventory.csv` as the live state. Refresh Zotero first.

The extraction script currently lives under ignored scratch space:

- `outputs/_deck_work/tmp/extract_zotero_metadata.py`

If the ignored scratch script is unavailable on another device, recreate a read-only Zotero extraction script or use the Zotero local API / Pyzotero CLI if installed.

## Latest Zotero State

After the user cleaned Zotero, the latest refresh found:

- Zotero paper-like records: 78
- Broad tier counts in Zotero:
  - no tier: 8
  - T1: 34
  - T2: 13
  - T3: 23

The latest actionable comparison report is:

- `outputs/zotero_markdown_actionable_inconsistencies.md`

Latest actionable mismatch counts:

- `zotero_not_in_markdown`: 1
- `wrong_broad_tier`: 4
- `missing_broad_tier`: 4
- `watchlist_item_in_core_tier`: 25
- `duplicate_or_split_zotero_items`: 1

The shorter actionable report intentionally excludes:

- optional fine-grained subfolder suggestions
- Watchlist candidates omitted from Zotero

This matters because the user intentionally did not add some low-signal or bad-paper candidates to Zotero.

## Paper Tiering Rules

The classification is practical and provisional. It is not a formal final CORE/SJR/JCR audit.

Use these broad categories:

- `T1`: strong top-venue signal, such as ICLR, ICML, NeurIPS, USENIX Security, NDSS, ACM CCS, ACL/EMNLP main, AAAI, KDD, ACM Computing Surveys, ACM TOSEM.
- `T2`: reputable peer-reviewed venue, Findings, reputable workshop/proceedings, Springer/ACM signal, or cautious Q2 journal evidence.
- `T3`: citeable but non-top evidence, including influential preprints, supported/mentioned preprints, or formal proceedings with direct relevance.
- `Watchlist`: low-signal preprints, weak-source candidates, Research Square/Zenodo-like records, venue quality risk, or items intentionally omitted from Zotero.

Fine-grained folders used in `zotero_tier_split_for_classification` include:

- `T2-caution-mdpi-q2`
- `T3-citable-proceedings`
- `T3-influential-preprint`
- `T3-supported-or-mentioned-preprint`
- `T3-contested-preprint`
- `Watchlist-low-signal-preprint`
- `Watchlist-low-source-confidence`
- `Watchlist-venue-quality-risk`
- `Watchlist-manual-verify`

## Specific Decisions Already Made

- ICLR main conference poster papers are treated as `T1`. Workshop papers/posters are not automatically `T1`; usually `T2` or verify.
- MDPI as a publisher is not itself a tier. Specific MDPI journals must be checked.
- MDPI *Information* article `10.3390/info17010054` is classified as `T2-caution-mdpi-q2`, useful as background/supporting evidence, not T1.
- SPIE paper `10.1117/12.3097390` is classified as `T3-citable-proceedings`, useful as supporting/case-study evidence, not T1/T2.
- Research Square / Zenodo / low-signal new preprints are generally Watchlist, and omission from Zotero can be intentional.
- Scite often matched DOI/title but did not always return raw tally. Do not invent exact citation counts; use available ranges or `Not estimated`.

## Current Caveats

- Some Watchlist candidates are still present in Zotero T1/T2/T3. This may be intentional or may need cleanup; check `zotero_markdown_actionable_inconsistencies.md`.
- Some items are duplicated in Zotero. Latest duplicate/split item to check: AgentDojo.
- Some papers in the markdown/classification table may intentionally be absent from Zotero because the user judged them weak or not worth adding.
- The Scite-derived citation fields are ranges, not exact counts.
- Avoid Excel date auto-conversion by using ranges like `10 to 24`, not `10-24`.

## Recommended Next Steps

1. Refresh Zotero state on the current device.
2. Regenerate `zotero_paper_inventory.csv`.
3. Regenerate `zotero_markdown_actionable_inconsistencies.md`.
4. Review only actionable mismatches first:
   - wrong broad tier
   - missing broad tier
   - watchlist item in core tier
   - duplicate/split Zotero items
   - Zotero item missing from classification table
5. Do not automatically add Watchlist/bad-paper candidates to Zotero.
6. Before presentation work, use the tier table to choose a small set of strongest T1/T2 papers for prior-work slides.

## Tone and User Preferences

The user prefers concise Chinese explanations, with enough rationale to decide Zotero placement. They do not want local filenames or generated documents to include individual supervisor names. They want generated CSV/MD/PPTX artifacts available in Git for cross-device use.
