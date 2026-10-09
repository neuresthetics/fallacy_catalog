#!/usr/bin/env python3
"""Validate fallacies.json and regenerate FALLACIES.md and SOURCES.md from it.

Usage:
    python3 tools/build_md.py           # validate, then rewrite FALLACIES.md and SOURCES.md
    python3 tools/build_md.py --check   # validate and fail if the generated files are out of date

fallacies.json is the source of truth. Do not edit FALLACIES.md or SOURCES.md by hand.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "fallacies.json"
MD_PATH = ROOT / "FALLACIES.md"
SOURCES_PATH = ROOT / "SOURCES.md"

CATEGORY_ORDER = [
    "formal: general",
    "formal: propositional",
    "formal: syllogistic",
    "formal: quantifier and modal",
    "informal: relevance",
    "informal: ambiguity and language",
    "informal: presumption",
    "informal: weak induction",
    "informal: causal",
    "informal: statistical and probabilistic",
    "informal: dialogue and evasion",
]
REQUIRED = ["id", "name", "aliases", "category", "definition", "example", "not_a_fallacy_when", "sources"]
SOURCE_FIELDS = ["ref", "title", "url", "locator"]
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate(doc):
    errors = []
    entries = doc.get("entries")
    if not isinstance(entries, list) or not entries:
        return ["'entries' must be a non-empty list"]
    refs = {r.get("ref") for r in doc.get("references", [])}
    seen = Counter(e.get("id") for e in entries)
    for dup, n in seen.items():
        if n > 1:
            errors.append(f"duplicate id: {dup}")
    for i, e in enumerate(entries):
        eid = e.get("id", f"#{i}")
        for f in REQUIRED:
            if f not in e:
                errors.append(f"{eid}: missing field '{f}'")
        if not ID_RE.match(str(e.get("id", ""))):
            errors.append(f"{eid}: id must be kebab-case")
        for f in ("name", "definition", "example"):
            if not str(e.get(f) or "").strip():
                errors.append(f"{eid}: empty '{f}'")
        if not isinstance(e.get("aliases"), list):
            errors.append(f"{eid}: 'aliases' must be a list")
        if e.get("category") not in CATEGORY_ORDER:
            errors.append(f"{eid}: unknown category '{e.get('category')}'")
        nf = e.get("not_a_fallacy_when")
        if nf is not None and not str(nf).strip():
            errors.append(f"{eid}: 'not_a_fallacy_when' must be null or non-empty text")
        src = e.get("sources")
        if src == "TODO":
            continue
        if not isinstance(src, list) or not src:
            errors.append(f"{eid}: 'sources' must be a non-empty list or the string \"TODO\"")
            continue
        for s in src:
            for f in SOURCE_FIELDS:
                if not str(s.get(f) or "").strip():
                    errors.append(f"{eid}: source missing '{f}'")
            if refs and s.get("ref") not in refs:
                errors.append(f"{eid}: source ref '{s.get('ref')}' is not in 'references'")
            if not str(s.get("url", "")).startswith("https://"):
                errors.append(f"{eid}: source url must be https")
    return errors


def anchor(text):
    a = re.sub(r"[^\w\- ]", "", text.lower()).strip()
    return re.sub(r"\s+", "-", a)


def md_escape(text):
    return str(text).replace("|", "\\|")


def render_fallacies(doc):
    entries = doc["entries"]
    by_cat = {c: [] for c in CATEGORY_ORDER}
    for e in entries:
        by_cat[e["category"]].append(e)
    for c in by_cat:
        by_cat[c].sort(key=lambda e: e["name"].lower())
    n_todo = sum(1 for e in entries if e["sources"] == "TODO")

    out = []
    out.append("# Fallacy Catalog\n")
    out.append("<!-- Generated from fallacies.json by tools/build_md.py. Do not edit by hand. -->\n")
    out.append(f"{len(entries)} named fallacies, grouped by category and listed alphabetically within each category. "
               f"{len(entries) - n_todo} entries have confirmed published sources; {n_todo} are marked TODO. "
               "See [SOURCES.md](SOURCES.md) for the references and [README.md](README.md) for how to use the catalog.\n")
    out.append("## Contents\n")
    out.append("| Category | Entries |\n|---|---:|")
    for c in CATEGORY_ORDER:
        if by_cat[c]:
            out.append(f"| [{c.capitalize()}](#{anchor(c)}) | {len(by_cat[c])} |")
    out.append("")
    for c in CATEGORY_ORDER:
        if not by_cat[c]:
            continue
        links = ", ".join(f"[{e['name']}](#{e['id']})" for e in by_cat[c])
        out.append(f"- **{c.capitalize()}**: {links}")
    out.append("")
    for c in CATEGORY_ORDER:
        if not by_cat[c]:
            continue
        out.append(f"## {c.capitalize()}\n")
        for e in by_cat[c]:
            out.append(f'<a id="{e["id"]}"></a>')
            out.append(f"### {e['name']}\n")
            if e["aliases"]:
                out.append(f"*Also called:* {', '.join(e['aliases'])}\n")
            out.append(f"{e['definition']}\n")
            out.append(f"**Example:** {e['example']}\n")
            if e.get("not_a_fallacy_when"):
                out.append(f"**Not a fallacy when:** {e['not_a_fallacy_when']}\n")
            if e["sources"] == "TODO":
                out.append("**Sources:** TODO (no confirmed published source yet)\n")
            else:
                out.append("**Sources:**\n")
                for s in e["sources"]:
                    out.append(f"- {s['title']}, {s['locator']}. <{s['url']}>")
                out.append("")
            out.append(f"`id: {e['id']}`\n")
    return "\n".join(out).rstrip() + "\n"


def render_sources(doc):
    entries = doc["entries"]
    counts = Counter()
    for e in entries:
        if e["sources"] != "TODO":
            for r in {s["ref"] for s in e["sources"]}:
                counts[r] += 1
    out = ["# Sources\n",
           "<!-- Generated from fallacies.json by tools/build_md.py. Do not edit by hand. -->\n",
           "Every source cited in the catalog is one of the references below. Each citation names the specific "
           "entry, section or chapter where the fallacy is listed, so a reader can check it. A citation was added "
           "only after the page was retrieved and the named entry, section or chapter was found to list that fallacy. "
           "An entry with no confirmed source is marked TODO instead of being given a guessed citation.\n",
           "The definitions and examples in the catalog are written in plain words for this catalog; they are not quotations from these references.\n",
           "| Reference | Link | Accessed | Entries citing it | How it is cited |",
           "|---|---|---|---:|---|"]
    for r in doc.get("references", []):
        out.append(f"| {md_escape(r['title'])} | <{r['url']}> | {r.get('accessed', '')} | {counts.get(r['ref'], 0)} | {md_escape(r.get('note', ''))} |")
    out.append("")
    out.append("## Notes on the references\n")
    out.append("- The Internet Encyclopedia of Philosophy (IEP) and Stanford Encyclopedia of Philosophy (SEP) are scholarly reference works written by philosophers. "
               "SEP Section 1 reviews the core fallacies that most logic textbooks share (following Irving Copi's *Introduction to Logic*), and Section 2 traces the list back to Aristotle, the Port-Royal Logic and Locke.")
    out.append("- Aristotle's *On Sophistical Refutations* is the original list of thirteen fallacies: six that depend on language (chapter 4) and seven that do not (chapters 4 and 5).")
    out.append("- *The Fallacy Files* is a long-running reference site on fallacies maintained by Gary N. Curtis, with one page per fallacy.")
    out.append("- Wikipedia's *List of fallacies* is used as a cross-check of common names; where a fallacy is listed only there, check the citations on that Wikipedia page before relying on it.")
    return "\n".join(out).rstrip() + "\n"


def main():
    check = "--check" in sys.argv[1:]
    doc = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    errors = validate(doc)
    if errors:
        print("Validation failed:")
        for e in errors:
            print("  -", e)
        return 1
    outputs = {MD_PATH: render_fallacies(doc), SOURCES_PATH: render_sources(doc)}
    stale = []
    for path, text in outputs.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != text:
            if check:
                stale.append(path.name)
            else:
                path.write_text(text, encoding="utf-8")
    entries = doc["entries"]
    n_todo = sum(1 for e in entries if e["sources"] == "TODO")
    print(f"OK: {len(entries)} entries, {len(entries) - n_todo} with sources, {n_todo} TODO")
    for c, n in sorted(Counter(e["category"] for e in entries).items(), key=lambda kv: CATEGORY_ORDER.index(kv[0])):
        print(f"  {c}: {n}")
    if stale:
        print("Out of date (run tools/build_md.py):", ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
