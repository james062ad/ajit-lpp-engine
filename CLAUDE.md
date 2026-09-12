# CLAUDE.md — AJIT LPP Engine session regime

Provenance: drafted 12 Sep 2026, adapted from the Citadel Public Record regime
(sha256 0b52311a…6816). Authority for this repository once committed.

## 0. Model line
Every paste block opens with `Model:`. Opus for mechanical work; Fable for firsts,
evaluation, design and anything touching the rule layer or the authorities; Sonnet for
pure reads. No block runs without a Model line.

## 1. What this engine is, and the line it must not cross
An LLM may propose evaluative facts. Deterministic rules dispose. Every evaluative
question routes to a human. UNKNOWN is never read as NO. The export refuses to produce a
NAT 75447 unless all authorities are verified, the claimant is named, and no HITL question
remains open. No change may weaken any of these; a change that does is a ruling in
DECISIONS.md, not a commit.

## 2. Authorities
Rule-layer citations are verified by the practitioner from the issuing court, or marked
pending in every record that relies on them. Claude never supplies, completes or
"confirms" a citation, pinpoint, bench or quotation — the 2026 error study catalogued nine
ways that goes wrong (citation drift, bench fabrication, polarity inversion, omission,
pinpoint drift, cross-judgment bleed, false precision, provenance laundering, hedge
erosion). Where an authority is unpaginated in the source consulted, no pinpoint is
claimed. Verification order (D-04): Mann v Carnell, Waterford, Heppner (US persuasive
only), Pratt, Daniels.

## 3. Machine and environment
iMac only, account `citadel`, clone `~/AJIT-LPP-Engine`. Engine is standard library only;
`.venv` exists solely for `openpyxl`, which the NAT 75447 export needs. Fixture mailboxes,
the April build and Desiatnik live at `/Volumes/Citadel Data/lpp_data/` (manifest
LPP_DATA.sha256, 7112 files), backed up to `My 750 GB/Citadel-Backup`. No mailbox, matter
or client document is ever committed to this repo.

## 4. Gates
`.venv/bin/python tests_gates.py` runs five gates: determinism (three-run byte-identical),
rule behaviour, golden set, synthetic taxonomy, NAT 75447 round-trip and its four refusals.
All five pass as of 12 Sep 2026. No commit lands with a gate failing; a gate that cannot
pass is a ruling, not a skip.

## 5. Opener, pen, close-out
Opener: `/rename`; read README, DECISIONS_OPEN.md, this file; report branch, ahead/behind,
dirty tree, stash, index; name the single thing; STOP. One committing session at a time;
`git add` never stages content; commits by explicit path. Close-out: commit by path or park
with a reason, push if pen-holder, export the transcript to `docs/sessions/`, one-line
state summary. Work that exists only in a chat tab does not exist.

## 6. Derive and prove
Counts derived, never carried. Two sources disagreeing is a STOP. Nothing stated without a
named authority: a committed hash, a primary source checked at the time, an operator
document, or a ruling. Otherwise omitted or marked [UNVERIFIED].
