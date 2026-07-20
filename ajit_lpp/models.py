"""
AJIT LPP Engine — canonical data model.

Design constraint (Ruling, 20 Jul 2026): the LLM proposes, deterministic rules
dispose. Everything in this module is on the *dispose* side: plain data, no
inference, no model calls, no I/O. A DocumentFacts record is the only thing the
rule layer is ever allowed to see.

Determinism contract: every value here is JSON-serialisable and ordered. No
timestamps, no UUIDs, no dict-ordering dependence inside a classification
record. Run metadata (when, by whom, on what) lives in the run log, never in the
record — so three runs over the same corpus produce byte-identical output.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


SCHEMA_VERSION = "ajit.facts/1"
RULESET_VERSION = "au.lpp/0.3"


class Tri(str, Enum):
    """Three-valued logic. UNKNOWN is a first-class answer and never guessed."""

    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class Limb(str, Enum):
    LEGAL_ADVICE = "legal_advice"
    LITIGATION = "litigation"
    NOT_ASSERTED = "not_asserted"


class Disposition(str, Enum):
    PRIVILEGED = "privileged"
    NOT_PRIVILEGED = "not_privileged"
    HITL_REQUIRED = "hitl_required"


@dataclass(frozen=True)
class Party:
    """A person on a communication.

    `is_lawyer` and `acting_in_legal_capacity` are deliberately separate. A
    lawyer who is not acting as one attracts no privilege (Waterford v
    Commonwealth (1987) 163 CLR 54 on salaried lawyers; CTP v PwC on the
    multi-disciplinary problem). Capacity is evaluative — if it is not recorded
    on the engagement, it stays UNKNOWN and the document goes to a human.
    """

    party_id: str
    role: str  # sender | recipient | cc | bcc | author | custodian
    is_lawyer: Tri = Tri.UNKNOWN
    acting_in_legal_capacity: Tri = Tri.UNKNOWN
    is_client_or_client_employee: Tri = Tri.UNKNOWN
    is_third_party: Tri = Tri.UNKNOWN
    organisation: str = ""
    position: str = ""


@dataclass(frozen=True)
class DocumentFacts:
    """The complete, and only, input to the deterministic rule layer.

    Populated by ingestion (mechanical fields) and by the LLM proposer
    (evaluative fields, each carrying its own confidence and never binding).
    """

    doc_id: str
    source_hash: str  # sha256 of the source bytes — provenance anchor
    doc_type: str = ""  # email | attachment | memo | file_note | ...
    date: str = ""  # ISO-8601 or "" — never inferred
    subject: str = ""
    page_count: int = 0
    is_copy: Tri = Tri.UNKNOWN
    has_attachments: Tri = Tri.UNKNOWN
    parent_doc_id: str = ""

    parties: tuple[Party, ...] = ()

    # --- Confidentiality (largely mechanisable) ---
    marked_confidential: Tri = Tri.UNKNOWN
    disclosed_to_third_party: Tri = Tri.UNKNOWN
    third_party_under_common_interest: Tri = Tri.UNKNOWN
    # Heppner (SDNY, 17 Feb 2026): content created in a training-permissive
    # public AI tool is not confidential at inception — privilege never
    # attaches, as distinct from being waived.
    created_in_public_ai_tool: Tri = Tri.UNKNOWN
    distribution_breadth: int = -1  # -1 = unknown; recipient count

    # --- Purpose (evaluative — proposer fills, rules never trust alone) ---
    asserted_limb: Limb = Limb.NOT_ASSERTED
    # Pratt Holdings (2004) 136 FCR 357: a third-party agent's document can
    # attract advice-limb privilege where brought into existence for provision
    # to the client's lawyer. Recordable fact, not an inference.
    prepared_for_provision_to_lawyer: Tri = Tri.UNKNOWN
    litigation_on_foot_or_anticipated: Tri = Tri.UNKNOWN
    proposed_dominant_purpose: str = ""  # free text from proposer
    proposer_confidence: float = 0.0  # 0.0-1.0; advisory only
    mixed_purpose_indicated: Tri = Tri.UNKNOWN

    # A-G (NT) v Kearney (1985) 159 CLR 500: privilege does not attach to
    # communications made in furtherance of an illegal or improper purpose.
    # This is a RECORDED finding (an operator or court has found it), never
    # an inference from content.
    improper_purpose_recorded: Tri = Tri.UNKNOWN

    # --- Compulsion / handling ---
    produced_under_compulsion: Tri = Tri.UNKNOWN
    prior_waiver_recorded: Tri = Tri.UNKNOWN

    def fingerprint(self) -> str:
        """Stable hash of the facts. Same facts in, same fingerprint out."""
        blob = json.dumps(to_jsonable(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RuleOutcome:
    """One rule's finding. Rules state a result and why, and nothing else."""

    rule_id: str
    disposition: Disposition
    basis: str  # plain-English reason, in our own words
    authority: str = ""  # citation, or "" where the rule is mechanical
    authority_verified: bool = False  # primary-source verified from issuing court
    decisive: bool = False  # a decisive NOT_PRIVILEGED short-circuits the chain


@dataclass(frozen=True)
class Classification:
    """The record that ends up in front of a judge. Everything is traceable."""

    doc_id: str
    facts_fingerprint: str
    schema_version: str = SCHEMA_VERSION
    ruleset_version: str = RULESET_VERSION
    disposition: Disposition = Disposition.HITL_REQUIRED
    limb: Limb = Limb.NOT_ASSERTED
    basis: str = ""
    outcomes: tuple[RuleOutcome, ...] = ()
    hitl_reasons: tuple[str, ...] = ()
    unverified_authorities: tuple[str, ...] = ()


def to_jsonable(obj: Any) -> Any:
    """Deterministic serialisation: enums to values, dataclasses to dicts."""
    if isinstance(obj, Enum):
        return obj.value
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_jsonable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, dict):
        return {k: to_jsonable(obj[k]) for k in sorted(obj)}
    return obj


def dumps(obj: Any) -> str:
    """Canonical JSON — the byte-identical determinism gate depends on this."""
    return json.dumps(to_jsonable(obj), sort_keys=True, separators=(",", ":"))
