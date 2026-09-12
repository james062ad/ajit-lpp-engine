# DECISIONS — AJIT LPP Engine

Pen-holder writes; each entry states what, scope, reason, who/when, how to reopen.
Open design questions live in DECISIONS_OPEN.md (D-01..D-04, July 2026) and are not
superseded by this file.

## A-001 — Rescued from single-copy, regime installed (12 Sep 2026)
Found on the MacBook only, no remote, last commit 22 July, with two uncommitted files —
AUTHORITIES_VERIFIED.md and VERIFICATION_PROOFS.md, carrying the practitioner's primary
text for the improper-purpose rule (ATO reproduction unpaginated, so no pinpoint claimed).
Committed 443a15a and pushed to the new private repo james062ad/ajit-lpp-engine; clone at
`~/AJIT-LPP-Engine` in the iMac `citadel` account via repo-scoped deploy key `github-ajit`.
CLAUDE.md committed 7240048 (sha256 1b46f19c…cefbb). Reopen by editing in a pen session.

## A-002 — Gates re-proven on a new machine (12 Sep 2026)
All five gates pass in the citadel clone: determinism (three-run byte-identical), rule
behaviour, golden set, synthetic taxonomy, NAT 75447 round-trip with its four refusals
(unresolved HITL, unnamed claimant, unconfirmed fields, default claimant). Environmental
note: the engine is standard library only, but the NAT 75447 export needs `openpyxl`, so a
`.venv` exists for that alone. First run without it failed at gate 5 — not a defect.

## A-003 — Fixture data off the repo, on the drive (12 Sep 2026)
`om_privilege_project` (Chevron-TP and Hart-Scheme fixture mailboxes, output, scripts),
`reference` and `lpp_solution` — 7112 files, 183 MB, all git-ignored — moved to
`/Volumes/Citadel Data/lpp_data/` with manifest LPP_DATA.sha256, verified 7112/7112 on
arrival, and copied to `My 750 GB/Citadel-Backup` (verified again). No mailbox, matter or
client document is ever committed to this repo.

## A-004 — Relationship to Citadel (12 Sep 2026)
Under Citadel Public Record D-006, this engine is Geoffrey's process-layer IP. Intended
role: the deterministic disposition layer behind a human-ruled privilege review surface on
the Citadel shell (forensic ingestion door + privilege skill + fixture matter). The 9 Sep
2026 ruling that the AJIT LPP Engine is not proceeding as a standalone product stands and
is NOT reopened here; a ruling reopening it as a review surface is owed before any demo is
built.

## A-005 — Stray file removed (12 Sep 2026)
`REQ-8B3F2D91_session_export.txt` (an OM analyst request, Martin Lawrence, buyback sweep)
sat at this repo's root — a mis-paste from a July session. The request's own capture folder
holds the full 207 KB export (23 Jul); the stray was a 54 KB partial from a different
session. Deleted after both were hashed and compared. No OM material remains in this tree.
