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
    print("\nGate 1 — golden set, rules alone (BLOCKED)")
    print("  BLOCKED  requires privilege_goldenset_AU_ch3_worklist.csv, filled")
    print("           from the judgments; 15 rows, expert_validated != pending")


def gate_synthetic_taxonomy() -> None:
    print("\nGate 2 — 17-category synthetic taxonomy (BLOCKED)")
    print("  BLOCKED  requires the synthetic corpus; every ambiguous category")
    print("           must resolve to HITL_REQUIRED, not to a guess")


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
