# PILOT_200 — runbook: 200 documents to a lodgeable NAT 75447

The engine's deciding machinery is proven (gates 1, 3, 4). This runbook is the
sequence from here to running a real ~200-document matter through it. Steps
are ordered; each is gated; none is skipped.

## Phase A — prerequisites (James)

**A1. Verify the load-bearing authorities from the issuing courts.**
The export refuses any claim resting on an unverified authority, so this is a
practical prerequisite, not hygiene. Priority order (by rule-chain load):

| Authority | Used by | Status |
|---|---|---|
| Esso [1999] HCA 67 | AU-PURP-01/02 | **verified** |
| Mann v Carnell (1999) 201 CLR 1 | AU-CONF-02/03 | pending |
| Pratt Holdings (2004) 136 FCR 357 | AU-PARTY-01 | pending |
| Waterford (1987) 163 CLR 54 | AU-PARTY-02 | pending |
| Heppner (SDNY 2026) | AU-CONF-01 | pending — US persuasive only; see note |

On verifying each: add it to `VERIFIED_AUTHORITIES` in `rules_au.py`, run the
gates, commit. Heppner note: verify from the SDNY docket, and record that the
Australian basis for AU-CONF-01 stands on the confidentiality element — the
citation is persuasive, not binding.

**A2. Golden set verification pass** (parallel, not blocking the pilot):
judgments from the issuing courts, flags flipped row by row. ARU and Jacobsen
first — they decide whether they score at all.

**A3. Confirm the claimant.** Replace the two `[CONFIRM]` fields in
`DEFAULT_CLAIMANT` (nat75447.py) with your styling as it should appear on a
regulator's form. The export refuses until this is done.

## Phase B — rehearsal on synthetic data (with an answer key)

**B1.** Copy a synthetic mailbox into the corpus:
```
cp -r om_privilege_project/mailboxes/CUB-v-CoT data/corpus/
python3 tests_gates.py        # Gate 2 parses it, checks hashes, all-HITL baseline
```

**B2.** Find the ground truth. The April generator
(`om_privilege_project/scripts/generate_cub_demo.py`) built these mailboxes
with ground truth — locate its output format:
```
grep -n "ground" om_privilege_project/scripts/generate_cub_demo.py | head
ls om_privilege_project/mailboxes/CUB-v-CoT | head
```
Report the format back; the ground-truth scorer gets wired to it and Gate 2
becomes a scored gate, not a smoke gate.

**B3.** Hand-record 20 of those emails through the facts intake:
```
python3 -m ajit_lpp.facts_intake template rehearsal_facts.csv
# fill 20 rows from the emails; blank = UNKNOWN; only explicit 'no' is NO
python3 -m ajit_lpp.facts_intake check rehearsal_facts.csv
python3 -m ajit_lpp.facts_intake run rehearsal_facts.csv
```
Compare dispositions against ground truth. Rule on the HITL queue via the
ledger. Export. This is the full pilot loop, rehearsed where mistakes are free.

## Phase C — the real matter

**C1. Scope.** One matter, one notice, ~200 documents, one claimant (you).
Local machine only; nothing leaves it. Client consent per your professional
obligations; the architecture is Heppner-safe by construction (no public AI
tool touches content), and the engagement record should say so.

**C2. Record.** `facts_intake template` → practitioner/paralegal fills facts
at a few minutes per document. The discipline that matters: **blank means
unknown**. Do not resolve doubts in the spreadsheet — that is what the HITL
queue is for, with a ledger.

**C3. Classify.** `facts_intake run`. Expect a real matter to land roughly:
a third disposed mechanically, the rest queued with reasons.

**C4. Rule.** Work the HITL queue. Every ruling on the ledger: question,
ruling, reason, count, downstream effect, how to reopen.

**C5. Export.** Named claimant, decided documents, verified authorities —
or it refuses, and the refusal says which gate. The log line goes in the
matter file; the export is reproducible from it alone.

**C6. Keep everything.** The facts CSV, the ledger, the log line, the gate
output — that bundle IS the defensibility story, and it is also the pilot
case study.

## What is deliberately NOT in this pilot

- PST/PDF ingestion (EML/mbox first; PST behind it)
- The LLM proposer (D-03 — built only after the gates that judge it)
- Any cloud or Azure step (gated by standing rule)

## Sequence summary

A1 authorities → A3 claimant → B1-B3 rehearsal → C1-C6 real matter.
A2 (golden verification) runs in parallel throughout.
