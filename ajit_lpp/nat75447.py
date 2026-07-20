"""
AJIT LPP Engine — NAT 75447 export.

The field map below is transcribed from the ATO form's own column headings, not
from any earlier implementation. Fourteen columns a-n on Q1; the April flat
schedule used a-l and was wrong.

Two disciplines this module enforces:

1. **The form is filled, not rebuilt.** We write into a copy of the ATO's
   workbook so that what is lodged is the ATO's form, with its own instructions,
   privacy notice and sheet structure intact. Rebuilding it from a fresh
   Workbook produces something that resembles the form and is not it.

2. **A claim is made by a person.** The export refuses to produce a lodgeable
   file unless a human claimant is named. Paragraph 38 particulars answered by
   a machine with no identified claimant are not a privilege claim; they are a
   spreadsheet. See `ClaimantNotNamed`.

Reproducibility: `export()` returns a log line containing the field-map
version, the ruleset version, the template hash, the ordered document
fingerprints and the output hash. `verify_from_log()` rebuilds the export from
that line alone and compares. That is Gate 4.
"""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from .models import Classification, Disposition, DocumentFacts, RULESET_VERSION

FIELD_MAP_VERSION = "nat75447.au/2021-09/1"

# Sheet names as they appear in the ATO workbook. Any drift here means the
# template has changed and the map needs re-verification, so we fail loudly
# rather than writing into whatever sheet happens to be at that index.
SHEET_ASSESS = "Assessing service or engagement"
SHEET_Q1 = "Explain your claim particulars"
SHEET_Q2 = "Particulars in-house counsel"
SHEET_Q3 = "Particulars specific engagement"
SHEET_Q4 = "Additional Information"
SHEET_IDENTITY = "Identity of person filling out"

REQUIRED_SHEETS = (
    "Instructions",
    SHEET_ASSESS,
    SHEET_Q1,
    SHEET_Q2,
    SHEET_Q3,
    SHEET_Q4,
    SHEET_IDENTITY,
)

Q1_HEADER_ROW = 3  # a. b. c. ...
Q1_DESC_ROW = 4  # the ATO's own description of each column
Q1_FIRST_DATA_ROW = 5
Q1_FIRST_COL = 2  # column B; column A is a spacer

# Column letter -> (offset from Q1_FIRST_COL, short name, the ATO's wording in
# abbreviated form for our own checking against the live template)
Q1_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("a", "document_reference", "document ID, file name or reference number"),
    ("b", "privilege_holders", "name of privilege holder(s)"),
    ("c", "date_prepared", "date the document was prepared or communication made"),
    ("d", "page_count", "number of pages in the document"),
    ("e", "title_or_subject", "title or subject line of the communication"),
    ("f", "communication_form", "form of the communication"),
    ("g", "document_type", "type of document"),
    ("h", "parties_and_roles", "identity and role of each person"),
    ("i", "is_copy", "whether the document is a copy"),
    ("j", "dominant_purpose", "the dominant purpose for which the communication was made"),
    ("k", "legal_issue", "the legal issue being advised upon"),
    ("l", "forwarded", "whether the communication was forwarded"),
    ("m", "claimed_full_or_part", "whether LPP is claimed in full or in part"),
    ("n", "attachments", "if there are attachments to the document"),
)

Q3_FIRST_DATA_ROW = 5
Q3_FIRST_COL = 2
Q3_FIELDS: tuple[tuple[str, str], ...] = (
    ("X", "document_reference"),
    ("a", "engagement_evaluation"),
    ("b", "all_main_purposes"),
    ("c", "why_legal_advice_dominant"),
    ("d", "non_legal_person_roles"),
    ("e", "preparation_participants"),
)


class TemplateMismatch(Exception):
    """The workbook is not the NAT 75447 form this field map was written for."""


class ClaimantNotNamed(Exception):
    """No human is named as making the claim. The export will not proceed."""


