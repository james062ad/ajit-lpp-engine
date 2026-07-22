"""
Generate VERIFICATION_PROOFS.md from the rule layer itself.

Every rule's basis text is extracted VERBATIM from ajit_lpp/rules_au.py by
parsing the source (adjacent string literals are already one constant at
parse time, so what is emitted is exactly what the engine prints). Nothing
is paraphrased, so the "Rule" side of every proof is machine-fact.

The "Court" side of every proof is left blank on purpose. Under the standing
control adopted 22 Jul 2026 after the LLM error study, the following fields
are NEVER machine-drafted: the source line, the bench, every quotation from
a judgment, every pinpoint, every Fit verdict, and the Verified-by line.
They are the practitioner's alone.

Run from the project root:
    python3 make_proof_register.py
Writes: VERIFICATION_PROOFS.md
"""

from __future__ import annotations

import ast
from pathlib import Path

RULES = Path("ajit_lpp/rules_au.py")
OUT = Path("VERIFICATION_PROOFS.md")

# Authority constant -> (display heading, case-specific watch-points)
AUTHORITIES = {
    "KEARNEY": (
        "Attorney-General (NT) v Kearney (1985) 158 CLR 500 — High Court",
        [
            "Transcribe the bench from the report itself — bench composition is "
            "a field class the error study proved LLMs fabricate.",
            "The engine is deliberately STRICTER than the case (recorded finding "
            "vs prima facie evidence). The Fit test is whether the basis text "
            "attributes to Kearney only what Kearney holds.",
            "Note where the improper-purpose width (abuse of statutory power, "
            "beyond crime/fraud) is stated, and by whom.",
        ],
    ),
    "DANIELS": (
        "Daniels Corporation International Pty Ltd v ACCC (2002) 213 CLR 543 — High Court",
        [
            "Quote the joint judgment's abrogation formulation exactly — the "
            "words 'clear', 'express', 'unmistakable and unambiguous', "
            "'necessary implication' matter; the rule must use the Court's "
            "formulation, not a blend.",
            "Quote the substantive-right characterisation the rule relies on.",
        ],
    ),
    "EXPENSE": (
        "Expense Reduction Analysts Group Pty Ltd v Armstrong Strategic "
        "Management and Marketing Pty Ltd (2013) 250 CLR 303 — High Court, "
        "single joint judgment",
        [
            "Decide and record whether the waiver point is ratio or applied "
            "principle within a case-management disposition — and check the "
            "basis text does not overclaim.",
            "Quote the passage on inadvertent production and inconsistency; it "
            "should sit comfortably with the conformed Mann text (0.4.1).",
        ],
    ),
    "WATERFORD": (
        "Waterford v Commonwealth (1987) 163 CLR 54 — High Court",
        [
            "THE SPREAD IS THE FINDING: quote each Justice's formulation of the "
            "adviser-qualification requirement separately (admission / "
            "entitlement to practise / competence-and-independence). Do not "
            "collapse them.",
            "This table feeds the open lawyer_qualification_basis rule "
            "decision — precision here is reused later.",
        ],
    ),
    "PRATT": (
        "Pratt Holdings Pty Ltd v Commissioner of Taxation (2004) 136 FCR 357 "
        "— Full Federal Court (FCR, not CLR)",
        [
            "Quote the formulation of whose purpose counts and how the third "
            "party's role is characterised (the rejection of the narrow "
            "agency line).",
            "The holding is capability, not outcome — check the basis text "
            "does not read as 'the accountant's report WAS privileged'.",
        ],
    ),
    "PROPEND": (
        "Commissioner of Australian Federal Police v Propend Finance Pty Ltd "
        "(1997) 188 CLR 501 — High Court, SEVEN judgments",
        [
            "Assemble the majority for the copy holding Justice by Justice — "
            "one Rule/Court/Fit block per supporting Justice. Name who "
            "dissents on the point. Do not import any composition from any "
            "AI draft, including this file's generator.",
            "Note in whose hands and for whose purpose the copying test is "
            "framed, per Justice.",
        ],
    ),
    "HEPPNER": (
        "United States v Heppner (SDNY, 2026) — persuasive only; verify from "
        "the docket (PACER/CourtListener), not secondary reporting",
        [
            "First prove the decision exists as described: docket number, "
            "judge, date, operative language — every identifying detail in "
            "any AI draft is unconfirmed until the docket shows it.",
            "Record explicitly that AU-CONF-01's Australian basis stands on "
            "the confidentiality element independently of Heppner.",
        ],
    ),
    "MANN": (
        "Mann v Carnell (1999) 201 CLR 1; [1999] HCA 66 — VERIFIED 22 Jul "
        "2026 (commit 11684e3). Included so the register is complete; "
        "retro-fit the quote blocks from your reading at [28]-[32] if you "
        "want uniform proof format across the set.",
        [],
    ),
    "ESSO": (
        "Esso Australia Resources Ltd v FCT [1999] HCA 67 — VERIFIED (worked "
        "record, 29 Jun session). Retro-fit quote blocks for uniformity when "
        "the worked record is recovered.",
        [],
    ),
}

