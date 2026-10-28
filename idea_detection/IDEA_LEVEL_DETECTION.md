# Idea-level fallacy detection — design (refined)

**Status:** repo layer under `idea_detection/`. Does not change published `fallacies.json` (pilot patterns stay in a side file). `METHOD.md` stays the human procedure; it only links here.  
**Constraints:** vanilla catalog; no MINDSPACE; no new Latin names; catalog (~221) is source of truth.

METHOD stays the human/Genius-Study procedure. This layer makes the same discipline **machine-checkable** over an idea graph.

---

## 1. Problem (one paragraph)

METHOD already thinks in ideas (quote → strongest reading → conditions → look-alikes → verdict). Algorithmic detection still needs: (1) a typed **Idea IR** of claims and support relations, (2) catalog conditions as **predicates over that IR**, (3) a hard split so an LLM may **extract** IR but only the **checker** may issue a flag, justified by predicates + quoted spans.

---

## 2. Extractor vs checker (contract)

| Role | May do | Must not do |
|---|---|---|
| **Extractor** (LLM or human) | Segment steps; emit claims, edges, terms, spans under METHOD charity; mark `unstated` / CK. If the passage has `so` / `must` / `therefore` / dismiss / ignore, do not emit only `report` with zero edges. A quoted adversary who is answered gets a separate speaker and at least one inferential edge. An “associated with” evaluation gets an agent trait and `supports`, not a required `attacks_person` | Emit a fallacy verdict, entry id, or “this is ad hominem” prose that the pipeline treats as authoritative |
| **Normalizer** (deterministic) | Downgrade hedges from span words; force `default_rule`+`procedural` on burden/null language; drop illustration-only `supports` unless reliance marked | Invent missing contrary evidence |
| **Checker** (deterministic) | Eval `ir_pattern` / `ir_forbid`; apply `outside_text_conditions` + `text_detectable`; family tie-breaks; emit flag / possible issue / no issue | Trust extractor prose; flag on surface cues alone |

**Verdict rule:** flag iff every atom in `ir_pattern` binds with a quote span, no `ir_forbid` matches, outside-text gates pass, and family rules pick this entry. Soft questions for `text_detectable: "no"` only — never flags.

Rhetorical surface cues (insult lexicon, “everyone knows”) are **optional weak priors** that may reorder which entries to check first. They never satisfy a condition.

---

## 3. Idea IR (minimal)

Drop from v1: `scale`, free-form `rhetorical_cues` as required structure, geometric Definition/Axiom/Proof node types. Keep only what predicates need.

```json
{
  "passage_id": "...",
  "source_text": "...",
  "steps": [{ "id": "s1", "claim_ids": ["c1","c2"], "span": {"quote": "..."} }],
  "claims": [ /* Claim */ ],
  "edges": [ /* Edge */ ],
  "terms": [ /* optional; equivocation */ ],
  "bindings": [ /* optional */ ],
  "evidence_sets": [ /* optional; selective evidence */ ],
  "agents": [ /* optional; ad hominem */ ],
  "extractor": { "kind": "llm", "charity_applied": true }
}
```

### Claim

| Field | Values |
|---|---|
| `id`, `text`, `span.quote` | required |
| `role` | `premise` \| `conclusion` \| `illustration` \| `recommendation` \| `default_rule` \| `report` \| `attribution` |
| `hedge` | `none` \| `weak` \| `strong` — map “may/suspect/likely/investigate” → `weak`; “proves/will/must” → `strong` |
| `scope` | `truth` \| `action` \| `investigate` \| `procedural` |
| `speaker` | agent id or null |
| `unstated` | bool |
| `common_knowledge` | bool (METHOD CK rule only) |

Charity lives in the **extractor** (plus normalizer), not the checker: hedges stay hedges; recommendations that rest only on a causal effect assert that effect; defaults are procedural; supply the strongest plausible unstated premise and mark `unstated: true`.

Optional passage gates (not required on every IR): `excerpt` (bool) and `contested_reading` (string). When set, a pattern match is at most **possible issue** — METHOD's excerpt-boundary and contested-reading rules. `expected_checker` is fixture metadata for the eval harness; the checker strips it and does not treat it as a verdict.

### Edge

`id`, `type`, `source`, `target`, `span.quote`, optional `warrant` (`asserted`\|`inductive`\|`deductive`), optional `answered` (bool).

