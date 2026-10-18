"""Portable, append-by-new-case investigation records and deterministic replay."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .acquire import AcquisitionError, acquire_local
from .compare import MIN_MATCH, SHINGLE, MAX_PAIRS, MAX_DIFF_WORK, compare
from .inventory import MAX_FILE_TOKENS, MAX_TOTAL_TOKENS, inspect
from .report import render


def public_inventory(inv: dict) -> dict:
    return {**inv, "files": [{k: v for k, v in f.items() if k not in {"text", "tokens", "token_lines"}} for f in inv["files"]]}


def save(case: dict, path: Path) -> None:
    (path / "case.json").write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (path / "report.md").write_text(render(case), encoding="utf-8")


def investigate(target: str, candidates: list[str], path: Path, *, discover: bool = False, client=None, max_candidates: int = 4, ai=None, follow_up: Path | None = None) -> dict:
    if path.exists() and any(path.iterdir()):
        raise AcquisitionError("Case directory is not empty; choose a new case directory to preserve prior evidence")
    path.mkdir(parents=True, exist_ok=True)
    case = {"id": uuid.uuid4().hex[:12], "version": __version__, "created_at": datetime.now(timezone.utc).isoformat(),
            "parameters": {"shingle_tokens": SHINGLE, "min_match_tokens": MIN_MATCH, "max_pairs": MAX_PAIRS, "max_diff_work": MAX_DIFF_WORK, "max_file_tokens": MAX_FILE_TOKENS, "max_total_tokens": MAX_TOTAL_TOKENS, "max_candidates": max_candidates},
            "comparisons": [], "discovery": [], "leads": [], "limitations": [
                "Analysis is bounded: 1 MB per file, 50 MB per snapshot, 10,000 files; ignored build/dependency directories and non-UTF-8/binary files are not analyzed.",
                "Only supported source extensions are compared. Python uses native tokenization, normalizes quote style and removes docstrings; other languages/Python syntax failures use a heuristic lexer.",
                "Source token limits: 30,000 per file and 200,000 per snapshot. Coverage is measured only within eligible analyzed application files, not the whole repository.",
                "At most 60 candidate file pairs per repository are selected; pairs exceeding 500,000 estimated token-equality operations are skipped and recorded; heavy rewrites, short code, and cross-language ports may be missed.",
                "Confidence is a transparent rule-based label, not a statistically calibrated probability.",
                "Local Git-ignored files and obvious credential filenames are excluded. This is not a comprehensive secret scanner; snapshots may contain private source.",
                "License files are reported as evidence; no legal conclusion about license compatibility or compliance is made."]}
    inventories = {}

    def acquire(value: str, label: str) -> dict:
        snapshot = path / "snapshots" / label
        if client is not None and not Path(value).expanduser().exists():
            info = client.acquire(value, snapshot)
        else:
            info = acquire_local(value, snapshot)
        inv = inspect(snapshot)
        info.update(snapshot=snapshot.relative_to(path).as_posix(), inventory=public_inventory(inv))
        inventories[label] = inv
        return info

    case["target"] = acquire(target, "target")
    leads = {}
    for c in candidates:
        leads[c] = ["Explicit candidate supplied by operator"]
    if follow_up:
        previous = json.loads((follow_up / "case.json").read_text())
        case["previous_case"] = {"id": previous["id"], "path": str(follow_up.resolve()), "target_digest": previous["target"]["inventory"]["digest"]}
        for c in previous["comparisons"]:
            leads.setdefault(c["candidate"]["input"], []).append("Revisited from prior case " + previous["id"])
    if discover:
        if client is None:
            raise AcquisitionError("Discovery requires a GitHub client")
        from .discovery import find_candidates
        found, trail = find_candidates(case["target"], inventories["target"], client, ai=ai)
        case["discovery"] = trail
        for name, reasons in found.items():
            leads.setdefault(name, []).extend(reasons)
    else:
        case["limitations"].append("Independent discovery was disabled by the operator.")
    for index, (value, reasons) in enumerate(leads.items()):
        lead = {"repository": value, "provenance": reasons, "status": "not examined: candidate budget"}
        case["leads"].append(lead)
        if index >= max_candidates:
            continue
        try:
            candidate = acquire(value, "candidate-" + str(index + 1))
            result = compare(inventories["target"], inventories["candidate-" + str(index + 1)])
            from .assessment import assess
            result = assess(result, case["target"], candidate)
            result.update(candidate=candidate, provenance=reasons)
            case["comparisons"].append(result)
            lead["status"] = result["verdict"]
        except (AcquisitionError, OSError, ValueError) as e:
            lead["status"] = "failed: " + str(e)
        save(case, path)
    if ai:
        case["ai"] = ai.interpret(case)
        case["ai_audit"] = ai.calls
    if follow_up:
        prior = {c["candidate"]["input"]: c["verdict"] for c in previous["comparisons"]}
        case["changes"] = {"target_changed": previous["target"]["inventory"]["digest"] != case["target"]["inventory"]["digest"],
                           "verdict_changes": [{"candidate": c["candidate"]["input"], "before": prior[c["candidate"]["input"]], "after": c["verdict"]} for c in case["comparisons"] if c["candidate"]["input"] in prior and prior[c["candidate"]["input"]] != c["verdict"]]}
    if client:
        case["requests"] = client.trail
    save(case, path)
    return case


def replay(path: Path) -> dict:
    case = json.loads((path / "case.json").read_text(encoding="utf-8"))
    if case["version"] != __version__:
        raise AcquisitionError("Replay requires matching Fossil version: " + case["version"])
    expected = {"shingle_tokens": SHINGLE, "min_match_tokens": MIN_MATCH, "max_pairs": MAX_PAIRS, "max_diff_work": MAX_DIFF_WORK, "max_file_tokens": MAX_FILE_TOKENS, "max_total_tokens": MAX_TOTAL_TOKENS}
    if any(case.get("parameters", {}).get(k) != v for k, v in expected.items()):
        raise AcquisitionError("Replay method parameters do not match this Fossil version")
    # Never follow snapshot paths from an untrusted ledger outside the case.
    def load(item):
        root = (path / item["snapshot"]).resolve()
        if not root.is_relative_to(path.resolve()) or root == path.resolve():
            raise AcquisitionError("Unsafe snapshot path in case")
        inv = inspect(root)
        if inv["digest"] != item["inventory"]["digest"]:
            raise AcquisitionError("Snapshot integrity check failed: " + item["input"])
        if public_inventory(inv) != item["inventory"]:
            raise AcquisitionError("Snapshot-derived inventory does not match case ledger: " + item["input"])
        return inv
    target = load(case["target"])
    from .assessment import assess
    for old in case["comparisons"]:
        candidate = load(old["candidate"])
        new = assess(compare(target, candidate), {**case["target"], "inventory": public_inventory(target)}, {**old["candidate"], "inventory": public_inventory(candidate)})
        for key in ("verdict", "direction", "matches", "application_token_coverage", "confidence", "documentary", "scope", "skipped_pairs"):
            if new[key] != old[key]:
                raise AcquisitionError("Replay mismatch: " + key)
    return case
