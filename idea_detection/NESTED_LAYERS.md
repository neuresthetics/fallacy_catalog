# Nested layers

Companion to the flat checker. [METHOD.md](../METHOD.md) stays the human procedure. This file is the machine layer, the same way [IDEA_LEVEL_DETECTION.md](IDEA_LEVEL_DETECTION.md) is. It does not change published `fallacies.json` verdicts or meanings, and it does not loosen `ir_forbid` or the precision-first gates in `check.py`.

A flat pass on excerpt IRs returns `possible_issue` whenever a pattern would have flagged, and it returns `possible_issue` when an outside-text predicate has no fact in the claim text. That is the checker doing what METHOD requires. Nested layers are how a client feeds the missing window back in and re-checks, instead of leaving every capped row as the last word.

## Philosophy survives, sophistry breaks

The peel is a stress test of dependence, not a second, looser verdict.

- A sound argument is re-checked at every premise, citation, and sub-claim the IR rests on. Extra text that does not meet a pattern, or that trips a look-alike, stays `no_issue`. The tree's stress is `survives`.
- A thin or fallacious move fails open: a child hard flag, or a gap that is still `possible_issue` when the expander has nothing further. Stress is `breaks` (`flagged` or `open`).
- The expander supplies real text or a real child IR. The checker does not invent claims, edges, or facts. Predicates and forbids are the ones already in the pilot file.

The flat `report` on each node is the ordinary `check_passage` result. Nesting does not rewrite it. `stress` / `outcome` say what the peel added.

## What is peeled

Every node, not only `possible_issue` rows:

| Kind | When |
|---|---|
| `cite` | Each `appeals_to_source` edge. The child keeps that appeal and the claims it joins. |
| `premise` | A premise, attribution, or default that something rests on, and that is not only the source of a citation. |
| `subclaim` | A claim with support coming in and support going out, or the target of `depends_on`. |
| `atom` | A flag or possible-issue span whose id is not already one of those nodes. |
| `excerpt` | The passage is an excerpt and a row was capped for the excerpt boundary. One peel, id `excerpt`. |
| `missing_fact` | A `possible_issue` names a missing fact and no structural peel already carries that entry. |

A `no_issue` passage still peels the premises and citations it rests on. A hard flag still peels them too. Stopping on the flag alone would skip the dependence test.

## Child IR

The expander is pluggable. `expand(request)` returns `None` or:

```json
{ "text": "...", "kind": "cite", "excerpt": false, "full": false, "ir": null }
```

`request` carries `passage_id`, `root_id`, `lookup_ids` (generated id, supplied id, ancestors), `target_id`, `claim_id`, `kind`, `quote`, `depth`, and `entry_ids`.

- **Supplied `ir`.** Used as the child. This package sets `passage_id` to `{parent}__l{depth}__{kind}-{target}` and applies `full` / `excerpt` when the context record sets them. It does not add claims.
- **Text only.** The child is the parent cone for that peel (the citation and what it supports, or the premise and what it rests on). `source_text` becomes the window when the window already contains the parent passage; otherwise the parent passage is kept and the window is appended, so existing quotes still sit in the text. The supplied string is written onto that peel's claim `text` so outside-text predicates can see a fact the client actually provided. Span quotes are not rewritten and no new edge is created. An excerpt peel copies the whole IR and does not smear the window onto every claim.
- **`excerpt` stays true** until the context record sets `"full": true` or `"excerpt": false`. A contested reading copied onto the child still caps a flag. Nesting does not settle it.

Grokipedia, or any other client, owns the corpus. It writes snapshot windows, cite text, or nearby-claim IRs into the context map. This package does not fetch them.

## Stop rules

A branch stops only for one of these:

