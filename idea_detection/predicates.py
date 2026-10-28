"""Predicate library for pilot ir_pattern / ir_forbid atoms.

Each predicate returns a list of envs. An empty list is false (the atom does
not bind). An env with open=True is an outside-text gap: possible issue, not
a flag. Look-alike predicates bind only when the passage states their features.
"""

from __future__ import annotations

import re

from idea_detection.model import (
    AGREE_RE,
    COMMITMENT_RE,
    COST_RE,
    DISAGREE_RE,
    EVIDENCE_RE,
    EXPERT_RE,
    HOLDER_ACCEPT_RE,
    HYPOTHESIS_RE,
    INSULT_RE,
    MISQUOTE_RE,
    MISSING_FACT,
    NOT_EXPERT_RE,
    RECURSIVE_RE,
    REJECT_RE,
    RULED_OUT_RE,
    SEQUENCE_RE,
    TESTIMONY_RE,
    THOROUGH_RE,
    UNTRUST_RE,
    WHOSE_VERSION_RE,
    anchor_span,
    claim_of,
    content_overlap,
    edge_of,
    quotes_related,
    find_cycle,
    has_inferential_attack,
    jaccard,
    matched_span,
    reaches,
    source_side_text,
    succeed,
    tokens,
)

REPORT_RE = re.compile(
    r"\b(?:says?|said|according to|claims?|agrees?|writes|wrote)\b",
    re.I,
)
SMALL_N_RE = re.compile(
    r"\b(?:one|two|three|a couple|a few|a single|a handful|"
    r"my (?:\w+ )?neighbou?rs?)\b",
    re.I,
)
SWEEP_RE = re.compile(
    r"\b(?:all|every|everyone|everybody|always|never|anyone|no one|"
    r"people|the whole|in general)\b",
    re.I,
)
UNIFORM_POP_RE = re.compile(
    r"\b(?:uniform|identical in this respect|known to be the same|all the same)\b",
    re.I,
)
LOW_STAKES_RE = re.compile(
    r"\b(?:low-stakes|low stakes|reversible|we can undo|easy to reverse)\b",
    re.I,
)
LARGE_EFFECT_RE = re.compile(
    r"\b(?:large,? consistent|large and consistent|consistent effect)\b",
    re.I,
)
SELECTION_BIAS_RE = re.compile(
    r"\b(?:unrepresentative|biased sample|self-selected|selection bias|"
    r"how the sample was chosen)\b",
    re.I,
)
EXCLUSIVE_RE = re.compile(
    r"\beither\b.+\bor\b|\bthe only (?:choice|options?|alternative|way)\b|"
    r"\bonly two (?:choices|options|possibilities)\b|"
    r"\bno other (?:choice|option|way)\b|\bmust be one or the other\b",
    re.I,
)
NON_EXCLUSIVE_RE = re.compile(
    r"\b(?:main options|among others|not the only|not saying (?:those|these) are the only|"
    r"could also|for example)\b",
    re.I,
)
EXHAUSTIVE_SPLIT_RE = re.compile(
    r"\b(?:true dichotomy|logically exhaustive|exhaust the possibilities|"
    r"no third possibility|these two exhaust)\b",
    re.I,
)
COMPLEMENT_RE = re.compile(
    r"\b(?:or not\b|whether or not|on or off|true or false|pass or fail|"
    r"guilty or not guilty|alive or dead)\b",
    re.I,
)
RELY_SPLIT_RE = re.compile(
    r"\b(?:must|have to|therefore|no choice|so we)\b",
    re.I,
)
SLOPE_LEAP_RE = re.compile(
    r"\b(?:soon|inevitabl\w*|before you know|no stopping|slippery|"
    r"will have no choice)\b",
    re.I,
)
MECHANISM_RE = re.compile(
    r"\b(?:precedents?|legal duty|bylaws?|statutes?|binding rule|binding precedent|"
    r"mechanism)\b",
    re.I,
)
LINE_DRAWING_RE = re.compile(
    r"\b(?:where (?:do|to) (?:you |we )?draw the line|no sharp (?:line|boundary)|"
    r"tiny vague steps?|no practical prediction)\b",
    re.I,
)
UNDESIRABLE_RE = re.compile(
    r"\b(?:worthless|disaster|collapse|ruined|catastrophe|lose everything)\b",
    re.I,
)
CROWD_RE = re.compile(
    r"\b(?:millions|everyone|everybody|most people|many people|the majority|"
    r"the masses|most users|people use|common belief|widespread)\b",
    re.I,
)
PREFERENCE_Q_RE = re.compile(
    r"\b(?:prefer\w*|tastes?|fashion|convention|what people (?:like|want)|"
    r"the popular|is popular|popular choice|in style)\b",
    re.I,
)
ASSOCIATION_RE = re.compile(
    r"\b(?:associated with|association with|backed by|endorsed by|linked to|"
    r"allied with|friend of|in league with|once supported|"
    r"the company (?:they|it) keeps)\b",
    re.I,
)
EVALUATIVE_REJECT_RE = re.compile(
    r"\b(?:must be (?:bad|wrong|a bad)|bad plan|condemn\w*|worthless plan)\b",
    re.I,
)
CAUTION_RE = re.compile(
    r"\b(?:cautious|be careful|be wary|for disclosure|merely noting|just noting|"
    r"not a reason to reject)\b",
    re.I,
)
PROBATIVE_LINK_RE = re.compile(
    r"\b(?:same (?:method|fraud|scheme)|witness(?:'s|s)? reliability|"
    r"paid to (?:say|write|claim)|bears on (?:the|this) (?:claim|plan)|"
    r"the link shows)\b",
    re.I,
)
SHARED_COMMITMENT_RE = re.compile(
    r"\b(?:actually shares|same commitment|the specific commitment|"
    r"endorses this exact|shares the commitment)\b",
    re.I,
)


def _closed(env, span, name, extra=None):
    return [succeed(env, span, atom="predicate", name=name, extra_bindings=extra)]