HEADER = """# VERIFICATION_PROOFS — rule text against the Court's words

Purpose: for every proposition the engine attributes to an authority, set the
rule's exact basis text beside the judgment's exact words at a pinpoint, with
a Fit verdict. A reader — or a judge — checks each pairing in seconds; there
is nothing to argue with except the Court's own language.

STANDING CONTROL (adopted 22 Jul 2026, LLM error study): every field marked
[PRACTITIONER] below is never machine-drafted — source, bench, quotations,
pinpoints, Fit verdicts, Verified-by. The Rule lines were extracted verbatim
from ajit_lpp/rules_au.py at generation time and are machine-fact.

Fit vocabulary: CONFORMS / OVERSTATES / UNDERSTATES / MISATTRIBUTES.
Anything but CONFORMS: STOP — the rule text conforms first (patch version
bump), then the authority enters VERIFIED_AUTHORITIES.

Per-case close-out, after all Fit lines read CONFORMS:
  1. Complete the Verified-by line.
  2. Add the authority's exact constant string to VERIFIED_AUTHORITIES.
  3. python3 tests_gates.py | tail -1   (green)
  4. git status   (only intended files)
  5. git add . && git commit -m "Verify <Case> from <source> — <rule IDs>"

"""

PROOF_BLOCK = """
**Proposition {n} — {rule_id}**

> Rule text (verbatim from the engine):
> "{basis}"

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________
"""

CASE_TAIL = """
Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________
"""


def extract_rules() -> dict[str, list[tuple[str, str]]]:
    """authority constant -> [(rule_id, verbatim basis text), ...]"""
    tree = ast.parse(RULES.read_text())
    out: dict[str, list[tuple[str, str]]] = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "_o"):
            continue
        args = node.args
        if len(args) < 3:
            continue
        rule_id = args[0].value if isinstance(args[0], ast.Constant) else "?"
        basis = args[2].value if isinstance(args[2], ast.Constant) else None
        auth = next(
            (a.id for a in args[3:] if isinstance(a, ast.Name)), None
        )
        if basis and auth:
            out.setdefault(auth, []).append((rule_id, basis))
    return out


def main() -> None:
    by_auth = extract_rules()
    parts = [HEADER]
    for const, (heading, watch) in AUTHORITIES.items():
        parts.append(f"\n---\n\n## {heading}\n")
        if watch:
            parts.append("Watch-points:\n")
            parts.extend(f"- {w}\n" for w in watch)
        rules = by_auth.get(const, [])
        if not rules:
            parts.append(
                "\n(No rule in the current chain cites this authority "
                "directly — record the verification for the register's "
                "completeness.)\n"
            )
        seen = set()
        n = 0
        for rule_id, basis in rules:
            key = (rule_id, basis)
            if key in seen:
                continue
            seen.add(key)
            n += 1
            parts.append(PROOF_BLOCK.format(n=n, rule_id=rule_id, basis=basis))
        parts.append(CASE_TAIL)
    parts.append(
        "\n---\n\n## Claimant confirmation (unblocks the final export refusal)\n"
        "\nPosition, as it should read on the form [PRACTITIONER]: __________\n"
        "\nOrganisation, as it should read on the form [PRACTITIONER]: ______\n"
        "\nConfirmed [PRACTITIONER]: ____ Jul 2026, by GJML\n"
        "\nThen: edit DEFAULT_CLAIMANT in ajit_lpp/nat75447.py — remove both "
        "[CONFIRM] markers — run the gates, commit as "
        "\"Claimant confirmed; final export refusal cleared\".\n"
    )
    OUT.write_text("".join(parts))
    total = sum(len(v) for v in by_auth.values())
    print(f"wrote {OUT} — {total} rule-basis extractions across "
          f"{len([a for a in AUTHORITIES if by_auth.get(a)])} cited authorities")


if __name__ == "__main__":
    main()
