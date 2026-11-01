"""Discovery benchmark: can Fossil find a known upstream when nobody left a note?

Each pair is investigated twice from a local snapshot with no Git history or
GitHub fork metadata: "intact" keeps every file, "stripped" deletes docs,
license/credit files and blanks lines that name the upstream or use
attribution phrasing. Usage (GITHUB_TOKEN is needed for code search):

    python bench/run.py prepare [--set holdout]
    python bench/run.py run --tag v2 [--set holdout] [--only ID ...]
    python bench/run.py score --tag v2 [--set holdout]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from fossil.acquire import extract_zip, git  # noqa: E402

SETS = {"tuning": "pairs.json", "holdout": "holdout.json"}
CONDITIONS = ("intact", "stripped")
DOC_NAME = re.compile(r"(?i)^(readme|changelog|changes|history|news|authors|contributors|credits|notice|licen[cs]e|copying|acknowledg|thanks|maintainers)")
DOC_EXT = {".md", ".rst", ".markdown", ".adoc"}
DOC_DIRS = {"docs", "doc", ".github"}
ATTRIBUTION = re.compile(r"(?i)\b(fork(?:ed)?|based\s+on|derived\s+from|inspired\s+by|originally|copied\s+from|adapted\s+from|port(?:ed)?\s+(?:of|from))\b|(?:github|gitlab)\.com/")
CONFIRMING = {"code_overlap", "component_overlap", "corroborated_derivation", "corroborated_component", "declared_fork", "shared_history"}


def fetch(pair: dict, intact: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "fetch", "-q", "--depth", "1", "https://github.com/" + pair["target"] + ".git", pair["ref"], timeout=900)
        archive = Path(tmp) / "snapshot.zip"
        git(repo, "archive", "--format=zip", "--output=" + str(archive), "FETCH_HEAD", timeout=300)
        extract_zip(archive, intact)


def strip(pair: dict, intact: Path, stripped: Path) -> dict:
    terms = re.compile(r"(?i)\b(?:" + "|".join(pair["terms"]) + r")\b")
    stats = {"files_removed": 0, "lines_blanked": 0}
    for path in sorted(intact.rglob("*")):
        rel = path.relative_to(intact)
        if not path.is_file():
            continue
        if DOC_DIRS & set(rel.parts[:-1]) or DOC_NAME.match(path.name) or path.suffix.lower() in DOC_EXT:
            stats["files_removed"] += 1
            continue
        out = stripped / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            out.write_bytes(raw)
            continue
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if terms.search(line) or ATTRIBUTION.search(line):
                # Blank instead of delete so line numbers stay comparable.
                lines[i] = ""
                stats["lines_blanked"] += 1
        out.write_text("\n".join(lines), encoding="utf-8", newline="")
    return stats


def load(name: str) -> list[dict]:
    return json.loads((ROOT / "bench" / SETS[name]).read_text(encoding="utf-8"))["pairs"]


def prepare(work: Path, pairs: list[dict]) -> None:
    for pair in pairs:
        base = work / "subjects" / pair["id"]
        # A neutral folder name keeps the README-title fallback from leaking the project name.
        intact, stripped = base / "intact" / "subject", base / "stripped" / "subject"
        if stripped.exists():
            print("prepared", pair["id"])
            continue
        print("fetching", pair["target"], pair["ref"][:10], flush=True)
        fetch(pair, intact)
        stats = strip(pair, intact, stripped)
        (base / "strip.json").write_text(json.dumps(stats), encoding="utf-8")
        print("  stripped:", stats, flush=True)


def run(work: Path, pairs: list[dict], tag: str, only: list[str], pause: int) -> None:
    if not (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")):
        sys.exit("Set GITHUB_TOKEN: code search is the path this benchmark measures.")
    for pair in pairs:
        if only and pair["id"] not in only:
            continue
        for condition in CONDITIONS:
            case = work / "cases" / tag / condition / pair["id"]
            if (case / "case.json").exists():
                print("done", condition, pair["id"])
                continue
            subject = work / "subjects" / pair["id"] / condition / "subject"
            cmd = [sys.executable, "-m", "fossil", "investigate", str(subject), "--case", str(case),
                   "--cache", str(work / "cache"), "--exclude", pair["target"]]
            print("running", condition, pair["id"], flush=True)
            started = time.time()
            p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
            (work / "logs").mkdir(parents=True, exist_ok=True)
            (work / "logs" / f"{tag}-{condition}-{pair['id']}.log").write_text(p.stdout + p.stderr, encoding="utf-8")
            print(f"  exit {p.returncode} in {time.time() - started:.0f}s", flush=True)
            time.sleep(pause)  # GitHub allows ~10 authenticated code searches per minute.


class Meta:
    """Cached GitHub repository metadata, used only for scoring relatives."""

    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    def lookup(self, name: str) -> dict:
        key = name.lower()
        if not isinstance(self.data.get(key), dict):
            headers = {"Accept": "application/vnd.github+json", "User-Agent": "fossil-bench"}
            if self.token:
                headers["Authorization"] = "Bearer " + self.token
            try:
                with urlopen(Request("https://api.github.com/repos/" + name, headers=headers), timeout=25) as r:
                    repo = json.loads(r.read())
                self.data[key] = {"name": repo.get("full_name", name).lower(), "network": (repo.get("source") or repo).get("full_name", name).lower()}
            except HTTPError:
                self.data[key] = {"name": key, "network": key}
            self.path.write_text(json.dumps(self.data, indent=1), encoding="utf-8")
        return self.data[key]

    def network(self, name: str) -> str:
        return self.lookup(name)["network"]

    def canonical(self, name: str) -> str:
        # GitHub redirects renamed repositories; kyren/rlua and mlua-rs/rlua are one upstream.
        return self.lookup(name)["name"]


def repository(value: str) -> str:
    return value.removeprefix("https://github.com/").partition("@")[0].lower()


def score(work: Path, pairs: list[dict], tag: str) -> dict:
    meta = Meta(work / "meta.json")
    rows = []
    for pair in pairs:
        upstream = meta.canonical(pair["upstream"])
        upstream_net = meta.network(pair["upstream"])
        target_net = meta.network(pair["target"])
        for condition in CONDITIONS:
            path = work / "cases" / tag / condition / pair["id"] / "case.json"
            if not path.exists():
                continue
            case = json.loads(path.read_text(encoding="utf-8"))
            leads = [meta.canonical(repository(lead["repository"])) for lead in case["leads"]]
            verdicts = {meta.canonical(repository(c["candidate"]["input"])): c for c in case["comparisons"]}
            rank = leads.index(upstream) + 1 if upstream in leads else None
            relatives = [x for x in leads if x != upstream and meta.network(x) == upstream_net]
            found = verdicts.get(upstream)
            others = []
            for name, c in verdicts.items():
                if name != upstream and c["verdict"] in CONFIRMING:
                    relation = "upstream network" if meta.network(name) == upstream_net else "target network" if meta.network(name) == target_net else "unlabelled"
                    others.append({"repository": name, "verdict": c["verdict"], "coverage": c["application_token_coverage"], "relation": relation})
            searches = [e for e in case["discovery"] if e["action"] == "code search"]
            rows.append({
                "id": pair["id"], "kind": pair["kind"], "condition": condition, "upstream": pair["upstream"],
                "lead_rank": rank, "lead_count": len(leads),
                "lead_provenance": next((lead["provenance"] for lead, name in zip(case["leads"], leads) if name == upstream), []),
                "upstream_verdict": found["verdict"] if found else None,
                "upstream_coverage": found["application_token_coverage"] if found else None,
                "upstream_matches": len(found["matches"]) if found else None,
                "upstream_relatives_in_leads": sorted(set(relatives)),
                "other_confirmed": others,
                "code_searches": [{"query": s.get("query"), "status": s.get("status")} for s in searches],
                "target_source_files": case["target"]["inventory"]["source_files"],
                "target_token_warnings": sum(w.startswith("Source token limit") for w in case["target"]["inventory"]["warnings"]),
            })
    return {"tag": tag, "scored_at": datetime.now(timezone.utc).isoformat(), "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("prepare", "run", "score"))
    parser.add_argument("--work", type=Path, default=Path.home() / ".cache" / "fossil-bench")
    parser.add_argument("--set", choices=SETS, default="tuning")
    parser.add_argument("--tag", default="baseline", help="Names a run, so results from different Fossil versions stay apart")
    parser.add_argument("--only", nargs="*", default=[])
    parser.add_argument("--pause", type=int, default=25, help="Seconds between runs, for the code search rate limit")
    args = parser.parse_args()
    work, pairs = args.work.resolve(), load(args.set)
    if args.command == "prepare":
        prepare(work, pairs)
    elif args.command == "run":
        run(work, pairs, args.tag, args.only, args.pause)
    else:
        result = score(work, pairs, args.tag)
        out = ROOT / "bench" / "results" / f"{args.tag}-{args.set}.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        for r in result["rows"]:
            print(f"{r['condition']:8} {r['id']:15} lead_rank={r['lead_rank']} verdict={r['upstream_verdict']} relatives={len(r['upstream_relatives_in_leads'])} others={[o['repository'] for o in r['other_confirmed']]}")


if __name__ == "__main__":
    main()