def _open(env, span, name):
    fact = MISSING_FACT.get(name, name)
    return [succeed(env, span, atom="predicate", name=name, missing=fact, open_=True)]


def _unknown(ctx, env, span, name):
    if name not in ctx.outside or span is None:
        return []
    return _open(env, span, name)


def _ck_span(ctx, regex):
    for claim in ctx.ir.claims.values():
        if not claim.get("common_knowledge"):
            continue
        blob = ctx.ir.text_of(claim["id"])
        if regex.search(blob):
            span = claim.get("span")
            if ctx.ir.quote_ok(span):
                return "closed", span
            return "open", None
    return None


def reasons_unanswered(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    if claim is None:
        return []
    supporters = [
        e for e in ctx.ir.edges
        if e.get("type") == "supports" and e.get("target") == claim["id"]
    ]
    if not supporters and not claim.get("is_argument_or_proposal"):
        return []
    reason_ids = {claim["id"]} | {e.get("source") for e in supporters}
    for edge in ctx.ir.edges:
        if edge.get("type") == "attacks_claim" and edge.get("target") in reason_ids:
            return []
        if edge.get("answered") is True and edge.get("target") in reason_ids:
            return []
    span = claim.get("span")
    for edge in ctx.ir.edges:
        if edge.get("type") == "ignores" and edge.get("target") == claim["id"] and ctx.ir.quote_ok(edge.get("span")):
            span = edge["span"]
            break
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "reasons_unanswered")


def trait_irrelevant_to_reasons(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    attack_ref = env.bindings.get(spec.get("trait_from"))
    if claim is None or not attack_ref:
        return []
    attack = ctx.ir.edge_by_id.get(attack_ref.get("id"))
    if attack is None:
        return []
    trait = ctx.ir.traits.get(attack.get("source"))
    trait_text = ctx.ir.text_of(attack.get("source"))
    if trait:
        trait_text = f"{trait.get('label') or ''} {trait_text}"
    claim_text = ctx.ir.text_of(claim["id"])
    for edge in ctx.ir.edges:
        if edge.get("type") == "supports" and edge.get("target") == claim["id"]:
            claim_text += " " + ctx.ir.text_of(edge.get("source"))
    if content_overlap(trait_text, claim_text):
        return []
    span = (trait or {}).get("span") or attack.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "trait_irrelevant_to_reasons")


def claim_rests_on_testimony(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    if claim is None:
        return []
    blob = ctx.ir.text_of(claim["id"])
    for edge in ctx.ir.edges:
        if edge.get("type") == "supports" and edge.get("target") == claim["id"]:
            blob += " " + ctx.ir.text_of(edge.get("source"))
    if EVIDENCE_RE.search(blob):
        return []
    testimony = bool(TESTIMONY_RE.search(blob)) or any(
        e.get("type") == "appeals_to_source" and e.get("target") == claim["id"]
        for e in ctx.ir.edges
    )
    if not testimony:
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "claim_rests_on_testimony")


def uses_opponents_own_commitments(ctx, env, spec):
    span = matched_span(ctx.ir.source, COMMITMENT_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "uses_opponents_own_commitments")


def insult_without_inferential_edge(ctx, env, spec):
    if has_inferential_attack(ctx.ir):
        return []
    for edge in ctx.ir.edges:
        if edge.get("type") == "attacks_person" and ctx.ir.quote_ok(edge.get("span")):
            return _closed(env, edge["span"], "insult_without_inferential_edge")
    span = matched_span(ctx.ir.source, INSULT_RE)
    if span and ctx.ir.quote_ok(span):
        return _closed(env, span, "insult_without_inferential_edge")
    return []


def _authority_edge(ctx, env, spec):
    edge = edge_of(ctx.ir, env, spec)
    if edge is None or edge.get("type") != "appeals_to_source":
        # Fall back to the bound edge even if the caller passed a non-appeal id.
        edge = edge_of(ctx.ir, env, spec)
    if edge is None:
        return None, "", None
    text = source_side_text(ctx.ir, edge)
    span = anchor_span(ctx.ir, edge)
    return edge, text, span


def source_not_expert_on_question(ctx, env, spec):
    _edge, text, span = _authority_edge(ctx, env, spec)
    if span is None:
        return []
    if NOT_EXPERT_RE.search(text):
        return _closed(env, span, "source_not_expert_on_question")
    ck = _ck_span(ctx, NOT_EXPERT_RE)
    if ck and ck[0] == "closed":
        return _closed(env, ck[1], "source_not_expert_on_question")
    if ck and ck[0] == "open":
        return _unknown(ctx, env, span, "source_not_expert_on_question")
    if EXPERT_RE.search(text):
        return []
    return _unknown(ctx, env, span, "source_not_expert_on_question")


def source_expert_in_field(ctx, env, spec):
    _edge, text, span = _authority_edge(ctx, env, spec)
    if span is None or NOT_EXPERT_RE.search(text) or not EXPERT_RE.search(text):
        return []
    return _closed(env, span, "source_expert_in_field")


def experts_substantially_disagree(ctx, env, spec):
    _edge, text, span = _authority_edge(ctx, env, spec)
    if span is None:
        return []
    if DISAGREE_RE.search(text):
        return _closed(env, span, "experts_substantially_disagree")
    if AGREE_RE.search(text):
        return []
    return _unknown(ctx, env, span, "experts_substantially_disagree")


def passage_reports_expert_agreement(ctx, env, spec):
    _edge, text, span = _authority_edge(ctx, env, spec)
    if span is None or DISAGREE_RE.search(text) or not AGREE_RE.search(text):
        return []
    return _closed(env, span, "passage_reports_expert_agreement")


def source_untrustworthy(ctx, env, spec):
    _edge, text, span = _authority_edge(ctx, env, spec)
    if span is None:
        return []
    if UNTRUST_RE.search(text):
        return _closed(env, span, "source_untrustworthy")
    return _unknown(ctx, env, span, "source_untrustworthy")


