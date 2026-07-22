"""
AJIT LPP Engine — Australian rule chain, ruleset au.lpp/0.4.

Rewritten after an element-by-element audit of both limbs. Ten defects in 0.3
were confirmed empirically before this file was written; each is named in the
rule that fixes it, with the doctrine it got wrong.

  Cross-cutting bars (decisive, and only on RECORDED findings)
    AU-STAT-01  statutory abrogation                     Daniels
    AU-CONF-01  confidentiality absent at creation       element; Heppner cmt
    AU-IMPR-01  illegal or improper purpose              Kearney
    AU-WAIV-01  a recorded waiver ruling                 Mann
  Common elements
    AU-CONF-05  the communication was confidential       Esso
    AU-WAIV-02  later disclosure — evaluative, NEVER decisive   Mann
    AU-COPY-01  copies                                   Propend
  Legal advice limb
    AU-PARTY-01 a lawyer, or the Pratt / circulation routes    Pratt
    AU-PARTY-02 that lawyer acting in a legal capacity         Waterford
    AU-PARTY-03 in-house independence                          Waterford
    AU-PURP-04  the purpose is LEGAL advice
  Litigation limb
    AU-PURP-01  litigation on foot or reasonably anticipated   Esso
    AU-PURP-05  the proceedings are adversarial
  Dominant purpose
    AU-PURP-02  positive only on a clean record                Esso
    AU-PURP-03  no limb asserted — no claim to test
  Notes (never affect the disposition)
    AU-COMP-01  production under compulsion following the Protocol

AUTHORITY STATUS: Esso verified from the High Court. Every other citation is
pending primary-source verification, is flagged in each record relying on it,
and the export refuses to lodge a claim resting on one.
"""

from __future__ import annotations

from .models import Disposition, DocumentFacts, Limb, Party, RuleOutcome, Tri

VERIFIED_AUTHORITIES = frozenset({
    "Esso Australia Resources Ltd v FCT [1999] HCA 67",
    "Mann v Carnell (1999) 201 CLR 1",
})

ESSO = "Esso Australia Resources Ltd v FCT [1999] HCA 67"
MANN = "Mann v Carnell (1999) 201 CLR 1"
WATERFORD = "Waterford v Commonwealth (1987) 163 CLR 54"
PRATT = "Pratt Holdings Pty Ltd v FCT (2004) 136 FCR 357"
PROPEND = "Commissioner of AFP v Propend Finance Pty Ltd (1997) 188 CLR 501"
DANIELS = "Daniels Corporation v ACCC (2002) 213 CLR 543"
KEARNEY = "Attorney-General (NT) v Kearney (1985) 158 CLR 500"
EXPENSE = "Expense Reduction Analysts v Armstrong Strategic (2013) 250 CLR 303"
HEPPNER = "United States v Heppner (SDNY, 17 Feb 2026)"


def _verified(c: str) -> bool:
    return c in VERIFIED_AUTHORITIES


def _o(rule_id, disposition, basis, authority="", decisive=False) -> RuleOutcome:
    return RuleOutcome(
        rule_id=rule_id, disposition=disposition, basis=basis, authority=authority,
        authority_verified=_verified(authority) if authority else True,
        decisive=decisive,
    )


def _any(parties, key) -> Tri:
    if any(key(p) is Tri.YES for p in parties):
        return Tri.YES
    if any(key(p) is Tri.UNKNOWN for p in parties):
        return Tri.UNKNOWN
    return Tri.NO


def _lawyer_capacity(parties) -> Tri:
    """DEFECT 7: capacity was read across ANY party, so a non-lawyer recorded as
    acting in a legal capacity masked a lawyer whose capacity was unknown and
    the engine disposed PRIVILEGED. Capacity is read from lawyer parties only."""
    lawyers = [p for p in parties if p.is_lawyer is Tri.YES]
    if not lawyers:
        return Tri.UNKNOWN
    return _any(tuple(lawyers), lambda p: p.acting_in_legal_capacity)


# ------------------------------------------------------------------- bars

