"""
AJIT LPP Engine — golden set loader.

Reads the chapter-3 worklist and types every row before anything scores:

  rule        — record_type=rule in notes (Esso, Spotless). Validated for
                content by a human, never scored: scoring the engine against
                the cases that state its own rules is circular.
  context     — record_type=context in notes (possibly Jacobsen, pending
                James's ruling). Mapped in by the guide's chapter structure,
                not by a privilege determination. Not scored.
  uncertain   — determination is UNCERTAIN or blank. Drafter declined to
                assert; held out until James's verification resolves it.
  mixed       — determination is category-dependent (Southcorp). Needs
                decomposition into sub-scenarios before it can score; held
                out until that decomposition exists.
  scorable    — a clean privileged / not_privileged determination.

Every held-out row is reported with its reason. The denominator is never
padded and never silently shrunk.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

SCORABLE = ("privileged", "not_privileged")


@dataclass(frozen=True)
class GoldenRow:
    id: str
    authority: str
    limb: str
    edge_tested: str
    determination: str
    basis: str
    notes: str
    expert_validated: str
    row_type: str  # rule | context | uncertain | mixed | scorable

    @property
    def held_out_reason(self) -> str:
        return {
            "rule": "rule-statement authority — circular to score",
            "context": "contextual authority — no privilege determination",
            "uncertain": "drafter declined to assert; awaiting verification",
            "mixed": "category-dependent determination — needs decomposition",
        }.get(self.row_type, "")


def _type_row(determination: str, notes: str) -> str:
    n = notes.lower()
    if "record_type=rule" in n:
        return "rule"
    if "record_type=context" in n:
        return "context"
    d = determination.strip().lower()
    if not d or d.startswith("uncertain"):
        return "uncertain"
    if d in SCORABLE:
        return "scorable"
    return "mixed"


def load_goldenset(path: Path) -> list[GoldenRow]:
    rows: list[GoldenRow] = []
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            det = (r.get("determination") or "").strip()
            notes = r.get("notes") or ""
            rows.append(
                GoldenRow(
                    id=r["id"],
                    authority=r.get("authority", ""),
                    limb=r.get("limb", ""),
                    edge_tested=r.get("edge_tested", ""),
                    determination=det.lower(),
                    basis=r.get("basis", ""),
                    notes=notes,
                    expert_validated=(r.get("expert_validated") or "").strip(),
                    row_type=_type_row(det, notes),
                )
            )
    return rows


def all_pending(rows: list[GoldenRow]) -> bool:
    """True while any row is unverified. The harness reports PROVISIONAL
    until every scored row carries expert validation — a number computed
    over unverified law is a draft number and must say so."""
    return any(
        r.expert_validated.lower() != "yes"
        for r in rows
        if r.row_type == "scorable"
    )
