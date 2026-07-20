# Golden set — reconstruction note, 20 Jul 2026

## Provenance of this worklist

`privilege_goldenset_AU_ch3_worklist.csv` was reconstructed on 20 Jul 2026
from the 25 Jun 2026 conversation record, because the original file was never
downloaded from that conversation's outputs. The 15 case rows (id, citation,
limb, edge_tested) were recovered verbatim from the retrieved text of the
original `make_ch3_template.py`. One repair: row AU-C3-10's limb field was
truncated in retrieval and is restored as `legal_advice`, consistent with its
edge (who_is_a_lawyer / independent_advice — Kennedy v Wallace).

All fill-in fields are blank and all provenance flags reset, exactly as the
original template had them.

## The 29 Jun session went further than this worklist — read before drafting

A later conversation ("Privilege and Esso continuation", 29 Jun 2026) produced
a **fully worked Esso record**, verified against the High Court's own copy of
[1999] HCA 67 (`primary_source_checked: yes`, `own_words_confirmed: yes`,
`expert_validated: pending`), with pinpoints. That work must not be redone from
scratch — recover it from that chat's outputs if they still download, or at
minimum honour its three architectural findings:

1. **Rule vs validation (circularity).** Esso states the rule the engine
   encodes. Scoring the engine against Esso is testing it against its own
   operative proposition. Recommendation from that session: add a
   `record_type {rule | determination}` field; rule-statement authorities
   (Esso, Spotless on the meaning of "dominant") live in the rule module as
   binding sources; the validation harness scores only
   `record_type=determination` rows. **[ADOPTED: James, 20 Jul 2026.]**
   AU-C3-01 and AU-C3-09 are tagged `record_type=rule` in their notes field
   (AU-C3-01's tag to be applied when the worked Esso record lands); the
   dedicated column comes later with the harness, which scores the other
   thirteen.

2. **Grant v Downs handling.** The sole-purpose *test* is displaced, but the
   document *result* survives — the multi-purpose internal incident reports
   fail the dominant purpose test too (Esso [38], [60]). Discard the test,
   keep the outcome: `not_privileged`, edge = multi-purpose internal corporate
   reports. This is already encoded in AU-C3-02's edge note.

3. **"Overruled" precision.** The Esso joint judgment does not overrule Grant
   v Downs; it declines to follow the sole-vs-dominant point, which was never
   argued in Grant. Draft holdings must not say "overruled".

## Standing disciplines (unchanged)

- Judgments from the issuing courts or authorised reports; AustLII prohibited.
- Desiatnik is a guide, never content. The extracted-cases JSON is quarantined
  in `reference/` and must not be consulted for drafting.
- Holdings in own words, from the judgment.
- Every row stays `expert_validated: pending` until expert-verified.
- First-pass drafts (D-02 option A): drafted from legal knowledge, flagged
  UNCERTAIN where confidence is lacking; James flips `primary_source_checked`
  and `own_words_confirmed` only after reading the judgment himself.