def r_stat_01(f):
    """DEFECT 5: no statutory-abrogation rule existed."""
    if f.statute_abrogates_privilege is Tri.YES:
        return _o("AU-STAT-01", Disposition.NOT_PRIVILEGED,
                  "It is recorded that a statute abrogates the privilege in this "
                  "context by clear words or necessary implication.", DANIELS, True)
    return None


def r_conf_01(f):
    """DEFECT 6: the rule keyed on 'created in a public AI tool' and disposed
    decisively, treating one species of evidence as the element itself. The
    element is whether confidentiality existed at creation; an enterprise tool
    with confidentiality-preserving terms does not destroy it."""
    if f.confidentiality_destroyed_at_creation is Tri.YES:
        return _o("AU-CONF-01", Disposition.NOT_PRIVILEGED,
                  "It is recorded that confidentiality did not exist at the moment "
                  "of creation. Privilege never attached — this is non-attachment, "
                  "not waiver, and no waiver analysis arises.", HEPPNER, True)
    if (f.created_in_public_ai_tool is Tri.YES
            and f.confidentiality_destroyed_at_creation is Tri.UNKNOWN):
        return _o("AU-CONF-01", Disposition.HITL_REQUIRED,
                  "Composed in a public AI tool. Whether that destroyed "
                  "confidentiality at creation turns on the tool's terms, which "
                  "are not recorded.", HEPPNER)
    return None


def r_impr_01(f):
    if f.improper_purpose_recorded is Tri.YES:
        return _o("AU-IMPR-01", Disposition.NOT_PRIVILEGED,
                  "A recorded finding that the communication was made in "
                  "furtherance of an illegal or improper purpose.", KEARNEY, True)
    return None


def r_waiv_01(f):
    if f.waiver_ruling_recorded is Tri.YES:
        scope = (" Recorded scope: " + f.waiver_scope_subject_matter + "."
                 if f.waiver_scope_subject_matter else
                 " No subject-matter scope is recorded against the ruling — the "
                 "reach of the waiver over associated material is unresolved.")
        return _o("AU-WAIV-01", Disposition.NOT_PRIVILEGED,
                  "A waiver ruling has been recorded over this document." + scope,
                  MANN, True)
    return None


# -------------------------------------------------------- common elements

def r_purp_03(f):
    if f.asserted_limb is Limb.NOT_ASSERTED:
        return _o("AU-PURP-03", Disposition.HITL_REQUIRED,
                  "No limb of the privilege has been asserted for this document, "
                  "so there is no claim for the rules to test.")
    return None


def r_conf_05(f):
    """DEFECT 3: confidentiality was tested as marked_confidential and the
    positive rule required a marking. Marking is evidence; the element is
    whether the communication was confidential in fact."""
    if f.communication_confidential is Tri.NO:
        return _o("AU-CONF-05", Disposition.NOT_PRIVILEGED,
                  "It is recorded that the communication was not confidential. "
                  "Confidentiality is an element of the privilege.", ESSO, True)
    if f.communication_confidential is Tri.UNKNOWN:
        if f.marked_confidential is Tri.YES:
            return _o("AU-CONF-05", Disposition.HITL_REQUIRED,
                      "Marked confidential, but whether it was confidential in "
                      "fact is not recorded. A marking is evidence of the element, "
                      "not the element.", ESSO)
        return _o("AU-CONF-05", Disposition.HITL_REQUIRED,
                  "Whether the communication was confidential is not recorded.", ESSO)
    return None


