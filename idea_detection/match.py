"""Match ir_pattern / ir_forbid trees against an Idea IR.

Atoms succeed only with an in-text quote span. Outside-text predicates may
succeed as open (possible issue). Unknown atoms fail closed.
"""

from __future__ import annotations

from idea_detection.model import (
    UNPROVEN_RE,
    Ctx,
    Env,
    rejects,
    succeed,
    uses_attack,
)
from idea_detection.predicates import PREDICATES


_CLAIM_KEYS = {
    "var", "is_argument_or_proposal", "role_in", "asserts_cause", "text_signals_unproven",
}
_EDGE_KEYS = {
    "type", "var", "target_var", "source_var", "from_attack", "to_reject_of", "set_var", "note",
}


def atom_label(node) -> str:
    if not isinstance(node, dict):
        return "atom"
    if "predicate" in node:
        return str(node["predicate"])
    if "all" in node:
        return "+".join(atom_label(child) for child in node["all"])
    if "any" in node:
        return "any(" + ",".join(atom_label(child) for child in node["any"]) + ")"
    if "exists_edge" in node:
        return "exists_edge:" + str(node["exists_edge"].get("type") or "*")
    if "exists_claim" in node:
        return "exists_claim"
    if "exists_agent_trait" in node:
        return "exists_agent_trait"
    if "not" in node:
        return "not"
    return "atom"


def match_node(node, ctx: Ctx, env: Env) -> list:
    if not isinstance(node, dict):
        return []
    if "all" in node:
        return _match_all(node["all"], ctx, env)
    if "any" in node:
        return _match_any(node["any"], ctx, env)
    if "not" in node:
        return _match_not(node["not"], ctx, env)
    if "exists_claim" in node:
        return _match_claim(node["exists_claim"], ctx, env)
    if "exists_edge" in node:
        return _match_edge(node["exists_edge"], ctx, env)
    if "exists_agent_trait" in node:
        return _match_trait(node["exists_agent_trait"], ctx, env)
    if "predicate" in node:
        return _match_predicate(node, ctx, env)
    ctx.warnings.append(f"unknown pattern node: {sorted(node)}")
    return []


def _match_all(atoms, ctx, env) -> list:
    if not atoms:
        return [env]
    found = []
    for nxt in match_node(atoms[0], ctx, env):
        found.extend(_match_all(atoms[1:], ctx, nxt))
    return found


def _match_any(atoms, ctx, env) -> list:
    closed = []
    opened = []
    for atom in atoms:
        for nxt in match_node(atom, ctx, env):
            if nxt.open:
                opened.append(nxt)
            else:
                closed.append(nxt)
    if closed:
        return closed
    if not opened:
        return []
    merged = opened[0].fork()
    for item in opened[1:]:
        for fact in item.missing_facts:
            if fact not in merged.missing_facts:
                merged.missing_facts.append(fact)
        merged.open = True
    return [merged]


def _match_not(inner, ctx, env) -> list:
    found = match_node(inner, ctx, env)
    if any(not item.open for item in found):
        return []
    if found:
        opened = env.fork()
        opened.open = True
        for item in found:
            for fact in item.missing_facts:
                if fact not in opened.missing_facts:
                    opened.missing_facts.append(fact)
        return [opened]
    return [env]


def _match_predicate(node, ctx: Ctx, env: Env) -> list:
    if ctx.mode == "structural":
        return [env.fork()]
    name = node.get("predicate")
    fn = PREDICATES.get(name)
    if fn is None:
        ctx.warnings.append(f"unknown predicate: {name}")
        return []
    return fn(ctx, env, node)


def _bound_id(env, var):
    if var not in env.bindings:
        return None
    return env.bindings[var].get("id")


def _match_claim(spec, ctx: Ctx, env: Env) -> list:
    if not isinstance(spec, dict) or set(spec) - _CLAIM_KEYS:
        ctx.warnings.append(f"unsupported exists_claim keys: {sorted(set(spec) - _CLAIM_KEYS)}")
        return []
    hits = []
    for claim in ctx.ir.claims.values():
        if "is_argument_or_proposal" in spec:
            if bool(claim.get("is_argument_or_proposal")) != bool(spec["is_argument_or_proposal"]):
                continue
        if "role_in" in spec and claim.get("role") not in spec["role_in"]:
            continue
        if "asserts_cause" in spec and bool(claim.get("asserts_cause")) != bool(spec["asserts_cause"]):
            continue
        if spec.get("text_signals_unproven"):
            blob = ctx.ir.text_of(claim["id"])
            if not UNPROVEN_RE.search(blob):
                continue
        var = spec.get("var")
        if var and _bound_id(env, var) not in (None, claim["id"]):
            continue
        span = claim.get("span")
        if not ctx.ir.quote_ok(span):
            continue
        new = succeed(
            env, span, atom="exists_claim", var=var, node_id=claim["id"], kind="claim", name="exists_claim",
        )
        hits.append(new)
    return hits


