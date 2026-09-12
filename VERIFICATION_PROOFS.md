# VERIFICATION_PROOFS — rule text against the Court's words

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


---

## Attorney-General (NT) v Kearney (1985) 158 CLR 500 — High Court
Watch-points:
- Transcribe the bench from the report itself — bench composition is a field class the error study proved LLMs fabricate.
- The engine is deliberately STRICTER than the case (recorded finding vs prima facie evidence). The Fit test is whether the basis text attributes to Kearney only what Kearney holds.
- Note where the improper-purpose width (abuse of statutory power, beyond crime/fraud) is stated, and by whom.

**Proposition 1 — AU-IMPR-01**

> Rule text (verbatim from the engine):
> "A recorded finding that the communication was made in furtherance of an illegal or improper purpose."

Court (Gibbs CJ, judgment; ATO reproduction unpaginated — no CLR page markers displayed) [PRACTITIONER]:
> "The privilege, which arises only because the public interest requires it, does not exist when it is seen that it would be contrary to a higher public interest to give effect to it."
>
> Murphy J. said, at p 159, that "it would be curious if the child's welfare were not paramount over legal professional privilege in circumstances such as those in this case". The case is authority for the view that legal professional privilege will be denied to a communication which is made for the purpose of frustrating the processes of the law itself, even though no crime or fraud is contemplated.
>
> In my opinion the present case comes within the principle which forms the basis of the rule that denies privilege to communications made to further an illegal purpose. It would be contrary to the public interest which the privilege is designed to secure - the better administration of justice - to allow it to be used to protect communications made to further a deliberate abuse of statutory power and by that abuse to prevent others from exercising their rights under the law. It would shake public confidence in the law if there was reasonable ground for believing that a regulation had been enacted for an unauthorized purpose and with the intent of frustrating legitimate claims, and yet the law protected from disclosure the communications made to seek and give advice in carrying out that purpose. It is unnecessary to consider whether the decision in Crescent Farm Sports v. Sterling Offices was too restrictive, or whether the view expressed in the modern United States cases that the principle extends to communications made for the purpose of committing a tort is too wide. The law strikes a balance between securing proper representation by encouraging full disclosure on the one hand, and requiring the production of all relevant evidence on the other, but the balance more readily inclines in favour of disclosure where privilege from disclosure might conceal an abuse of delegated powers to enact legislation, and thus obstruct a proper challenge to the validity of part of the law itself. The basis of the privilege is not endangered if it is held that it does not protect communications made by a public authority for the purpose of obtaining advice or assistance to exceed its statutory powers.
>
> The privilege is of course not displaced by making a mere charge of crime or fraud or, as in the present case, a charge that powers have been exercised for an ulterior purpose. This was made clear in Bullivant v. Attorney-General for Victoria, at pp 201, 203, 205, and in O'Rourke v. Darbishire [1920] AC 581 , at pp 604, 613-614, 622-623, 632-633. As Viscount Finlay said in the latter case, at p 604, "there must be something to give colour to the charge". His Lordship continued:"

Fit [PRACTITIONER]: ____________  — ____________________________________

Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________

---

## Daniels Corporation International Pty Ltd v ACCC (2002) 213 CLR 543 — High Court
Watch-points:
- Quote the joint judgment's abrogation formulation exactly — the words 'clear', 'express', 'unmistakable and unambiguous', 'necessary implication' matter; the rule must use the Court's formulation, not a blend.
- Quote the substantive-right characterisation the rule relies on.

**Proposition 1 — AU-STAT-01**

> Rule text (verbatim from the engine):
> "It is recorded that a statute abrogates the privilege in this context by clear words or necessary implication."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________

---

## Expense Reduction Analysts Group Pty Ltd v Armstrong Strategic Management and Marketing Pty Ltd (2013) 250 CLR 303 — High Court, single joint judgment
Watch-points:
- Decide and record whether the waiver point is ratio or applied principle within a case-management disposition — and check the basis text does not overclaim.
- Quote the passage on inadvertent production and inconsistency; it should sit comfortably with the conformed Mann text (0.4.1).

**Proposition 1 — AU-WAIV-02**

