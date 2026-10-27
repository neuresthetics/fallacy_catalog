"""Validate and normalize an Idea IR. Charity adjustments live here, not in the verdict."""

from __future__ import annotations

from copy import deepcopy

from idea_detection.model import (
    CLAIM_ROLES,
    DEFAULT_RE,
    EDGE_TYPES,
    HEDGES,
    SCOPES,
    WARRANTS,
    WEAK_RE,
)


def validate(data: dict) -> list:
    errors = []
    if not isinstance(data, dict):
        return ["IR must be a JSON object"]
    allowed = {
        "passage_id", "source_text", "excerpt", "contested_reading", "expected_checker",
        "steps", "claims", "edges", "terms", "bindings", "evidence_sets", "agents", "extractor",
    }
    for key in data:
        if key not in allowed:
            errors.append(f"unexpected field '{key}'")
    for key in ("passage_id", "source_text", "steps", "claims", "edges"):
        if key not in data:
            errors.append(f"missing '{key}'")
    if not isinstance(data.get("passage_id"), str) or not data.get("passage_id", "").strip():
        errors.append("passage_id must be a non-empty string")
    if not isinstance(data.get("source_text"), str):
        errors.append("source_text must be a string")
    if "excerpt" in data and not isinstance(data.get("excerpt"), bool):
        errors.append("excerpt must be a boolean")
    contested = data.get("contested_reading", None)
    if "contested_reading" in data and contested is not None and not isinstance(contested, str):
        errors.append("contested_reading must be a string or null")
    _validate_expected(data.get("expected_checker"), errors)
    steps = data.get("steps")
    claims = data.get("claims")
    edges = data.get("edges")
    if not isinstance(steps, list):
        errors.append("steps must be a list")
        steps = []
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    if not isinstance(edges, list):
        errors.append("edges must be a list")
        edges = []
    claim_ids = _validate_claims(claims, errors)
    _validate_steps(steps, claim_ids, errors)
    _validate_edges(edges, errors)
    _validate_terms(data.get("terms"), data.get("bindings"), claim_ids, errors)
    _validate_sets(data.get("evidence_sets"), claim_ids, errors)
    _validate_agents(data.get("agents"), errors)
    _validate_extractor(data.get("extractor"), errors)
    return errors


def _validate_expected(expected, errors):
    if expected is None:
        return
    if not isinstance(expected, dict):
        errors.append("expected_checker must be an object")
        return
    for key in expected:
        if key not in ("entry_id", "verdict", "reason"):
            errors.append(f"expected_checker.{key} is not allowed")
    if not isinstance(expected.get("entry_id"), str):
        errors.append("expected_checker.entry_id must be a string")
    if expected.get("verdict") not in ("flag", "possible_issue", "no_issue"):
        errors.append("expected_checker.verdict is invalid")


def _validate_claims(claims, errors) -> set:
    ids = set()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claims[{index}] must be an object")
            continue
        cid = claim.get("id")
        if not isinstance(cid, str) or not cid:
            errors.append(f"claims[{index}] missing id")
        elif cid in ids:
            errors.append(f"duplicate claim id '{cid}'")
        else:
            ids.add(cid)
        for key in ("text", "role", "hedge", "scope"):
            if key not in claim:
                errors.append(f"claim '{cid}' missing '{key}'")
        if claim.get("role") not in CLAIM_ROLES:
            errors.append(f"claim '{cid}' has unknown role '{claim.get('role')}'")
        if claim.get("hedge") not in HEDGES:
            errors.append(f"claim '{cid}' has unknown hedge '{claim.get('hedge')}'")
        if claim.get("scope") not in SCOPES:
            errors.append(f"claim '{cid}' has unknown scope '{claim.get('scope')}'")
        _validate_span(claim.get("span"), f"claim '{cid}'", errors, required=False)
    return ids


def _validate_steps(steps, claim_ids, errors):
    seen = set()
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append(f"steps[{index}] must be an object")
            continue
        sid = step.get("id")
        if not isinstance(sid, str) or not sid:
            errors.append(f"steps[{index}] missing id")
        elif sid in seen:
            errors.append(f"duplicate step id '{sid}'")
        else:
            seen.add(sid)
        if not isinstance(step.get("claim_ids"), list):
            errors.append(f"step '{sid}' missing claim_ids")
        else:
            for cid in step["claim_ids"]:
                if cid not in claim_ids:
                    errors.append(f"step '{sid}' references unknown claim '{cid}'")
        _validate_span(step.get("span"), f"step '{sid}'", errors, required=False)


def _validate_edges(edges, errors):
    seen = set()
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{index}] must be an object")
            continue
        eid = edge.get("id")
        if not isinstance(eid, str) or not eid:
            errors.append(f"edges[{index}] missing id")
        elif eid in seen:
            errors.append(f"duplicate edge id '{eid}'")
        else:
            seen.add(eid)
        if edge.get("type") not in EDGE_TYPES:
            errors.append(f"edge '{eid}' has unknown type '{edge.get('type')}'")
        for key in ("source", "target"):
            if not isinstance(edge.get(key), str) or not edge.get(key):
                errors.append(f"edge '{eid}' missing '{key}'")
        if "warrant" in edge and edge.get("warrant") not in WARRANTS:
            errors.append(f"edge '{eid}' has unknown warrant")
        _validate_span(edge.get("span"), f"edge '{eid}'", errors, required=False)


