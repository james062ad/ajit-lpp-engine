"""
AJIT LPP Engine — facts intake.

The bridge between a matter and the engine, for pilots run before automated
ingestion exists: a practitioner records each document's facts in a CSV; this
module validates every row strictly and emits DocumentFacts.

Design rules:

1. **Blank means UNKNOWN, never NO.** An unfilled cell is an honest gap and
   routes the question to a human. Only an explicit 'no' is a NO.
2. **Malformed rows stop the run.** The loader refuses the whole file with a
   numbered error list rather than skipping or repairing rows. A facts file
   with silent repairs is not a record.
3. **Hashes are real.** If a source file path is given, the intake hashes it;
   if not, the row must say so explicitly (source_hash=UNAVAILABLE), and that
   lands in the record.

CLI:
    python3 -m ajit_lpp.facts_intake template <out.csv>   # blank template + example
    python3 -m ajit_lpp.facts_intake check <facts.csv>    # validate only
    python3 -m ajit_lpp.facts_intake run <facts.csv>      # classify, print summary
"""

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

from .models import Disposition, DocumentFacts, Limb, Party, Tri
from .engine import classify

TRI_MAP = {"yes": Tri.YES, "y": Tri.YES, "no": Tri.NO, "n": Tri.NO,
           "unknown": Tri.UNKNOWN, "u": Tri.UNKNOWN, "": Tri.UNKNOWN}
LIMB_MAP = {"legal_advice": Limb.LEGAL_ADVICE, "advice": Limb.LEGAL_ADVICE,
            "litigation": Limb.LITIGATION, "": Limb.NOT_ASSERTED,
            "not_asserted": Limb.NOT_ASSERTED, "none": Limb.NOT_ASSERTED}

# Party encoding, one party per segment, segments separated by ' ; ':
#   name | role | lawyer y/n/u | legal_capacity y/n/u | client y/n/u |
#   third_party y/n/u | organisation | position
# Trailing fields may be omitted.
PARTY_FIELDS = 8

COLUMNS = [
    "doc_id", "source_path", "source_hash", "doc_type", "date", "subject",
    "page_count", "is_copy", "has_attachments", "parent_doc_id", "parties",
    "marked_confidential", "disclosed_to_third_party",
    "third_party_under_common_interest", "created_in_public_ai_tool",
    "distribution_breadth", "asserted_limb", "prepared_for_provision_to_lawyer",
    "litigation_on_foot_or_anticipated", "proposed_dominant_purpose",
    "mixed_purpose_indicated", "produced_under_compulsion",
    "prior_waiver_recorded", "improper_purpose_recorded", "recorder_notes",
]

EXAMPLE_ROW = {
    "doc_id": "EXAMPLE-001 (delete this row before use)",
    "source_path": "",
    "source_hash": "UNAVAILABLE",
    "doc_type": "Email",
    "date": "2025-03-14",
    "subject": "Advice on the s353-10 notice",
    "page_count": "1",
    "is_copy": "no",
    "has_attachments": "no",
    "parent_doc_id": "",
    "parties": "M Chen|sender|y|y|n|n|Kingston Legal|Partner ; "
               "R Thompson|recipient|n|n|y|n|EnergyCorp Pty Ltd|CFO",
    "marked_confidential": "yes",
    "disclosed_to_third_party": "no",
    "third_party_under_common_interest": "",
    "created_in_public_ai_tool": "no",
    "distribution_breadth": "1",
    "asserted_limb": "legal_advice",
    "prepared_for_provision_to_lawyer": "",
    "litigation_on_foot_or_anticipated": "",
    "proposed_dominant_purpose": "Obtaining legal advice on the notice response",
    "mixed_purpose_indicated": "no",
    "produced_under_compulsion": "no",
    "prior_waiver_recorded": "no",
    "improper_purpose_recorded": "no",
    "recorder_notes": "Blank cells mean UNKNOWN and route to a human. Only an explicit 'no' is a NO.",
}


