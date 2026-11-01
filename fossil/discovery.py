"""Target-derived leads, bounded searches, explicit failures, no built-in ancestors."""
from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlencode

from .acquire import AcquisitionError, repo_name
from .assessment import DERIVATION, INFLUENCE
from .inventory import context


MAX_LEADS = 24


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
            rank = min(70, rank + 5 * (len(entry["queries"]) - 1))
        entry["rank"] = max(entry["rank"], rank)
        entry["position"] = min(entry["position"], position)
        entry["reasons"][reason] = max(rank, entry["reasons"].get(reason, 0))

    meta = target.get("metadata", {})
    for key in ("parent", "source"):
        if meta.get(key):
            add(meta[key]["full_name"], "GitHub fork " + key + " metadata", 100)
    for ref in inventory["references"]:
        relation = bool(DERIVATION.search(ref.get("statement", ref["text"])) or INFLUENCE.search(ref.get("statement", ref["text"])))
        doc = bool(re.search(r"readme|notice|copying|licen[cs]e|authors|credits|history", ref["path"], re.I))
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
                    add(name, f"GitHub {kind} search: {query}" + ("; " + item["html_url"] if item.get("html_url") else ""), 60 if kind == "code" else 35,
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
