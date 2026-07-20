"""
AJIT LPP Engine — EML ingestion (mechanical facts only).

Parses RFC-822 .eml files into DocumentFacts. The load-bearing constraint:

  INGESTION FILLS ONLY WHAT THE FILE MECHANICALLY CONTAINS.

Headers give parties, roles, date, subject, distribution breadth; the bytes
give the hash; MIME structure gives attachments. Everything evaluative —
who is a lawyer, capacity, confidentiality, limb, purpose — stays UNKNOWN.
Enrichment of those fields is the proposer's job (D-03) or a human's, never
the parser's. An email address does not tell you someone is a lawyer, and
this module refuses to pretend otherwise.

Consequence, by design: a freshly ingested corpus classifies ~100% to
HITL_REQUIRED, because no claim has been asserted and no evaluative fact
recorded. That is the correct baseline — the distance from there to a
disposed corpus is exactly the work the proposer and the practitioner do,
made visible.

CLI:
    python3 -m ajit_lpp.ingest_eml <dir-of-eml-files> [--summary]
"""

from __future__ import annotations

import hashlib
import sys
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path

from .models import DocumentFacts, Party, Tri
from .engine import classify


def _party(name: str, addr: str, role: str) -> Party:
    label = name.strip() or addr
    org = addr.split("@", 1)[1] if "@" in addr else ""
    return Party(
        party_id=label,
        role=role,
        is_lawyer=Tri.UNKNOWN,                 # never inferred from a domain
        acting_in_legal_capacity=Tri.UNKNOWN,
        is_client_or_client_employee=Tri.UNKNOWN,
        is_third_party=Tri.UNKNOWN,
        organisation=org,                      # mechanical: the mail domain
        position="",
    )


def facts_from_eml(path: Path) -> DocumentFacts:
    raw = Path(path).read_bytes()
    msg = BytesParser(policy=policy.default).parsebytes(raw)

    parties: list[Party] = []
    for hdr, role in (("From", "sender"), ("To", "recipient"),
                      ("Cc", "cc"), ("Bcc", "bcc")):
        for name, addr in getaddresses([msg.get(hdr, "") or ""]):
            if addr or name:
                parties.append(_party(name, addr, role))

    date = ""
    if msg.get("Date"):
        try:
            date = parsedate_to_datetime(msg["Date"]).date().isoformat()
        except (TypeError, ValueError):
            date = ""  # a bad header is a blank fact, not a guess

    attachments = Tri.NO
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                attachments = Tri.YES
                break

    recipients = [p for p in parties if p.role in ("recipient", "cc", "bcc")]

    return DocumentFacts(
        doc_id=Path(path).stem,
        source_hash=hashlib.sha256(raw).hexdigest(),
        doc_type="Email",
        date=date,
        subject=(msg.get("Subject") or "").strip(),
        page_count=0,                          # not a mechanical email fact
        is_copy=Tri.UNKNOWN,
        has_attachments=attachments,
        parties=tuple(parties),
        distribution_breadth=len(recipients) if recipients else -1,
        # Everything below is evaluative and stays at its UNKNOWN default:
        # marked_confidential, disclosed_to_third_party, limb, purpose,
        # capacity, provision-to-lawyer, litigation state, waiver.
    )


def ingest_dir(directory: Path) -> tuple[list[DocumentFacts], list[str]]:
    """Parse every .eml under directory. Returns (facts, errors) — a file
    that fails to parse is reported, never silently skipped."""
    directory = Path(directory)
    facts, errors = [], []
    for p in sorted(directory.rglob("*.eml")):
        try:
            facts.append(facts_from_eml(p))
        except Exception as e:  # noqa: BLE001 — report, don't die mid-corpus
            errors.append(f"{p.name}: {type(e).__name__}: {e}")
    return facts, errors


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        sys.exit(__doc__)
    facts, errors = ingest_dir(Path(argv[1]))
    print(f"parsed {len(facts)} .eml file(s); {len(errors)} error(s)")
    for e in errors[:10]:
        print(f"  ERROR {e}")
    if not facts:
        return
    # Determinism check: same bytes, same fingerprints.
    fp1 = [f.fingerprint() for f in facts]
    fp2 = [facts_from_eml_path.fingerprint() for facts_from_eml_path in
           [facts_from_eml(p) for p in sorted(Path(argv[1]).rglob("*.eml"))]]
    print(f"re-parse fingerprint-identical: {fp1 == fp2}")
    counts: dict[str, int] = {}
    for f in facts:
        counts[classify(f).disposition.value] = \
            counts.get(classify(f).disposition.value, 0) + 1
    print("dispositions on mechanical facts alone (expected: ~all hitl_required):")
    for k in sorted(counts):
        print(f"  {counts[k]:>5}  {k}")


if __name__ == "__main__":
    main(sys.argv)