def source_misquoted(ctx, env, spec):
    _edge, text, span = _authority_edge(ctx, env, spec)
    if span is None:
        return []
    if MISQUOTE_RE.search(text):
        return _closed(env, span, "source_misquoted")
    return _unknown(ctx, env, span, "source_misquoted")


def _treated_as_settling(ctx, env, spec, name):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    if claim is None:
        return []
    if claim.get("hedge") == "weak" or claim.get("role") == "default_rule":
        return []
    if claim.get("scope") in ("investigate", "procedural"):
        return []
    others = [
        e for e in ctx.ir.edges
        if e.get("target") == claim["id"] and e.get("type") in ("supports", "causes")
    ]
    if others:
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, name)


def authority_treated_as_settling(ctx, env, spec):
    return _treated_as_settling(ctx, env, spec, "authority_treated_as_settling")


def _one_piece_among_others(ctx, env, spec, name):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    if claim is None:
        return []
    others = [
        e for e in ctx.ir.edges
        if e.get("target") == claim["id"] and e.get("type") in ("supports", "causes", "correlates")
    ]
    if not others:
        return []
    span = others[0].get("span") if ctx.ir.quote_ok(others[0].get("span")) else claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, name)


def authority_one_piece_among_others(ctx, env, spec):
    return _one_piece_among_others(ctx, env, spec, "authority_one_piece_among_others")


def _term_bindings(ctx, term_id):
    return [b for b in ctx.ir.bindings if b.get("term_id") == term_id and ctx.ir.quote_ok(b.get("span"))]


def term_occurs_at_least(ctx, env, spec):
    n = int(spec.get("n") or 2)
    var = spec.get("term_var")
    bound = env.bindings.get(var) if var else None
    candidates = []
    if bound and bound.get("kind") == "term":
        candidates = [ctx.ir.terms[bound["id"]]]
    else:
        candidates = list(ctx.ir.terms.values())
    for term in candidates:
        spans = _term_bindings(ctx, term["id"])
        if len(spans) >= n:
            extra = {var: {"kind": "term", "id": term["id"], "span": spans[0]["span"]}} if var else None
            return _closed(env, spans[0]["span"], "term_occurs_at_least", extra)
    return []


def sense_shift(ctx, env, spec):
    var = spec.get("term_var")
    bound = env.bindings.get(var) if var else None
    candidates = []
    if bound and bound.get("kind") == "term":
        candidates = [bound["id"]]
    else:
        candidates = list(ctx.ir.terms)
    for term_id in candidates:
        spans = _term_bindings(ctx, term_id)
        senses = {b.get("sense_id") for b in spans}
        if len(senses) >= 2:
            extra = {var: {"kind": "term", "id": term_id, "span": spans[0]["span"]}} if var else None
            return _closed(env, spans[0]["span"], "sense_shift", extra)
    return []


def conclusion_requires_sense_identity(ctx, env, spec):
    var = spec.get("term_var")
    bound = env.bindings.get(var) if var else None
    if not bound or bound.get("kind") != "term":
        return []
    spans = _term_bindings(ctx, bound["id"])
    by_sense = {}
    for binding in spans:
        by_sense.setdefault(binding.get("sense_id"), []).append(binding)
    if len(by_sense) < 2:
        return []
    sense_items = list(by_sense.items())
    for sense_a, group_a in sense_items:
        for sense_b, group_b in sense_items:
            if sense_a == sense_b:
                continue
            for left in group_a:
                for right in group_b:
                    c_left, c_right = left.get("claim_id"), right.get("claim_id")
                    if c_left == c_right or c_right not in ctx.ir.claims:
                        continue
                    if ctx.ir.claims[c_right].get("role") not in ("conclusion", "recommendation"):
                        continue
                    if not reaches(ctx.ir, c_left, c_right):
                        continue
                    if ctx.ir.quote_ok(right.get("span")):
                        return _closed(env, right["span"], "conclusion_requires_sense_identity")
    return []


def single_sense_throughout(ctx, env, spec):
    var = spec.get("term_var")
    bound = env.bindings.get(var) if var else None
    if not bound or bound.get("kind") != "term":
        return []
    spans = _term_bindings(ctx, bound["id"])
    senses = {b.get("sense_id") for b in spans}
    if len(spans) >= 1 and len(senses) == 1:
        return _closed(env, spans[0]["span"], "single_sense_throughout")
    return []


def wordplay_not_argument(ctx, env, spec):
    if ctx.ir.steps and all(step.get("no_argument") for step in ctx.ir.steps):
        span = ctx.ir.steps[0].get("span")
        if ctx.ir.quote_ok(span):
            return _closed(env, span, "wordplay_not_argument")
    var = spec.get("term_var")
    bound = env.bindings.get(var) if var else None
    if not bound:
        return []
    claim_ids = [b.get("claim_id") for b in ctx.ir.bindings if b.get("term_id") == bound["id"]]
    claims = [ctx.ir.claims[c] for c in claim_ids if c in ctx.ir.claims]
    if claims and all(c.get("role") == "illustration" for c in claims):
        span = claims[0].get("span")
        if ctx.ir.quote_ok(span):
            return _closed(env, span, "wordplay_not_argument")
    return []


def _causal_blob(ctx, env, spec):
    texts = []
    span = None
    endpoints = set()
    ref = env.bindings.get(spec.get("of"))
    if ref and ref.get("kind") == "edge" and ref["id"] in ctx.ir.edge_by_id:
        edge = ctx.ir.edge_by_id[ref["id"]]
        texts.append(source_side_text(ctx.ir, edge))
        texts.append(ctx.ir.text_of(edge.get("target")))
        endpoints.update([edge.get("source"), edge.get("target")])
        if ctx.ir.quote_ok(edge.get("span")):
            span = edge["span"]
    for key in ("K", spec.get("of")):
        claim = claim_of(ctx.ir, env, key) if key else None
        if claim is None:
            continue
        texts.append(ctx.ir.text_of(claim["id"]))
        endpoints.add(claim["id"])
        if span is None and ctx.ir.quote_ok(claim.get("span")):
            span = claim["span"]
    return " ".join(texts), span, endpoints


