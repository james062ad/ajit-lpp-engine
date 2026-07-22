"""
AJIT LPP Engine — disposition.

Ordering of precedence, and the reason for it:

  1. A decisive NOT_PRIVILEGED short-circuits. If confidentiality never existed
     or has been destroyed, nothing downstream can restore the claim, and the
     rest of the chain is not run.
  2. Any HITL_REQUIRED outcome dominates any PRIVILEGED outcome. The engine
     never resolves an open evaluative question in favour of the claim.
  3. PRIVILEGED requires a positive rule to have fired. Silence is not a claim.

The default is HITL_REQUIRED. A document the engine does not understand goes to
a human, every time.
"""

from __future__ import annotations

from .models import (
    Classification,
    Disposition,
    DocumentFacts,
    RuleOutcome,
)
from .rules_au import RULE_CHAIN


def classify(facts: DocumentFacts, chain=RULE_CHAIN) -> Classification:
    outcomes: list[RuleOutcome] = []

    for rule in chain:
        outcome = rule(facts)
        if outcome is None:
            continue
        outcomes.append(outcome)
        if outcome.decisive and outcome.disposition is Disposition.NOT_PRIVILEGED:
            break

    disposition, basis = _dispose(outcomes)

    hitl_reasons = tuple(
        f"{o.rule_id}: {o.basis}"
        for o in outcomes
        if o.disposition is Disposition.HITL_REQUIRED
    )
    unverified = tuple(
        sorted(
            {
                o.authority
                for o in outcomes
                if o.authority and not o.authority_verified
            }
        )
    )

    return Classification(
        doc_id=facts.doc_id,
        facts_fingerprint=facts.fingerprint(),
        disposition=disposition,
        limb=facts.asserted_limb,
        basis=basis,
        outcomes=tuple(outcomes),
        hitl_reasons=hitl_reasons,
        unverified_authorities=unverified,
    )


def _dispose(outcomes: list[RuleOutcome]) -> tuple[Disposition, str]:
    for o in outcomes:
        if o.decisive and o.disposition is Disposition.NOT_PRIVILEGED:
            return Disposition.NOT_PRIVILEGED, o.basis

    # NOTED outcomes are recorded observations and never move a disposition.
    hitl = [o for o in outcomes if o.disposition is Disposition.HITL_REQUIRED]
    if hitl:
        return (
            Disposition.HITL_REQUIRED,
            "Referred for human determination: " + hitl[0].basis,
        )

    granted = [o for o in outcomes if o.disposition is Disposition.PRIVILEGED]
    if granted:
        return Disposition.PRIVILEGED, granted[-1].basis

    return (
        Disposition.HITL_REQUIRED,
        "No rule reached a conclusion on the facts recorded for this document.",
    )