@dataclass(frozen=True)
class Claimant:
    """The person who makes the claim and answers for it."""

    name: str
    position: str
    organisation: str
    is_legal_practitioner: bool
    admission_jurisdiction: str = ""

    def render(self) -> str:
        parts = [self.name, self.position, self.organisation]
        line = ", ".join(p for p in parts if p)
        if self.is_legal_practitioner and self.admission_jurisdiction:
            line += f" (legal practitioner, admitted {self.admission_jurisdiction})"
        return line


def resolve_sheet(workbook, wanted: str):
    """Return the worksheet whose stripped name matches.

    The genuine ATO download names its last sheet 'Identity of person filling
    out ' — trailing space included. A re-saved copy may strip it. Both are the
    same sheet; neither should fail the map.
    """
    for name in workbook.sheetnames:
        if name.strip() == wanted:
            return workbook[name]
    return None


def validate_template(workbook) -> None:
    """Fail loudly if the workbook is not the form we mapped.

    The ATO revises its forms. A silent write into a shifted column is the worst
    available failure mode, because the output still looks like a lodgeable
    claim.
    """
    missing = [s for s in REQUIRED_SHEETS if resolve_sheet(workbook, s) is None]
    if missing:
        raise TemplateMismatch(f"sheets absent from workbook: {missing}")

    ws = resolve_sheet(workbook, SHEET_Q1)
    for offset, (letter, _name, expected) in enumerate(Q1_FIELDS):
        col = Q1_FIRST_COL + offset
        got_letter = (ws.cell(Q1_HEADER_ROW, col).value or "").strip().rstrip(".")
        if got_letter != letter:
            raise TemplateMismatch(
                f"Q1 column {col}: expected heading '{letter}', found '{got_letter}'"
            )
        desc = (ws.cell(Q1_DESC_ROW, col).value or "").strip().lower()
        if not desc.startswith(expected[:24].lower()):
            raise TemplateMismatch(
                f"Q1 column {letter}: description does not match the mapped "
                f"wording. Expected it to begin '{expected[:24]}', found "
                f"'{desc[:40]}'. The form may have been revised."
            )


def template_is_blank(workbook) -> bool:
    """True if Q1 has no data rows. A populated template is not a template."""
    ws = resolve_sheet(workbook, SHEET_Q1)
    return ws.cell(Q1_FIRST_DATA_ROW, Q1_FIRST_COL).value in (None, "")


