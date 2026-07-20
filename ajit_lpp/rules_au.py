"""
AJIT LPP Engine — Australian deterministic rule layer.

The load-bearing discipline: a rule may only reach a conclusion on facts that
are *mechanisable*. Every evaluative judgment — whether a purpose was dominant,
whether a lawyer was acting as one, whether an inconsistency amounts to waiver —
either resolves on recorded facts or goes to a human. The engine never guesses,
and an UNKNOWN fact is never read as a NO.

Authority status (per the standing sourcing rule: issuing courts and licensed
databases; AustLII prohibited as an evaluation source):
  VERIFIED  — Esso Australia Resources v FCT [1999] HCA 67
  PENDING   — every other citation below. Marked in output until pulled from
              the issuing court. Nothing goes external on a pending authority.
"""

from __future__ import annotations

from .models import Disposition, DocumentFacts, Limb, Party, RuleOutcome, Tri

VERIFIED_AUTHORITIES = frozenset({"Esso Australia Resources Ltd v FCT [1999] HCA 67"})

ESSO = "Esso Australia Resources Ltd v FCT [1999] HCA 67"
MANN = "Mann v Carnell (1999) 201 CLR 1"
WATERFORD = "Waterford v Commonwealth (1987) 163 CLR 54"
PRATT = "Pratt Holdings Pty Ltd v FCT (2004) 136 FCR 357"
DANIELS = "Daniels Corporation v ACCC (2002) 213 CLR 543"
HEPPNER = "United States v Heppner (SDNY, 17 Feb 2026)"


def _verified(citation: str) -> bool:
    return citation in VERIFIED_AUTHORITIES


def _outcome(
    rule_id: str,
    disposition: Disposition,
    basis: str,
    authority: str = "",
    decisive: bool = False,
) -> RuleOutcome:
    return RuleOutcome(
        rule_id=rule_id,
        disposition=disposition,
        basis=basis,
        authority=authority,
        authority_verified=_verified(authority) if authority else True,
        decisive=decisive,
    )


def _has(parties: tuple[Party, ...], predicate) -> Tri:
    """YES if any party satisfies it; UNKNOWN if any could and none does."""
    if any(predicate(p) is Tri.YES for p in parties):
        return Tri.YES
    if any(predicate(p) is Tri.UNKNOWN for p in parties):
        return Tri.UNKNOWN
    return Tri.NO


# --------------------------------------------------------------------------
# Confidentiality — the element that must exist before anything else matters
# --------------------------------------------------------------------------

def r_conf_01_public_ai_tool(f: DocumentFacts) -> RuleOutcome | None:
    """Content composed in a training-permissive public AI tool is not
    confidential at inception, so privilege never attaches. This is a
    non-attachment failure, not a waiver — do not analyse it under Mann."""
    if f.created_in_public_ai_tool is Tri.YES:
        return _outcome(
            "AU-CONF-01",
            Disposition.NOT_PRIVILEGED,
            "Communication was created in a public AI tool whose terms permit "
            "the provider to use the content. Confidentiality did not exist at "
            "the moment of creation, so no privilege attached to it.",
            HEPPNER,
            decisive=True,
        )
    return None


def r_conf_02_third_party_disclosure(f: DocumentFacts) -> RuleOutcome | None:
    """Disclosure outside the privileged circle. Common interest is a recorded
    fact, not an inference — if it is not recorded, this goes to a human."""
    if f.disclosed_to_third_party is Tri.YES:
        if f.third_party_under_common_interest is Tri.YES:
            return None
        if f.third_party_under_common_interest is Tri.NO:
            return _outcome(
                "AU-CONF-02",
                Disposition.NOT_PRIVILEGED,
                "The communication was disclosed to a third party with no "
                "recorded common interest, which is inconsistent with the "
                "maintenance of confidentiality.",
                MANN,
                decisive=True,
            )
        return _outcome(
            "AU-CONF-02",
            Disposition.HITL_REQUIRED,
            "Disclosed to a third party, but whether a common interest exists "
            "is not recorded. Whether the disclosure is inconsistent with "
            "maintaining confidentiality is an evaluative question.",
            MANN,
        )
    if f.disclosed_to_third_party is Tri.UNKNOWN:
        return _outcome(
            "AU-CONF-02",
            Disposition.HITL_REQUIRED,
            "Whether the communication left the privileged circle has not been "
            "established from the record.",
        )
    return None


def r_conf_03_prior_waiver(f: DocumentFacts) -> RuleOutcome | None:
    if f.prior_waiver_recorded is Tri.YES:
        return _outcome(
            "AU-CONF-03",
            Disposition.NOT_PRIVILEGED,
            "A waiver over this document has already been recorded and ruled on.",
            MANN,
            decisive=True,
        )
    return None


# --------------------------------------------------------------------------
# Lawyer and capacity
# --------------------------------------------------------------------------

