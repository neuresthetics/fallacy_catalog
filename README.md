# fallacy_catalog

A plain, sourced catalog of named logical fallacies, for checking arguments against the standard list rather than a custom framework.

Each entry gives:

- the standard **name** and common **aliases** (Latin names included);
- a **category** (formal, or an informal type such as relevance, ambiguity, presumption, weak induction, causal, or statistical);
- a one- or two-sentence **definition** in plain words;
- a short **example**;
- where it applies, a **"not a fallacy when"** note, because many of these patterns are reasonable in the right circumstances;
- **sources**: the published references that list the fallacy, with the exact entry, section or chapter so anyone can check them.

The catalog currently has 228 entries. The references are the *Internet Encyclopedia of Philosophy* and *Stanford Encyclopedia of Philosophy* articles on fallacies, Aristotle's *On Sophistical Refutations*, *The Fallacy Files*, and Wikipedia's *List of fallacies*. See [SOURCES.md](SOURCES.md).

## Files

| File | What it is |
|---|---|
| [`fallacies.json`](fallacies.json) | The catalog in machine-readable form. This is the source of truth. |
| [`FALLACIES.md`](FALLACIES.md) | The readable version, grouped by category and alphabetical within each category, with a table of contents. Generated from the JSON. |
| [`SOURCES.md`](SOURCES.md) | The references used and how they are cited. Generated from the JSON. |
| [`tools/build_md.py`](tools/build_md.py) | Validates the JSON and regenerates the two Markdown files. |

## How to use it to check an argument

1. **Quote the passage.** Copy the exact words you think go wrong, with enough context that the reader can see what the speaker meant.
2. **Name the fallacy.** Find the closest entry in [FALLACIES.md](FALLACIES.md) and use its standard name.
3. **Say why it fits.** Show how the passage matches the definition: which premise, which step, which word shifts meaning, or which evidence is missing.
4. **Check the "not a fallacy when" note.** Many patterns are legitimate in some settings. Citing a genuine expert in their field is not a fallacious appeal to authority. A slippery-slope warning is fair when each step is actually likely. If the exception applies, it is not a fallacy.
5. **Point to the source.** Link the entry, or its listed reference, so the reader can check the definition for themselves.

A fallacy flag is a judgment, not a verdict. The same words can be fallacious in one context and reasonable in another, and naming a fallacy in an argument does not show that its conclusion is false (that would be the [argument from fallacy](FALLACIES.md#argument-from-fallacy)). Treat every flag as a claim to be checked against the passage and the definition.

## Editing the catalog

Edit `fallacies.json`, then run:

```
python3 tools/build_md.py           # validate and regenerate FALLACIES.md and SOURCES.md
python3 tools/build_md.py --check   # validate and confirm the generated files are up to date
```

The validator checks that ids are unique and in kebab-case, that every entry has a name, category, definition and example, and that every entry has at least one source or is explicitly marked `"sources": "TODO"`.

Rules for sources:

- Cite only a reference you have actually opened and confirmed lists that fallacy, and give the specific entry, section or chapter.
- If you cannot confirm a source, set `"sources": "TODO"` rather than guessing.
- Write definitions and examples in your own words; do not copy long passages from the references.

Entry fields: `id`, `name`, `aliases`, `category`, `definition`, `example`, `not_a_fallacy_when` (text or `null`), and `sources` (a list of `{ref, title, url, locator}` or `"TODO"`).

## License

MIT. See [LICENSE](LICENSE).

---

[github.com/neuresthetics](https://github.com/neuresthetics)