def file_hash(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare_output(template: Path, destination: Path) -> Path:
    """Copy the ATO workbook. We never write into the template in place."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template, destination)
    return destination


def log_line(
    template: Path,
    claimant: Claimant,
    classifications: list[Classification],
    output_hash: str,
) -> str:
    """One line from which the export can be rebuilt and compared."""
    fingerprints = "+".join(c.facts_fingerprint[:16] for c in classifications)
    return "\t".join(
        [
            f"field_map={FIELD_MAP_VERSION}",
            f"ruleset={RULESET_VERSION}",
            f"template_sha256={file_hash(template)}",
            f"claimant={claimant.render()}",
            f"n_documents={len(classifications)}",
            f"documents={hashlib.sha256(fingerprints.encode()).hexdigest()}",
            f"output_sha256={output_hash}",
        ]
    )


def guard(claimant: Claimant | None, classifications: list[Classification]) -> None:
    """Pre-flight. Everything that would make the export indefensible."""
    if claimant is None or not claimant.name.strip():
        raise ClaimantNotNamed(
            "NAT 75447 requires the identity of the person filling out the form "
            "and, at paragraph 40, of the person making the claim. A "
            "computer-assisted assessment does not answer either question. "
            "Name the claimant."
        )
    if "[CONFIRM]" in claimant.render() or "[CLAIMANT" in claimant.render():
        raise ClaimantNotNamed(
            "The claimant identity contains unconfirmed placeholder fields: "
            f"'{claimant.render()}'. Confirm every field before export — a "
            "regulator-facing form does not go out with a proposed identity."
        )

    unresolved = [
        c.doc_id for c in classifications if c.disposition is Disposition.HITL_REQUIRED
    ]
    if unresolved:
        raise ValueError(
            f"{len(unresolved)} document(s) are still awaiting human "
            f"determination and cannot be exported as claims: "
            f"{unresolved[:5]}{'...' if len(unresolved) > 5 else ''}. Resolve "
            f"them and record each ruling in the HITL ledger first."
        )

    pending = sorted(
        {a for c in classifications for a in c.unverified_authorities}
    )
    if pending:
        raise ValueError(
            "Export blocked: these authorities have not been verified from the "
            f"issuing court and this form goes to a regulator: {pending}"
        )


# ---------------------------------------------------------------------------
# Writing the form
# ---------------------------------------------------------------------------

def _q1_row(facts: DocumentFacts, cls: Classification) -> dict[str, str]:
    """Render one Q1 row from facts + classification. Pure function of its
    inputs — this is what makes the export reproducible from its log line."""
    from .models import Tri, Limb

    def tri(v, yes: str, no: str, unk: str = "Not recorded") -> str:
        return {Tri.YES: yes, Tri.NO: no}.get(v, unk)

    authors = [p for p in facts.parties if p.role in ("sender", "author")]
    recips = [p for p in facts.parties if p.role in ("recipient", "cc", "bcc")]

    def render_party(p) -> str:
        bits = [p.party_id]
        if p.position:
            bits.append(p.position)
        if p.organisation:
            bits.append(p.organisation)
        return ", ".join(bits)

    parties = "Author/Sender: " + "; ".join(render_party(p) for p in authors)
    if recips:
        parties += ". Recipients: " + "; ".join(render_party(p) for p in recips)

    holders = "; ".join(
        render_party(p)
        for p in facts.parties
        if p.is_client_or_client_employee is Tri.YES
    ) or "Not recorded"

    claimed = cls.disposition is Disposition.PRIVILEGED

    return {
        "document_reference": facts.doc_id,
        "privilege_holders": holders,
        "date_prepared": facts.date or "Not recorded",
        "page_count": str(facts.page_count or ""),
        "title_or_subject": facts.subject,
        "communication_form": facts.doc_type,
        "document_type": (
            "Legal advice / privileged communication"
            if claimed
            else "Business communication — no privilege claimed"
        ),
        "parties_and_roles": parties,
        "is_copy": tri(facts.is_copy, "Yes — copy", "No — original communication"),
        "dominant_purpose": (
            facts.proposed_dominant_purpose
            if claimed
            else "Communication not made for the dominant purpose of obtaining "
            "or giving legal advice or for use in litigation"
        ),
        "legal_issue": (
            facts.proposed_dominant_purpose and cls.basis and
            "See basis of claim" or "N/A — no privilege claimed"
        ) if not claimed else "As per engagement — stated at claim level",
        "forwarded": tri(
            facts.disclosed_to_third_party,
            "Yes — see Q3 particulars for confidentiality explanation",
            "No — not forwarded outside the privileged circle",
        ),
        "claimed_full_or_part": "In full" if claimed else "Not claimed",
        "attachments": tri(
            facts.has_attachments,
            "Has attachments — claims particularised separately",
            "No attachments",
        ),
    }


def _normalise_archive(path: Path) -> None:
    """Rewrite the xlsx so identical content gives identical bytes.

    openpyxl stamps every zip ENTRY with the wall-clock save time at second
    granularity — so two exports of the same content differ across a second
    boundary. Gate 4 caught this the first time a run straddled one. Entry
    order and content are preserved; timestamps are pinned; compression is
    made uniform. The wall clock never enters the file.
    """
    import zipfile

    import re

    entries = []
    with zipfile.ZipFile(path, "r") as zin:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "docProps/core.xml":
                # openpyxl overwrites dcterms:modified with the wall clock at
                # save time regardless of what was set on the workbook. Pin
                # both stamps here, where nothing can overwrite them again.
                data = re.sub(
                    rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*(</dcterms:(?:created|modified)>)",
                    rb"\g<1>2000-01-01T00:00:00Z\g<2>",
                    data,
                )
            entries.append((info.filename, data))
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(info, data)


def export(
    template: Path,
    destination: Path,
    claimant: Claimant,
    documents: list[tuple[DocumentFacts, Classification]],
) -> str:
    """Fill a copy of the ATO form. Returns the reproducibility log line."""
    import openpyxl

    classifications = [c for _, c in documents]
    guard(claimant, classifications)

    src = openpyxl.load_workbook(template)
    validate_template(src)
    if not template_is_blank(src):
        raise TemplateMismatch(
            f"{template} already contains data rows. The export writes into a "
            "pristine ATO form only."
        )
    src.close()

    prepare_output(Path(template), Path(destination))
    wb = openpyxl.load_workbook(destination)

    ws = resolve_sheet(wb, SHEET_Q1)
    # Deterministic row order: sorted by doc_id, never by input order.
    ordered = sorted(documents, key=lambda t: t[0].doc_id)
    for i, (facts, cls) in enumerate(ordered):
        row = Q1_FIRST_DATA_ROW + i
        rendered = _q1_row(facts, cls)
        for offset, (_letter, name, _desc) in enumerate(Q1_FIELDS):
            ws.cell(row, Q1_FIRST_COL + offset, rendered[name])

    ident = resolve_sheet(wb, SHEET_IDENTITY)
    ident.cell(3, 2, claimant.render())

    q4 = resolve_sheet(wb, SHEET_Q4)
    q4.cell(5, 4, "Yes")
    q4.cell(
        5,
        5,
        f"AJIT LPP Engine, field map {FIELD_MAP_VERSION}, ruleset "
        f"{RULESET_VERSION}. The engine proposes and applies deterministic "
        "rules to recorded facts; every evaluative question is determined by "
        "the named claimant, whose rulings are recorded in an append-only "
        "decision ledger.",
    )
    q4.cell(7, 4, "Yes")
    q4.cell(
        7,
        5,
        f"Claim made by {claimant.render()}, who reviewed the classification "
        "record for each document over which privilege is claimed.",
    )

    # Pin volatile workbook properties so identical inputs give identical
    # bytes. openpyxl cannot serialise None here, so we pin to a fixed instant;
    # the wall clock never enters the file.
    from datetime import datetime, timezone

    epoch = datetime(2000, 1, 1, tzinfo=timezone.utc)
    wb.properties.created = epoch
    wb.properties.modified = epoch
    wb.save(destination)
    _normalise_archive(Path(destination))

    out_hash = file_hash(Path(destination))
    return log_line(Path(template), claimant, [c for _, c in ordered], out_hash)


def verify_from_log(
    line: str,
    template: Path,
    claimant: Claimant,
    documents: list[tuple[DocumentFacts, Classification]],
    scratch: Path,
) -> bool:
    """Gate 4: rebuild the export from the same inputs and compare hashes
    against the log line. True iff byte-identical."""
    rebuilt = export(template, scratch, claimant, documents)
    want = dict(kv.split("=", 1) for kv in line.split("\t"))
    got = dict(kv.split("=", 1) for kv in rebuilt.split("\t"))
    return want == got


# ---------------------------------------------------------------------------
# Default claimant
# ---------------------------------------------------------------------------
# Name and admission are from the record. Position and organisation are
# PROPOSED defaults awaiting James's confirmation — flagged in-band so they
# cannot silently reach a lodged form: guard() rejects any claimant whose
# rendered identity still contains an unconfirmed marker.

DEFAULT_CLAIMANT = Claimant(
    name="Geoffrey James Lambert",
    position="Principal [CONFIRM]",
    organisation="AJIT [CONFIRM]",
    is_legal_practitioner=True,
    admission_jurisdiction="Supreme Court of South Australia",
)
