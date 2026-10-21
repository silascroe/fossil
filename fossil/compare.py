"""Conservative overlap evidence. No similarity score is a plagiarism score."""
from __future__ import annotations

import hashlib
import heapq
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher

SHINGLE = 25
MIN_MATCH = 80
MAX_PAIRS = 60
MAX_DIFF_WORK = 500_000


def informative(tokens: list[str]) -> bool:
    ids = {t for t in tokens if re.fullmatch(r"[A-Za-z_$][\w$]*", t)}
    return len(tokens) >= MIN_MATCH and len(ids) >= 16


def shingles(tokens: list[str]) -> set[bytes]:
    # Every offset preserves matches after insertions; stable digests allow replay.
    return {hashlib.blake2b("\x1f".join(tokens[i:i + SHINGLE]).encode(), digest_size=12).digest()
            for i in range(0, len(tokens) - SHINGLE + 1)}


def compare(target: dict, candidate: dict) -> dict:
    left = [f for f in target["files"] if f["source"] and informative(f["tokens"])]
    right = [f for f in candidate["files"] if f["source"] and informative(f["tokens"])]
    index = defaultdict(set)
    for j, f in enumerate(right):
        prints = shingles(f["tokens"])
        for h in prints:
            index[h].add(j)
    pairs = []
    pair_count = 0
    for i, f in enumerate(left):
        counts = defaultdict(int)
        for h in shingles(f["tokens"]):
            for j in index.get(h, ()):
                counts[j] += 1
        for j, count in counts.items():
            if count >= 3:
                pair_count += 1
                score = (count, -i, -j)
                if len(pairs) < MAX_PAIRS:
                    heapq.heappush(pairs, score)
                elif score > pairs[0]:
                    heapq.heapreplace(pairs, score)
    matches = []
    skipped_pairs = []
    covered = defaultdict(list)
    for _, neg_i, neg_j in sorted(pairs, reverse=True):
        a, b = left[-neg_i], right[-neg_j]
        if a["sha256"] == b["sha256"]:
            blocks = [(0, 0, len(a["tokens"]))]
            kind = "exact_source"
        elif a["tokens"] == b["tokens"]:
            blocks = [(0, 0, len(a["tokens"]))]
            kind = "normalized_source"
        else:
            ca, cb = Counter(a["tokens"]), Counter(b["tokens"])
            work = sum(n * cb[t] for t, n in ca.items())
            if work > MAX_DIFF_WORK:
                skipped_pairs.append({"target_path": a["path"], "candidate_path": b["path"], "reason": "deterministic diff work budget exceeded", "estimated_work": work})
                continue
            blocks = [(m.a, m.b, m.size) for m in SequenceMatcher(None, a["tokens"], b["tokens"], autojunk=False).get_matching_blocks()]
            kind = "contiguous_tokens"
        valid = [(x, y, n) for x, y, n in blocks if informative(a["tokens"][x:x+n])]
        for x, y, n in sorted(valid, key=lambda block: -block[2])[:3]:
            al = [a["token_lines"][x], a["token_lines"][x+n-1]]
            bl = [b["token_lines"][y], b["token_lines"][y+n-1]]
            if al[1] - al[0] < 4 or bl[1] - bl[0] < 4:
                continue
            ctx = "application" if a["context"] == b["context"] == "application" else a["context"] + " / " + b["context"]
            matches.append({"kind": kind, "target_path": a["path"], "candidate_path": b["path"],
                            "target_lines": al, "candidate_lines": bl, "tokens": n, "context": ctx,
                            "target_sha256": a["sha256"], "candidate_sha256": b["sha256"],
                            "example": "\n".join(a["text"].splitlines()[al[0]-1:min(al[1], al[0]+10)]),
                            "token_sha256": hashlib.sha256("\x1f".join(a["tokens"][x:x+n]).encode()).hexdigest()})
            if ctx == "application":
                covered[a["path"]].append((x, x+n))
    matched_tokens = 0
    for intervals in covered.values():
        end = 0
        for a, b in sorted(intervals):
            matched_tokens += max(0, b - max(end, a))
            end = max(end, b)
    total = sum(len(f["tokens"]) for f in left if f["context"] == "application")
    app = [m for m in matches if m["context"] == "application"]
    verdict = "code_overlap" if app else "component_overlap" if matches else "not_established"
    return {"verdict": verdict, "confidence": "high (overlap only)" if app else "limited" if matches else "insufficient",
            "direction": "undetermined", "matches": matches, "shared_dependencies": sorted(set(target["dependencies"]) & set(candidate["dependencies"])),
            "application_token_coverage": round(matched_tokens / total, 4) if total else 0,
            "matched_application_files": len(covered), "pairs_considered": pair_count, "pairs_examined": len(pairs) - len(skipped_pairs), "skipped_pairs": skipped_pairs,
            "limitations": ["Identifier-preserving token matches miss heavy rewrites and cross-language ports.",
                            "A matching component may come from a third upstream or template; overlap alone cannot establish direction."]}