class IntakeError(Exception):
    """The facts file is not a record. Fix the listed rows and re-run."""


def _tri(value: str, row: int, col: str, errors: list[str]) -> Tri:
    v = (value or "").strip().lower()
    if v in TRI_MAP:
        return TRI_MAP[v]
    errors.append(f"row {row}: {col}='{value}' — use yes / no / unknown / blank")
    return Tri.UNKNOWN


def _parse_parties(raw: str, row: int, errors: list[str]) -> tuple[Party, ...]:
    if not raw.strip():
        errors.append(f"row {row}: parties is empty — at least one party is required")
        return ()
    out = []
    for seg in raw.split(";"):
        seg = seg.strip()
        if not seg:
            continue
        bits = [b.strip() for b in seg.split("|")]
        if len(bits) < 2:
            errors.append(f"row {row}: party '{seg[:40]}' needs at least name|role")
            continue
        bits += [""] * (PARTY_FIELDS - len(bits))
        name, role, lw, cap, cl, tp, org, pos = bits[:PARTY_FIELDS]
        out.append(Party(
            party_id=name, role=role.lower(),
            is_lawyer=_tri(lw, row, f"party '{name}' lawyer", errors),
            acting_in_legal_capacity=_tri(cap, row, f"party '{name}' capacity", errors),
            is_client_or_client_employee=_tri(cl, row, f"party '{name}' client", errors),
            is_third_party=_tri(tp, row, f"party '{name}' third_party", errors),
            organisation=org, position=pos,
        ))
    return tuple(out)


def _hash_source(path_value: str, declared: str, row: int,
                 base: Path, errors: list[str]) -> str:
    declared = (declared or "").strip()
    if path_value.strip():
        p = (base / path_value).resolve() if not Path(path_value).is_absolute() \
            else Path(path_value)
        if not p.exists():
            errors.append(f"row {row}: source_path '{path_value}' does not exist")
            return "MISSING"
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if declared and declared.upper() != "UNAVAILABLE" and declared != digest:
            errors.append(f"row {row}: declared source_hash does not match the file")
        return digest
    if declared.upper() == "UNAVAILABLE":
        return "UNAVAILABLE"
    if declared:
        return declared
    errors.append(f"row {row}: give source_path, a source_hash, or "
                  f"source_hash=UNAVAILABLE — silence is not an answer")
    return "MISSING"


def write_template(dest: Path) -> None:
    with Path(dest).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerow(EXAMPLE_ROW)


