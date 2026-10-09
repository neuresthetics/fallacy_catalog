# Independent audits of the catalog

Before any blind testing, the catalog was audited twice by a separate model instance that had not written it. The auditor read the catalog and the cached source pages it cites, and edited nothing. The builder then applied the findings, and recorded any it disagreed with.

## Audit run 1 (v0.1.0, 228 entries)

Every entry was checked against the source pages it cites: the *Internet Encyclopedia of Philosophy* "Fallacies" article (section 6), the *Stanford Encyclopedia of Philosophy* "Fallacies" article (sections 1–2), Aristotle's *On Sophistical Refutations* (MIT Internet Classics text), Wikipedia's "List of fallacies", and 93 *Fallacy Files* pages. Per-entry results: [audit_run1.csv](audit_run1.csv) (columns: id, verdict, issue_type, specific_problem, proposed_corrected_text, evidence).

| Verdict | Entries |
|---|---:|
| OK | 110 |
| FIX | 103 |
| MERGE | 12 |
| DROP | 3 |
| **Total** | **228** |

No entry cited a source that lacked the named fallacy outright. The source problems were mismatches: the page existed but said something different, or was only a "see X" cross-reference.

**What the 103 FIX rows were about.** One row can raise more than one kind of problem, so these counts add up to more than 103. The grouping of the auditor's `issue_type` labels is ours.

| Problem | FIX rows |
|---|---:|
| A legitimate exception or caveat was missing (including 3 that the source itself states) | 44 |
| Duplicate of, or overlap with, another entry | 35 |
| Definition or name too broad (would fit almost any argument) | 18 |
| Source problem (citation mismatch, overclaim, or a cross-reference used as a description) | 13 |
| Alias problem (an alias that widens the label or collides with another entry) | 10 |
| Wrong category | 9 |
| Definition wording | 5 |
| Name disputed or not standard | 5 |
| Wrong or incomplete example | 4 |
| A cognitive bias or non-argument listed as a fallacy | 4 |
| Needs outside evidence to apply | 1 |

**MERGE (12):** ambiguous middle, bad seed, circular reasoning, definist fallacy, faulty comparison, illicit process, masked man, opposition, self-selection, slanting, smear tactic, vested interest. Each was folded into the entry describing the same mistake and kept as an alias, with a redirect.

**DROP (3):** hyperbolic discounting and lying (not fallacies of reasoning), and questionable premise (too broad: the *IEP* itself calls it a broad category).

The auditor's main recommendations were to mark catch-all labels (non sequitur, false cause, formal fallacy and similar) as fallbacks to be used only when nothing more specific fits; to add "use only one" families for clusters that name the same move; to restore exceptions that the sources state; and to require, before any flag, a quote, a condition-by-condition mapping to the text, an exception check and a specificity check. Version 0.2.0 implemented these as the `required_conditions`, `legitimate_lookalikes`, `use_only_if_nothing_more_specific` and `families` fields and METHOD.md. It also added two entries, leaving 215.

## Audit run 2 (v0.2.0, 215 entries)

The second audit checked whether run 1 had been resolved, ruled on the builder's disagreements, and audited the new fields. Per-entry results: [audit_run2.csv](audit_run2.csv) (230 rows: 215 entries plus 15 removed ids).

- **Run-1 resolution:** of 118 FIX, MERGE and DROP rows, 113 were resolved and 5 partly resolved. None was unresolved.
- **The builder's 5 disagreements with run 1:** the auditor accepted 4. On the fifth (keeping both argument from repetition and proof by assertion), it accepted the decision in principle but required the conditions to be rewritten so that the two entries no longer overlapped. The auditor also corrected one of its own run-1 recommendations: the Wikipedia element "lack of objection as evidence" should have been kept.
- **New fields:** 48 entries had 49 issues (2 High, 20 Medium, 27 Low). These included 7 look-alike caveats marked `caveat_source: source` whose wording was not in the cited source. They were re-cited to the right entry, or downgraded to `catalog wording`.
- **False-positive test (written and judged by the auditor, not blind):** 78 passages, 40 legitimate arguments built to resemble the most over-applied entries and 38 fallacies. Results: 0 hard false positives, 3 soft (possible issue on a legitimate passage), 34 of 38 fallacies flagged with an acceptable label, 4 soft misses, 0 hard misses. Every soft error was traced to a specific condition. The proposed wording fixes were applied in v0.3.0. Passages and results: [fp_test_passages.csv](fp_test_passages.csv), [fp_test_results.csv](fp_test_results.csv).

The auditor's own caveat on that test: it wrote the passages, the ground truth and the verdicts itself, knowing where the catalog was weak, so the test checks consistency, not independent validity.
