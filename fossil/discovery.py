"""Target-derived leads, bounded searches, explicit failures, no built-in ancestors."""
from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlencode

from .acquire import AcquisitionError, repo_name
from .assessment import DERIVATION, INFLUENCE


MAX_LEADS = 24


def find_candidates(target: dict, inventory: dict, client, *, ai=None) -> tuple[dict, list]:
    ranked = {}
    trail = []
    own = target.get("repository", "").lower()

    def add(name: str, reason: str, rank: int):
        base, sep, ref = name.partition("@")
        valid = repo_name(base)
        if valid and sep:
            valid += "@" + ref
        if not valid or valid.lower() == own:
            return
        key = valid.lower()
        if key not in ranked:
            ranked[key] = {"name": valid, "rank": rank, "reasons": {}}
        ranked[key]["rank"] = max(ranked[key]["rank"], rank)
        ranked[key]["reasons"][reason] = max(rank, ranked[key]["reasons"].get(reason, 0))

    meta = target.get("metadata", {})
    for key in ("parent", "source"):
        if meta.get(key):
            add(meta[key]["full_name"], "GitHub fork " + key + " metadata", 100)
    for ref in inventory["references"]:
        relation = bool(DERIVATION.search(ref.get("statement", ref["text"])) or INFLUENCE.search(ref.get("statement", ref["text"])))
        doc = bool(re.search(r"readme|notice|copying|licen[cs]e|authors|credits|history", ref["path"], re.I))
        rank = 90 if relation and doc else 75 if relation else 25 if doc else 10
        add(ref["repository"] + ("@" + ref["ref"] if ref.get("ref") else ""), f"Target reference at {ref['path']}:{ref['line']}: {ref['text'][:220]}", rank)
    trail.append({"action": "target evidence", "detail": f"Extracted {len(ranked)} non-self repository references; these are leads, not ancestry findings"})

    def search(kind, query):
        try:
            data = client.get("/search/" + kind + "?" + urlencode({"q": query, "per_page": 5}))
            items = data.get("items", [])
            trail.append({"action": "code search" if kind == "code" else "repository search", "query": query, "status": f"{len(items)} results", "results": [x.get("html_url", x.get("full_name")) for x in items]})
            if data.get("incomplete_results"):
                trail.append({"action": "search limitation", "detail": "GitHub marked search incomplete", "query": query})
            for item in items:
                name = item.get("repository", {}).get("full_name") if kind == "code" else item.get("full_name")
                if name:
                    add(name, f"GitHub {kind} search: {query}" + ("; " + item["html_url"] if item.get("html_url") else ""), 60 if kind == "code" else 35)
            return True
        except AcquisitionError as e:
            trail.append({"action": "code search" if kind == "code" else "repository search", "query": query, "status": "failed: " + str(e)})
            return False

    # Distinctive lexical identifiers are a route beyond explicit acknowledgements.
    for symbol in inventory["symbols"][:3]:
        if not search("code", '"' + symbol + '"'):
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
    ordered = sorted(ranked.values(), key=lambda x: (-x["rank"], x["name"].lower()))[:MAX_LEADS]
    return OrderedDict((r["name"], sorted(r["reasons"], key=lambda reason: (-r["reasons"][reason], reason))[:8]) for r in ordered), trail