| `type` | Use |
|---|---|
| `supports` | premise → conclusion |
| `depends_on` | prerequisite (cycles → begging) |
| `causes` / `correlates` | causal vs mere co-occurrence/sequence |
| `appeals_to_source` | authority / testimony |
| `attacks_person` | trait/person used against claim or speaker |
| `attacks_claim` | rebuttal of reasons |
| `misattributes` | restatement claimed as opponent’s view |
| `shifts_burden` | demand other side prove/disprove |
| `selects_subset` / `ignores` | selective evidence |
| `instantiates` | case under a general rule |

### Term / binding

`Term`: `id`, `surface`, `senses[{id,gloss}]`.  
`TermBinding`: `term_id`, `claim_id`, `sense_id`, `span`.  
Checker: `sense_shift` if same surface, different `sense_id`, and conclusion needs identity.

### EvidenceSet (when needed)

`id`, `member_ids[]`, `selection_time` (`before_data`\|`after_data`\|`unknown`), `stated_in_text`, `direction` (`favors`\|`against`\|`mixed`), `prior_prediction` (bool\|null).

### Agent (when needed)

`id`, `name_span`, `traits[{label,span}]`.

---

## 4. Pipeline

```
passage
  → [1] segment steps
  → [2] extract strongest-reading IR (charity)
  → [3] normalize hedges / defaults / illustrations; bind term senses
  → [4] match ir_pattern (or compiled required_conditions)
  → [5] ir_forbid / look-alikes
  → [6] outside-text + text_detectable gates
  → [7] family / cross-family tie-breaks (catalog rules)
  → [8] optional second reviewer (METHOD (h), unchanged)
```

Fallback entries (`use_only_if_nothing_more_specific`) only if no specific match. Two labels in one step only if two separate fully met errors (METHOD).

---

## 5. Concrete `ir_pattern` / `ir_forbid` (JSON)

Pattern language: `{ "all": [ atom, ... ] }` or `{ "any": [ ... ] }`.  
Atoms: `exists_claim`, `exists_edge`, `exists_agent_trait`, `predicate`, `not`.  
Every successful atom must expose a `span` binding at eval time.

### 5.1 `ad-hominem`

```json
{
  "id": "ad-hominem",
  "ir_pattern": {
    "all": [
      { "exists_claim": { "var": "C", "is_argument_or_proposal": true } },
      { "exists_edge": { "type": "attacks_person", "target_var": "C", "var": "E_att" } },
      { "exists_edge": { "type": "supports", "source_var": "E_att.source", "target_var": "REJECT",
                        "note": "attack offered as reason to reject; REJECT may be C or 'ignore C'" } },
      { "predicate": "reasons_unanswered", "of": "C" },
      { "predicate": "trait_irrelevant_to_reasons", "of": "C", "trait_from": "E_att" }
    ]
  },
  "ir_forbid": [
    { "predicate": "claim_rests_on_testimony", "of": "C" },
    { "predicate": "uses_opponents_own_commitments" },
    { "predicate": "insult_without_inferential_edge" }
  ],
  "support_must_be_absent": ["unanswered_reasons"]
}
```

Maps to METHOD conditions 1–4 and the three look-alikes. No outside-text conditions. The executable atom is the pilot file's form (`from_attack` / `to_reject_of` on the inferential `supports` edge). The checker also accepts `source_var` / `target_var`.

### 5.2 `appeal-to-authority`

```json
{
  "id": "appeal-to-authority",
  "ir_pattern": {
    "all": [
      { "exists_claim": { "var": "K", "role_in": ["conclusion", "recommendation"] } },
      { "exists_edge": { "type": "appeals_to_source", "target_var": "K", "var": "E_auth" } },
      { "any": [
          { "predicate": "source_not_expert_on_question", "of": "E_auth" },
          { "predicate": "experts_substantially_disagree", "of": "E_auth" },
          { "predicate": "source_untrustworthy", "of": "E_auth" },
          { "predicate": "source_misquoted", "of": "E_auth" }
        ] },
      { "predicate": "authority_treated_as_settling", "of": "K" }
    ]
  },
  "ir_forbid": [
    { "all": [
        { "predicate": "source_expert_in_field", "of": "E_auth" },
        { "predicate": "passage_reports_expert_agreement", "of": "E_auth" }
      ] },
    { "predicate": "authority_one_piece_among_others", "of": "K" }
  ],
  "outside_text_predicates": ["source_not_expert_on_question", "experts_substantially_disagree",
                              "source_untrustworthy", "source_misquoted"]
}
```