def r_waiv_02(f):
    """DEFECT 4, the serious one. The old AU-CONF-02 disposed NOT_PRIVILEGED,
    decisively, where a document had been disclosed to a third party with no
    recorded common interest — citing Mann. Mann holds the opposite on
    comparable facts: disclosure for a limited purpose was NOT inconsistent
    with maintaining confidentiality, so privilege survived. The old rule also
    collapsed non-attachment into waiver and made common interest the only
    escape from a set that includes limited-purpose disclosure, disclosure
    under an obligation of confidence, disclosure to agents, and inadvertence.

    Waiver is imputed by law from conduct inconsistent with maintaining
    confidentiality, assessed objectively on the whole of the circumstances.
    That is evaluative, so this rule NEVER disposes negatively; only a recorded
    waiver ruling (AU-WAIV-01) does."""
    if f.disclosed_to_third_party is Tri.UNKNOWN:
        return _o("AU-WAIV-02", Disposition.HITL_REQUIRED,
                  "Whether the communication was disclosed outside the privileged "
                  "circle is not recorded.")
    if f.disclosed_to_third_party is Tri.NO:
        return None
    if f.disclosure_inadvertent is Tri.YES:
        return _o("AU-WAIV-02", Disposition.HITL_REQUIRED,
                  "Disclosure is recorded as inadvertent. Inadvertent disclosure "
                  "is a mistake to be corrected, not of itself a waiver — but "
                  "whether privilege survives is for a human to determine.", EXPENSE)
    protected = (f.third_party_under_common_interest is Tri.YES
                 or (f.disclosure_purpose_limited is Tri.YES
                     and f.disclosure_under_obligation_of_confidence is Tri.YES))
    if protected:
        return _o("AU-WAIV-02", Disposition.NOTED,
                  "Disclosed to a third party, but on recorded facts consistent "
                  "with maintaining confidentiality (common interest, or a limited "
                  "purpose under an obligation of confidence). Such disclosure does "
                  "not of itself establish waiver.", MANN)
    return _o("AU-WAIV-02", Disposition.HITL_REQUIRED,
              "Disclosed to a third party. Whether that conduct is inconsistent "
              "with maintaining confidentiality — and so imputes waiver — is "
              "assessed objectively on the whole of the circumstances, informed "
              "where necessary by considerations of fairness. Disclosure does "
              "not of itself necessarily establish waiver.", MANN)


def r_copy_01(f):
    """DEFECT 8: is_copy was recorded and never read. A copy made for the
    privileged purpose can attract privilege even where the original does not."""
    if f.is_copy is Tri.YES and f.copy_made_for_privileged_purpose is Tri.UNKNOWN:
        return _o("AU-COPY-01", Disposition.HITL_REQUIRED,
                  "The document is a copy. Whether it was made for the privileged "
                  "purpose is not recorded.", PROPEND)
    return None


# ----------------------------------------------------- legal advice limb

def r_party_01(f):
    """DEFECT 2: where no lawyer was a party the chain killed the claim unless
    the Pratt fact was recorded — so internal circulation of advice already
    received (disclosure of which would disclose the advice) was disposed
    NOT_PRIVILEGED."""
    if f.asserted_limb is not Limb.LEGAL_ADVICE:
        return None
    present = _any(f.parties, lambda p: p.is_lawyer)
    if present is Tri.YES:
        return None
    if present is Tri.UNKNOWN:
        return _o("AU-PARTY-01", Disposition.HITL_REQUIRED,
                  "Whether any party is a lawyer has not been established.")
    if f.circulates_existing_legal_advice is Tri.YES:
        return _o("AU-PARTY-01", Disposition.NOTED,
                  "No lawyer is a party, but the communication is recorded as "
                  "circulating legal advice already obtained; its disclosure would "
                  "disclose the advice.")
    if f.prepared_for_provision_to_lawyer is Tri.YES:
        return None
    if (f.prepared_for_provision_to_lawyer is Tri.UNKNOWN
            or f.circulates_existing_legal_advice is Tri.UNKNOWN):
        return _o("AU-PARTY-01", Disposition.HITL_REQUIRED,
                  "No lawyer is a party. Whether the document was prepared for "
                  "provision to the client's lawyer, or circulates advice already "
                  "obtained, is not recorded — either keeps the claim alive.", PRATT)
    return _o("AU-PARTY-01", Disposition.NOT_PRIVILEGED,
              "No lawyer is a party, the advice limb is asserted, and it is "
              "recorded that the document was neither prepared for provision to a "
              "lawyer nor circulates advice already obtained.", PRATT, True)


