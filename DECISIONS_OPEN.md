# AJIT LPP Engine — open decisions

Nothing below has been assumed. Each is a fork the engine cannot resolve for
itself, recorded so the next session picks up without guessing.

---

## D-01 — Harvest the April build, or start clean? **[DECISION REQUIRED: James]**

This is the one that changes the shape of everything else, and it wasn't in the
state-of-play.

`om_priviledge_project` (April 2026, `~/projects/agents/6_mcp/community_contributions/`)
is not a sketch. It contains:

- `lpp_privilege_system.ipynb` — 28 cells, runs end-to-end on three synthetic
  matters: 307 emails, 69 threads, 113 attachments, 420 evidence objects
- a 4-rule deterministic engine (lawyer involvement, dominant purpose,
  confidentiality, legal-language patterns) at ~85.7% ground-truth agreement
- **an exact 7-sheet NAT 75447 replica**, verified against the ATO template
- EML generation with round-trip ingestion validation, 100% cross-pipeline
  agreement
- JSON reasoning logs per classification, and investigation risk scoring
- a FastAPI + React app with working Upload, Dashboard, Evidence, Threads and
  Export pages (Graph and Timeline backends work; frontends unfinished)

The NAT 75447 export alone is weeks of work already done and verified against
the real template. What it predates is the 20 July architecture: hybrid
proposer/disposer, the four validation gates, the HITL ledger, the
authority-verification discipline.

Options:

- **(A) Harvest** — lift the NAT 75447 export and the synthetic corpus into the
  new architecture, rewrite the 4-rule engine as the rule layer built here.
  Fastest to a demonstrable v1. Risk: the old accuracy figure travels with the
  code and gets quoted as if the new engine earned it.
- **(B) Clean build, old repo as reference** — the export module is
  re-implemented against the template rather than lifted. Slower; every number
  is one this architecture actually produced.
- **(C) Harvest the export only.** The NAT 75447 replica is mechanical and
  template-verified, so it carries no accuracy claim. The rule layer is built
  fresh. This is the recommendation.

**Recommendation: (C).** The 85.7% figure is the reason. It was measured against
synthetic ground truth on a rule set that pre-dates the discipline that anything
evaluative goes to a human — and under the current rule layer, a large share of
those documents would resolve to HITL_REQUIRED rather than to a classification
at all. The two numbers are not comparable, and carrying the old code forward
invites the comparison. The export is different: it either matches the ATO
template or it doesn't.

---

## D-02 — Golden set: who fills the 15 rows? **[DECISION REQUIRED: James]**

The chapter-3 worklist (`privilege_goldenset_AU_ch3_worklist.csv`) exists with
blank `determination`, `document`, `parties_roles`, `purpose` and `basis` fields.
Gate 1 cannot run until they are filled from the judgments themselves.

Standing constraints already settled: judgments from the issuing courts, not
AustLII; Desiatnik as guide, not content; holdings in your own words; every row
stays `expert_validated: pending` until an expert signs it.

The open question is the same one from June, still unanswered: Claude drafts
first-pass holdings for your verification (A), or you pull each judgment
yourself (B). It has been open a month, which is itself the argument for (A).

---

## D-03 — Proposer model and prompt contract **[DECISION REQUIRED: James]**

The rule layer is built and does not depend on this. But `DocumentFacts` has a
proposer-filled half — `proposed_dominant_purpose`, `mixed_purpose_indicated`,
`litigation_on_foot_or_anticipated`, party capacity flags — and the proposer's
contract needs to be explicit before Phase 1:

- which model, and does it run locally or in Azure (your no-unapproved-Azure
  rule means this is gated either way)
- the proposer must be able to return UNKNOWN and must be scored on how often it
  does so correctly, not on how often it commits
- whether the proposer sees the whole document or a redacted structural view

---

## D-04 — Authorities verification order

Seven authorities are cited in the rule layer. One is verified from the issuing
court (*Esso*). The rest are marked pending in every record that relies on them,
which is correct but not sustainable.

Priority order suggested by how load-bearing each is in the rule chain:
*Mann v Carnell* (two rules), *Waterford* (capacity), *Heppner* (the SDNY
docket, 25-cr-503 — and it is US persuasive authority only, so the Australian
basis has to stand on the confidentiality element without it), then *Pratt*,
*Daniels*.

No decision needed — just sequence. Flagged so it doesn't drift.