def support_only_correlate_or_sequence(ctx, env, spec):
    blob, span, endpoints = _causal_blob(ctx, env, spec)
    correlate = False
    for edge in ctx.ir.edges:
        if edge.get("type") != "correlates":
            continue
        if endpoints and not ({edge.get("source"), edge.get("target")} & endpoints):
            continue
        correlate = True
        if span is None and ctx.ir.quote_ok(edge.get("span")):
            span = edge["span"]
    if not correlate and not SEQUENCE_RE.search(blob):
        return []
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "support_only_correlate_or_sequence")


def obvious_alternative_left_open(ctx, env, spec):
    if RULED_OUT_RE.search(ctx.ir.source):
        return []
    _blob, span, _ends = _causal_blob(ctx, env, spec)
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "obvious_alternative_left_open")


def no_more_specific_causal_entry_matches(ctx, env, spec):
    if ctx.causal_specific:
        return []
    _blob, span, _ends = _causal_blob(ctx, env, spec)
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "no_more_specific_causal_entry_matches")


def tentative_hypothesis_for_testing(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of")) or claim_of(ctx.ir, env, "K")
    claims = [claim] if claim else [c for c in ctx.ir.claims.values() if c.get("asserts_cause")]
    for item in claims:
        if item is None:
            continue
        blob = ctx.ir.text_of(item["id"])
        hedged = item.get("hedge") == "weak" or item.get("scope") == "investigate"
        if hedged or HYPOTHESIS_RE.search(blob):
            span = item.get("span")
            if ctx.ir.quote_ok(span):
                return _closed(env, span, "tentative_hypothesis_for_testing")
    return []


def depends_on_cycle(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    if claim is None:
        return []
    found = find_cycle(ctx.ir, claim["id"])
    if not found:
        return []
    path, edges = found
    span = None
    for edge in edges:
        if ctx.ir.quote_ok(edge.get("span")):
            span = edge["span"]
            break
    if span is None:
        return []
    others = [node for node in path if node != claim["id"] and node in ctx.ir.claims]
    premise_id = others[0] if others else claim["id"]
    extra = {"P": {"kind": "claim", "id": premise_id, "span": ctx.ir.claims[premise_id].get("span")}}
    return _closed(env, span, "depends_on_cycle", extra)


def _reported_content(ctx, premise, conclusion) -> bool:
    """A report that the conclusion was said is not itself an assertion of it."""
    if any(
        edge.get("type") == "appeals_to_source"
        and edge.get("source") == premise["id"]
        and edge.get("target") == conclusion["id"]
        for edge in ctx.ir.edges
    ):
        return True
    premise_text = ctx.ir.text_of(premise["id"])
    if not REPORT_RE.search(premise_text):
        return False
    inner = tokens(ctx.ir.text_of(conclusion["id"]))
    return bool(inner) and inner <= tokens(premise_text)


def premise_asserts_or_presupposes(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    if claim is None:
        return []
    var = spec.get("premise_var") or "P"
    best = None
    best_score = 0.0
    for other in ctx.ir.claims.values():
        if other["id"] == claim["id"]:
            continue
        if other.get("role") not in ("premise", "conclusion", "attribution"):
            continue
        if _reported_content(ctx, other, claim):
            continue
        score = jaccard(ctx.ir.text_of(claim["id"]), ctx.ir.text_of(other["id"]))
        # Shared wording is not enough; the premise has to restate the conclusion.
        if score >= 0.6 and score > best_score and ctx.ir.quote_ok(other.get("span")):
            best = other
            best_score = score
    if best is None:
        return []
    extra = {var: {"kind": "claim", "id": best["id"], "span": best.get("span")}}
    return _closed(env, best["span"], "premise_asserts_or_presupposes", extra)


def _cycle_nodes(ctx, claim_id):
    found = find_cycle(ctx.ir, claim_id)
    if not found:
        return set()
    path, _edges = found
    return set(path)


def not_independently_supported(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    if claim is None:
        return []
    k_ref = env.bindings.get("K")
    cycle = _cycle_nodes(ctx, k_ref["id"]) if k_ref and k_ref.get("kind") == "claim" else set()
    cycle.add(claim["id"])
    independent = [
        e for e in ctx.ir.edges
        if e.get("type") == "supports" and e.get("target") == claim["id"] and e.get("source") not in cycle
    ]
    if independent:
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "not_independently_supported")


def premise_independently_defensible(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    if claim is None:
        return []
    k_ref = env.bindings.get("K")
    cycle = _cycle_nodes(ctx, k_ref["id"]) if k_ref and k_ref.get("kind") == "claim" else set()
    for edge in ctx.ir.edges:
        if edge.get("type") == "supports" and edge.get("target") == claim["id"] and edge.get("source") not in cycle:
            span = edge.get("span") if ctx.ir.quote_ok(edge.get("span")) else claim.get("span")
            if ctx.ir.quote_ok(span):
                return _closed(env, span, "premise_independently_defensible")
    return []


def proper_recursive_definition(ctx, env, spec):
    span = matched_span(ctx.ir.source, RECURSIVE_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "proper_recursive_definition")


def valid_containment_only(ctx, env, spec):
    k_claim = claim_of(ctx.ir, env, "K")
    if k_claim is None:
        return []
    if find_cycle(ctx.ir, k_claim["id"]):
        return []
    for edge in ctx.ir.edges:
        if edge.get("type") != "supports" or edge.get("target") != k_claim["id"]:
            continue
        if edge.get("warrant") != "deductive":
            continue
        premise = ctx.ir.claims.get(edge.get("source"))
        if premise is None:
            continue
        if jaccard(ctx.ir.text_of(premise["id"]), ctx.ir.text_of(k_claim["id"])) >= 0.6:
            continue
        span = edge.get("span") if ctx.ir.quote_ok(edge.get("span")) else premise.get("span")
        if ctx.ir.quote_ok(span):
            return _closed(env, span, "valid_containment_only")
    return []


def _set_of(ctx, env, spec):
    key = spec.get("set_var") or spec.get("of")
    ref = env.bindings.get(key)
    if not ref or ref.get("kind") != "set":
        return None, None
    return ref["id"], ctx.ir.sets.get(ref["id"])


def rest_against_or_dilutes(ctx, env, spec):
    set_id, evidence = _set_of(ctx, env, spec)
    if not evidence or evidence.get("direction") not in ("against", "mixed"):
        return []
    for member in evidence.get("member_ids") or []:
        claim = ctx.ir.claims.get(member)
        if claim and ctx.ir.quote_ok(claim.get("span")):
            return _closed(env, claim["span"], "rest_against_or_dilutes")
    return []


def conclusion_rests_on_subset(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of"))
    _set_id, evidence = _set_of(ctx, env, spec)
    if claim is None or not evidence:
        return []
    members = set(evidence.get("member_ids") or [])
    for edge in ctx.ir.edges:
        if edge.get("type") == "supports" and edge.get("target") == claim["id"] and edge.get("source") in members:
            span = edge.get("span") if ctx.ir.quote_ok(edge.get("span")) else claim.get("span")
            if ctx.ir.quote_ok(span):
                return _closed(env, span, "conclusion_rests_on_subset")
    return []


def _selected_members(ctx, evidence):
    members = set(evidence.get("member_ids") or [])
    selected = set()
    for edge in ctx.ir.edges:
        if edge.get("type") != "selects_subset":
            continue
        if edge.get("target") in members:
            selected.add(edge.get("target"))
        if edge.get("source") in members:
            selected.add(edge.get("source"))
    return members, selected


def rest_unanswered(ctx, env, spec):
    _set_id, evidence = _set_of(ctx, env, spec)
    if not evidence:
        return []
    members, selected = _selected_members(ctx, evidence)
    rest = members - selected
    if not rest:
        return []
    for edge in ctx.ir.edges:
        if edge.get("target") in rest and edge.get("type") == "attacks_claim":
            return []
        if edge.get("answered") is True and edge.get("target") in rest:
            return []
    for member in rest:
        claim = ctx.ir.claims.get(member)
        if claim and ctx.ir.quote_ok(claim.get("span")):
            return _closed(env, claim["span"], "rest_unanswered")
    return []


def subset_pre_specified_independent_reason(ctx, env, spec):
    _set_id, evidence = _set_of(ctx, env, spec)
    if not evidence or evidence.get("selection_time") != "before_data":
        return []
    for member in evidence.get("member_ids") or []:
        claim = ctx.ir.claims.get(member)
        if claim and ctx.ir.quote_ok(claim.get("span")):
            return _closed(env, claim["span"], "subset_pre_specified_independent_reason")
    return []


def rest_acknowledged_and_answered(ctx, env, spec):
    _set_id, evidence = _set_of(ctx, env, spec)
    if not evidence:
        return []
    members, selected = _selected_members(ctx, evidence)
    rest = members - selected
    for edge in ctx.ir.edges:
        if edge.get("target") in rest and (edge.get("type") == "attacks_claim" or edge.get("answered") is True):
            span = edge.get("span") if ctx.ir.quote_ok(edge.get("span")) else None
            if span:
                return _closed(env, span, "rest_acknowledged_and_answered")
    return []


def contrary_absent_from_text_use_suppressed_evidence(ctx, env, spec):
    _set_id, evidence = _set_of(ctx, env, spec)
    if not evidence or evidence.get("stated_in_text") is not False:
        return []
    for edge in ctx.ir.edges:
        if edge.get("type") == "selects_subset" and ctx.ir.quote_ok(edge.get("span")):
            return _closed(env, edge["span"], "contrary_absent_from_text_use_suppressed_evidence")
    return []


def misattributes(ctx, env, spec):
    """True when a restatement and an in-text original diverge. Outside-text if the original is missing."""
    rest = claim_of(ctx.ir, env, spec.get("of")) or claim_of(ctx.ir, env, "R")
    edge = None
    for candidate in ctx.ir.edges:
        if candidate.get("type") == "misattributes":
            edge = candidate
            break
    if edge is None:
        return []
    original = ctx.ir.claims.get(edge.get("target"))
    span = edge.get("span") if ctx.ir.quote_ok(edge.get("span")) else (rest.get("span") if rest else None)
    if not ctx.ir.quote_ok(span):
        return []
    if original is None or original.get("unstated") or not ctx.ir.quote_ok(original.get("span")):
        return _unknown(ctx, env, span, "misattributes")
    if rest and jaccard(ctx.ir.text_of(rest["id"]), ctx.ir.text_of(original["id"])) >= 0.6:
        return []
    return _closed(env, span, "misattributes")


def presented_as_refuting_actual_position(ctx, env, spec):
    rest = claim_of(ctx.ir, env, spec.get("of"))
    if rest is None:
        return []
    for edge in ctx.ir.edges:
        if edge.get("type") == "attacks_claim" and edge.get("target") == rest["id"] and ctx.ir.quote_ok(edge.get("span")):
            return _closed(env, edge["span"], "presented_as_refuting_actual_position")
    return []


def restatement_holder_would_accept(ctx, env, spec):
    span = matched_span(ctx.ir.source, HOLDER_ACCEPT_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "restatement_holder_would_accept")


def draws_actual_commitment_consequence(ctx, env, spec):
    span = matched_span(ctx.ir.source, COMMITMENT_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "draws_actual_commitment_consequence")


def names_whose_version_is_rebutted(ctx, env, spec):
    span = matched_span(ctx.ir.source, WHOSE_VERSION_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "names_whose_version_is_rebutted")


def absence_of_proof_used_as_proof(ctx, env, spec):
    u = claim_of(ctx.ir, env, spec.get("from") or "U")
    k = claim_of(ctx.ir, env, spec.get("to") or "K")
    if u is None or k is None:
        return []
    if k.get("scope") in ("procedural", "investigate") or k.get("role") == "default_rule" or k.get("hedge") == "weak":
        return []
    for edge in ctx.ir.edges:
        if edge.get("type") == "supports" and edge.get("source") == u["id"] and edge.get("target") == k["id"]:
            span = edge.get("span") if ctx.ir.quote_ok(edge.get("span")) else k.get("span")
            if ctx.ir.quote_ok(span):
                return _closed(env, span, "absence_of_proof_used_as_proof")
    return []


def no_thorough_search_shown(ctx, env, spec):
    if THOROUGH_RE.search(ctx.ir.source):
        return []
    claim = claim_of(ctx.ir, env, "U") or claim_of(ctx.ir, env, spec.get("of"))
    span = claim.get("span") if claim else None
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "no_thorough_search_shown")


def thorough_search_done(ctx, env, spec):
    span = matched_span(ctx.ir.source, THOROUGH_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "thorough_search_done")


def procedural_default_action_only(ctx, env, spec):
    claim = claim_of(ctx.ir, env, "K") or claim_of(ctx.ir, env, spec.get("of"))
    if claim is None:
        return []
    if claim.get("scope") == "truth":
        return []
    if claim.get("role") == "default_rule" or claim.get("scope") == "procedural":
        span = claim.get("span")
        if ctx.ir.quote_ok(span):
            return _closed(env, span, "procedural_default_action_only")
    return []


def _claim_blob(ctx, claim):
    return ctx.ir.text_of(claim["id"])


def sample_too_small_for_sweep(ctx, env, spec):
    edge = edge_of(ctx.ir, env, spec)
    conclusion = claim_of(ctx.ir, env, spec.get("conclusion") or "K")
    if edge is None or edge.get("type") != "instantiates" or conclusion is None:
        return []
    sample = source_side_text(ctx.ir, edge)
    if not SMALL_N_RE.search(sample) or not SWEEP_RE.search(_claim_blob(ctx, conclusion)):
        return []
    span = edge.get("span") if ctx.ir.quote_ok(edge.get("span")) else conclusion.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "sample_too_small_for_sweep")


def population_known_uniform(ctx, env, spec):
    span = matched_span(ctx.ir.source, UNIFORM_POP_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "population_known_uniform")


def cautious_generalization(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "K")
    if claim is None:
        return []
    blob = _claim_blob(ctx, claim)
    cautious = (
        claim.get("hedge") == "weak"
        or claim.get("scope") == "investigate"
        or HYPOTHESIS_RE.search(blob)
    )
    if not cautious:
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "cautious_generalization")


def low_stakes_consistent_effect(ctx, env, spec):
    if not LOW_STAKES_RE.search(ctx.ir.source) or not LARGE_EFFECT_RE.search(ctx.ir.source):
        return []
    span = matched_span(ctx.ir.source, LOW_STAKES_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "low_stakes_consistent_effect")


def doubt_is_sample_selection(ctx, env, spec):
    span = matched_span(ctx.ir.source, SELECTION_BIAS_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "doubt_is_sample_selection")


def _split_blob(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "D")
    if claim is None:
        return None, ""
    return claim, _claim_blob(ctx, claim)


def exclusive_split_claimed(ctx, env, spec):
    claim, blob = _split_blob(ctx, env, spec)
    if claim is None or NON_EXCLUSIVE_RE.search(blob) or not EXCLUSIVE_RE.search(blob):
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "exclusive_split_claimed")


def split_not_a_true_dichotomy(ctx, env, spec):
    claim, blob = _split_blob(ctx, env, spec)
    if claim is None:
        return []
    if EXHAUSTIVE_SPLIT_RE.search(blob) or COMPLEMENT_RE.search(blob):
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "split_not_a_true_dichotomy")


