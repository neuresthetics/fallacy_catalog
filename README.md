# fallacy_catalog

A catalog of 221 named logical fallacies, with sources, and a written procedure for checking an argument against it. It is meant for analysing real arguments, so most of its design is about avoiding false accusations.

Current version: **0.6.1**.

## What it is and what it isn't

**It is:**
- A list of standard fallacy names. Each entry has a plain definition, an example, the conditions that must all be shown from the text before the label applies, the legitimate arguments that look similar but are not the fallacy, and the published references that list it.
- A procedure ([METHOD.md](METHOD.md)) for applying the list one argument step at a time, with explicit rules for when *not* to flag.
- A record of how the catalog was audited and tested, with all the test data ([tests/](tests/)).

**It isn't:**
- A judgement that a conclusion is false. A fallacy flag says that one step does not support its conclusion. The conclusion may still be true, and inferring otherwise is itself a fallacy ([argument from fallacy](FALLACIES.md#argument-from-fallacy)).
- A complete theory of argument. It does not grade evidence quality in general, check facts, or score how persuasive an argument is.
- Validated by human experts. All review so far has been done by AI models (see [Limitations](#limitations)).

## Files

| File | What it is |
|---|---|
| [`fallacies.json`](fallacies.json) | The catalog in machine-readable form. This is the source of truth. |
| [`FALLACIES.md`](FALLACIES.md) | Readable version, grouped by category and alphabetical within each category. Generated from the JSON. |
| [`METHOD.md`](METHOD.md) | The procedure for checking an argument, with worked examples. |
| [`IDEA_DETECTION.md`](IDEA_DETECTION.md) | Idea-level checker: an extractor may propose an Idea IR; only the deterministic checker verdicts. Pilot patterns, not a new catalog. |
| [`idea_detection/DEV_PROCESS.md`](idea_detection/DEV_PROCESS.md) | How that checker is designed, tested on fixtures, scored on the held-out rounds, and extended. |
| [`SOURCES.md`](SOURCES.md) | The references and how they are cited. Generated from the JSON. |
| [`tools/build_md.py`](tools/build_md.py) | Validates the JSON and regenerates the two generated Markdown files. |
| [`frameworks/`](frameworks/) | Sourced reference frameworks kept separate from the fallacy list, currently MINDSPACE (Dolan et al. 2010) for detecting persuasion levers. Not part of the audit method; see the folder README. |
| [`tests/`](tests/) | Audits, blind test rounds, answer keys, reviewer verdicts, scores, scoring scripts and regression checks. |

## How the entries were produced

### Sources

Every entry cites at least one published reference that lists the fallacy. No entry in v0.6.1 is unsourced. The references are:
- the *Internet Encyclopedia of Philosophy* (IEP) article "Fallacies", section 6 (its alphabetical list);
- the *Stanford Encyclopedia of Philosophy* (SEP) article "Fallacies";
- Aristotle, *On Sophistical Refutations* (MIT Internet Classics Archive text);
- *The Fallacy Files* (individual entry pages);
- Wikipedia, "List of fallacies";
- for some later entries: the SEP entries "Simpson's Paradox" and "Fatalism", individual Wikipedia articles (for example "Confusion of the inverse", "Parable of the broken window", "Modal fallacy"), and Bastiat's essay "What Is Seen and What Is Not Seen".

[SOURCES.md](SOURCES.md) gives each reference with its URL and access date. Each citation in an entry names the exact entry, section, list item or chapter, so anyone can check it.

### How each citation was checked

- **The page was fetched, not recalled.** Each reference page was downloaded, and each citation was matched to a specific heading, list item or chapter in the downloaded copy. A citation was written only if the page listed that fallacy. When no page could be confirmed, the entry was marked `TODO` rather than given a guessed source. Two entries added in v0.6.0 (appeal to inevitability and appeal to sincerity) were dropped in v0.6.1 because no citable reference listing either as a fallacy could be found.
- **For the pages added in v0.5.0 and v0.6.0, the check was scripted.** The script that wrote each new citation first asserted that specific phrases from the definition occur in the fetched page, and stopped if any were missing. These one-off build scripts are not part of the repository; the resulting citations are in `fallacies.json`.
- **Every citation was re-checked by an independent audit.** Audit run 1 compared all citations in v0.1.0 with the cached pages (see [tests/audit/SUMMARY.md](tests/audit/SUMMARY.md)). It found no entry whose source lacked the fallacy outright, but it found mismatches: a "see X" cross-reference cited as if it described the entry, a modern sense attributed to Aristotle, and a Wikipedia one-liner paraphrased past what it says. These were re-cited, annotated or removed.
- Definitions and examples are written in the catalog's own words, and long passages are not copied. The downloaded pages are not included in this repository, but the URLs and locators are.

### `caveat_source`: whose caveat is it?

Each legitimate look-alike carries a `caveat_source`:
- `source`: the caveat is stated in a cited reference, and the specific reference and locator are given with it. Audit run 2 checked every caveat marked `source` against its reference. Seven did not match, and they were re-cited or downgraded.
- `catalog wording`: the catalog's own guard note, written to prevent a false positive. It is not claimed to come from any reference.

### `status`: standard or contested

- `standard` (209 entries): a name used in the references for a recognised error.
- `contested` (12 entries): the name is disputed, used by only one source, or describes something whose status as a fallacy is debated (for example motte-and-bailey and the hot-hand fallacy). If you use a contested entry, say so.

This is separate from the per-row "contested reading" in METHOD.md, which marks a *passage* whose fallacy charge is disputed in the scholarly literature (for example Mill's "proof" of utility).

### Other fields

| Field | Meaning |
|---|---|
| `id` | Stable kebab-case identifier. |
| `name`, `aliases` | Standard name and other names in use, including Latin names and names folded in from merged entries. |
| `category` | Formal (general, propositional, syllogistic, quantifier and modal) or informal (relevance, ambiguity and language, presumption, weak induction, causal, statistical and probabilistic, dialogue and evasion). |
| `text_detectable` | `yes` (174 entries): can be shown from the text. `partly` (43): at least one condition may need a fact from outside the text. `no` (4: confirmation bias, selective attention, availability heuristic, rationalization): depends on motive or inner bias, so it may be raised as a question but never flagged. |
| `outside_text_conditions` | Which numbered conditions may need facts from outside the passage. Such a condition is met only if the passage states the fact or it is common knowledge; otherwise the verdict is at most "possible issue". |
| `use_only_if_nothing_more_specific` | `true` for 11 broad fallback labels (such as non sequitur, false cause and formal fallacy). Use them only when no specific entry fits. |
| `definition`, `example` | Plain-words definition and an original example. |
| `required_conditions` | 2 to 5 numbered conditions. All must be shown before flagging. |
| `legitimate_lookalikes` | Reasonable arguments that resemble the fallacy, as `{text, caveat_source}`. |
| `families`, `related` | "Use only one" families (35 in all), each with a rule for choosing between members, so one step gets one label. |
| `sources` | `{ref, title, url, locator}` (optional `note`). The validator also accepts `"TODO"` for an entry under construction; none is in the released catalog. |

The top-level `redirects` list holds 12 names folded into other entries.

## How to check an argument

Follow [METHOD.md](METHOD.md). In outline, for each step of an argument:

1. Quote the exact words.
2. Restate the argument in its strongest reasonable form. Read hedges as hedges, supply common-knowledge premises, treat stated defaults (burden of proof, presumption of innocence) as defaults, and respect the conclusion's scope.
3. Pick the single most specific entry, following the family and cross-family tie-breaks.
4. Show the words that meet each required condition. If any condition is unmet, do not flag.
5. Rule out each legitimate look-alike.
6. Handle conditions that may need outside facts.
7. Give a verdict: **flag**, **possible issue** (say what would settle it) or **no issue**.

### Idea-level checker

[IDEA_DETECTION.md](IDEA_DETECTION.md) is the machine-checkable companion to this procedure. An extractor may propose an Idea IR (claims, support edges, quoted spans). A deterministic checker matches pilot `ir_pattern` / `ir_forbid` entries and is the only component that emits **flag**, **possible issue**, or **no issue**. It does not replace METHOD, does not add fallacy names, and does not consult MINDSPACE. Patterns stay in a side file; they are not merged into `fallacies.json`.

The development loop for that layer — design, refine from a run, implement, fixture tests, held-out scoring, miss taxonomy, next pilot — is [idea_detection/DEV_PROCESS.md](idea_detection/DEV_PROCESS.md). Bulk full-detail output is `python3 -m idea_detection --method-record <folder-of-irs>/`: one METHOD-shaped record per flag or possible issue (entry, quotes, conditions, look-alikes). It is an assist from the checker, not a hand METHOD review, and it does not emit a flag for a `no_issue` passage. Thirteen pilots are in the side file (the original eight, plus hasty generalization, slippery slope, false dilemma, appeal to the people, and guilt by association). Charity forbids stay in place: a weak hedge, a procedural default, a precaution, and a testimony or relevance look-alike are not bought back as recall. [METHOD.md](METHOD.md) remains the procedure for hand audits, including Genius Study audits.

Held-out scoring uses `python3 -m idea_detection.score_eval` on a results CSV. A flag on legit or no-argument is the false-positive gate. A `possible_issue` under the wrong name is `wrong_possible`, not a hit. Misses split into `expected_outside`, `expected_charity`, `ir_gap`, `pattern_gap`, and `contested_stay`. Genetic fallacy, bulverism, ad hoc rescue, and special pleading are inside coverage only if those ids are pilots. Guilt by association is a pilot; its name does not count as ad hominem. The eight-pilot N=398 totals (58 hits, 0 false positives, 0 failures) are in [idea_detection/E2E_SUMMARY.md](idea_detection/E2E_SUMMARY.md). They predate the five added pilots.

### False-positive controls

The procedure is built to avoid accusing a sound argument. Each control below was added or tightened because an audit or test showed it was needed.
- **Required conditions.** A label applies only if every numbered condition is shown from the passage's own words. Resemblance is not enough.
- **Look-alike rule-out.** Each entry lists the legitimate arguments that look like it, such as questioning a paid witness's reliability, a negotiated compromise, or a precaution under uncertainty. The reviewer must say why each one does not apply. A look-alike downgrades a flag only if the passage, or common knowledge, supplies its features.
- **Outside-text conditions.** Where a condition depends on facts that are not in the passage (what a study did, how common something is), the verdict is at most "possible issue" unless the passage states the fact or it is common knowledge. Bias and motive entries are never flagged.
- **Reported arguments and no-argument passages.** A passage that reports, teaches, reviews or quotes someone else's fallacy, or makes no argument at all, gets "no issue", and the displayed fallacy is recorded under `reported_fallacy`. In a dialogue, each participant who advances an argument is scored separately. Correctly naming a fallacy, or a fair reduction to absurdity, is no issue.
- **Real texts.** In an excerpt, a condition that fails only because the support may lie past the excerpt's end gives at most "possible issue". A famous argument whose fallacy charge is disputed in the scholarly literature is marked "contested reading" and given "possible issue" unless its words settle the matter.
- **Not everything is a fallacy.** Invective and charged wording that no inference rests on go in "rhetorical notes". Arithmetic and factual slips go in "other errors". Neither changes the verdict.
- **The "possible issue" verdict.** Doubtful cases are not forced into flag or no issue. They are reported with the fact that would settle them.
- **Specificity and one label per step.** Fallback labels are used only when nothing specific fits. Labels from the same family are not stacked.
- **A blind second reviewer.** A second reviewer, who has not seen the first reviewer's verdicts, re-checks every flag. Only flags both agree on are reported as flags; disagreements become "possible issue".

## Build history

| Version | Commit | Entries | What changed |
|---|---|---|---|
| 0.1.0 | ae96f20 | 228 | First catalog: names, definitions, examples, sourced from the five references above. |
| 0.2.0 | 91dc7db | 215 | **Independent audit run 1** of all 228 entries: 110 OK, 103 FIX, 12 MERGE, 3 DROP. Fixes applied, 12 merges (kept as aliases and redirects), 3 drops, and 2 additions (separate Aristotle-sense entries for accident and non-cause). Added required conditions, look-alikes, detectability, status, fallback flags, use-only-one families, and METHOD.md. |
| 0.3.0 | df075a2 | 215 | **Independent audit run 2**: 113 of 118 run-1 rows resolved and 5 partly resolved; 49 issues in the new fields (2 High, 20 Medium, 27 Low); 7 mis-attributed `source` caveats corrected; wording fixes from a 78-passage false-positive test; METHOD step (b) made concrete. |
| 0.4.0 | ccc9a6f | 216 | **Blind test round 1** fixes: the per-condition `outside_text_conditions` field and METHOD step (f); new cherry-picking entry and selective-evidence tie-break; middle ground, slippery slope and other condition fixes; tie-breaks and reporting rules. |
| 0.5.0 | 347a415, 46e8036 | 220 | **Blind test round 2** fixes: defaults vs precaution; new entries confusion of the inverse, Simpson's paradox, statistical vs practical significance, and relative vs absolute risk framing; causation and nature tie-breaks; "other errors" note. Two tie-break fixes from the non-blind regression check. |
| 0.6.0 | deb6e75, e369e78 | 223 | **Blind test round 3** fixes: rules for dialogues, real excerpts, contested readings and rhetorical notes; new entries appeal to inevitability, appeal to sincerity and broken window fallacy; condition or look-alike changes to 16 entries; three fixes from the regression check. |
| 0.6.1 | (this release) | 221 | Dropped the two v0.6.0 entries that had no citable source (appeal to inevitability, appeal to sincerity) and removed every reference to them. Passages of those kinds now route to sourced entries: "unavoidable or already here, so good" with no value premise to is-ought (as in R084, with appeal to nature for its "survival of the fittest" step); "poor, so no reason to lie, so true" to appeal to poverty (as in R023). Neither move has a dedicated entry, which is a known gap. |

Details: [tests/audit/SUMMARY.md](tests/audit/SUMMARY.md) and each round's `FIXES.md`.

## Testing

The catalog was produced and tested by the audit and blind-round protocol below. The idea-level checker is a separate loop: fixture tests in `tests/idea_detection/`, and a held-out score that reads the same passage files. Both are summarized here; the checker loop is written out in [idea_detection/DEV_PROCESS.md](idea_detection/DEV_PROCESS.md).

### Protocol

1. **Held-out passages.** For each round, a separate model instance, barred from reading the catalog, wrote a new set of passages and an answer key. The passages are a mix of legitimate arguments (many built to resemble common fallacies), fallacies, borderline cases (round 1), passages with no argument (rounds 2–3), and passages that contain both a sound argument and an error (round 3). Round 3 includes 20 real public-domain excerpts (Darwin, Mill, Paine, Hume, Lincoln, Douglass, Plato and others).
2. **Two blind reviewers.** Two model instances applied the catalog and METHOD.md to the passages without seeing the key or each other's work. From round 2 on, one reviewer was told to apply every rule strictly and literally, and the other to apply the method as a practical analyst would. Each verdict records the evidence for every condition and the look-alikes ruled out.
3. **Scoring with adjudication.** A scorer compared both reviewers with the key and traced every error to its cause: the catalog, a reviewer, or the key. The scorer could overrule the key only with a stated reason. Results are reported both "as keyed" and adjudicated, and every overrule is recorded in the answer key's `original_key` and `overrule_reason` columns.
4. **Fixes, then a regression check.** The catalog was revised in response, and the builder re-applied the method to the affected earlier passages. This check is **not blind**: the builder had the keys in view.

### Results

Numbers below are copied from the score files ([round 1](tests/round1/scores.md), [round 2](tests/round2/scores.md), [round 3](tests/round3/scores.md)). Where two values are given, they are the two reviewers. "Hard FP" means a flag on a legitimate or no-argument passage. "Soft FP" means a possible issue on one. A soft miss is a possible issue on a keyed fallacy, and a hard miss is no issue on one.

| | Round 1 | Round 2 | Round 3 |
|---|---|---|---|
| Catalog version (commit) | v0.3.0 (df075a2) | v0.4.0 (ccc9a6f) | v0.5.0 (46e8036) |
| Entries | 215 | 216 | 220 |
| Reviewers | A, B (same style) | C strict, D practical | E strict, F practical |
| Passages | 120 | 100 | 100 (114 / 108 rows) |
| Mix | 50 legit, 50 fallacy, 20 borderline | 40 legit, 20 no-argument, 40 fallacy | 43 legit, 11 no-argument, 35 fallacy, 11 mixed; 20 real excerpts |
| Hard FP on legit + no-argument | 0/50, 0/50 | 0/60, 0/60 | 0/54, 0/54 |
| Soft FP on legit + no-argument | 0, 0 | 0, 0 | 0, 0 |
| Fallacy hit with acceptable label | 50/50, 49/50 | 35/40, 38/40 | 31/35, 30/35 (as keyed) |
| Wrong label | 0, 1 | 1, 0 | 2, 1 |
| Soft miss (as keyed) | 0, 0 | 4, 2 | 1, 4 |
| Hard miss (as keyed) | 0, 0 | 0, 0 | 1, 0 |
| Misses after key adjudication | 0, 0 | 3, 1 (Q012 both; Q010 and Q050 C only) * | 1, 2 |
| Mixed: error units found | n/a | n/a | 11/14, 11/14 as keyed; 10/12, 11/12 adjudicated |
| Borderline matching the key | 19/20, 20/20 (lenient) | n/a | n/a |
| Passage verdict agreement | 119/120 (κ 0.985) | 98/100 (κ 0.960) | 95/100 (κ 0.903) |
| Label agreement on joint flags or steps | 51/52 (98%) | 33/36 (92%) | 48/51 (94%) |
| Key errors found | 6 | 5 | 6 (R021, R040, R041, R063, R092, R082) |

\* Round 2, after adjudication: Q014 was overruled to possible issue for both reviewers. Q012 stayed a soft miss for both. Q010 and Q050 were soft misses for C only.

In all three rounds, no legitimate or no-argument passage was flagged or given a possible issue by either reviewer: 0 of 328 reviewer judgments. Misses fell as fixes landed, then appeared in new places each round. Agreement between reviewers fell as the material became more realistic: in round 3, 4 of the 5 passage-level disagreements were real excerpts.

**Regression check for v0.6.0 (non-blind):** 159 earlier passages were re-checked against the adjudicated keys, including all 20 real excerpts. Three problems were found and fixed before commit: two gaps in the new rules (a quoted exercise or review would have been scored as an argument; no routing between appeal to poverty and appeal to sincerity) and one mismatch carried over from v0.5.0 (P097). That check referred to two entries since dropped in v0.6.1; R023 now routes to appeal to poverty (the keyed label) and R084 to is-ought and appeal to nature (both keyed), as noted in the file. See [tests/regression/regression_v060.md](tests/regression/regression_v060.md). v0.6.x has not yet had a blind round.

### Idea-level checker

Fixture tests and `python3 -m idea_detection.eval_fixtures` cover the METHOD examples and the pilot look-alikes. They do not replace the blind rounds above.

One held-out machine run scored all 398 passages in round 1, round 2, round 3, and `tests/audit/fp_test_passages.csv` against the original eight pilots: 58 hits, 0 false positives, 0 extractor failures. Totals, and the miss labels from the review of that run, are in [idea_detection/E2E_SUMMARY.md](idea_detection/E2E_SUMMARY.md). The five pilots added later are not in that table. A local re-run writes its IR dump and results CSV under `tmp/` and scores them with `python3 -m idea_detection.score_eval`. That extract is not part of CI.

## Limitations

- **The reviewers are not independent of each other.** The set writers, reviewers, scorers and auditors are all AI model instances from the same model family, and the same family built the catalog. They probably share blind spots. Round 1's two reviewers agreed on 119 of 120 verdicts and gave the same six possible issues, which the round-1 scorer judged to be consistency of the setup rather than two independent judgments. Later rounds used a strict and a practical reviewer to pull the two apart.
- **Most test passages are model-written.** Only the 20 round-3 excerpts are real texts. Constructed passages tend to be cleaner than real arguments, and on real texts agreement was lower.
- **The scorer adjudicated the key.** The scorer changed 18 answer-key rows across the three rounds (17 corrections and 1 clarified reason), usually towards the reviewers' answer. The reasons are recorded, and the "as keyed" numbers are reported alongside.
- **Regression checks are not blind.** The person who writes the fixes also checks them, with the keys in view. Each new version is only properly tested by the next blind round, and v0.6.x has not had one yet.
- **No human expert has validated the catalog or the test results.**
- **"Possible issue" is used.** The method prefers "possible issue" to a forced call. Reviewers gave it on 6 and 7 of 120 passages (round 1) and 4 and 2 of 100 (round 2). In round 3 they gave it on 5 of 114 and 7 of 108 rows, and it was the worst verdict on 1 and 4 of 100 passages. On keyed fallacies, a possible issue counts as a soft miss. A user who needs a yes/no answer must decide what to do with these cases.
- **Every entry has a published source; 0 are unsourced.** Two candidate entries (appeal to inevitability, appeal to sincerity) were dropped for lack of a citable source, so those moves have no dedicated entry and are handled by the nearest sourced entry (is-ought, appeal to poverty).
- **Coverage is not exhaustive.** No list of fallacies is complete. Errors outside the catalog get "no issue" from the catalog even when the reasoning is poor, and are at best noted as "weak premise".

## Reproducing

Validate the catalog and confirm that the generated files are up to date:

```
python3 tools/build_md.py --check
```

Regenerate FALLACIES.md and SOURCES.md after editing fallacies.json:

```
python3 tools/build_md.py
```

Recompute each round's scores from the reviewer verdicts and answer key (run from the repository root; Python 3 standard library only):

```
python3 tests/round1/score.py
```

```
python3 tests/round2/score.py
```

```
python3 tests/round3/score.py
```

Check the idea-level fixtures (METHOD example 1 flags `ad-hominem`; example 2 is `no_issue` on `appeal-to-authority`):

```
python3 -m idea_detection.eval_fixtures
```

```
python3 -m unittest tests/idea_detection/test_checker.py
```

```
python3 -m unittest tests/idea_detection/test_score_eval.py
```

Score a held-out results CSV (columns `id`, `truth`, `acceptable`, `flagged`, `possible`, optional `miss_class`):

```
python3 -m idea_detection.score_eval idea_detection/examples/score_eval_example.csv
```

Confirm that the recomputed scores match the committed ones:

```
git diff --stat tests/
```

To re-run a blind test, give a reviewer only `fallacies.json`, `FALLACIES.md`, `METHOD.md`, this README and a round's `passages.csv`, and compare their verdicts with `answer_key.csv`.

## Editing the catalog

Edit `fallacies.json`, then run `python3 tools/build_md.py`. The validator checks that ids are unique kebab-case; that every entry has a name, category, definition, example, status and 2 to 5 required conditions; that `text_detectable` agrees with `outside_text_conditions`; that related ids, family members and redirect targets exist; that look-alikes marked `source` carry a complete citation; and that every entry has a source or is marked `TODO`.

Rules for sources:
- Cite only a reference you have opened and confirmed lists that fallacy, with the specific entry, section or chapter.
- If you cannot confirm a source, use `"sources": "TODO"`.
- Write definitions and examples in your own words.

## How to cite and use

When you report a flag made with this catalog, give the entry id and the catalog version (for example `straw-man`, fallacy_catalog v0.6.1), quote the passage, and show the conditions and look-alikes as in METHOD.md's record format. Report contested entries and contested readings as such.

To cite the catalog: neuresthetics, *fallacy_catalog: a sourced catalog of logical fallacies with a false-positive-controlled checking method*, version 0.6.1, 2026.

## License

MIT. See [LICENSE](LICENSE).

---

[github.com/neuresthetics](https://github.com/neuresthetics)
