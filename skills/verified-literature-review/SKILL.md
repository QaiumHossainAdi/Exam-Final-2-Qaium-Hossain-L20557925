---
name: verified-literature-review
description: >
  Use when drafting a literature review, related-work section, annotated
  bibliography, or any prose that cites external sources from model memory.
  Verifies every citation against a primary source before the document is
  treated as final, and separates a preprint's posting date/venue from the
  peer-reviewed venue and year of record.
---

## Procedure

1. Draft freely first. Write the full section with in-text citations and a
   reference list exactly as normal — do not stop to verify mid-draft.

2. Extract every citation claim into a checklist: one row per reference,
   with the five fields a citation asserts — authors, year, title, venue,
   and identifier (DOI / arXiv id).

3. Verify each row against a primary source (publisher page, conference
   proceedings, arXiv abstract page, DBLP, or the digital library of
   record) — not a secondary summary. Record the source URL used.

4. Classify each reference as one of:
   - Verified — all five fields match a primary source.
   - Metadata error — the paper is real but one field (commonly venue or
     year) is wrong. This is the dominant failure mode, not fabrication.
   - Fabricated — no primary source can be found for the claimed paper.

5. For preprints, always check whether a peer-reviewed version exists and
   cite the venue of record (e.g., ICLR/NeurIPS/ICML), not just the arXiv
   posting date, unless the work is genuinely unpublished.

6. Apply every correction as a tracked change (insertions/deletions), never
   a silent edit, so a reviewer can see exactly what was wrong and why.

7. Re-run step 3 once after edits are applied, and report a short
   verification summary (n verified / n corrected / n fabricated) alongside
   the final document.