> Rule text (verbatim from the engine):
> "Disclosure is recorded as inadvertent. Inadvertent disclosure is a mistake to be corrected, not of itself a waiver — but whether privilege survives is for a human to determine."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________

---

## Waterford v Commonwealth (1987) 163 CLR 54 — High Court
Watch-points:
- THE SPREAD IS THE FINDING: quote each Justice's formulation of the adviser-qualification requirement separately (admission / entitlement to practise / competence-and-independence). Do not collapse them.
- This table feeds the open lawyer_qualification_basis rule decision — precision here is reused later.

**Proposition 1 — AU-PARTY-02**

> Rule text (verbatim from the engine):
> "The lawyer was not acting in a legal capacity on this communication."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 2 — AU-PARTY-02**

> Rule text (verbatim from the engine):
> "The capacity in which the lawyer acted is not recorded against the engagement. Capacity is evaluative and is never inferred from a position or an employer."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 3 — AU-PARTY-03**

> Rule text (verbatim from the engine):
> "The adviser is in-house and it is recorded that the requisite independence was absent."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 4 — AU-PARTY-03**

> Rule text (verbatim from the engine):
> "The adviser is in-house. A salaried relationship does not of itself defeat privilege, but the adviser's independence is not recorded and is evaluative."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 5 — AU-PURP-04**

> Rule text (verbatim from the engine):
> "It is recorded that the purpose was not the giving or obtaining of legal advice. Commercial, strategic or administrative advice does not attract privilege merely because a lawyer gave it."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________

---

## Pratt Holdings Pty Ltd v Commissioner of Taxation (2004) 136 FCR 357 — Full Federal Court (FCR, not CLR)
Watch-points:
- Quote the formulation of whose purpose counts and how the third party's role is characterised (the rejection of the narrow agency line).
- The holding is capability, not outcome — check the basis text does not read as 'the accountant's report WAS privileged'.

**Proposition 1 — AU-PARTY-01**

> Rule text (verbatim from the engine):
> "No lawyer is a party, the advice limb is asserted, and it is recorded that the document was neither prepared for provision to a lawyer nor circulates advice already obtained."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 2 — AU-PARTY-01**

> Rule text (verbatim from the engine):
> "No lawyer is a party. Whether the document was prepared for provision to the client's lawyer, or circulates advice already obtained, is not recorded — either keeps the claim alive."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________

---

## Commissioner of Australian Federal Police v Propend Finance Pty Ltd (1997) 188 CLR 501 — High Court, SEVEN judgments
Watch-points:
- Assemble the majority for the copy holding Justice by Justice — one Rule/Court/Fit block per supporting Justice. Name who dissents on the point. Do not import any composition from any AI draft, including this file's generator.
- Note in whose hands and for whose purpose the copying test is framed, per Justice.

**Proposition 1 — AU-COPY-01**

> Rule text (verbatim from the engine):
> "The document is a copy. Whether it was made for the privileged purpose is not recorded."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________

---

## United States v Heppner (SDNY, 2026) — persuasive only; verify from the docket (PACER/CourtListener), not secondary reporting
Watch-points:
- First prove the decision exists as described: docket number, judge, date, operative language — every identifying detail in any AI draft is unconfirmed until the docket shows it.
- Record explicitly that AU-CONF-01's Australian basis stands on the confidentiality element independently of Heppner.

**Proposition 1 — AU-CONF-01**

> Rule text (verbatim from the engine):
> "It is recorded that confidentiality did not exist at the moment of creation. Privilege never attached — this is non-attachment, not waiver, and no waiver analysis arises."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 2 — AU-CONF-01**

> Rule text (verbatim from the engine):
> "Composed in a public AI tool. Whether that destroyed confidentiality at creation turns on the tool's terms, which are not recorded."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________

---

## Mann v Carnell (1999) 201 CLR 1; [1999] HCA 66 — VERIFIED 22 Jul 2026 (commit 11684e3). Included so the register is complete; retro-fit the quote blocks from your reading at [28]-[32] if you want uniform proof format across the set.

**Proposition 1 — AU-WAIV-02**