def r_party_02(f):
    if f.asserted_limb is not Limb.LEGAL_ADVICE:
        return None
    if _any(f.parties, lambda p: p.is_lawyer) is not Tri.YES:
        return None
    cap = _lawyer_capacity(f.parties)
    if cap is Tri.NO:
        return _o("AU-PARTY-02", Disposition.NOT_PRIVILEGED,
                  "The lawyer was not acting in a legal capacity on this "
                  "communication.", WATERFORD, True)
    if cap is Tri.UNKNOWN:
        return _o("AU-PARTY-02", Disposition.HITL_REQUIRED,
                  "The capacity in which the lawyer acted is not recorded against "
                  "the engagement. Capacity is evaluative and is never inferred "
                  "from a position or an employer.", WATERFORD)
    return None


def r_party_03(f):
    """DEFECT 9: no in-house handling, though the form has a sheet for it."""
    if f.asserted_limb is not Limb.LEGAL_ADVICE:
        return None
    if f.lawyer_is_in_house is not Tri.YES:
        return None
    if f.in_house_independence_recorded is Tri.NO:
        return _o("AU-PARTY-03", Disposition.NOT_PRIVILEGED,
                  "The adviser is in-house and it is recorded that the requisite "
                  "independence was absent.", WATERFORD, True)
    if f.in_house_independence_recorded is Tri.UNKNOWN:
        return _o("AU-PARTY-03", Disposition.HITL_REQUIRED,
                  "The adviser is in-house. A salaried relationship does not of "
                  "itself defeat privilege, but the adviser's independence is not "
                  "recorded and is evaluative.", WATERFORD)
    return None


def r_purp_04(f):
    """DEFECT 1, the worst false positive: the dominant-purpose rule fired on
    ANY articulated purpose text, so a document whose stated purpose was
    'negotiating the purchase price — pure commercial' was disposed
    PRIVILEGED."""
    if f.asserted_limb is not Limb.LEGAL_ADVICE:
        return None
    if f.purpose_is_legal_advice is Tri.NO:
        return _o("AU-PURP-04", Disposition.NOT_PRIVILEGED,
                  "It is recorded that the purpose was not the giving or obtaining "
                  "of legal advice. Commercial, strategic or administrative advice "
                  "does not attract privilege merely because a lawyer gave it.",
                  WATERFORD, True)
    if f.purpose_is_legal_advice is Tri.UNKNOWN:
        return _o("AU-PURP-04", Disposition.HITL_REQUIRED,
                  "Whether the articulated purpose is the giving or obtaining of "
                  "legal advice, as distinct from commercial or other advice, is "
                  "not recorded.")
    return None


# ------------------------------------------------------- litigation limb

def r_purp_01(f):
    if f.asserted_limb is not Limb.LITIGATION:
        return None
    if f.litigation_on_foot_or_anticipated is Tri.NO:
        return _o("AU-PURP-01", Disposition.NOT_PRIVILEGED,
                  "The litigation limb is asserted, but no litigation was on foot "
                  "or reasonably anticipated at the date of the communication.",
                  ESSO, True)
    if f.litigation_on_foot_or_anticipated is Tri.UNKNOWN:
        return _o("AU-PURP-01", Disposition.HITL_REQUIRED,
                  "Whether litigation was on foot or reasonably anticipated at the "
                  "date of the communication has not been established. A mere "
                  "possibility of litigation is not enough.", ESSO)
    return None


def r_purp_05(f):
    """DEFECT 3b: nothing tested whether the proceedings were adversarial, so a
    document prepared to answer an audit was disposed PRIVILEGED on the
    litigation limb."""
    if f.asserted_limb is not Limb.LITIGATION:
        return None
    if f.proceedings_adversarial is Tri.NO:
        return _o("AU-PURP-05", Disposition.NOT_PRIVILEGED,
                  "It is recorded that the proceedings are not adversarial. "
                  "Litigation privilege does not extend to material prepared for "
                  "an investigative or inquisitorial process.", ESSO, True)
    if f.proceedings_adversarial is Tri.UNKNOWN:
        return _o("AU-PURP-05", Disposition.HITL_REQUIRED,
                  "Whether the proceedings are adversarial is not recorded. An "
                  "audit or regulatory information-gathering process is not, of "
                  "itself, litigation.", ESSO)
    return None


