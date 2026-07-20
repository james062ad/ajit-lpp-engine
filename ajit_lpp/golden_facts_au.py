"""
AJIT LPP Engine — golden facts fixtures, AU chapter 3.

The worklist rows are prose; the engine eats DocumentFacts. This module is the
bridge: for each scorable case, a structured rendering of the document
scenario the court ruled on.

DISCIPLINE — read before editing:

These fixtures are FIRST-PASS DRAFTS under the same rule as the CSV rows:
drafted from legal knowledge, verified by James against the judgment before
anything relying on them goes external. `verified=False` on every fixture
until he flips it. The harness reports PROVISIONAL while any scored fixture
is unverified.

A fixture encodes only facts the judgment records. Where the judgment is
silent on a field, the field stays UNKNOWN — and if that sends the engine to
HITL_REQUIRED on a case the court decided, that is a FINDING about what the
rule layer can mechanise, not an error to be papered over by inventing facts.

Expected outcomes carry two values:
  court   — what the court determined (must match the CSV row).
  engine  — what the engine SHOULD do on these facts under current rules,
            which may legitimately be hitl_required where the deciding
            question was evaluative. court != engine is the honest record
            of the mechanisation boundary.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import DocumentFacts, Limb, Party, Tri


@dataclass(frozen=True)
class GoldenFixture:
    case_id: str
    facts: DocumentFacts
    court: str  # privileged | not_privileged
    engine: str  # privileged | not_privileged | hitl_required
    rationale: str  # why engine may differ from court
    verified: bool = False


def _f(case_id: str, **kw) -> DocumentFacts:
    kw.setdefault("source_hash", "0" * 64)
    return DocumentFacts(doc_id=case_id, **kw)


FIXTURES: tuple[GoldenFixture, ...] = (
    # ------------------------------------------------------------------
    GoldenFixture(
        case_id="AU-C3-02",  # Grant v Downs
        facts=_f(
            "AU-C3-02",
            doc_type="internal report",
            subject="Incident reports following patient death",
            parties=(
                Party("hospital staff", "author", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
                Party("hospital authority", "recipient", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
            ),
            marked_confidential=Tri.UNKNOWN,
            disclosed_to_third_party=Tri.NO,
            created_in_public_ai_tool=Tri.NO,
            asserted_limb=Limb.LITIGATION,
            litigation_on_foot_or_anticipated=Tri.YES,
            proposed_dominant_purpose="Routine internal reporting of the incident; possible use by legal advisers",
            mixed_purpose_indicated=Tri.YES,
            prior_waiver_recorded=Tri.NO,
        ),
        court="not_privileged",
        engine="hitl_required",
        rationale=(
            "Which of several concurrent purposes predominated was the very "
            "question the Court decided. Under current rules a recorded mixed "
            "purpose routes to a human (AU-PURP-02); the engine correctly "
            "declines to decide dominance. A rule disposing multi-purpose "
            "routine reports negatively on recorded facts is a possible future "
            "refinement — a James decision, not a default."
        ),
    ),
    # ------------------------------------------------------------------
    GoldenFixture(
        case_id="AU-C3-03",  # Baker v Campbell
        facts=_f(
            "AU-C3-03",
            doc_type="solicitor file documents",
            subject="Client documents held by solicitor, seized under s 10 warrant",
            parties=(
                Party("solicitor", "custodian", Tri.YES, Tri.YES, Tri.NO, Tri.NO),
                Party("client", "author", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
            ),
            marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.NO,
            created_in_public_ai_tool=Tri.NO,
            asserted_limb=Limb.LEGAL_ADVICE,
            proposed_dominant_purpose="Obtaining and giving legal advice",
            mixed_purpose_indicated=Tri.NO,
            prior_waiver_recorded=Tri.NO,
        ),
        court="privileged",
        engine="privileged",
        rationale=(
            "The privileged character of the communications was not the "
            "contested question; on the recorded facts every element is "
            "satisfied and the engine should dispose positively."
        ),
    ),
    # ------------------------------------------------------------------
    GoldenFixture(
        case_id="AU-C3-04",  # Propend — copies of documents
        facts=_f(
            "AU-C3-04",
            doc_type="copy documents",
            subject="Copies of non-privileged originals, made for provision to solicitor for advice",
            parties=(
                Party("solicitor", "recipient", Tri.YES, Tri.YES, Tri.NO, Tri.NO),
                Party("client", "sender", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
            ),
            is_copy=Tri.YES,
            marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.NO,
            created_in_public_ai_tool=Tri.NO,
            asserted_limb=Limb.LEGAL_ADVICE,
            proposed_dominant_purpose="Copies made for the purpose of obtaining legal advice",
            mixed_purpose_indicated=Tri.NO,
            prior_waiver_recorded=Tri.NO,
        ),
        court="privileged",
        engine="privileged",
        rationale=(
            "Propend: a copy made for the privileged purpose can attract "
            "privilege even where the original does not. The engine has no "
            "rule that penalises is_copy=YES, so the claim rides on the "
            "ordinary elements — which is the correct doctrine. If a future "
            "rule ever makes copy status decisive against a claim, this "
            "fixture is the regression tripwire."
        ),
    ),
    # ------------------------------------------------------------------
    GoldenFixture(
        case_id="AU-C3-05",  # Pratt Holdings
        facts=_f(
            "AU-C3-05",
            doc_type="third-party report",
            subject="Accountant's report prepared for provision to lawyers",
            parties=(
                Party("accountant", "author", Tri.NO, Tri.NO, Tri.NO, Tri.YES),
                Party("client", "recipient", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
            ),
            marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.YES,
            third_party_under_common_interest=Tri.UNKNOWN,
            created_in_public_ai_tool=Tri.NO,
            asserted_limb=Limb.LEGAL_ADVICE,
            prepared_for_provision_to_lawyer=Tri.YES,
            proposed_dominant_purpose=(
                "Prepared for the dominant purpose of provision to the "
                "client's lawyers for legal advice"
            ),
            mixed_purpose_indicated=Tri.UNKNOWN,
            prior_waiver_recorded=Tri.NO,
        ),
        court="privileged",
        engine="hitl_required",
        rationale=(
            "Pratt turns on an evaluative characterisation: whether the third "
            "party's document was brought into existence for the requisite "
            "dominant purpose, with the third party's involvement not "
            "defeating confidentiality. The engine's third-party rule "
            "(AU-CONF-02) and mixed-purpose handling correctly route this to "
            "a human. The lawyer-not-party structure also exercises the "
            "advice-limb boundary. If the engine says NOT_PRIVILEGED here, "
            "that is a rule-layer BUG — the third-party agent doctrine is not "
            "yet encoded."
        ),
    ),
    # ------------------------------------------------------------------
    GoldenFixture(
        case_id="AU-C3-07",  # A-G (NT) v Maurice — source materials
        facts=_f(
            "AU-C3-07",
            doc_type="source materials",
            subject="Underlying source materials compiled for a claim book in proceedings",
            parties=(
                Party("counsel/advisers", "recipient", Tri.YES, Tri.YES, Tri.NO, Tri.NO),
                Party("claimants", "author", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
            ),
            marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.NO,
            created_in_public_ai_tool=Tri.NO,
            asserted_limb=Limb.LITIGATION,
            litigation_on_foot_or_anticipated=Tri.YES,
            proposed_dominant_purpose="Preparation of the claim for the proceeding",
            mixed_purpose_indicated=Tri.NO,
            prior_waiver_recorded=Tri.NO,
        ),
        court="privileged",
        engine="privileged",
        rationale=(
            "The source materials themselves were not disclosed; the claim "
            "book was. The waiver contest — whether tabling the claim book "
            "waived privilege over the sources — is represented only as "
            "prior_waiver_recorded=NO, matching the drafted determination "
            "that privilege over the sources stood. The imputed-waiver "
            "fairness analysis itself is NOT mechanised and is not claimed "
            "to be; a recorded waiver ruling is the only waiver fact the "
            "engine consumes."
        ),
    ),
    # ------------------------------------------------------------------
    GoldenFixture(
        case_id="AU-C3-08",  # Carter
        facts=_f(
            "AU-C3-08",
            doc_type="solicitor communications",
            subject="Client-solicitor communications sought for defence of criminal charges",
            parties=(
                Party("solicitor", "recipient", Tri.YES, Tri.YES, Tri.NO, Tri.NO),
                Party("client", "author", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
            ),
            marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.NO,
            created_in_public_ai_tool=Tri.NO,
            asserted_limb=Limb.LEGAL_ADVICE,
            proposed_dominant_purpose="Obtaining legal advice",
            mixed_purpose_indicated=Tri.NO,
            prior_waiver_recorded=Tri.NO,
        ),
        court="privileged",
        engine="privileged",
        rationale=(
            "Carter's contest was whether an accused's interest could "
            "displace an otherwise valid claim — a no-balancing scope point. "
            "The underlying communications satisfy every element on the "
            "recorded facts; no displacement mechanism exists in the rule "
            "layer, deliberately."
        ),
    ),
    # ------------------------------------------------------------------
    GoldenFixture(
        case_id="AU-C3-11",  # Waterford
        facts=_f(
            "AU-C3-11",
            doc_type="internal advice",
            subject="Advice by salaried government lawyers to their agency",
            parties=(
                Party(
                    "government lawyer", "author",
                    Tri.YES, Tri.YES, Tri.NO, Tri.NO,
                    organisation="Commonwealth agency", position="Legal officer",
                ),
                Party("agency", "recipient", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
            ),
            marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.NO,
            created_in_public_ai_tool=Tri.NO,
            asserted_limb=Limb.LEGAL_ADVICE,
            proposed_dominant_purpose="Giving legal advice to the agency",
            mixed_purpose_indicated=Tri.NO,
            prior_waiver_recorded=Tri.NO,
        ),
        court="privileged",
        engine="privileged",
        rationale=(
            "With capacity RECORDED as legal (acting_in_legal_capacity=YES) "
            "the salaried relationship does not defeat the claim — which is "
            "Waterford's point. The companion probe below shows the same "
            "case with capacity unrecorded, which must route to a human."
        ),
    ),
    # ------------------------------------------------------------------
    GoldenFixture(
        case_id="AU-C3-11b",  # Waterford probe — capacity unrecorded
        facts=_f(
            "AU-C3-11b",
            doc_type="internal advice",
            subject="Advice by salaried government lawyers, capacity not recorded",
            parties=(
                Party("government lawyer", "author", Tri.YES, Tri.UNKNOWN, Tri.NO, Tri.NO),
                Party("agency", "recipient", Tri.NO, Tri.NO, Tri.YES, Tri.NO),
            ),
            marked_confidential=Tri.YES,
            disclosed_to_third_party=Tri.NO,
            created_in_public_ai_tool=Tri.NO,
            asserted_limb=Limb.LEGAL_ADVICE,
            proposed_dominant_purpose="Giving legal advice to the agency",
            mixed_purpose_indicated=Tri.NO,
            prior_waiver_recorded=Tri.NO,
        ),
        court="privileged",
        engine="hitl_required",
        rationale=(
            "Not a scored row — a probe derived from AU-C3-11. Capacity is "
            "evaluative when unrecorded (AU-PARTY-02, citing Waterford); the "
            "engine must decline rather than infer it from the job title."
        ),
    ),
)


def fixtures_by_case() -> dict[str, GoldenFixture]:
    return {f.case_id: f for f in FIXTURES}