| Reason | When |
|---|---|
| `hard_flag` | Checker aggregate is `flag` (gates already applied, so an excerpt cap is not a flag) and there is no further peel, or every remaining peel is empty or a cycle. |
| `confirmed_no_issue` | Aggregate is `no_issue` and there is no further peel, or every remaining peel is empty or a cycle. |
| `empty_expander` | The expander returned no text and no child IR. An open gap with nothing further stays `open`. |
| `cycle` | The same `(kind, target_id)` is already on the peel path, or the child IR fingerprint (normalized source, excerpt bit, contested reading, claim ids, edge ids) repeats an ancestor. |
| `max_depth` | `--max-depth N` was set and this node is at depth `N`. The node is checked. Its premises are not peeled. |
| `invalid_ir` | The seed or a supplied child failed validation. Nothing is repaired into a flag. |

Default depth is **unlimited**. Cycle detection is the bound. `--max-depth` is an ops safety valve (`0` checks the seed only). It is not a product cap of 3.

`possible_issue` is not a stop. A `no_issue` node that still has peelable premises is not a stop either: those premises are peeled. `confirmed_no_issue` is the leaf, once nothing remains that the expander can open.

## Stress on the tree

Checked bottom-up:

- `flagged` if this node or any checked descendant has aggregate `flag`.
- `open` if a `possible_issue` remains that a child did not close, or a descendant is `open`. Contested readings and `text_detectable: no` questions are not closed by a clean child.
- `survives` if this node is `no_issue`, or its only open rows are excerpt / missing-fact gaps and a cite, excerpt, or missing-fact child (or a child that carries that entry) itself `survives`.

`stress` is `survives` or `breaks` (`flagged` and `open` break). Empty expansion of a `no_issue` node does not manufacture a gap.

## Report and METHOD records

`check_nested` returns a tree. Each node has `layer` (`L0`), `layer_path` (`L0→L1→L2`), `peel_path` (`cite:e_auth → premise:p1`), the flat `report`, and `children` under the peel they came from.

METHOD records for flag and possible-issue rows are the flat records plus `layer_path` and `peel_path`. The first lines stay **idea_detection assist / lead-to-check**. `substitute_for_hand_method` stays false, including when a hard flag has closed spans. A possible-issue leaf is not promoted to a flag because a deeper layer exists; only the child checker's own flag is a flag.

```
python3 -m idea_detection.nested path/to/irs/
python3 -m idea_detection.nested --max-depth 32 --context-map contexts.jsonl path/to/irs/
python3 -m idea_detection.nested --context-dir path/to/context/ --json path/to/one.json
python3 -m idea_detection.nested --method-record --context-map contexts.jsonl path/to/irs/
python3 -m idea_detection.nested --method-record --method-format jsonl --context-map contexts.jsonl path/to/irs/
```

Run from the repository root.

### Context map

JSONL (one object per line) or a JSON list / `{"expansions": [...]}`.

```json
{"passage_id": "ex1", "kind": "snapshot_window", "full": true, "expand": "…whole article text including the excerpt…"}
{"passage_id": "physicist_diet", "target_id": "e_auth", "kind": "cite", "expand": "Pat is not an expert on this question."}
{"passage_id": "chain0", "target_id": "p0", "kind": "premise", "ir": {"passage_id": "chain1"}}
```

Kinds: `snapshot_window` (matches an excerpt peel), `cite`, `nearby_claim` (matches a premise or sub-claim), `premise`, `subclaim`, `atom`, `excerpt`, `missing_fact`.

A record with no `target_id` answers only an excerpt peel. It is not applied to every premise. First matching record wins. Lookup tries the node's passage id, the supplied child id, the root id, then ancestors.

### Context directory

- `{passage_id}.txt` — snapshot window for an excerpt peel.
- `{passage_id}.json` — one context record, a list, or a bare Idea IR used as the child.
- `{passage_id}/{target_id}.json` or `.txt` — one peel target.

`--context-map` is searched before `--context-dir`.

## What this will not do

- Invent a fact, a claim, or an edge so a gap can close.
- Treat expander text as common knowledge unless it is attached to the peeled claim from a record the client wrote.
- Clear `text_detectable: no` or a contested reading.
- Edit `fallacies.json` or METHOD.md.
- Fetch grokipedia, the web, or a snapshot store. The client writes the map.