> Rule text (verbatim from the engine):
> "Disclosed to a third party. Whether that conduct is inconsistent with maintaining confidentiality — and so imputes waiver — is assessed objectively on the whole of the circumstances, informed where necessary by considerations of fairness. Disclosure does not of itself necessarily establish waiver."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 2 — AU-WAIV-02**

> Rule text (verbatim from the engine):
> "Disclosed to a third party, but on recorded facts consistent with maintaining confidentiality (common interest, or a limited purpose under an obligation of confidence). Such disclosure does not of itself establish waiver."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________

---

## Esso Australia Resources Ltd v FCT [1999] HCA 67 — VERIFIED (worked record, 29 Jun session). Retro-fit quote blocks for uniformity when the worked record is recovered.

**Proposition 1 — AU-PURP-02**

> Rule text (verbatim from the engine):
> "A confidential communication brought into existence for the single articulated dominant purpose of use in adversarial litigation that was on foot or reasonably anticipated."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 2 — AU-CONF-05**

> Rule text (verbatim from the engine):
> "It is recorded that the communication was not confidential. Confidentiality is an element of the privilege."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 3 — AU-CONF-05**

> Rule text (verbatim from the engine):
> "Whether the communication was confidential is not recorded."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 4 — AU-PURP-01**

> Rule text (verbatim from the engine):
> "The litigation limb is asserted, but no litigation was on foot or reasonably anticipated at the date of the communication."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 5 — AU-PURP-01**

> Rule text (verbatim from the engine):
> "Whether litigation was on foot or reasonably anticipated at the date of the communication has not been established. A mere possibility of litigation is not enough."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 6 — AU-PURP-05**

> Rule text (verbatim from the engine):
> "It is recorded that the proceedings are not adversarial. Litigation privilege does not extend to material prepared for an investigative or inquisitorial process."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 7 — AU-PURP-05**

> Rule text (verbatim from the engine):
> "Whether the proceedings are adversarial is not recorded. An audit or regulatory information-gathering process is not, of itself, litigation."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 8 — AU-PURP-02**

> Rule text (verbatim from the engine):
> "More than one purpose is indicated. Which purpose was dominant is a matter of judgment on the whole of the evidence, not a mechanical determination."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 9 — AU-PURP-02**

> Rule text (verbatim from the engine):
> "Whether the communication served more than one purpose is not recorded."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 10 — AU-PURP-02**

> Rule text (verbatim from the engine):
> "No dominant purpose has been articulated."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 11 — AU-PURP-02**

> Rule text (verbatim from the engine):
> "The confidentiality element is not established on the record."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 12 — AU-PURP-02**

> Rule text (verbatim from the engine):
> "A confidential communication with a lawyer acting in a legal capacity, for the single articulated dominant purpose of obtaining or giving legal advice, with no conduct on the record inconsistent with maintaining confidentiality."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 13 — AU-PURP-02**

> Rule text (verbatim from the engine):
> "The litigation predicate is not fully established."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 14 — AU-CONF-05**

> Rule text (verbatim from the engine):
> "Marked confidential, but whether it was confidential in fact is not recorded. A marking is evidence of the element, not the element."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

**Proposition 15 — AU-PURP-02**

> Rule text (verbatim from the engine):
> "The purpose is not recorded as the giving or obtaining of legal advice."

Court (at [____], ______ J/JJ) [PRACTITIONER]:
> "____________________________________________"

Fit [PRACTITIONER]: ____________  — ____________________________________

Source read [PRACTITIONER]: ______________________________________________
Bench, as printed in the report [PRACTITIONER]: __________________________
Verified [PRACTITIONER]: ____ Jul 2026, by GJML
Notes / divergences [PRACTITIONER]: ______________________________________

---

## Claimant confirmation (unblocks the final export refusal)

Position, as it should read on the form [PRACTITIONER]: __________

Organisation, as it should read on the form [PRACTITIONER]: ______

Confirmed [PRACTITIONER]: ____ Jul 2026, by GJML

Then: edit DEFAULT_CLAIMANT in ajit_lpp/nat75447.py — remove both [CONFIRM] markers — run the gates, commit as "Claimant confirmed; final export refusal cleared".
