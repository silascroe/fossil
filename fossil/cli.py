"""Fossil's local-first command line."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .acquire import AcquisitionError
from .case import investigate, replay


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="fossil", description="Investigate software relationships from verifiable evidence.")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("investigate", help="Inspect a GitHub repo, local directory, or ZIP")
    run.add_argument("target")
    run.add_argument("--candidate", action="append", default=[], help="Optional candidate; repeatable")
    run.add_argument("--no-discovery", action="store_true", help="Only test explicit/prior candidates")
    run.add_argument("--case", type=Path, help="New, empty output directory")
    run.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "fossil")
    run.add_argument("--max-candidates", type=int, default=4, choices=range(1, 11), metavar="1..10")
    run.add_argument("--offline", action="store_true", help="Use cached HTTP/Git data only")
    run.add_argument("--refresh", action="store_true", help="Refresh cached GitHub data")
    run.add_argument("--follow-up", type=Path, help="Revisit candidates from a saved case; preserve the original")
    run.add_argument("--ai", action="store_true", help="Enable optional OpenAI-compatible lead suggestions and interpretation")
    rep = sub.add_parser("replay", help="Verify and recompute a saved case without network access")
    rep.add_argument("case", type=Path)
    hist = sub.add_parser("history", help="List saved investigations")
    hist.add_argument("--cases", type=Path, default=Path.home() / ".fossil" / "cases")
    args = parser.parse_args(argv)
    try:
        if args.command == "history":
            for path in sorted(args.cases.glob("*/case.json")):
                c = json.loads(path.read_text(encoding="utf-8"))
                print(c["created_at"], c["id"], c["target"]["input"], path.parent)
            return 0
        if args.command == "replay":
            c = replay(args.case.resolve())
            print(f"Verified case {c['id']}: snapshot hashes and {len(c['comparisons'])} comparisons reproduced offline.")
            return 0
        if args.offline and args.refresh:
            parser.error("--offline and --refresh are mutually exclusive")
        path = (args.case or Path.home() / ".fossil" / "cases" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")).resolve()
        client = None
        if not args.no_discovery or any(not Path(x).expanduser().exists() for x in [args.target] + args.candidate):
            from .github import GitHub
            client = GitHub(args.cache.resolve(), offline=args.offline, refresh=args.refresh)
        ai = None
        if args.ai:
            from .ai import Advisor
            ai = Advisor()
        case = investigate(args.target, args.candidate, path, discover=not args.no_discovery, client=client,
                           max_candidates=args.max_candidates, ai=ai, follow_up=args.follow_up)
        print("Report:", path / "report.md")
        print("Evidence:", path / "case.json")
        for c in case["comparisons"]:
            print(f"{c['candidate']['input']}: {c['verdict']} ({len(c['matches'])} source matches)")
        if not case["comparisons"]:
            print("No candidate comparison completed; see discovery trail and limitations.")
        return 0
    except (AcquisitionError, OSError, ValueError) as e:
        print("Fossil:", str(e), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Fossil: interrupted; completed evidence may remain in the case directory.", file=sys.stderr)
        return 130
