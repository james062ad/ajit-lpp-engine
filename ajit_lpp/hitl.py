"""
AJIT LPP Engine — human-in-the-loop ledger.

Standing rule: nothing silently accepted becomes silently permanent. Every
operator ruling records what was set aside, how many rows it touched, the
reason, who ruled and when, the downstream effect, and how to reopen it.

The ledger is append-only. A reversal is a new entry that supersedes an old one
by id; entries are never edited or deleted, because the question a court asks is
not "what does the register say now" but "what did you decide, when, and why".
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .models import to_jsonable


@dataclass(frozen=True)
class HitlDecision:
    decision_id: str
    doc_ids: tuple[str, ...]
    question: str  # what the engine could not resolve
    ruling: str  # what the human decided
    reason: str  # why
    ruled_by: str
    ruled_at: str  # ISO-8601 UTC
    downstream_effect: str
    how_to_reopen: str
    supersedes: str = ""  # decision_id this replaces, or ""

    @property
    def count(self) -> int:
        return len(self.doc_ids)


def new_decision(
    decision_id: str,
    doc_ids: list[str],
    question: str,
    ruling: str,
    reason: str,
    ruled_by: str,
    downstream_effect: str,
    how_to_reopen: str,
    supersedes: str = "",
) -> HitlDecision:
    return HitlDecision(
        decision_id=decision_id,
        doc_ids=tuple(sorted(doc_ids)),
        question=question,
        ruling=ruling,
        reason=reason,
        ruled_by=ruled_by,
        ruled_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        downstream_effect=downstream_effect,
        how_to_reopen=how_to_reopen,
        supersedes=supersedes,
    )


class HitlLedger:
    """Append-only JSONL ledger, with a Markdown rendering for humans."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def append(self, decision: HitlDecision) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(to_jsonable(decision), sort_keys=True) + "\n")

    def entries(self) -> list[HitlDecision]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(HitlDecision(**json.loads(line)))
        return out

    def live(self) -> list[HitlDecision]:
        """Entries not superseded by a later one."""
        superseded = {e.supersedes for e in self.entries() if e.supersedes}
        return [e for e in self.entries() if e.decision_id not in superseded]

    def to_markdown(self) -> str:
        lines = [
            "# HITL_DECISIONS",
            "",
            "Append-only. Superseded entries are retained, not removed.",
            "",
        ]
        for e in self.entries():
            status = "SUPERSEDED" if e.decision_id in {
                x.supersedes for x in self.entries() if x.supersedes
            } else "LIVE"
            lines += [
                f"## {e.decision_id} — {status}",
                "",
                f"- **Question the engine could not resolve:** {e.question}",
                f"- **Ruling:** {e.ruling}",
                f"- **Reason:** {e.reason}",
                f"- **Documents affected:** {e.count}",
                f"- **Ruled by:** {e.ruled_by} at {e.ruled_at}",
                f"- **Downstream effect:** {e.downstream_effect}",
                f"- **How to reopen:** {e.how_to_reopen}",
            ]
            if e.supersedes:
                lines.append(f"- **Supersedes:** {e.supersedes}")
            lines.append("")
        return "\n".join(lines)