def conclusion_relies_on_split(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "K")
    if claim is None or claim.get("hedge") == "weak":
        return []
    if not RELY_SPLIT_RE.search(_claim_blob(ctx, claim)):
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "conclusion_relies_on_split")


def options_not_claimed_exhaustive(ctx, env, spec):
    claim, blob = _split_blob(ctx, env, spec)
    k = claim_of(ctx.ir, env, "K")
    texts = [blob]
    if k is not None:
        texts.append(_claim_blob(ctx, k))
    joined = " ".join(texts)
    if not NON_EXCLUSIVE_RE.search(joined):
        return []
    span = matched_span(ctx.ir.source, NON_EXCLUSIVE_RE)
    if span is None and claim is not None:
        span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "options_not_claimed_exhaustive")


def split_shown_exhaustive(ctx, env, spec):
    claim, blob = _split_blob(ctx, env, spec)
    if claim is None:
        return []
    if not (EXHAUSTIVE_SPLIT_RE.search(blob) or COMPLEMENT_RE.search(blob)):
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "split_shown_exhaustive")


def _incoming_causes(ctx):
    incoming = {}
    for edge in ctx.ir.edges:
        if edge.get("type") == "causes" and edge.get("source") and edge.get("target"):
            incoming.setdefault(edge.get("target"), []).append(edge)
    return incoming