def r_comp_01(f):
    """DEFECT 10: produced_under_compulsion was recorded and no rule read it."""
    if f.produced_under_compulsion is Tri.YES and f.protocol_followed is Tri.YES:
        return _o("AU-COMP-01", Disposition.NOTED,
                  "Produced under compulsion with the LPP Protocol followed. The "
                  "provision of particulars in that manner is not a voluntary "
                  "disclosure and does not of itself waive privilege.")
    return None


def r_purp_02(f):
    """Dominant purpose. Positive only where every supporting fact is recorded.
    Proposer confidence has no path here and never will."""
    if f.asserted_limb is Limb.NOT_ASSERTED:
        return None
    if f.mixed_purpose_indicated is Tri.YES:
        return _o("AU-PURP-02", Disposition.HITL_REQUIRED,
                  "More than one purpose is indicated. Which purpose was dominant "
                  "is a matter of judgment on the whole of the evidence, not a "
                  "mechanical determination.", ESSO)
    if f.mixed_purpose_indicated is Tri.UNKNOWN:
        return _o("AU-PURP-02", Disposition.HITL_REQUIRED,
                  "Whether the communication served more than one purpose is not "
                  "recorded.", ESSO)
    if not f.proposed_dominant_purpose:
        return _o("AU-PURP-02", Disposition.HITL_REQUIRED,
                  "No dominant purpose has been articulated.", ESSO)
    if f.communication_confidential is not Tri.YES:
        return _o("AU-PURP-02", Disposition.HITL_REQUIRED,
                  "The confidentiality element is not established on the record.",
                  ESSO)
    # DEFECT 11, found by the exhaustive proof and invisible to example tests.
    # The bars (statutory abrogation, improper purpose, waiver, confidentiality
    # destroyed at creation) fire only on a recorded YES, so an UNKNOWN read as
    # "no bar" — and blanking a recorded bar turned NOT_PRIVILEGED into
    # PRIVILEGED. Ignorance must never help a claim. A positive disposition
    # therefore requires each bar to be affirmatively recorded as absent. This
    # is also what the form asks for: state the assumptions your claim rests on.
    bars = {
        "statutory abrogation": f.statute_abrogates_privilege,
        "improper purpose": f.improper_purpose_recorded,
        "a recorded waiver ruling": f.waiver_ruling_recorded,
        "confidentiality destroyed at creation":
            f.confidentiality_destroyed_at_creation,
    }
    unrecorded = [name for name, v in bars.items() if v is not Tri.NO]
    if unrecorded:
        return _o("AU-PURP-02", Disposition.HITL_REQUIRED,
                  "Every element of the claim is made out, but the following have "
                  "not been affirmatively excluded on the record: "
                  + "; ".join(unrecorded)
                  + ". A claim is not asserted on facts nobody has checked.", ESSO)
    if f.asserted_limb is Limb.LEGAL_ADVICE:
        if f.purpose_is_legal_advice is not Tri.YES:
            return _o("AU-PURP-02", Disposition.HITL_REQUIRED,
                      "The purpose is not recorded as the giving or obtaining of "
                      "legal advice.", ESSO)
        return _o("AU-PURP-02", Disposition.PRIVILEGED,
                  "A confidential communication with a lawyer acting in a legal "
                  "capacity, for the single articulated dominant purpose of "
                  "obtaining or giving legal advice, with no conduct on the record "
                  "inconsistent with maintaining confidentiality.", ESSO)
    if (f.proceedings_adversarial is not Tri.YES
            or f.litigation_on_foot_or_anticipated is not Tri.YES):
        return _o("AU-PURP-02", Disposition.HITL_REQUIRED,
                  "The litigation predicate is not fully established.", ESSO)
    return _o("AU-PURP-02", Disposition.PRIVILEGED,
              "A confidential communication brought into existence for the single "
              "articulated dominant purpose of use in adversarial litigation that "
              "was on foot or reasonably anticipated.", ESSO)


RULE_CHAIN = (
    r_stat_01, r_conf_01, r_impr_01, r_waiv_01,
    r_purp_03, r_conf_05,
    r_party_01, r_party_02, r_party_03, r_purp_04,
    r_purp_01, r_purp_05,
    r_copy_01, r_waiv_02, r_comp_01,
    r_purp_02,
)
