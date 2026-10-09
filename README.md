# fallacy_catalog

A plain, sourced catalog of named logical fallacies, for checking arguments against the standard list rather than a custom framework.

Each entry gives:

- the standard **name** and common **aliases** (Latin names included);
- a **category** (formal, or an informal type such as relevance, ambiguity, presumption, weak induction, causal, or statistical);
- a one- or two-sentence **definition** in plain words;
- a short **example**;
- the **required conditions** that must all be shown from the text before the label applies;
- **legitimate look-alikes**: reasonable arguments that look similar but are not the fallacy;
- whether it is **detectable from the text** alone, whether it is a **contested** name, and whether it is a broad **fallback** label;
- **related** entries to choose between, so one step gets one label;
- **sources**: the published references that list the fallacy, with the exact entry, section or chapter so anyone can check them.

The catalog currently has 215 entries. A further 12 names that describe the same mistake as another entry are folded into that entry as aliases and listed under "Names folded into other entries" in FALLACIES.md. The references are the *Internet Encyclopedia of Philosophy* and *Stanford Encyclopedia of Philosophy* articles on fallacies, Aristotle's *On Sophistical Refutations*, *The Fallacy Files*, and Wikipedia's *List of fallacies*. See [SOURCES.md](SOURCES.md).

## Files

| File | What it is |
|---|---|
| [`fallacies.json`](fallacies.json) | The catalog in machine-readable form. This is the source of truth. |
| [`FALLACIES.md`](FALLACIES.md) | The readable version, grouped by category and alphabetical within each category, with a table of contents. Generated from the JSON. |
| [`METHOD.md`](METHOD.md) | The procedure for checking an argument, with a false-positive check and two worked examples. |
| [`SOURCES.md`](SOURCES.md) | The references used and how they are cited. Generated from the JSON. |
| [`tools/build_md.py`](tools/build_md.py) | Validates the JSON and regenerates the two Markdown files. |

## How to use it to check an argument

Follow [METHOD.md](METHOD.md). In short: quote the exact passage; restate the argument in its strongest reasonable form; pick the single most specific entry; show the words that meet each required condition (if any condition is unmet, do not flag); say why each legitimate look-alike does not apply; treat entries that are not detectable from the text as questions only; and give a verdict of flag, possible issue or no issue. A second, independent reviewer should re-check each flag.

A fallacy flag is a judgment, not a verdict. The same words can be fallacious in one context and reasonable in another, and naming a fallacy in an argument does not show that its conclusion is false (that would be the [argument from fallacy](FALLACIES.md#argument-from-fallacy)). Treat every flag as a claim to be checked against the passage and the definition.

## Editing the catalog

Edit `fallacies.json`, then run:

```
python3 tools/build_md.py           # validate and regenerate FALLACIES.md and SOURCES.md
python3 tools/build_md.py --check   # validate and confirm the generated files are up to date
```

The validator checks that ids are unique and in kebab-case; that every entry has a name, category, definition and example; that every entry has 2 to 5 required conditions, a `text_detectable` value and a `status`; that related ids, families and redirect targets exist; that sourced look-alikes carry a complete citation; and that every entry has at least one source or is explicitly marked `"sources": "TODO"`.

Rules for sources:

- Cite only a reference you have actually opened and confirmed lists that fallacy, and give the specific entry, section or chapter.
- If you cannot confirm a source, set `"sources": "TODO"` rather than guessing.
- Write definitions and examples in your own words; do not copy long passages from the references.

### Entry fields

| Field | Meaning |
|---|---|
| `id` | Stable kebab-case identifier. |
| `name`, `aliases` | Standard name and other names in use, including Latin names and names folded in from merged entries. |
| `category` | Formal (general, propositional, syllogistic, quantifier and modal) or informal (relevance, ambiguity and language, presumption, weak induction, causal, statistical and probabilistic, dialogue and evasion). |
| `status` | `standard`, or `contested` for names that are disputed or not widely used. Say so if you use a contested entry. |
| `text_detectable` | `yes`: can be shown from the text. `partly`: needs at least one fact from outside the text. `no`: depends on motive, inner bias or outside facts; raise as a question only, never as a flag. |
| `use_only_if_nothing_more_specific` | `true` for broad fallback labels (such as non sequitur, false cause, formal fallacy). Use them only when no more specific entry fits. |
| `definition`, `example` | Plain-words definition and an original example. |
| `required_conditions` | 2 to 5 numbered conditions, all of which must be shown from the text before flagging. |
| `legitimate_lookalikes` | List of `{text, caveat_source}`. `caveat_source` is `"source"` (the caveat is stated in the cited reference, given in `source`) or `"catalog wording"` (the catalog's own guard note). |
| `families`, `related` | The use-only-one families the entry belongs to, and the other members of those families. Pick one per step. |
| `sources` | A list of `{ref, title, url, locator}` (with an optional `note`), or `"TODO"`. |

Top-level `families` lists each family with its rule for choosing; `redirects` lists names folded into other entries.

## License

MIT. See [LICENSE](LICENSE).

---

[github.com/neuresthetics](https://github.com/neuresthetics)