def _chains_ending_at(ctx, claim_id):
    incoming = _incoming_causes(ctx)
    found = []

    def walk(node, path, seen):
        preds = [edge for edge in incoming.get(node, []) if edge.get("source") not in seen]
        if not preds:
            if len(path) >= 2:
                found.append(list(reversed(path)))
            return
        for edge in preds:
            walk(edge.get("source"), path + [edge], seen | {node})

    if claim_id:
        walk(claim_id, [], set())
    return found


def _edge_blob(ctx, edge):
    return " ".join([
        source_side_text(ctx.ir, edge),
        ctx.ir.text_of(edge.get("target")),
    ])


def _chain_for(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "K")
    if claim is None:
        return None, []
    chains = _chains_ending_at(ctx, claim["id"])
    if not chains:
        return claim, []
    return claim, chains[0]


def _chain_text(ctx, chain):
    return " ".join(_edge_blob(ctx, edge) for edge in chain)


def _links_have_mechanism(ctx, chain):
    return bool(chain) and all(MECHANISM_RE.search(_edge_blob(ctx, edge)) for edge in chain)


def causal_chain_to_outcome(ctx, env, spec):
    claim, chain = _chain_for(ctx, env, spec)
    if claim is None or len(chain) < 2:
        return []
    blob = _chain_text(ctx, chain) + " " + _claim_blob(ctx, claim)
    if not UNDESIRABLE_RE.search(blob) and not REJECT_RE.search(ctx.ir.source):
        return []
    span = chain[-1].get("span") if ctx.ir.quote_ok(chain[-1].get("span")) else claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "causal_chain_to_outcome")


