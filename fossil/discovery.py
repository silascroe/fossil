"""Target-derived leads, bounded searches, explicit failures, no built-in ancestors."""
from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlencode

from .acquire import AcquisitionError, repo_name
from .assessment import DERIVATION, INFLUENCE
from .inventory import SOURCE, SUPPORT_DIRS, context


MAX_LEADS = 24
DOC = re.compile(r"readme|notice|copying|licen[cs]e|authors|credits|history", re.I)


def own_source(path: str | None) -> bool:
    """Whether a code-search hit sits in a project's own source rather than a bundled copy or a data/doc file.

    Popular code is committed inside virtualenvs, vendor trees and generated reports far more often than
    it is maintained; those copies otherwise outnumber the project that actually develops it.
    """
    if not path:
        return True
    suffix = Path(path).suffix.lower()
    # Extensionless files may be scripts (neofetch is one); only a known non-source extension demotes.
    return (not suffix or suffix in SOURCE) and context(path, "") not in {"vendored/external", "generated"}


CONFIRMING = {"code_overlap", "component_overlap", "corroborated_derivation", "corroborated_component", "shared_history", "declared_fork"}


def second_hop(candidate: dict, inventory: dict, result: dict, skip: set[str]) -> list[tuple[str, list[str]]]:
    """Repositories that a confirmed copy names, ranked by how much shared code names them.

    A copy of the target often keeps credits the target lost. Only references inside files
    that overlapped the target, or relationship statements in the copy's docs, count;
    a copy's other links describe the copy, not the shared code. These are leads only:
    each still has to show source overlap with the target itself.
    """
    if result["verdict"] not in CONFIRMING:
        return []
    matched = {m["candidate_path"] for m in result["matches"]}
    source = (candidate.get("repository") or candidate["input"]).lower()
    found = {}
    for ref in inventory["references"]:
        name = repo_name(ref["repository"])
        if not name or name.lower() in skip or name.lower() == source:
            continue
        if SUPPORT_DIRS & set(Path(ref["path"]).parts[:-1]):
            continue  # CI, packaging and doc tooling link to their own dependencies
        statement = ref.get("statement", ref["text"])
        # As for the target's own credits: a project's lineage is stated in its docs; a comment
        # such as "based on CPython" in source credits one snippet, so it counts as a plain mention.
        relation = bool(DERIVATION.search(statement) or INFLUENCE.search(statement)) and bool(DOC.search(ref["path"])) \
            and context(ref["path"], "") == "application"
        if ref["path"] not in matched and not relation:
            continue
        entry = found.setdefault(name.lower(), {"name": name, "files": set(), "relation": False, "example": ref})
        if ref["path"] in matched:
            entry["files"].add(ref["path"])
        if relation and not entry["relation"]:
            entry["relation"], entry["example"] = True, ref
    # One stray link in one shared file is not enough; two shared files or a stated relationship is.
    score = lambda e: len(e["files"]) + 2 * e["relation"]
    ranked = sorted((e for e in found.values() if score(e) >= 2), key=lambda e: (-score(e), e["name"].lower()))
    hops = []
    for e in ranked:
        basis = " and ".join(x for x in (f"{len(e['files'])} file(s) it shares with the target" if e["files"] else "",
                                         "a relationship statement" if e["relation"] else "") if x)
        ex = e["example"]
        hops.append((e["name"], [f"Named by confirmed candidate {source} in {basis}; e.g. {ex['path']}:{ex['line']}: {ex['text'][:200]}"]))
    return hops


