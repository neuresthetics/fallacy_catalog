"""Shared types for the idea-level checker.

The extractor proposes an Idea IR. Only the checker in this package issues a
verdict. Nothing here reads rhetorical scores or persuasion frameworks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Optional


STOP = {
    "a", "an", "the", "of", "for", "from", "to", "in", "on", "at", "by", "with",
    "and", "or", "but", "so", "her", "his", "their", "she", "he", "they", "them",
    "we", "our", "you", "your", "was", "were", "been", "be", "is", "are", "it",
    "its", "that", "this", "as", "can", "not", "no", "if", "than", "then", "into",
    "over", "under", "about", "because", "who", "whom", "what", "which", "when",
    "while", "just", "only", "also", "has", "have", "had", "did", "does", "do",
    "will", "would", "should",
}

TOKEN_RE = re.compile(r"[a-z0-9']+")

WEAK_RE = re.compile(
    r"\b(?:may|might|could|suspect(?:s|ed)?|likely|probably|perhaps|possibly|"
    r"i think|i suspect)\b|\bshould be investigated\b|\bbe investigated\b|"
    r"\bnot worried\b|\bnot sure\b",
    re.I,
)
DEFAULT_RE = re.compile(
    r"\b(?:burden of proof|presumption of innocence|null hypothesis|house rule)\b",
    re.I,
)
EXPERT_RE = re.compile(
    r"health agenc|regulatory agenc|\bexperts?\b|\bspecialists?\b|peer-reviewed|"
    r"trial data|systematic reviews?|\bmeta-analysis\b",
    re.I,
)
NOT_EXPERT_RE = re.compile(
    r"not an expert|no expertise|outside (?:his|her|their) field|\bcelebrity\b|"
    r"\bfamous actor\b|\binfluencer\b",
    re.I,
)
DISAGREE_RE = re.compile(
    r"\b(?:disagree\w*|no consensus|experts differ|divided|split)\b",
    re.I,
)
AGREE_RE = re.compile(r"\b(?:agree\w*|consensus|unanimous)\b", re.I)
UNTRUST_RE = re.compile(
    r"\b(?:untrustworthy|cannot be trusted|can't be trusted|lied|liar|"
    r"paid (?:by|to)|conflict of interest|fabricat\w*)\b",
    re.I,
)
MISQUOTE_RE = re.compile(
    r"\b(?:misquot\w*|out of context|taken out of context)\b",
    re.I,
)
REJECT_RE = re.compile(
    r"\b(?:ignore|reject|dismiss|disregard|don't listen|do not listen)\b",
    re.I,
)
EVIDENCE_RE = re.compile(
    r"\b(?:readings?|data|reports?|stud(?:y|ies)|measurements?|evidence|inspection)\b",
    re.I,
)
TESTIMONY_RE = re.compile(
    r"\b(?:trust me|take (?:his|her|their) word|testimony|eyewitness)\b",
    re.I,
)
COMMITMENT_RE = re.compile(
    r"\b(?:you yourself|your own (?:principle|view|words)|by your own|you said|"
    r"you argued|their own (?:principle|commitment))\b",
    re.I,
)
INSULT_RE = re.compile(r"\b(?:idiot|moron|fool|stupid|jerk)\b", re.I)
UNPROVEN_RE = re.compile(
    r"\b(?:never (?:been )?proved|never been shown|no (?:one|body) has proved|"
    r"hasn'?t been shown|has not been shown|unproven|no proof|no evidence|"
    r"cannot (?:dis)?prove|can'?t (?:dis)?prove|absence of (?:proof|evidence)|"
    r"not been proven)\b",
    re.I,
)
SEQUENCE_RE = re.compile(
    r"\b(?:after|afterwards|following|whenever|correlated|correlation|"
    r"associated with|coincided|and then)\b",
    re.I,
)
RULED_OUT_RE = re.compile(
    r"\b(?:ruled out|only explanation|no other (?:cause|explanation)|"
    r"controlled for|randomized|randomised)\b",
    re.I,
)
THOROUGH_RE = re.compile(
    r"\b(?:thorough search|exhaustive|systematically reviewed|we searched|"
    r"reviewed the literature|comprehensive review)\b",
    re.I,
)
HYPOTHESIS_RE = re.compile(
    r"\b(?:hypothesis|worth testing|to be tested|test whether)\b",
    re.I,
)
RECURSIVE_RE = re.compile(r"\brecursive\b", re.I)
COST_RE = re.compile(
    r"\b(?:costs? of being wrong|weighed|on balance|precaution(?:ary)?)\b",
    re.I,
)
HOLDER_ACCEPT_RE = re.compile(
    r"\bas (?:she|he|they) would (?:say|put it|accept)\b",
    re.I,
)
WHOSE_VERSION_RE = re.compile(
    r"\b(?:on [A-Z][a-z]+'s (?:version|view)|as [A-Z][a-z]+ (?:states|puts it)|"
    r"whose version)\b",
)

MISSING_FACT = {
    "source_not_expert_on_question": "whether the source is an expert on this question",
    "experts_substantially_disagree": "whether experts substantially disagree",
    "source_untrustworthy": "whether the source can be trusted",
    "source_misquoted": "whether the source is misquoted",
    "misattributes": "the original wording of the position being restated",
}

CLAIM_ROLES = {
    "premise", "conclusion", "illustration", "recommendation",
    "default_rule", "report", "attribution",
}
HEDGES = {"none", "weak", "strong"}
SCOPES = {"truth", "action", "investigate", "procedural"}
EDGE_TYPES = {
    "supports", "depends_on", "causes", "correlates", "appeals_to_source",
    "attacks_person", "attacks_claim", "misattributes", "shifts_burden",
    "selects_subset", "ignores", "instantiates",
}
WARRANTS = {"asserted", "inductive", "deductive"}
CAUSAL_FAMILIES = {"causation", "non-cause: ancient and modern"}


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def tokens(text: str) -> set:
    return {
        t for t in TOKEN_RE.findall((text or "").lower())
        if t not in STOP and len(t) > 2
    }


def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def quotes_related(a: str, b: str) -> bool:
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return False
    if na in nb or nb in na:
        return True
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return False
    return len(ta & tb) / min(len(ta), len(tb)) >= 0.6


def content_overlap(a: str, b: str) -> bool:
    return bool(tokens(a) & tokens(b))


def matched_span(source: str, regex: re.Pattern) -> Optional[dict]:
    match = regex.search(source or "")
    if not match:
        return None
    return {"quote": match.group(0)}


@dataclass
class Env:
    bindings: dict = field(default_factory=dict)
    atom_spans: list = field(default_factory=list)
    missing_facts: list = field(default_factory=list)
    open: bool = False

    def fork(self) -> "Env":
        return Env(
            bindings=dict(self.bindings),
            atom_spans=list(self.atom_spans),
            missing_facts=list(self.missing_facts),
            open=self.open,
        )


def succeed(
    env: Env,
    span: dict,
    *,
    atom: str,
    name: Optional[str] = None,
    var: Optional[str] = None,
    node_id: Optional[str] = None,
    kind: Optional[str] = None,
    extra_bindings: Optional[dict] = None,
    missing: Optional[str] = None,
    open_: bool = False,
) -> Env:
    new = env.fork()
    if extra_bindings:
        new.bindings.update(extra_bindings)
    if var and node_id and kind:
        new.bindings[var] = {"kind": kind, "id": node_id, "span": span}
    new.atom_spans.append({
        "atom": atom,
        "name": name,
        "var": var,
        "id": node_id,
        "quote": span.get("quote") if isinstance(span, dict) else None,
    })
    if open_ or missing:
        new.open = True
        if missing and missing not in new.missing_facts:
            new.missing_facts.append(missing)
    return new


@dataclass
class IndexedIR:
    data: dict
    source: str
    claims: dict
    edges: list
    edge_by_id: dict
    agents: dict
    traits: dict
    terms: dict
    bindings: list
    sets: dict
    steps: list
    excerpt: bool
    contested_reading: Optional[str]

    @classmethod
    def from_data(cls, data: dict) -> "IndexedIR":
        claims = {c["id"]: c for c in data.get("claims") or []}
        edges = list(data.get("edges") or [])
        agents = {a["id"]: a for a in data.get("agents") or []}
        traits = {}
        for agent in agents.values():
            for trait in agent.get("traits") or []:
                traits[trait["id"]] = trait
        contested = data.get("contested_reading")
        if not isinstance(contested, str) or not contested.strip():
            contested = None
        return cls(
            data=data,
            source=data.get("source_text") or "",
            claims=claims,
            edges=edges,
            edge_by_id={e["id"]: e for e in edges},
            agents=agents,
            traits=traits,
            terms={t["id"]: t for t in data.get("terms") or []},
            bindings=list(data.get("bindings") or []),
            sets={s["id"]: s for s in data.get("evidence_sets") or []},
            steps=list(data.get("steps") or []),
            excerpt=bool(data.get("excerpt")),
            contested_reading=contested,
        )

    def quote_ok(self, span) -> bool:
        if not isinstance(span, dict):
            return False
        quote = span.get("quote")
        if not isinstance(quote, str) or not quote.strip():
            return False
        return norm(quote) in norm(self.source)

    def text_of(self, node_id: str) -> str:
        if node_id in self.claims:
            claim = self.claims[node_id]
            quote = ((claim.get("span") or {}).get("quote") or "")
            return f"{claim.get('text') or ''} {quote}"
        if node_id in self.traits:
            trait = self.traits[node_id]
            quote = ((trait.get("span") or {}).get("quote") or "")
            return f"{trait.get('label') or ''} {quote}"
        if node_id in self.agents:
            return ((self.agents[node_id].get("name_span") or {}).get("quote") or "")
        return ""


@dataclass
class Ctx:
    ir: IndexedIR
    entry: dict
    catalog_entry: dict
    mode: str
    outside: frozenset
    causal_specific: tuple = ()
    warnings: list = field(default_factory=list)

    def replace_mode(self, mode: str) -> "Ctx":
        return Ctx(
            ir=self.ir,
            entry=self.entry,
            catalog_entry=self.catalog_entry,
            mode=mode,
            outside=self.outside,
            causal_specific=self.causal_specific,
            warnings=self.warnings,
        )


def uses_attack(ir: IndexedIR, support_edge: dict, attack_edge: dict) -> bool:
    if support_edge.get("source") == attack_edge.get("source"):
        return True
    src_text = ir.text_of(support_edge.get("source"))
    att_text = " ".join([
        (attack_edge.get("span") or {}).get("quote") or "",
        ir.text_of(attack_edge.get("source")),
    ])
    return quotes_related(src_text, att_text)


def rejects(ir: IndexedIR, support_edge: dict, claim_id: str) -> bool:
    target = ir.claims.get(support_edge.get("target"))
    if target is None:
        return False
    if target.get("role") not in ("conclusion", "recommendation") and target["id"] != claim_id:
        return False
    for edge in ir.edges:
        if edge.get("type") in ("ignores", "attacks_claim") and edge.get("target") == claim_id:
            if edge.get("source") in (target["id"], support_edge.get("source")):
                return True
    blob = f"{target.get('text') or ''} {(target.get('span') or {}).get('quote') or ''}"
    return bool(REJECT_RE.search(blob))


def has_inferential_attack(ir: IndexedIR) -> bool:
    attacks = [e for e in ir.edges if e.get("type") == "attacks_person"]
    for attack in attacks:
        target = attack.get("target")
        if target not in ir.claims:
            continue
        for support in ir.edges:
            if support.get("type") != "supports":
                continue
            if uses_attack(ir, support, attack) and rejects(ir, support, target):
                return True
    return False


def reaches(ir: IndexedIR, src: str, dst: str) -> bool:
    if src == dst:
        return False
    graph = {}
    for edge in ir.edges:
        if edge.get("type") in ("supports", "depends_on"):
            graph.setdefault(edge.get("source"), []).append(edge.get("target"))
    seen = set()
    stack = [src]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        for nxt in graph.get(node, []):
            if nxt == dst:
                return True
            stack.append(nxt)
    return False


def find_cycle(ir: IndexedIR, start: str):
    graph = {}
    for edge in ir.edges:
        if edge.get("type") in ("supports", "depends_on"):
            graph.setdefault(edge.get("source"), []).append((edge.get("target"), edge))
    stack = [(start, [start], [])]
    while stack:
        node, path, edges = stack.pop()
        for nxt, edge in graph.get(node, []):
            if nxt == start and path:
                return path, edges + [edge]
            if nxt in path:
                continue
            stack.append((nxt, path + [nxt], edges + [edge]))
    return None


def anchor_span(ir: IndexedIR, edge: dict):
    if ir.quote_ok(edge.get("span")):
        return edge["span"]
    source = ir.claims.get(edge.get("source"))
    if source and ir.quote_ok(source.get("span")):
        return source["span"]
    return None


def edge_of(ir: IndexedIR, env: Env, spec: dict):
    ref = env.bindings.get(spec.get("of"))
    if not ref or ref.get("kind") != "edge":
        return None
    return ir.edge_by_id.get(ref["id"])


def claim_of(ir: IndexedIR, env: Env, key: str):
    ref = env.bindings.get(key)
    if not ref or ref.get("kind") != "claim":
        return None
    return ir.claims.get(ref["id"])


def source_side_text(ir: IndexedIR, edge: dict) -> str:
    return " ".join([
        ir.text_of(edge.get("source")),
        (edge.get("span") or {}).get("quote") or "",
    ])