def later_link_unsupported(ctx, env, spec):
    claim, chain = _chain_for(ctx, env, spec)
    if claim is None or len(chain) < 2 or _links_have_mechanism(ctx, chain):
        return []
    blob = _chain_text(ctx, chain)
    span = None
    for edge in chain:
        if SLOPE_LEAP_RE.search(_edge_blob(ctx, edge)) and ctx.ir.quote_ok(edge.get("span")):
            span = edge["span"]
            break
    if SLOPE_LEAP_RE.search(blob):
        if span is None:
            span = matched_span(ctx.ir.source, SLOPE_LEAP_RE) or claim.get("span")
        if not ctx.ir.quote_ok(span):
            return []
        return _closed(env, span, "later_link_unsupported")
    anchor = chain[-1].get("span") if ctx.ir.quote_ok(chain[-1].get("span")) else claim.get("span")
    if not ctx.ir.quote_ok(anchor):
        return []
    return _unknown(ctx, env, anchor, "later_link_unsupported")


def each_causal_link_supported(ctx, env, spec):
    claim, chain = _chain_for(ctx, env, spec)
    if claim is None or len(chain) < 2 or not _links_have_mechanism(ctx, chain):
        return []
    span = None
    for edge in chain:
        if MECHANISM_RE.search(_edge_blob(ctx, edge)) and ctx.ir.quote_ok(edge.get("span")):
            span = edge["span"]
            break
    if span is None:
        span = matched_span(ctx.ir.source, MECHANISM_RE)
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "each_causal_link_supported")


def line_drawing_without_prediction(ctx, env, spec):
    if not LINE_DRAWING_RE.search(ctx.ir.source):
        return []
    if UNDESIRABLE_RE.search(ctx.ir.source) or REJECT_RE.search(ctx.ir.source):
        return []
    span = matched_span(ctx.ir.source, LINE_DRAWING_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "line_drawing_without_prediction")


def source_is_number_of_people(ctx, env, spec):
    _edge, text, span = _authority_edge(ctx, env, spec)
    if span is None or not CROWD_RE.search(text) or EXPERT_RE.search(text):
        return []
    return _closed(env, span, "source_is_number_of_people")


def popularity_treated_as_settling(ctx, env, spec):
    return _treated_as_settling(ctx, env, spec, "popularity_treated_as_settling")


def popularity_one_piece_among_others(ctx, env, spec):
    return _one_piece_among_others(ctx, env, spec, "popularity_one_piece_among_others")


def popularity_not_decisive(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "K")
    if claim is None:
        return []
    weak = (
        claim.get("hedge") == "weak"
        or claim.get("role") == "default_rule"
        or claim.get("scope") in ("investigate", "procedural")
    )
    if not weak:
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "popularity_not_decisive")


def expert_agreement_on_the_question(ctx, env, spec):
    _edge, text, span = _authority_edge(ctx, env, spec)
    if span is None or not EXPERT_RE.search(text) or not AGREE_RE.search(text):
        return []
    return _closed(env, span, "expert_agreement_on_the_question")


def claim_not_about_popularity_itself(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "K")
    if claim is None or PREFERENCE_Q_RE.search(_claim_blob(ctx, claim)):
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "claim_not_about_popularity_itself")


def question_is_convention_taste_or_popularity(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "K")
    if claim is None or not PREFERENCE_Q_RE.search(_claim_blob(ctx, claim)):
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "question_is_convention_taste_or_popularity")


def _trait_from(ctx, env, spec):
    ref = env.bindings.get(spec.get("trait_var") or spec.get("of"))
    if not ref or ref.get("kind") != "trait":
        return None
    return ctx.ir.traits.get(ref["id"])


def trait_is_association(ctx, env, spec):
    trait = _trait_from(ctx, env, spec)
    if trait is None:
        return []
    trait_text = f"{trait.get('label') or ''} {ctx.ir.text_of(trait['id'])}"
    if not ASSOCIATION_RE.search(trait_text):
        return []
    edge = edge_of(ctx.ir, env, {"of": spec.get("edge") or "E_assoc"})
    if edge is None or edge.get("type") != "supports":
        return []
    edge_text = source_side_text(ctx.ir, edge)
    same = (
        edge.get("source") == trait["id"]
        or ASSOCIATION_RE.search(edge_text)
        or quotes_related(edge_text, trait_text)
        or content_overlap(edge_text, trait_text)
    )
    if not same:
        return []
    span = trait.get("span") if ctx.ir.quote_ok(trait.get("span")) else edge.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "trait_is_association")


def association_used_as_evaluative_reason(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "K")
    if claim is None or claim.get("hedge") == "weak":
        return []
    blob = _claim_blob(ctx, claim)
    if CAUTION_RE.search(blob) or not EVALUATIVE_REJECT_RE.search(blob):
        return []
    span = claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "association_used_as_evaluative_reason")


def independent_merits_engaged(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "K")
    if claim is None:
        return []
    for edge in ctx.ir.edges:
        if edge.get("target") != claim["id"] or edge.get("type") not in ("supports", "causes"):
            continue
        blob = source_side_text(ctx.ir, edge)
        if ASSOCIATION_RE.search(blob):
            continue
        span = edge.get("span") if ctx.ir.quote_ok(edge.get("span")) else claim.get("span")
        if ctx.ir.quote_ok(span):
            return _closed(env, span, "independent_merits_engaged")
    return []


