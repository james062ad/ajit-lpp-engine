"""
AJIT LPP Engine — demonstration.

Run:  python3 demo.py

Six synthetic documents walk the engine's distinctive behaviours end to end:
classification with full reasoning, refusal to guess on evaluative questions,
an export that declines to produce a lodgeable form until a human has ruled
and a claimant is named, and a byte-identical reproducibility proof.

Nothing in this demo is a mock. It is the same engine, the same rules, the
same export that the gate suite tests.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from ajit_lpp.models import DocumentFacts, Disposition, Limb, Party, Tri
from ajit_lpp.engine import classify
from ajit_lpp.hitl import HitlLedger, new_decision
from ajit_lpp import nat75447 as n

W = 78


def rule(char="─"):
    print(char * W)


def h(title):
    print()
    rule("═")
    print(f"  {title}")
    rule("═")


def show(facts, cls):
    print(f"\n  {facts.doc_id}  —  {facts.subject}")
    print(f"  disposition : {cls.disposition.value.upper()}")
    print(f"  basis       : {cls.basis[:200]}")
    for o in cls.outcomes:
        flag = "" if o.authority_verified else "  [authority pending verification]"
        cite = f"  ({o.authority})" if o.authority else ""
        print(f"    · {o.rule_id}: {o.disposition.value}{cite}{flag}")
    if cls.hitl_reasons:
        print(f"  → routed to a named human: {cls.hitl_reasons[0][:160]}")


LAWYER = Party("M Chen", "sender", Tri.YES, Tri.YES, Tri.NO, Tri.NO,
               "Kingston Legal", "Partner")
CLIENT = Party("R Thompson", "recipient", Tri.NO, Tri.NO, Tri.YES, Tri.NO,
               "EnergyCorp Pty Ltd", "CFO")
ACCOUNTANT = Party("P Rossi", "author", Tri.NO, Tri.NO, Tri.NO, Tri.YES,
                   "Rossi Advisory", "Principal")


def make_docs():
    base = dict(source_hash="d" * 64, doc_type="Email", date="2025-03-14",
                page_count=1, is_copy=Tri.NO, has_attachments=Tri.NO,
                created_in_public_ai_tool=Tri.NO, prior_waiver_recorded=Tri.NO)
    return [
        DocumentFacts(doc_id="DEMO-001",
            subject="Advice on the s353-10 notice",
            parties=(LAWYER, CLIENT), marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.NO, asserted_limb=Limb.LEGAL_ADVICE,
            proposed_dominant_purpose="Obtaining legal advice on the notice response",
            mixed_purpose_indicated=Tri.NO, **base),
        DocumentFacts(doc_id="DEMO-002",
            subject="Draft response composed in a public AI chatbot",
            parties=(CLIENT,), marked_confidential=Tri.UNKNOWN,
            disclosed_to_third_party=Tri.UNKNOWN, asserted_limb=Limb.LEGAL_ADVICE,
            proposed_dominant_purpose="Preparing legal position",
            **{**base, "created_in_public_ai_tool": Tri.YES}),
        DocumentFacts(doc_id="DEMO-003",
            subject="Board pack: restructure commercial terms + legal risk",
            parties=(LAWYER, CLIENT), marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.NO, asserted_limb=Limb.LEGAL_ADVICE,
            proposed_dominant_purpose="Board approval of restructure; legal risk annex",
            mixed_purpose_indicated=Tri.YES, **base),
        DocumentFacts(doc_id="DEMO-004",
            subject="Valuation report prepared for provision to Kingston Legal",
            parties=(ACCOUNTANT, CLIENT), marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.YES,
            third_party_under_common_interest=Tri.UNKNOWN,
            asserted_limb=Limb.LEGAL_ADVICE,
            prepared_for_provision_to_lawyer=Tri.YES,
            proposed_dominant_purpose="Provision to lawyers for advice on the restructure",
            mixed_purpose_indicated=Tri.NO, **base),
        DocumentFacts(doc_id="DEMO-005",
            subject="Internal sales forecast",
            parties=(CLIENT,), marked_confidential=Tri.NO,
            disclosed_to_third_party=Tri.NO, asserted_limb=Limb.LEGAL_ADVICE,
            prepared_for_provision_to_lawyer=Tri.NO,
            proposed_dominant_purpose="Quarterly forecasting",
            mixed_purpose_indicated=Tri.NO, **base),
        DocumentFacts(doc_id="DEMO-006",
            subject="Litigation strategy note, matter on foot",
            parties=(LAWYER, CLIENT), marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.NO, asserted_limb=Limb.LITIGATION,
            litigation_on_foot_or_anticipated=Tri.YES,
            proposed_dominant_purpose="Use in the current Federal Court proceeding",
            mixed_purpose_indicated=Tri.NO, **base),
    ]


def main():
    template = Path("template_blank.xlsx")
    if not template.exists():
        sys.exit("template_blank.xlsx not found — run from the project root.")

    h("AJIT LPP ENGINE — six documents, no guesses")
    print("""
  The engine below applies deterministic Australian privilege rules to
  recorded facts. Where a question is evaluative — dominant purpose in a
  mixed-purpose document, an unrecorded fact — it does not score, weigh,
  or estimate. It refuses, says why, cites its authority, and routes the
  document to a named human whose ruling is recorded and reopenable.""")

    docs = make_docs()
    results = [(f, classify(f)) for f in docs]

    h("1 · CLASSIFICATION — every disposition carries its trace")
    for f, c in results:
        show(f, c)

    counts = {}
    for _, c in results:
        counts[c.disposition.value] = counts.get(c.disposition.value, 0) + 1
    print(f"\n  {len(results)} documents: " + ", ".join(
        f"{v} {k}" for k, v in sorted(counts.items())))

    h("2 · THE EXPORT REFUSES — three ways")
    claimant = n.Claimant(name="A Practitioner", position="Principal",
                          organisation="Demo Chambers",
                          is_legal_practitioner=True,
                          admission_jurisdiction="Supreme Court of South Australia")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "form.xlsx"
        print("\n  a) With evaluative questions still open:")
        try:
            n.export(template, out, claimant, results)
        except ValueError as e:
            print(f"     REFUSED — {str(e)[:180]}")

        print("\n  b) With no named claimant:")
        try:
            n.export(template, out, None,
                     [(f, c) for f, c in results
                      if c.disposition is not Disposition.HITL_REQUIRED])
        except n.ClaimantNotNamed as e:
            print(f"     REFUSED — {str(e)[:180]}")

        print("\n  c) With an unconfirmed default identity:")
        try:
            n.export(template, out, n.DEFAULT_CLAIMANT,
                     [(f, c) for f, c in results
                      if c.disposition is not Disposition.HITL_REQUIRED])
        except n.ClaimantNotNamed as e:
            print(f"     REFUSED — {str(e)[:180]}")

    h("3 · A HUMAN RULES — recorded, counted, reopenable")
    ledger = HitlLedger(Path("output") / "DEMO_HITL_DECISIONS.jsonl")
    open_docs = [f.doc_id for f, c in results
                 if c.disposition is Disposition.HITL_REQUIRED]
    d = new_decision(
        decision_id="DEMO-HITL-001",
        doc_ids=open_docs,
        question="Dominant purpose in mixed-purpose and third-party documents",
        ruling="On review of each document: DEMO-003 not privileged (board "
               "approval predominated) — produced; DEMO-004 privileged (Pratt "
               "— prepared for provision to lawyers)",
        reason="Evaluative determination on the whole of the material",
        ruled_by="A Practitioner",
        downstream_effect="DEMO-003 is produced. DEMO-004's claim is held at "
               "the authority gate: it rests on Pratt, which is not yet "
               "verified from the Federal Court, and no claim reaches a "
               "regulator on an unverified authority",
        how_to_reopen="Supersede DEMO-HITL-001 with a new entry",
    )
    ledger.append(d)
    print(f"\n  {d.decision_id}: {d.count} document(s) ruled by {d.ruled_by}")
    print(f"  ledger: output/DEMO_HITL_DECISIONS.jsonl (append-only; "
          f"reversal = supersession, never deletion)")

    # Apply the rulings as recorded facts and re-classify.
    from dataclasses import replace
    final = []
    for f, c in results:
        if f.doc_id == "DEMO-003":
            f2 = replace(f, mixed_purpose_indicated=Tri.NO,
                         asserted_limb=Limb.NOT_ASSERTED)
            final.append((f2, classify(f2)))
        elif f.doc_id == "DEMO-004":
            f2 = replace(f, third_party_under_common_interest=Tri.YES,
                         mixed_purpose_indicated=Tri.NO)
            final.append((f2, classify(f2)))
        else:
            final.append((f, c))
    exportable = [(f, c) for f, c in final
                  if c.disposition is Disposition.PRIVILEGED]

    h("4 · A FOURTH REFUSAL — unverified authority never reaches a regulator")
    with tempfile.TemporaryDirectory() as td:
        try:
            n.export(template, Path(td) / "x.xlsx", claimant,
                     [(f, c) for f, c in final
                      if c.disposition is not Disposition.HITL_REQUIRED])
        except ValueError as e:
            print(f"\n  REFUSED — {str(e)[:230]}")
    print("""
  Two dispositions rest on authorities not yet pulled from the issuing
  court (Heppner from the SDNY docket; Pratt from the Federal Court).
  The engine will classify on a pending authority — and flags it in the
  record — but it will not put one in front of a regulator. The claim
  schedule below contains only claims resting on verified authority.""")

    h("5 · THE FORM — the ATO's own workbook, filled")
    Path("output").mkdir(exist_ok=True)
    dest = Path("output") / "AJIT_DEMO_NAT75447.xlsx"
    line = n.export(template, dest, claimant, exportable)
    print(f"\n  written: {dest}")
    print("  log line (the export is reproducible from this alone):")
    for kv in line.split("\t"):
        print(f"    {kv[:110]}")

    h("6 · PROOF — run it again, byte for byte")
    with tempfile.TemporaryDirectory() as td:
        ok = n.verify_from_log(line, template, claimant, exportable,
                               Path(td) / "again.xlsx")
    print(f"\n  rebuilt from the log line and compared: "
          f"{'IDENTICAL' if ok else 'MISMATCH'}")
    print("""
  That is the demonstration: no probability thresholds, no silent calls,
  no unnamed decisions. Every disposition traceable, every refusal
  explained, every human ruling on the ledger, every export reproducible.

  Privilege doesn't have an error budget. This engine doesn't spend one.
""")


if __name__ == "__main__":
    main()