def find_candidates(target: dict, inventory: dict, client, *, ai=None, exclude: set[str] = frozenset()) -> tuple[dict, list]:
    ranked = {}
    trail = []
    own = target.get("repository", "").lower()
    excluded = {}

    def add(name: str, reason: str, rank: int, *, query: str | None = None, position: int = 99):
        base, sep, ref = name.partition("@")
        valid = repo_name(base)
        if valid and sep:
            valid += "@" + ref
        if not valid or valid.lower() == own:
            return
        if base.lower() in exclude:
            excluded[base.lower()] = excluded.get(base.lower(), 0) + 1
            return
        key = valid.lower()
        if key not in ranked:
            ranked[key] = {"name": valid, "rank": rank, "reasons": {}, "queries": set(), "position": position}
        entry = ranked[key]
        if query:
            # Independent code searches converging on one repository is stronger than any single hit.
            entry["queries"].add(query)
            rank = min(rank + 10, rank + 5 * (len(entry["queries"]) - 1))
        entry["rank"] = max(entry["rank"], rank)
        entry["position"] = min(entry["position"], position)
        entry["reasons"][reason] = max(rank, entry["reasons"].get(reason, 0))

    meta = target.get("metadata", {})
    for key in ("parent", "source"):
        if meta.get(key):
            add(meta[key]["full_name"], "GitHub fork " + key + " metadata", 100)
    for ref in inventory["references"]:
        relation = bool(DERIVATION.search(ref.get("statement", ref["text"])) or INFLUENCE.search(ref.get("statement", ref["text"])))
        doc = bool(DOC.search(ref["path"]))
        # A credit inside vendored, test or generated files describes that bundled code's lineage, not the
        # target's; ranking it like a project statement lets deps/*/README files crowd out code-search hits.
        bundled = context(ref["path"], "") != "application"
        rank = 30 if relation and bundled else 90 if relation and doc else 75 if relation else 25 if doc else 10
        add(ref["repository"] + ("@" + ref["ref"] if ref.get("ref") else ""), f"Target reference at {ref['path']}:{ref['line']}: {ref['text'][:220]}", rank)
    trail.append({"action": "target evidence", "detail": f"Extracted {len(ranked)} non-self repository references; these are leads, not ancestry findings"})

    def search(kind, query):
        try:
            data = client.get("/search/" + kind + "?" + urlencode({"q": query, "per_page": 10}))
            items = data.get("items", [])
            trail.append({"action": "code search" if kind == "code" else "repository search", "query": query, "status": f"{len(items)} results", "results": [x.get("html_url", x.get("full_name")) for x in items]})
            if data.get("incomplete_results"):
                trail.append({"action": "search limitation", "detail": "GitHub marked search incomplete", "query": query})
            for position, item in enumerate(items):
                name = item.get("repository", {}).get("full_name") if kind == "code" else item.get("full_name")
                if name:
                    rank = (60 if own_source(item.get("path")) else 45) if kind == "code" else 35
                    add(name, f"GitHub {kind} search: {query}" + ("; " + item["html_url"] if item.get("html_url") else ""), rank,
                        query=query if kind == "code" else None, position=position)
            return True
        except AcquisitionError as e:
            trail.append({"action": "code search" if kind == "code" else "repository search", "query": query, "status": "failed: " + str(e)})
            return False

    # Distinctive lexical identifiers are a route beyond explicit acknowledgements.
    # Names defined in the same file are searched together: both must appear in one result file.
    groups = inventory.get("search_terms") or [[s] for s in inventory["symbols"]]
    for group in groups[:3]:
        if not search("code", " ".join('"' + s + '"' for s in group)):
            break  # repeated 401/rate-limit requests are useless
    # Query names actually present in target acknowledgements, never a built-in mapping.
    relation_names = []
    for ref in inventory["references"]:
        if DERIVATION.search(ref.get("statement", ref["text"])) or INFLUENCE.search(ref.get("statement", ref["text"])):
            n = ref["repository"].split("/")[-1]
            if n not in relation_names:
                relation_names.append(n)
    for name in relation_names[:2]:
        search("repositories", name + " in:name")
    # README title gives a fallback even for local folders/archives without remotes.
    title = next((line.lstrip("# ").strip() for f in inventory["files"] if re.search(r"(^|/)readme", f["path"], re.I)
                  for line in f["text"].splitlines()[:15] if line.startswith("# ")), "")
    terms = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", title)
    query = " ".join(terms[:3]) or (target.get("repository", "").split("/")[-1] or Path(target["input"]).stem)
    if query:
        search("repositories", query + " in:name,description,readme")
    if ai:
        try:
            for name in ai.suggest(target, inventory):
                add(name, "Unverified optional AI suggestion derived from target; requires deterministic evaluation", 40)
            trail.append({"action": "AI lead suggestion", "detail": "Candidate names proposed; none accepted as ancestry without independent evidence"})
        except (AcquisitionError, ValueError, OSError) as e:
            trail.append({"action": "AI lead suggestion", "status": "failed: " + str(e)})
    if exclude:
        trail.append({"action": "operator exclusion", "detail": f"Excluded {', '.join(sorted(exclude))}; dropped {sum(excluded.values())} matching leads"})
    ordered = sorted(ranked.values(), key=lambda x: (-x["rank"], x["position"], x["name"].lower()))[:MAX_LEADS]
    return OrderedDict((r["name"], sorted(r["reasons"], key=lambda reason: (-r["reasons"][reason], reason))[:8]) for r in ordered), trail