def association_mere_disclosure(ctx, env, spec):
    claim = claim_of(ctx.ir, env, spec.get("of") or "K")
    if claim is None:
        return []
    blob = _claim_blob(ctx, claim)
    disclosed = CAUTION_RE.search(blob) or CAUTION_RE.search(ctx.ir.source) or claim.get("hedge") == "weak"
    if not disclosed or EVALUATIVE_REJECT_RE.search(blob):
        return []
    span = matched_span(ctx.ir.source, CAUTION_RE) or claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "association_mere_disclosure")


def association_bears_on_the_claim(ctx, env, spec):
    span = matched_span(ctx.ir.source, PROBATIVE_LINK_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "association_bears_on_the_claim")


def shares_the_criticised_commitment(ctx, env, spec):
    span = matched_span(ctx.ir.source, SHARED_COMMITMENT_RE)
    if not span or not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "shares_the_criticised_commitment")


def precautionary_decision_with_costs_weighed(ctx, env, spec):
    claim = claim_of(ctx.ir, env, "K") or claim_of(ctx.ir, env, spec.get("of"))
    if claim is None or claim.get("scope") != "action":
        return []
    if not COST_RE.search(ctx.ir.source):
        return []
    span = matched_span(ctx.ir.source, COST_RE) or claim.get("span")
    if not ctx.ir.quote_ok(span):
        return []
    return _closed(env, span, "precautionary_decision_with_costs_weighed")


PREDICATES = {
    "reasons_unanswered": reasons_unanswered,
    "trait_irrelevant_to_reasons": trait_irrelevant_to_reasons,
    "claim_rests_on_testimony": claim_rests_on_testimony,
    "uses_opponents_own_commitments": uses_opponents_own_commitments,
    "insult_without_inferential_edge": insult_without_inferential_edge,
    "source_not_expert_on_question": source_not_expert_on_question,
    "experts_substantially_disagree": experts_substantially_disagree,
    "source_untrustworthy": source_untrustworthy,
    "source_misquoted": source_misquoted,
    "authority_treated_as_settling": authority_treated_as_settling,
    "source_expert_in_field": source_expert_in_field,
    "passage_reports_expert_agreement": passage_reports_expert_agreement,
    "authority_one_piece_among_others": authority_one_piece_among_others,
    "term_occurs_at_least": term_occurs_at_least,
    "sense_shift": sense_shift,
    "conclusion_requires_sense_identity": conclusion_requires_sense_identity,
    "single_sense_throughout": single_sense_throughout,
    "wordplay_not_argument": wordplay_not_argument,
    "support_only_correlate_or_sequence": support_only_correlate_or_sequence,
    "obvious_alternative_left_open": obvious_alternative_left_open,
    "no_more_specific_causal_entry_matches": no_more_specific_causal_entry_matches,
    "tentative_hypothesis_for_testing": tentative_hypothesis_for_testing,
    "depends_on_cycle": depends_on_cycle,
    "premise_asserts_or_presupposes": premise_asserts_or_presupposes,
    "not_independently_supported": not_independently_supported,
    "premise_independently_defensible": premise_independently_defensible,
    "proper_recursive_definition": proper_recursive_definition,
    "valid_containment_only": valid_containment_only,
    "rest_against_or_dilutes": rest_against_or_dilutes,
    "conclusion_rests_on_subset": conclusion_rests_on_subset,
    "rest_unanswered": rest_unanswered,
    "subset_pre_specified_independent_reason": subset_pre_specified_independent_reason,
    "rest_acknowledged_and_answered": rest_acknowledged_and_answered,
    "contrary_absent_from_text_use_suppressed_evidence": contrary_absent_from_text_use_suppressed_evidence,
    "misattributes": misattributes,
    "presented_as_refuting_actual_position": presented_as_refuting_actual_position,
    "restatement_holder_would_accept": restatement_holder_would_accept,
    "draws_actual_commitment_consequence": draws_actual_commitment_consequence,
    "names_whose_version_is_rebutted": names_whose_version_is_rebutted,
    "absence_of_proof_used_as_proof": absence_of_proof_used_as_proof,
    "no_thorough_search_shown": no_thorough_search_shown,
    "thorough_search_done": thorough_search_done,
    "procedural_default_action_only": procedural_default_action_only,
    "precautionary_decision_with_costs_weighed": precautionary_decision_with_costs_weighed,
    "sample_too_small_for_sweep": sample_too_small_for_sweep,
    "population_known_uniform": population_known_uniform,
    "cautious_generalization": cautious_generalization,
    "low_stakes_consistent_effect": low_stakes_consistent_effect,
    "doubt_is_sample_selection": doubt_is_sample_selection,
    "exclusive_split_claimed": exclusive_split_claimed,
    "split_not_a_true_dichotomy": split_not_a_true_dichotomy,
    "conclusion_relies_on_split": conclusion_relies_on_split,
    "options_not_claimed_exhaustive": options_not_claimed_exhaustive,
    "split_shown_exhaustive": split_shown_exhaustive,
    "causal_chain_to_outcome": causal_chain_to_outcome,
    "later_link_unsupported": later_link_unsupported,
    "each_causal_link_supported": each_causal_link_supported,
    "line_drawing_without_prediction": line_drawing_without_prediction,
    "source_is_number_of_people": source_is_number_of_people,
    "popularity_treated_as_settling": popularity_treated_as_settling,
    "popularity_one_piece_among_others": popularity_one_piece_among_others,
    "popularity_not_decisive": popularity_not_decisive,
    "expert_agreement_on_the_question": expert_agreement_on_the_question,
    "claim_not_about_popularity_itself": claim_not_about_popularity_itself,
    "question_is_convention_taste_or_popularity": question_is_convention_taste_or_popularity,
    "trait_is_association": trait_is_association,
    "association_used_as_evaluative_reason": association_used_as_evaluative_reason,
    "independent_merits_engaged": independent_merits_engaged,
    "association_mere_disclosure": association_mere_disclosure,
    "association_bears_on_the_claim": association_bears_on_the_claim,
    "shares_the_criticised_commitment": shares_the_criticised_commitment,
}