def _validate_span(span, where, errors, required):
    if span is None:
        if required:
            errors.append(f"{where} missing span")
        return
    if not isinstance(span, dict) or not isinstance(span.get("quote"), str):
        errors.append(f"{where} span.quote must be a string")


def _validate_terms(terms, bindings, claim_ids, errors):
    if terms is None:
        terms = []
    if bindings is None:
        bindings = []
    if not isinstance(terms, list) or not isinstance(bindings, list):
        errors.append("terms and bindings must be lists")
        return
    term_ids = set()
    senses = {}
    for term in terms:
        if not isinstance(term, dict) or not term.get("id") or not isinstance(term.get("surface"), str):
            errors.append("term missing id or surface")
            continue
        if term["id"] in term_ids:
            errors.append(f"duplicate term id '{term['id']}'")
        term_ids.add(term["id"])
        senses[term["id"]] = set()
        for sense in term.get("senses") or []:
            if isinstance(sense, dict) and sense.get("id"):
                senses[term["id"]].add(sense["id"])
    for binding in bindings:
        if not isinstance(binding, dict):
            errors.append("binding must be an object")
            continue
        for key in ("term_id", "claim_id", "sense_id"):
            if not isinstance(binding.get(key), str):
                errors.append(f"binding missing '{key}'")
        if binding.get("term_id") not in term_ids:
            errors.append(f"binding references unknown term '{binding.get('term_id')}'")
        elif binding.get("sense_id") not in senses.get(binding.get("term_id"), set()):
            errors.append(f"binding sense '{binding.get('sense_id')}' is not on its term")
        if binding.get("claim_id") not in claim_ids:
            errors.append(f"binding references unknown claim '{binding.get('claim_id')}'")
        _validate_span(binding.get("span"), "binding", errors, required=False)


def _validate_sets(sets, claim_ids, errors):
    if sets is None:
        return
    if not isinstance(sets, list):
        errors.append("evidence_sets must be a list")
        return
    seen = set()
    for item in sets:
        if not isinstance(item, dict) or not item.get("id"):
            errors.append("evidence set missing id")
            continue
        if item["id"] in seen:
            errors.append(f"duplicate evidence set '{item['id']}'")
        seen.add(item["id"])
        if not isinstance(item.get("member_ids"), list):
            errors.append(f"evidence set '{item['id']}' missing member_ids")
            continue
        for member in item["member_ids"]:
            if member not in claim_ids:
                errors.append(f"evidence set '{item['id']}' references unknown claim '{member}'")


def _validate_agents(agents, errors):
    if agents is None:
        return
    if not isinstance(agents, list):
        errors.append("agents must be a list")
        return
    seen = set()
    trait_ids = set()
    for agent in agents:
        if not isinstance(agent, dict) or not agent.get("id"):
            errors.append("agent missing id")
            continue
        if agent["id"] in seen:
            errors.append(f"duplicate agent id '{agent['id']}'")
        seen.add(agent["id"])
        _validate_span(agent.get("name_span"), f"agent '{agent['id']}'", errors, required=False)
        for trait in agent.get("traits") or []:
            if not isinstance(trait, dict) or not trait.get("id") or not isinstance(trait.get("label"), str):
                errors.append(f"agent '{agent['id']}' has a trait missing id or label")
                continue
            if trait["id"] in trait_ids:
                errors.append(f"duplicate trait id '{trait['id']}'")
            trait_ids.add(trait["id"])
            _validate_span(trait.get("span"), f"trait '{trait['id']}'", errors, required=False)


def _validate_extractor(extractor, errors):
    if extractor is None:
        return
    if not isinstance(extractor, dict):
        errors.append("extractor must be an object")
        return
    for key in extractor:
        if key not in ("kind", "model", "charity_applied"):
            errors.append(f"extractor.{key} is not allowed")
    if "kind" in extractor and extractor.get("kind") not in ("llm", "human"):
        errors.append("extractor.kind must be llm or human")


def normalize(data: dict) -> dict:
    """Downgrade hedges, force procedural defaults, drop illustration-only supports.

    Does not invent missing contrary evidence and does not issue a verdict.
    """
    out = deepcopy(data)
    claim_by_id = {c["id"]: c for c in out.get("claims") or []}
    for claim in claim_by_id.values():
        blob = f"{claim.get('text') or ''} {((claim.get('span') or {}).get('quote') or '')}"
        if WEAK_RE.search(blob) and claim.get("hedge") in ("none", "strong"):
            claim["hedge"] = "weak"
        if DEFAULT_RE.search(blob):
            claim["role"] = "default_rule"
            claim["scope"] = "procedural"
    kept = []
    for edge in out.get("edges") or []:
        source = claim_by_id.get(edge.get("source"))
        if edge.get("type") == "supports" and source and source.get("role") == "illustration":
            continue
        kept.append(edge)
    out["edges"] = kept
    return out