def _match_edge(spec, ctx: Ctx, env: Env) -> list:
    if not isinstance(spec, dict) or set(spec) - _EDGE_KEYS:
        ctx.warnings.append(f"unsupported exists_edge keys: {sorted(set(spec) - _EDGE_KEYS)}")
        return []
    hits = []
    for edge in ctx.ir.edges:
        if spec.get("type") and edge.get("type") != spec["type"]:
            continue
        var = spec.get("var")
        if var and _bound_id(env, var) not in (None, edge["id"]):
            continue
        if "target_var" in spec:
            bound = _bound_id(env, spec["target_var"])
            if bound is None or edge.get("target") != bound:
                continue
        if "source_var" in spec:
            bound = _bound_id(env, spec["source_var"])
            if bound is None or edge.get("source") != bound:
                continue
        if "from_attack" in spec:
            attack_id = _bound_id(env, spec["from_attack"])
            attack = ctx.ir.edge_by_id.get(attack_id)
            if attack is None or not uses_attack(ctx.ir, edge, attack):
                continue
        if "to_reject_of" in spec:
            claim_id = _bound_id(env, spec["to_reject_of"])
            if claim_id is None or not rejects(ctx.ir, edge, claim_id):
                continue
        span = edge.get("span")
        if not ctx.ir.quote_ok(span):
            continue
        extra = {}
        set_var = spec.get("set_var")
        if set_var:
            set_id = None
            if edge.get("source") in ctx.ir.sets:
                set_id = edge.get("source")
            elif edge.get("target") in ctx.ir.sets:
                set_id = edge.get("target")
            if set_id is None:
                continue
            extra[set_var] = {"kind": "set", "id": set_id, "span": span}
        new = succeed(
            env, span, atom="exists_edge", var=var, node_id=edge["id"], kind="edge",
            name=edge.get("type"), extra_bindings=extra or None,
        )
        if (
            edge.get("type") == "misattributes"
            and "misattributes" in ctx.outside
            and _original_missing(ctx, edge, env, spec)
        ):
            new.open = True
            fact = "the original wording of the position being restated"
            if fact not in new.missing_facts:
                new.missing_facts.append(fact)
            if new.atom_spans:
                new.atom_spans[-1]["open"] = True
        hits.append(new)
    return hits


def _original_missing(ctx, edge, env, spec) -> bool:
    rest_id = None
    if spec.get("source_var"):
        rest_id = _bound_id(env, spec["source_var"])
    ends = [edge.get("source"), edge.get("target")]
    originals = [i for i in ends if i != rest_id] if rest_id else ends
    for original_id in originals:
        claim = ctx.ir.claims.get(original_id)
        if claim is None or claim.get("unstated") or not ctx.ir.quote_ok(claim.get("span")):
            return True
    return False


def _match_trait(spec, ctx: Ctx, env: Env) -> list:
    if not isinstance(spec, dict):
        return []
    hits = []
    var = spec.get("var")
    for trait_id, trait in ctx.ir.traits.items():
        if var and _bound_id(env, var) not in (None, trait_id):
            continue
        span = trait.get("span")
        if not ctx.ir.quote_ok(span):
            continue
        hits.append(succeed(
            env, span, atom="exists_agent_trait", var=var, node_id=trait_id, kind="trait",
            name="exists_agent_trait",
        ))
    return hits


def closed_forbid(forbid_list, ctx: Ctx, env: Env):
    """Return labels of forbid items that fully match. Open matches do not count.

    The pattern env may already be open because some other atom is an
    outside-text gap. That must not smear into the look-alike: a forbid is
    definite only when its own atoms close.
    """
    base = env.fork()
    base.open = False
    base.missing_facts = []
    labels = []
    full = ctx.replace_mode("full")
    for item in forbid_list or []:
        found = [hit for hit in match_node(item, full, base) if not hit.open]
        if found:
            labels.append(atom_label(item))
    return labels


def pattern_status(pattern, ctx: Ctx):
    """Return (closed envs, open envs) for a pattern in full mode."""
    if not pattern:
        return [], []
    found = match_node(pattern, ctx.replace_mode("full"), Env())
    closed = [item for item in found if not item.open]
    opened = [item for item in found if item.open]
    return closed, opened


def structural_envs(pattern, ctx: Ctx) -> list:
    if not pattern:
        return []
    return match_node(pattern, ctx.replace_mode("structural"), Env())
