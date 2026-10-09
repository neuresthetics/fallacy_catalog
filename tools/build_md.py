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
REQUIRED = ["id", "name", "aliases", "category", "status", "text_detectable", "use_only_if_nothing_more_specific",
            "definition", "example", "required_conditions", "legitimate_lookalikes", "families", "related", "sources"]
TEXT_DETECTABLE = {"yes", "partly", "no"}
STATUS = {"standard", "contested"}
CAVEAT_SOURCES = {"source", "catalog wording"}
SOURCE_FIELDS = ["ref", "title", "url", "locator"]
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate(doc):
    errors = []
    entries = doc.get("entries")
    if not isinstance(entries, list) or not entries:
        return ["'entries' must be a non-empty list"]
    refs = {r.get("ref") for r in doc.get("references", [])}
    seen = Counter(e.get("id") for e in entries)
    families = {}
    for fam in doc.get("families", []):
        families[fam.get("name")] = fam
        if not str(fam.get("rule") or "").strip():
            errors.append(f"family '{fam.get('name')}': missing 'rule'")
        for m in fam.get("members", []):
            if m not in seen:
                errors.append(f"family '{fam.get('name')}': member '{m}' does not exist")
    for r in doc.get("redirects", []):
        if r.get("target") not in seen:
            errors.append(f"redirect '{r.get('id')}': target '{r.get('target')}' does not exist")
        if r.get("id") in seen:
            errors.append(f"redirect '{r.get('id')}' is also an entry id")
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
        if e.get("status") not in STATUS:
            errors.append(f"{eid}: 'status' must be one of {sorted(STATUS)}")
        if e.get("text_detectable") not in TEXT_DETECTABLE:
            errors.append(f"{eid}: 'text_detectable' must be one of {sorted(TEXT_DETECTABLE)}")
        if not isinstance(e.get("use_only_if_nothing_more_specific"), bool):
            errors.append(f"{eid}: 'use_only_if_nothing_more_specific' must be true or false")
        rc = e.get("required_conditions")
        if not isinstance(rc, list) or not 2 <= len(rc) <= 5 or not all(str(c).strip() for c in rc):
            errors.append(f"{eid}: 'required_conditions' must be a list of 2 to 5 non-empty conditions")
        la = e.get("legitimate_lookalikes")
        if not isinstance(la, list):
            errors.append(f"{eid}: 'legitimate_lookalikes' must be a list")
        else:
            for item in la:
                if not str(item.get("text") or "").strip():
                    errors.append(f"{eid}: look-alike missing 'text'")
                cs = item.get("caveat_source")
                if cs not in CAVEAT_SOURCES:
                    errors.append(f"{eid}: look-alike 'caveat_source' must be one of {sorted(CAVEAT_SOURCES)}")
                elif cs == "source":
                    so = item.get("source") or {}
                    if any(not str(so.get(f) or "").strip() for f in SOURCE_FIELDS) or (refs and so.get("ref") not in refs):
                        errors.append(f"{eid}: sourced look-alike needs a complete 'source' with a known ref")
        for f in ("families", "related"):
            if not isinstance(e.get(f), list):
                errors.append(f"{eid}: '{f}' must be a list")
        for r in e.get("related") or []:
            if r not in seen:
                errors.append(f"{eid}: related id '{r}' does not exist")
            if r == e.get("id"):
                errors.append(f"{eid}: lists itself as related")
        for fam in e.get("families") or []:
            if fam not in families:
                errors.append(f"{eid}: unknown family '{fam}'")
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
    for e in entries:
        for fam in e.get("families") or []:
            if fam in families and e.get("id") not in families[fam].get("members", []):
                errors.append(f"{e.get('id')}: listed in family '{fam}' but not a member of it")
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
    names = {e["id"]: e["name"] for e in entries}
    td = Counter(e["text_detectable"] for e in entries)
    n_contested = sum(1 for e in entries if e["status"] == "contested")
    n_fallback = sum(1 for e in entries if e["use_only_if_nothing_more_specific"])

    out = []
    out.append("# Fallacy Catalog\n")
    out.append("<!-- Generated from fallacies.json by tools/build_md.py. Do not edit by hand. -->\n")
    out.append(f"{len(entries)} named fallacies, grouped by category and listed alphabetically within each category. "
               f"{len(entries) - n_todo} entries have confirmed published sources; {n_todo} are marked TODO. "
               "See [SOURCES.md](SOURCES.md) for the references, [METHOD.md](METHOD.md) for how to check an argument, "
               "and [README.md](README.md) for what each field means.\n")
    out.append(f"Detectable from the text alone: {td['yes']} yes, {td['partly']} partly, {td['no']} no "
               "(entries marked *no* may only be raised as questions). "
               f"{n_contested} entries are contested names. {n_fallback} are broad fallbacks, to be used only when nothing more specific fits.\n")
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
    if doc.get("redirects"):
        out.append("## Names folded into other entries\n")
        out.append("These names are not separate entries. Use the entry they point to.\n")
        for r in sorted(doc["redirects"], key=lambda r: r["name"].lower()):
            note = f" {r['note']}" if r.get("note") else ""
            out.append(f"- **{r['name']}**: see [{names[r['target']]}](#{r['target']}).{note}")
        out.append("")
    if doc.get("families"):
        out.append("## Use-only-one families\n")
        out.append("Entries in the same family describe neighbouring mistakes. For a single step of an argument, pick the one that fits best and do not stack labels from the same family.\n")
        for fam in doc["families"]:
            mem = ", ".join(f"[{names[m]}](#{m})" for m in fam["members"])
            out.append(f"- **{fam['name'].capitalize()}**: {mem}. {fam['rule']}")
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
            tags = [f"Status: {e['status']}", f"Detectable from text: {e['text_detectable']}"]
            if e["use_only_if_nothing_more_specific"]:
                tags.append("Fallback: use only if nothing more specific fits")
            out.append(" · ".join(tags) + "\n")
            out.append(f"**Example:** {e['example']}\n")
            out.append("**Required conditions** (all must be shown from the text):\n")
            for n, c in enumerate(e["required_conditions"], 1):
                out.append(f"{n}. {c}")
            out.append("")
            if e["legitimate_lookalikes"]:
                out.append("**Legitimate look-alikes** (not this fallacy):\n")
                for item in e["legitimate_lookalikes"]:
                    if item["caveat_source"] == "source":
                        so = item["source"]
                        src = f"source: {so['ref']}, {so['locator']}"
                    else:
                        src = "catalog wording"
                    out.append(f"- {item['text']} *({src})*")
                out.append("")
            if e["related"]:
                rel = ", ".join(f"[{names[r]}](#{r})" for r in e["related"])
                if e["families"]:
                    fams = ", ".join(e["families"])
                    out.append(f"**Related, use only one per step** ({fams}): {rel}\n")
                else:
                    out.append(f"**Related:** {rel}\n")
            if e["sources"] == "TODO":
                out.append("**Sources:** TODO (no confirmed published source yet)\n")
            else:
                out.append("**Sources:**\n")
                for s in e["sources"]:
                    note = f" Note: {s['note']}." if s.get("note") else ""
                    out.append(f"- {s['title']}, {s['locator']}. <{s['url']}>{note}")
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
    td = Counter(e["text_detectable"] for e in entries)
    print(f"  text_detectable: yes {td['yes']}, partly {td['partly']}, no {td['no']}")
    print(f"  contested: {sum(1 for e in entries if e['status'] == 'contested')}; "
          f"fallbacks: {sum(1 for e in entries if e['use_only_if_nothing_more_specific'])}; "
          f"redirects: {len(doc.get('redirects', []))}; families: {len(doc.get('families', []))}")
    for c, n in sorted(Counter(e["category"] for e in entries).items(), key=lambda kv: CATEGORY_ORDER.index(kv[0])):
        print(f"  {c}: {n}")
    if stale:
        print("Out of date (run tools/build_md.py):", ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