def load_facts(path: Path) -> list[DocumentFacts]:
    path = Path(path)
    errors: list[str] = []
    facts: list[DocumentFacts] = []
    seen: set[str] = set()

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise IntakeError(f"columns missing from {path.name}: {missing}")
        for i, r in enumerate(reader, start=2):  # header is line 1
            doc_id = (r["doc_id"] or "").strip()
            if not doc_id:
                errors.append(f"row {i}: doc_id is empty")
                continue
            if doc_id.startswith("EXAMPLE-"):
                errors.append(f"row {i}: the example row is still in the file")
                continue
            if doc_id in seen:
                errors.append(f"row {i}: duplicate doc_id '{doc_id}'")
                continue
            seen.add(doc_id)

            limb_raw = (r["asserted_limb"] or "").strip().lower()
            if limb_raw not in LIMB_MAP:
                errors.append(f"row {i}: asserted_limb='{r['asserted_limb']}' — "
                              f"use legal_advice / litigation / blank")
                limb_raw = ""

            try:
                pages = int(r["page_count"]) if (r["page_count"] or "").strip() else 0
            except ValueError:
                errors.append(f"row {i}: page_count must be a number")
                pages = 0
            try:
                breadth = int(r["distribution_breadth"]) \
                    if (r["distribution_breadth"] or "").strip() else -1
            except ValueError:
                errors.append(f"row {i}: distribution_breadth must be a number")
                breadth = -1

            facts.append(DocumentFacts(
                doc_id=doc_id,
                source_hash=_hash_source(r["source_path"] or "", r["source_hash"] or "",
                                         i, path.parent, errors),
                doc_type=(r["doc_type"] or "").strip(),
                date=(r["date"] or "").strip(),
                subject=(r["subject"] or "").strip(),
                page_count=pages,
                is_copy=_tri(r["is_copy"], i, "is_copy", errors),
                has_attachments=_tri(r["has_attachments"], i, "has_attachments", errors),
                parent_doc_id=(r["parent_doc_id"] or "").strip(),
                parties=_parse_parties(r["parties"] or "", i, errors),
                marked_confidential=_tri(r["marked_confidential"], i,
                                         "marked_confidential", errors),
                disclosed_to_third_party=_tri(r["disclosed_to_third_party"], i,
                                              "disclosed_to_third_party", errors),
                third_party_under_common_interest=_tri(
                    r["third_party_under_common_interest"], i,
                    "third_party_under_common_interest", errors),
                created_in_public_ai_tool=_tri(r["created_in_public_ai_tool"], i,
                                               "created_in_public_ai_tool", errors),
                distribution_breadth=breadth,
                asserted_limb=LIMB_MAP[limb_raw],
                prepared_for_provision_to_lawyer=_tri(
                    r["prepared_for_provision_to_lawyer"], i,
                    "prepared_for_provision_to_lawyer", errors),
                litigation_on_foot_or_anticipated=_tri(
                    r["litigation_on_foot_or_anticipated"], i,
                    "litigation_on_foot_or_anticipated", errors),
                proposed_dominant_purpose=(r["proposed_dominant_purpose"] or "").strip(),
                mixed_purpose_indicated=_tri(r["mixed_purpose_indicated"], i,
                                             "mixed_purpose_indicated", errors),
                produced_under_compulsion=_tri(r["produced_under_compulsion"], i,
                                               "produced_under_compulsion", errors),
                prior_waiver_recorded=_tri(r["prior_waiver_recorded"], i,
                                           "prior_waiver_recorded", errors),
                improper_purpose_recorded=_tri(r["improper_purpose_recorded"], i,
                                               "improper_purpose_recorded", errors),
            ))

    if errors:
        raise IntakeError(
            f"{path.name}: {len(errors)} problem(s); nothing was classified.\n  "
            + "\n  ".join(errors[:40])
            + ("" if len(errors) <= 40 else f"\n  ... and {len(errors)-40} more")
        )
    if not facts:
        raise IntakeError(f"{path.name}: no data rows")
    return facts


def run(path: Path) -> None:
    facts = load_facts(path)
    results = [(f, classify(f)) for f in facts]
    counts: dict[str, int] = {}
    for _, c in results:
        counts[c.disposition.value] = counts.get(c.disposition.value, 0) + 1
    print(f"{len(results)} documents classified (ruleset in every record):")
    for k in sorted(counts):
        print(f"  {counts[k]:>4}  {k}")
    hitl = [(f, c) for f, c in results if c.disposition is Disposition.HITL_REQUIRED]
    if hitl:
        print(f"\nAwaiting human determination ({len(hitl)}):")
        for f, c in hitl[:25]:
            print(f"  {f.doc_id}: {c.hitl_reasons[0][:110]}")
        if len(hitl) > 25:
            print(f"  ... and {len(hitl)-25} more")
    print("\nNext: rule on the HITL queue (ledger), then export via nat75447.")


def main(argv: list[str]) -> None:
    if len(argv) == 3 and argv[1] == "template":
        write_template(Path(argv[2]))
        print(f"template written: {argv[2]} — delete the example row before use")
    elif len(argv) == 3 and argv[1] == "check":
        n = len(load_facts(Path(argv[2])))
        print(f"{argv[2]}: {n} rows valid")
    elif len(argv) == 3 and argv[1] == "run":
        run(Path(argv[2]))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
