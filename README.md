# AJIT LPP Engine — Phase 0

Deterministic legal professional privilege classification. Australian rule layer
first; UK, Singapore, US follow the same method later.

**Architecture (ruling, 20 Jul 2026):** the LLM proposes, deterministic rules
dispose. Nothing evaluative is decided by a score.

## Layout

```
ajit_lpp/
  models.py     DocumentFacts, Party, Classification, canonical JSON
  rules_au.py   the Australian rule chain — 8 rules, mechanisable facts only
  engine.py     disposition and precedence
  hitl.py       append-only HITL ledger
tests_gates.py  validation gates
DECISIONS_OPEN.md
```

## Run it

```bash
python3 tests_gates.py
```

No dependencies. Standard library only, deliberately — the rule layer is the
part that has to survive cross-examination, and it should be readable by someone
who does not run it.

## What is built

- The full Australian rule chain: confidentiality (public AI tool, third-party
  disclosure, prior waiver), lawyer and capacity, litigation predicate, dominant
  purpose.
- Disposition precedence: a decisive NOT_PRIVILEGED short-circuits; any open
  evaluative question beats any positive finding; the default is HITL_REQUIRED.
- Gate 3, the three-run byte-identical determinism proof — the one shown to a
  regulator. It passes.
- The HITL ledger, append-only, with supersession rather than editing.
- Authority verification surfaced per record: any classification resting on an
  unverified citation says so in its own output.

## What is not built

- Gate 1 (golden set on rules alone) — blocked on the 15 chapter-3 rows.
- Gate 2 (17-category synthetic taxonomy) — blocked on the corpus.
- Gate 4 (NAT 75447 round-trip) — blocked on the export module. See D-01: a
  verified 7-sheet replica already exists in the April build.
- Ingestion. PST, PDF and mixed corpora are all v1 scope and none is started.
- The proposer. See D-03.

## The disciplines this code enforces

1. UNKNOWN is never read as NO.
2. Proposer confidence has no path to a disposition. It is metadata.
3. Every unverified authority is named in the record that relies on it.
4. Run metadata never enters a classification record — that is what makes the
   determinism gate possible.
5. Every human ruling is recorded with what was set aside, how many rows, why,
   by whom, when, the downstream effect, and how to reopen it.