Aligns with METHOD: condition 2 is outside-text; if the illegitimacy disjunct is neither stated nor CK → **possible issue**, not flag. Genuine-expert look-alike → **no issue** (METHOD example 2).

### 5.3 `equivocation`

```json
{
  "id": "equivocation",
  "ir_pattern": {
    "all": [
      { "predicate": "term_occurs_at_least", "term_var": "T", "n": 2 },
      { "predicate": "sense_shift", "term_var": "T" },
      { "predicate": "conclusion_requires_sense_identity", "term_var": "T" }
    ]
  },
  "ir_forbid": [
    { "predicate": "single_sense_throughout", "term_var": "T" },
    { "predicate": "wordplay_not_argument" }
  ],
  "term_identity_required": true,
  "tie_break": "If same sense but rule rationale fails case → accident, not equivocation (METHOD cross-family)."
}
```

### 5.4 `false-cause` (fallback)

```json
{
  "id": "false-cause",
  "use_only_if_nothing_more_specific": true,
  "ir_pattern": {
    "all": [
      { "any": [
          { "exists_edge": { "type": "causes", "var": "E_c" } },
          { "exists_claim": { "var": "K", "asserts_cause": true } }
        ] },
      { "predicate": "support_only_correlate_or_sequence", "of": "E_c" },
      { "predicate": "obvious_alternative_left_open", "of": "E_c" },
      { "predicate": "no_more_specific_causal_entry_matches" }
    ]
  },
  "ir_forbid": [
    { "predicate": "tentative_hypothesis_for_testing", "of": "K" }
  ]
}
```

Full pilot set (13 entries) lives in `idea_detection/pilot_ir_patterns.json`.

### 5.5 Post-e2e batch

Hasty generalization, slippery slope, false dilemma, appeal to the people, and guilt by association are pilot-only. Appeal to the people is the catalog id (appeal to popularity is an alias). Guilt by association is split from ad hominem: do not edit ad hominem atoms or forbids, and do not require `attacks_person` for an association used as the sole support of an evaluative conclusion.

| Id | IR shape | `ir_forbid` (look-alikes) |
|---|---|---|
| `hasty-generalization` | `instantiates` from a small-n case into a sweeping conclusion | uniform population; cautious / low-stakes consistent effect; doubt is selection, not size |
| `slippery-slope` | two or more `causes` steps into an undesirable conclusion; a stated leap (`soon`, `inevitably`) closes the outside-text gap | each link has a mechanism (precedent, bylaw, statute); line-drawing with no prediction |
| `false-dilemma` | exclusive premise `supports` a conclusion that relies on the split | main options not claimed exhaustive; true dichotomy or stated exhaustiveness |
| `appeal-to-the-people` | `appeals_to_source` whose source is the crowd, treated as settling | expert agreement; the question is taste or popularity; one piece among others; hedge not decisive |
| `guilt-by-association` | agent trait of association + `supports` into an evaluative conclusion | merits engaged; mere disclosure or proportionate caution; the link bears on the claim; the person shares the criticised commitment |

Slippery slope lists `later_link_unsupported` as outside-text: a bare chain with no leap cue is possible issue, not a flag. “Probably” does not supply the missing link and is not a forbid. Hedge, `default_rule`, and precautionary charity are unchanged.

---

## 6. Predicate library (v1, implementable)

| Predicate | Returns true when |
|---|---|
| `reasons_unanswered(C)` | C has supporting reasons in IR and no `attacks_claim`/`supports` engagement of those reasons |
| `trait_irrelevant_to_reasons(C, trait)` | trait does not bear on whether C’s reasons support C |
| `claim_rests_on_testimony(C)` | C’s support is speaker testimony, not independent evidence |
| `insult_without_inferential_edge` | person-attack language with no `supports`/`attacks_person` into a reject-conclusion |
| `authority_treated_as_settling(K)` | hedge/scope not weak; no other material support edges into K |
| `sense_shift(T)` | ≥2 bindings, distinct `sense_id` |
| `conclusion_requires_sense_identity(T)` | substituting glosses breaks the stated inference |
| `depends_on_cycle(K)` | cycle in `depends_on`/`supports` through contested K |
| `support_only_correlate_or_sequence` | causal conclusion with only `correlates` (or sequence) support |
| `subset_selected` / `rest_against` / `rest_ignored` | cherry-picking triple |
| `misattributes(R, O)` | restatement R ≠ original O (needs O in text or → possible issue) |

