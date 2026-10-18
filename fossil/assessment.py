"""Explicit evidence rules; claims, overlap and historical direction stay distinct."""
from __future__ import annotations

import re

DERIVATION = re.compile(r"\b(fork(?:ed)?\s+(?:of|from)|based\s+(?:on|off)|deriv(?:ed|ative)|adapt(?:ed|ation)|port(?:ed)?\s+(?:of|from)|originally\s+(?:from|by)|original\s+repository|copied\s+from)\b", re.I)
INFLUENCE = re.compile(r"\b(inspir(?:ed|ation)|influenc(?:ed|e))\b", re.I)


def relationship(statement: str) -> bool:
    # Negations are evidence against a documentary ancestry claim, not support.
    if re.search(r"\b(?:not|never|unrelated|isn.t|wasn.t)\b.{0,45}\b(?:fork|based|derived|inspired|influence|adapt|port)", statement, re.I):
        return False
    if re.search(r"\b(?:example|tutorial|how to|you can|you could|create a fork|consider forking)\b", statement, re.I):
        return False
    return bool(DERIVATION.search(statement) or INFLUENCE.search(statement))


def assess(result: dict, target: dict, candidate: dict) -> dict:
    name = candidate.get("repository", "").lower()
    docs = [r for r in target["inventory"]["references"] if name and r["repository"].lower() == name
            and not r["path"].lower().endswith(("lock", "lock.json", "package.json", "go.sum"))
            and relationship(r.get("statement", r["text"]))]
    shared = sorted({c["sha"] for c in target["git"].get("commits", [])} & {c["sha"] for c in candidate["git"].get("commits", [])})
    parent = target.get("metadata", {}).get("parent", {}) or {}
    is_parent = name and parent.get("full_name", "").lower() == name
    result.update(documentary=docs, shared_commits=shared, scope="undetermined")
    result["explanation"] = {
        "code_overlap": "Distinctive source overlap is directly supported. Ancestry and direction remain undetermined without corroborating historical evidence.",
        "component_overlap": "Overlap is confined to vendored, generated, test, or example contexts. Project-level ancestry was not established.",
        "not_established": "Available evidence does not establish a meaningful relationship. Similar descriptions, conventions, licenses, and dependencies do not establish ancestry."
    }[result["verdict"]]
    if shared:
        result.update(verdict="shared_history", confidence="high (common Git history)",
                      explanation="Identical commit IDs establish shared Git history within the sampled logs. They do not by themselves establish which current project is the ancestor.")
    if is_parent:
        result.update(verdict="declared_fork", confidence="high (GitHub fork metadata)", direction="candidate → target (GitHub fork metadata)",
                      explanation="GitHub identifies the candidate as the target's fork parent. Source overlap and history are reported independently below.")
    derivative = [r for r in docs if DERIVATION.search(r.get("statement", r["text"]))]
    if derivative and result["matches"] and any(m["context"] == "application" for m in result["matches"]):
        result.update(verdict="corroborated_derivation", confidence="high (statement plus source overlap)", direction="candidate → target (target's declaration, corroborated by overlap)",
                      explanation="The target explicitly describes derivation from this candidate, and distinctive application source overlap corroborates the declaration. Exact historical scope and intermediate upstreams may remain unresolved.")
        project_docs = [r for r in derivative if re.search(r"(?:^|/)(?:readme|authors|credits|notice)", r["path"], re.I)
                        and not re.search(r"\b(?:component|adapter|module|function|class|snippet|portion|file|only the)\b", r.get("statement", r["text"]), re.I)]
        if not project_docs and not is_parent and not shared:
            result.update(verdict="corroborated_component", scope="component", confidence="high (component statement plus source overlap)",
                          explanation="A source file declares derivation and distinctive code overlap corroborates a component relationship. This does not establish whole-project ancestry.")
        else:
            result["scope"] = "project declaration"
    elif docs and not is_parent and not shared:
        result.update(verdict="declared_relationship", confidence="moderate (documentary claim)", direction="candidate → target (declared, not independently proven)",
                      explanation="The target declares derivation or conceptual influence. This records the statement; the sampled source evidence does not independently establish project-level code ancestry.")
    if name and target.get("repository", "").lower() == name:
        result.update(verdict="same_repository", direction="not applicable", scope="canonical repository identity",
                      confidence="high (GitHub canonical name)", explanation="Both inputs resolve to the same canonical GitHub repository. This is repository identity, not evidence of a separate descendant.")
    return result
