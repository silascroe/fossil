"""Readable reports are projections of the saved evidence ledger."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import quote


def safe(value: object) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").replace("[", "\\[").replace("]", "\\]").replace("<", "&lt;").replace(">", "&gt;").replace("`", "'")


def source_link(item: dict, path: str, lines: list[int] | None = None) -> str:
    sha = item.get("git", {}).get("head")
    if item.get("repository") and sha:
        url = "https://github.com/" + item["repository"] + "/blob/" + sha + "/" + quote(path)
        if lines:
            url += f"#L{lines[0]}-L{lines[1]}"
    else:
        url = quote(item["snapshot"] + "/" + path)
        if lines:
            url += f"#L{lines[0]}"
    return f"[{safe(path)}]({url})"


def render(case: dict) -> str:
    target = case["target"]
    out = ["# Fossil investigation", "", f"Target: **{safe(target['input'])}**", "",
           f"Case `{case['id']}` · Fossil {case['version']} · {case['created_at']}", "",
           "## Finding", ""]
    if not case["comparisons"]:
        out += ["No candidate was successfully compared. A meaningful relationship **was not established**. This is not proof of independent origin.", ""]
    for c in case["comparisons"]:
        out += [f"- **{safe(c['candidate']['input'])}**: `{c['verdict']}`; confidence: {safe(c['confidence'])}. {c['explanation']}"]
    if case.get("changes"):
        out += ["", f"Follow-up of case `{case['previous_case']['id']}`: target changed: {case['changes']['target_changed']}."]
        for change in case["changes"]["verdict_changes"]:
            out += [f"- {safe(change['candidate'])}: `{change['before']}` → `{change['after']}`"]
    out += ["", "Confidence labels describe evidence strength, not calibrated probabilities. No finding is a plagiarism or legal judgment.", "", "## Scope and timeline", ""]
    for item in [target] + [c["candidate"] for c in case["comparisons"]]:
        inv, h = item["inventory"], item["git"]
        out += [f"### {safe(item['input'])}", "", f"{len(inv['files'])} text files; {inv['source_files']} source files; snapshot `{inv['digest']}`."]
        if h.get("available"):
            out += [f"Revision `{h['head']}`; dirty working tree: {h['dirty']}; shallow history: {h['shallow']}."]
            if h["commits"]:
                oldest = min(h["commits"], key=lambda x: x["committed"])
                newest = max(h["commits"], key=lambda x: x["committed"])
                out += [f"Sampled {len(h['commits'])} commits (limit {h['log_limit']}): committed dates {oldest['committed']} through {newest['committed']}."]
        else:
            out += ["Git history unavailable."]
        meta = item.get("metadata", {})
        if meta.get("created_at"):
            out += [f"GitHub repository created: {meta['created_at']}. Repository creation is not code publication or authorship."]
        out += ["Dependencies: " + (", ".join(safe(x) for x in inv["dependencies"][:40]) or "none detected") + "."]
        for license in inv["licenses"][:10]:
            out += [f"License/notice evidence: {source_link(item, license['path'])} (`{license['sha256']}`)."]
        out += [""]
    out += ["Dates can be rewritten, imported, or inherited. The earliest sampled commit is not automatically an origin date.", "", "## Hypotheses and evidence", ""]
    for c in case["comparisons"]:
        candidate = c["candidate"]
        out += [f"### {safe(candidate['input'])}", "", f"Hypothesis: a meaningful relationship to the target. Decision: **{c['verdict']}**.", "", c["explanation"], "", f"Direction: {safe(c['direction'])}.", "", "Lead provenance:"]
        for reason in c.get("provenance", []):
            out += [f"- {safe(reason)}"]
        for e in c.get("documentary", []):
            out += [f"- Target statement at {source_link(target, e['path'], [e['line'], e['line']])}: {safe(e['text'])}"]
        if c.get("shared_commits"):
            out += [f"Shared commit IDs ({len(c['shared_commits'])} sampled): " + ", ".join(f"`{s}`" for s in c["shared_commits"][:8]) + "."]
        out += ["", f"Application token coverage: {c['application_token_coverage']:.1%}; {c['matched_application_files']} matched application files. This is a bounded lexical measurement, not an ancestry probability.", "",
                "Shared dependencies (context only): " + (", ".join(safe(x) for x in c["shared_dependencies"][:40]) or "none detected") + ".", ""]
        if c.get("skipped_pairs"):
            out += [f"{len(c['skipped_pairs'])} file pairs skipped by the deterministic diff work budget; see case.json for paths. A negative result is incomplete for those pairs.", ""]
        if not c["matches"]:
            out += ["No sufficiently distinctive contiguous source match passed the threshold. This rejects this lead under the tested methods; it does not prove unrelatedness.", ""]
        for m in c["matches"][:12]:
            a, b = m["target_lines"], m["candidate_lines"]
            out += [f"- {m['kind']}: {m['tokens']} tokens; context: {safe(m['context'])}.",
                    f"  Target {source_link(target, m['target_path'], a)} lines {a[0]}–{a[1]}; candidate {source_link(candidate, m['candidate_path'], b)} lines {b[0]}–{b[1]}.",
                    f"  Token fingerprint `{m['token_sha256']}`.", "", "Example from target (untrusted source text):", "", "````text", m["example"].replace("````", "''''"), "````", ""]
        if len(c["matches"]) > 12:
            out += [f"{len(c['matches'])-12} further matches are recorded in case.json.", ""]
        out += ["Alternative explanations: shared upstream sources, templates, vendored modules, and independent implementation remain relevant. Matching identifiers and long contiguous blocks are stronger than shared descriptions, but do not by themselves identify who copied whom.", ""]
    out += ["## Discovery trail", ""]
    for event in case.get("discovery", []):
        out += [f"- {safe(event['action'])}: {safe(event.get('query', event.get('detail', '')))}" + (f" → {safe(event['status'])}" if event.get("status") else "")]
    for lead in case.get("leads", []):
        out += [f"- {safe(lead['repository'])}: {safe(lead['status'])}; " + "; ".join(safe(x) for x in lead["provenance"])]
    if case.get("ai"):
        out += ["", "## Optional AI notes (unverified interpretation)", "", safe(case["ai"])]
    out += ["", "## Uncertainty and reproducibility", ""]
    for note in case["limitations"]:
        out += ["- " + safe(note)]
    for item in [target] + [c["candidate"] for c in case["comparisons"]]:
        for note in item.get("warnings", []) + item["inventory"].get("warnings", []):
            out += [f"- {safe(item['input'])}: {safe(note)}"]
    out += ["", "The case contains the acquired text snapshots, SHA-256 file manifest, query/request trail, sampled Git history, comparisons, and algorithm parameters. Run `fossil replay PATH_TO_CASE` to verify snapshot hashes and recompute comparisons offline. Replay verifies this saved sample and recorded method, not authenticity of the editable external metadata/history ledger, completeness of the internet, or historical truth.", ""]
    return "\n".join(out)