Predicates that need facts not in text consult `outside_text_predicates` / entry `outside_text_conditions` → possible issue naming the missing fact.

---

## 7. Outside-text & `text_detectable` (METHOD-faithful)

- Only listed outside-text conditions may be satisfied by CK or stated fact; all others from text.
- Unmet outside-text → **possible issue**, not flag.
- `text_detectable: "no"` (confirmation bias, selective attention, availability, rationalization) → **never flag**.
- Excerpt boundary: support may lie past excerpt → at most possible issue.
- Contested scholarly readings → possible issue + named reading (METHOD (b)).

---

## 8. Geometric engine

**Reuse:** typed-break mindset; invariants (no silent sense-shift; no `depends_on` cycle; non-proof notes don’t settle). Optional `geometric_break_ref` (e.g. `F001`) on a pilot pattern.  
**Do not:** treat F001–F080 as SoT; import bias-hardening/dual-case/consent into verdicts; require Definition/Axiom/Proof nodes for informal passages.

---

## 9. Worked IR sketches (METHOD examples)

### 9.1 Flag — ad-hominem

Passage: Reyes + corrosion readings; reply “fired for lateness, so ignore her bridge argument.”

```
claims: C_arg (bearings need replacing; reasons=readings), C_rej (ignore her argument)
edges:  attacks_person(trait_late → C_arg), supports(trait_late → C_rej), ignores(readings)
```

Checker: pattern matches; forbids fail (not testimony-only; `so` = inferential). → **flag ad-hominem**.  
Full fixture: `idea_detection/fixtures/method_ex1_ad_hominem.json`.

### 9.2 No issue — appeal-to-authority look-alike

Passage: national health agencies + trial reviews agree side effects rare → not worried.

```
claims: K (risk low), S (agencies/reviews agree on trial data)
edges:  appeals_to_source(S → K), warrant inductive
```

Illegitimacy disjunct false; `ir_forbid` expert-agreement matches. → **no issue**.  
Fixture: `idea_detection/fixtures/method_ex2_authority.json`.

---

## 10. Additive catalog fields (optional, later merge)

Do not edit published JSON until reviewed. Side file: `idea_detection/pilot_ir_patterns.json`.

| Field | Purpose |
|---|---|
| `ir_pattern` | required atoms |
| `ir_forbid` | look-alike blockers |
| `term_identity_required` | bool |
| `support_must_be_absent` | e.g. `["unanswered_reasons"]` |
| `outside_text_predicates` | names predicates tied to `outside_text_conditions` |
| `geometric_break_ref` | optional F-id pointer |

`required_conditions` / `legitimate_lookalikes` prose remain authoritative for humans; patterns must not contradict them.

---

## 11. Evaluation (short)

- Gold: METHOD’s 2 examples + look-alike suite; precision-first.  
- `text_detectable: no` suite → 0 flags.  
- Ablate surface-only vs full checker (surface-only must FP more).  
- Proposed bar: FP(flag) ≤ 5% on look-alike suite.

---

## 12. Non-goals

Rewrite METHOD; replace catalog with geometric-80; motive flags; new fallacy names; MINDSPACE; claiming NLU is always correct without spans.

---

## 13. Decisions (no Jason blocker)

1. Bootstrap patterns for the pilot set (originally eight; the post-e2e batch adds five). Compile remaining prose conditions later with span verification.  
2. Geometric node taxonomy optional.

## 14. Next build steps

1. Checker and fixture eval: `python3 -m idea_detection.eval_fixtures` (METHOD example 1 flags `ad-hominem`; example 2 is `no_issue` on `appeal-to-authority`).  
2. Review `pilot_ir_patterns.json` against prose conditions before any merge into `fallacies.json`.  
3. Use `EXTRACTOR_PROMPT.md` for a dry-run extraction; diff vs hand fixtures. The checker, not the extractor, verdicts.
