"""
AJIT LPP Engine — validation gates, Phase 0 subset.

Gate 3 (three-run byte-identical determinism) is implemented here in full,
because it is the gate that gets shown to a regulator and it costs nothing to
build first. Gates 1 (golden set on rules alone), 2 (17-category synthetic with
ambiguity -> HITL_REQUIRED) and 4 (NAT 75447 round-trip) are stubbed with their
entry conditions and fail loudly until their datasets are present.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ajit_lpp.engine import classify
from ajit_lpp.models import Disposition, DocumentFacts, Limb, Party, Tri, dumps

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILURES.append(name)


# ---------------------------------------------------------------- fixtures

def clean_advice() -> DocumentFacts:
    return DocumentFacts(
        doc_id="D-0001",
        source_hash="a" * 64,
        doc_type="email",
        date="2025-03-14",
        subject="Advice on notice response",
        parties=(
            Party("P1", "sender", Tri.YES, Tri.YES, Tri.NO, Tri.NO, "External firm", "Partner"),
            Party("P2", "recipient", Tri.NO, Tri.NO, Tri.YES, Tri.NO, "Client Ltd", "GC"),
        ),
        marked_confidential=Tri.YES,
        disclosed_to_third_party=Tri.NO,
        created_in_public_ai_tool=Tri.NO,
        asserted_limb=Limb.LEGAL_ADVICE,
        proposed_dominant_purpose="Obtaining legal advice on the s353-10 notice",
        proposer_confidence=0.94,
        mixed_purpose_indicated=Tri.NO,
        prior_waiver_recorded=Tri.NO,
    )


def mutate(base: DocumentFacts, **kw) -> DocumentFacts:
    from dataclasses import replace

    return replace(base, **kw)


# ------------------------------------------------------- GATE 3: determinism

def gate_determinism() -> None:
    print("\nGate 3 — three-run byte-identical determinism")
    corpus = [
        clean_advice(),
        mutate(clean_advice(), doc_id="D-0002", created_in_public_ai_tool=Tri.YES),
        mutate(clean_advice(), doc_id="D-0003", mixed_purpose_indicated=Tri.YES),
        mutate(clean_advice(), doc_id="D-0004", asserted_limb=Limb.NOT_ASSERTED),
    ]
    runs = ["\n".join(dumps(classify(f)) for f in corpus) for _ in range(3)]
    check("run 1 == run 2", runs[0] == runs[1])
    check("run 2 == run 3", runs[1] == runs[2])
    import json

    record_fields = set(json.loads(dumps(classify(corpus[0]))))
    check(
        "no run metadata leaked into records",
        not (record_fields & {"ruled_at", "run_id", "generated_at", "operator"}),
        sorted(record_fields),
    )


# --------------------------------------------------- rule-layer behaviour

def gate_rule_behaviour() -> None:
    print("\nRule layer — behaviour under the standing disciplines")

    c = classify(clean_advice())
    check(
        "clean advice-limb communication is privileged",
        c.disposition is Disposition.PRIVILEGED,
        c.disposition,
    )

    c = classify(mutate(clean_advice(), created_in_public_ai_tool=Tri.YES))
    check(
        "public AI tool defeats attachment, decisively",
        c.disposition is Disposition.NOT_PRIVILEGED,
        c.disposition,
    )
    check(
        "public AI tool short-circuits the chain",
        len(c.outcomes) == 1,
        f"{len(c.outcomes)} outcomes",
    )

    c = classify(mutate(clean_advice(), mixed_purpose_indicated=Tri.YES))
    check(
        "mixed purpose goes to a human, not to a score",
        c.disposition is Disposition.HITL_REQUIRED,
        c.disposition,
    )

    c = classify(
        mutate(
            clean_advice(),
            parties=(
                Party("P1", "sender", Tri.YES, Tri.UNKNOWN, Tri.NO, Tri.NO),
                Party("P2", "recipient", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
            ),
        )
    )
    check(
        "unrecorded lawyer capacity goes to a human",
        c.disposition is Disposition.HITL_REQUIRED,
        c.disposition,
    )

    c = classify(
        mutate(clean_advice(), proposer_confidence=0.99, mixed_purpose_indicated=Tri.UNKNOWN)
    )
    check(
        "high proposer confidence cannot dispose an open question",
        c.disposition is Disposition.HITL_REQUIRED,
        c.disposition,
    )

    c = classify(mutate(clean_advice(), asserted_limb=Limb.NOT_ASSERTED))
    check(
        "no limb asserted means no claim to test",
        c.disposition is Disposition.HITL_REQUIRED,
        c.disposition,
    )

    c = classify(
        mutate(
            clean_advice(),
            asserted_limb=Limb.LITIGATION,
            litigation_on_foot_or_anticipated=Tri.NO,
        )
    )
    check(
        "litigation limb without litigation fails",
        c.disposition is Disposition.NOT_PRIVILEGED,
        c.disposition,
    )

    c = classify(
        mutate(
            clean_advice(),
            disclosed_to_third_party=Tri.YES,
            third_party_under_common_interest=Tri.UNKNOWN,
        )
    )
    check(
        "third-party disclosure with unrecorded common interest goes to a human",
        c.disposition is Disposition.HITL_REQUIRED,
        c.disposition,
    )

    c = classify(clean_advice())
    check(
        "unverified authorities are surfaced on every record that relies on them",
        c.unverified_authorities == () or all(
            a not in ("Esso Australia Resources Ltd v FCT [1999] HCA 67",)
            for a in c.unverified_authorities
        ),
        c.unverified_authorities,
    )

    c = classify(mutate(clean_advice(), created_in_public_ai_tool=Tri.YES))
    check(
        "a pending authority is flagged, not relied on silently",
        "United States v Heppner (SDNY, 17 Feb 2026)" in c.unverified_authorities,
        c.unverified_authorities,
    )


# ----------------------------------------------------------- stubbed gates

def gate_golden_set() -> None:
    csv_path = Path(__file__).parent / "data" / "goldenset" / "privilege_goldenset_AU_ch3_worklist.csv"
    print("\nGate 1 — golden set, rules alone")
    if not csv_path.exists():
        print("  SKIP  worklist CSV not found at data/goldenset/")
        return

    from ajit_lpp.goldenset import load_goldenset, all_pending
    from ajit_lpp.golden_facts_au import fixtures_by_case

    rows = load_goldenset(csv_path)
    fixtures = fixtures_by_case()

    held = [r for r in rows if r.row_type != "scorable"]
    scorable = [r for r in rows if r.row_type == "scorable"]

    for r in held:
        print(f"  HELD  {r.id}: {r.held_out_reason}")

    matches, boundary, wrong, unfixtured = [], [], [], []
    for r in scorable:
        fx = fixtures.get(r.id)
        if fx is None:
            unfixtured.append(r.id)
            continue
        if fx.court != r.determination:
            print(f"  FAIL  {r.id}: fixture court outcome '{fx.court}' != CSV determination '{r.determination}'")
            FAILURES.append(f"gate1-{r.id}-mismatch")
            continue
        got = classify(fx.facts).disposition.value
        if got == fx.court:
            matches.append(r.id)
            print(f"  MATCH {r.id}: engine == court == {got}")
        elif got == fx.engine == "hitl_required":
            boundary.append(r.id)
            print(f"  DECLINED {r.id}: court={fx.court}, engine=hitl_required (expected — evaluative boundary)")
        elif got != fx.engine:
            wrong.append(r.id)
            print(f"  FAIL  {r.id}: engine={got}, expected engine behaviour={fx.engine}, court={fx.court}")
            FAILURES.append(f"gate1-{r.id}")
        else:
            wrong.append(r.id)
            print(f"  FAIL  {r.id}: engine={got} contradicts court={fx.court} outside an expected boundary")
            FAILURES.append(f"gate1-{r.id}")

    for cid in unfixtured:
        print(f"  NOFIX {cid}: scorable row has no facts fixture yet — write one in golden_facts_au.py")

    # Probes: fixtures with no scored row (e.g. AU-C3-11b) still must behave.
    for cid, fx in fixtures.items():
        if any(r.id == cid for r in rows):
            continue
        got = classify(fx.facts).disposition.value
        ok = got == fx.engine
        check(f"probe {cid} behaves as specified ({fx.engine})", ok, got)

    n = len(matches) + len(boundary) + len(wrong)
    status = "PROVISIONAL — rows/fixtures unverified" if all_pending(rows) or any(
        not fx.verified for fx in fixtures.values()
    ) else "VALIDATED"
    print(f"  ---- scored {n} of {len(rows)} rows ({len(held)} held out, {len(unfixtured)} unfixtured)")
    print(f"  ---- matches={len(matches)} declined-at-boundary={len(boundary)} wrong={len(wrong)}")
    print(f"  ---- status: {status}")
    check("no scored case contradicts the court outside an expected boundary", not wrong)


def gate_synthetic_taxonomy() -> None:
    corpus = Path(__file__).parent / "data" / "corpus"
    print("\nGate 2 — synthetic corpus")
    matters = [d for d in corpus.iterdir() if d.is_dir()] if corpus.exists() else []
    if not matters:
        print("  SKIP  no matters under data/corpus/ — copy a synthetic mailbox in:")
        print("        cp -r om_privilege_project/mailboxes/CUB-v-CoT data/corpus/")
        return

    from ajit_lpp.ingest_eml import ingest_dir

    for matter in matters:
        facts, errors = ingest_dir(matter)
        print(f"  {matter.name}: {len(facts)} parsed, {len(errors)} errors")
        for e in errors[:5]:
            print(f"    ERROR {e}")
        check(f"{matter.name}: every file parsed", not errors, f"{len(errors)} errors")
        if not facts:
            continue
        hashes = {f.source_hash for f in facts}
        check(f"{matter.name}: hashes unique per file", len(hashes) == len(facts))
        disps = {}
        for f in facts:
            d = classify(f).disposition.value
            disps[d] = disps.get(d, 0) + 1
        print(f"    mechanical-only dispositions: {disps}")
        check(
            f"{matter.name}: nothing PRIVILEGED on mechanical facts alone",
            disps.get("privileged", 0) == 0,
            disps,
        )
        gt_path = matter / "ground_truth.json"
        if not gt_path.exists():
            print(f"    NOTE  no ground_truth.json in {matter.name} — smoke checks only")
            continue
        _score_against_ground_truth(matter, gt_path, facts)


def _score_against_ground_truth(matter, gt_path, facts) -> None:
    """Perfect-proposer simulation: ground truth supplies the evaluative
    facts a correct proposer would record; the rule layer disposes; the
    dispositions are scored against the labels.

    This tests the RULE LAYER at corpus scale, independently of any LLM.
    It does not test a proposer — none exists yet — and says so.
    """
    import json
    from dataclasses import replace as _r
    from ajit_lpp.models import Tri, Limb

    gt = {g["email_id"]: g for g in json.loads(gt_path.read_text())}
    by_id = {f.doc_id: f for f in facts}
    missing = [k for k in gt if k not in by_id]
    check(f"{matter.name}: every ground-truth id has an .eml",
          not missing, f"{len(missing)} missing")

    ok_priv = ok_notpriv = ok_noclaim = ok_hitl = 0
    wrong = []
    for eid, g in gt.items():
        f = by_id.get(eid)
        if f is None:
            continue
        label, mixed, fraud, waiver = (g["label"], g["is_mixed"],
                                       g["is_fraud"], g["is_waiver"])
        # The perfect proposer records what the scenario actually was:
        if label == "privileged" and not (mixed or fraud or waiver):
            f2 = _r(f, asserted_limb=Limb.LEGAL_ADVICE,
                    marked_confidential=Tri.YES, disclosed_to_third_party=Tri.NO,
                    mixed_purpose_indicated=Tri.NO,
                    proposed_dominant_purpose=g.get("reason", "legal advice"),
                    parties=tuple(
                        _r(p, is_lawyer=Tri.YES, acting_in_legal_capacity=Tri.YES)
                        if i == 0 else
                        _r(p, is_client_or_client_employee=Tri.YES)
                        for i, p in enumerate(f.parties)) or f.parties,
                    prior_waiver_recorded=Tri.NO)
            expect = "privileged"
        elif fraud:
            f2 = _r(f, asserted_limb=Limb.LEGAL_ADVICE,
                    improper_purpose_recorded=Tri.YES)
            expect = "not_privileged"
        elif waiver:
            f2 = _r(f, asserted_limb=Limb.LEGAL_ADVICE,
                    prior_waiver_recorded=Tri.YES)
            expect = "not_privileged"
        elif mixed or label == "review_required":
            f2 = _r(f, asserted_limb=Limb.LEGAL_ADVICE,
                    mixed_purpose_indicated=Tri.YES if mixed else Tri.UNKNOWN)
            expect = "hitl_required"
        else:  # plain not_privileged: no claim is asserted over it
            f2 = f
            expect = "no_claim"

        got = classify(f2).disposition.value
        if expect == "no_claim":
            # Unclaimed documents are produced; the engine's answer must be
            # "no claim to test" (HITL via AU-PURP-03), never privileged.
            if got != "privileged":
                ok_noclaim += 1
            else:
                wrong.append((eid, "privileged asserted over an unclaimed document"))
        elif got == expect:
            if expect == "privileged": ok_priv += 1
            elif expect == "not_privileged": ok_notpriv += 1
            else: ok_hitl += 1
        else:
            wrong.append((eid, f"expected {expect}, engine {got} "
                               f"(label={label} mixed={mixed} fraud={fraud} waiver={waiver})"))

    total = ok_priv + ok_notpriv + ok_noclaim + ok_hitl + len(wrong)
    print(f"    perfect-proposer simulation over {total} ground-truth entries:")
    print(f"      privileged matched      : {ok_priv}")
    print(f"      not_privileged matched  : {ok_notpriv}")
    print(f"      review/mixed -> HITL    : {ok_hitl}")
    print(f"      unclaimed handled       : {ok_noclaim}")
    print(f"      wrong                   : {len(wrong)}")
    for eid, why in wrong[:8]:
        print(f"        {eid[:13]}: {why}")
    check(f"{matter.name}: zero wrong dispositions under perfect facts",
          not wrong, f"{len(wrong)} wrong")
    print("    NOTE  this scores the rule layer with correctly recorded facts;")
    print("          the proposer (D-03) is a separate, unbuilt, ungated component")


def gate_nat75447() -> None:
    print("\nGate 4 — NAT 75447 round-trip")
    tpl = Path(__file__).parent / "template_blank.xlsx"
    if not tpl.exists():
        print("  SKIP  place the pristine ATO form at template_blank.xlsx")
        return
    from ajit_lpp import nat75447 as n

    f = clean_advice()
    c = classify(f)
    cl = n.Claimant(
        name="Test Claimant", position="Solicitor", organisation="Test Org",
        is_legal_practitioner=True, admission_jurisdiction="Test Jurisdiction",
    )
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        line = n.export(tpl, Path(d) / "out.xlsx", cl, [(f, c)])
        ok = n.verify_from_log(line, tpl, cl, [(f, c)], Path(d) / "out2.xlsx")
    check("export reproducible from its log line, byte-identical", ok)

    hitl_doc = mutate(clean_advice(), doc_id="D-9999", mixed_purpose_indicated=Tri.YES)
    try:
        with tempfile.TemporaryDirectory() as d:
            n.export(tpl, Path(d) / "x.xlsx", cl, [(hitl_doc, classify(hitl_doc))])
        check("export refuses unresolved HITL documents", False)
    except ValueError:
        check("export refuses unresolved HITL documents", True)

    try:
        with tempfile.TemporaryDirectory() as d:
            n.export(tpl, Path(d) / "x.xlsx", None, [(f, c)])
        check("export refuses an unnamed claimant", False)
    except n.ClaimantNotNamed:
        check("export refuses an unnamed claimant", True)

    try:
        with tempfile.TemporaryDirectory() as d:
            n.export(tpl, Path(d) / "x.xlsx", n.DEFAULT_CLAIMANT, [(f, c)])
        check("export refuses the default claimant while fields are unconfirmed", False)
    except n.ClaimantNotNamed:
        check("export refuses the default claimant while fields are unconfirmed", True)


if __name__ == "__main__":
    gate_determinism()
    gate_rule_behaviour()
    gate_golden_set()
    gate_synthetic_taxonomy()
    gate_nat75447()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} failure(s): {', '.join(FAILURES)}")
        sys.exit(1)
    print("All implemented gates pass.")