def r_party_01_lawyer_present(f: DocumentFacts) -> RuleOutcome | None:
    """Absence of a lawyer is decisive for the advice limb only. The litigation
    limb reaches client-to-third-party communications, so it is handled by the
    litigation rules instead."""
    if f.asserted_limb is not Limb.LEGAL_ADVICE:
        return None
    present = _has(f.parties, lambda p: p.is_lawyer)
    if present is Tri.NO:
        return _outcome(
            "AU-PARTY-01",
            Disposition.NOT_PRIVILEGED,
            "No lawyer is a party to the communication, and the claim is made "
            "on the legal advice limb.",
            decisive=True,
        )
    if present is Tri.UNKNOWN:
        return _outcome(
            "AU-PARTY-01",
            Disposition.HITL_REQUIRED,
            "Whether any party is a lawyer has not been established.",
        )
    return None


def r_party_02_legal_capacity(f: DocumentFacts) -> RuleOutcome | None:
    """A lawyer attracts privilege only when acting in that capacity. Capacity
    is a per-engagement record, not a job title."""
    if f.asserted_limb is not Limb.LEGAL_ADVICE:
        return None
    capacity = _has(f.parties, lambda p: p.acting_in_legal_capacity)
    if capacity is Tri.NO:
        return _outcome(
            "AU-PARTY-02",
            Disposition.NOT_PRIVILEGED,
            "The lawyer party was not acting in a legal capacity on this "
            "communication; the advice is not legal advice for the purpose of "
            "the privilege.",
            WATERFORD,
            decisive=True,
        )
    if capacity is Tri.UNKNOWN:
        return _outcome(
            "AU-PARTY-02",
            Disposition.HITL_REQUIRED,
            "The capacity in which the lawyer was acting is not recorded "
            "against the engagement. Capacity is evaluative and is not inferred "
            "from position or organisation.",
            WATERFORD,
        )
    return None


# --------------------------------------------------------------------------
# Purpose — the dominant purpose test
# --------------------------------------------------------------------------

def r_purpose_01_litigation_predicate(f: DocumentFacts) -> RuleOutcome | None:
    if f.asserted_limb is not Limb.LITIGATION:
        return None
    if f.litigation_on_foot_or_anticipated is Tri.NO:
        return _outcome(
            "AU-PURP-01",
            Disposition.NOT_PRIVILEGED,
            "The litigation limb is asserted, but no litigation was on foot or "
            "reasonably anticipated at the date of the communication.",
            ESSO,
            decisive=True,
        )
    if f.litigation_on_foot_or_anticipated is Tri.UNKNOWN:
        return _outcome(
            "AU-PURP-01",
            Disposition.HITL_REQUIRED,
            "Whether litigation was on foot or reasonably anticipated at the "
            "date of the communication has not been established.",
            ESSO,
        )
    return None


def r_purpose_02_dominant_purpose(f: DocumentFacts) -> RuleOutcome | None:
    """The dominant purpose test is evaluative and the engine does not decide
    it. It disposes positively only in the narrow case where every supporting
    fact is recorded and no mixed purpose is indicated; otherwise a human rules.

    The proposer's confidence score is never consulted here. It is advisory
    metadata and has no path to a disposition.
    """
    if f.mixed_purpose_indicated is Tri.YES:
        return _outcome(
            "AU-PURP-02",
            Disposition.HITL_REQUIRED,
            "More than one purpose is indicated. Which purpose was dominant is "
            "a matter of judgment on the whole of the evidence, not a "
            "mechanical determination.",
            ESSO,
        )
    if not f.proposed_dominant_purpose:
        return _outcome(
            "AU-PURP-02",
            Disposition.HITL_REQUIRED,
            "No dominant purpose has been articulated for this communication.",
            ESSO,
        )
    clean = (
        f.marked_confidential is Tri.YES
        and f.disclosed_to_third_party is Tri.NO
        and f.mixed_purpose_indicated is Tri.NO
    )
    if clean and f.asserted_limb is Limb.LEGAL_ADVICE:
        return _outcome(
            "AU-PURP-02",
            Disposition.PRIVILEGED,
            "A confidential communication between client and lawyer acting in "
            "a legal capacity, not disclosed outside the privileged circle, "
            "with a single articulated purpose of obtaining or giving legal "
            "advice.",
            ESSO,
        )
    if clean and f.asserted_limb is Limb.LITIGATION:
        return _outcome(
            "AU-PURP-02",
            Disposition.PRIVILEGED,
            "A confidential communication brought into existence for the "
            "single articulated purpose of use in litigation that was on foot "
            "or reasonably anticipated.",
            ESSO,
        )
    return _outcome(
        "AU-PURP-02",
        Disposition.HITL_REQUIRED,
        "The supporting facts for a dominant purpose finding are not all on "
        "the record.",
        ESSO,
    )


def r_purpose_03_no_limb_asserted(f: DocumentFacts) -> RuleOutcome | None:
    if f.asserted_limb is Limb.NOT_ASSERTED:
        return _outcome(
            "AU-PURP-03",
            Disposition.HITL_REQUIRED,
            "No limb of the privilege has been asserted for this document, so "
            "there is no claim for the rules to test.",
        )
    return None


RULE_CHAIN = (
    r_conf_01_public_ai_tool,
    r_conf_03_prior_waiver,
    r_purpose_03_no_limb_asserted,
    r_party_01_lawyer_present,
    r_party_02_legal_capacity,
    r_purpose_01_litigation_predicate,
    r_conf_02_third_party_disclosure,
    r_purpose_02_dominant_purpose,
)
