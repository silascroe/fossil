# Fossil

A local software archaeology investigator. Give Fossil a GitHub repository, directory, or ZIP. It collects evidence, forms upstream hypotheses, searches for candidates, compares source, rejects weak leads, and writes a reproducible case.

**Evidence before ancestry.** A shared dependency, familiar algorithm, or similar description is not proof of copying. Fossil distinguishes observed overlap, declared inspiration, shared Git history, project derivation, and borrowed components. It does not issue plagiarism accusations or legal opinions.

## Install

Requires **Python 3.11+** and **Git** on your PATH. Runtime dependencies: Python's standard library only. Run these from the unpacked project or a checkout containing the implementation:

```sh
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install .
fossil --help
```

Without installing: `python -m fossil --help` from the project directory. This also avoids a command-name conflict if you already use Fossil SCM.

## Investigate

```sh
# Discovery is on by default. No candidate names supplied.
fossil investigate django-q2/django-q2 --case ./cases/django-q2

# Verify a known relationship.
fossil investigate django-q2/django-q2 --candidate Koed00/django-q --no-discovery --case ./cases/verification

# Local, offline comparison. Keep the case OUTSIDE the investigated folders.
fossil investigate ./project --candidate ./possible-upstream --no-discovery --case ./cases/local

# ZIP input: no code is executed, and original directory structure is preserved.
fossil investigate ./project.zip --case ./cases/archive

# Follow a historical lead or pin an exact input revision.
fossil investigate django-q2/django-q2 --candidate althonos/pronto@3384010dfb4fc7c66a219f59276adef3288a886b --no-discovery --case ./cases/queue

# Revisit old hypotheses, compare changed findings, retain the original case.
fossil investigate django-q2/django-q2 --follow-up ./cases/django-q2 --refresh --case ./cases/django-q2-followup

# Verify preserved evidence and recompute conclusions without network access.
fossil replay ./cases/django-q2
fossil history
fossil history --cases ./cases
```

GitHub inputs accept `owner/repo`, `https://github.com/owner/repo`, and an optional `@commit-or-tag`. Private remote Git authentication is not built into v0.1; investigate a local checkout instead. Local input includes tracked and unignored working files and records whether the worktree is dirty. Symlinks are never followed. Git submodules are not fetched.

Git history is collected only when the input directory is a repository root. Nested directories are inspected as files without inheriting an enclosing repository's history; this limitation is recorded in the case.

Default cases go under `~/.fossil/cases`. Cache: `~/.cache/fossil`, override with `--cache`. API cache lifetime is 24 hours. Git revisions are reused until `--refresh`; reports disclose the exact revision and cache status. `--offline` permits cached HTTP/Git only. `replay` needs neither the cache nor GitHub. Do not run refreshes concurrently against the same cache; use separate `--cache` directories for concurrent investigators.

### GitHub search

Public metadata, clones, links, and repository search can work without credentials. **GitHub code search requires a token** with appropriate read access; rate limits also apply:

```sh
# Linux/macOS; use a token from your environment/secret manager.
export GITHUB_TOKEN='your-read-only-token'
# PowerShell equivalent:
# $env:GITHUB_TOKEN='your-read-only-token'
fossil investigate owner/repository --max-candidates 4
```

`GH_TOKEN` is also accepted. Tokens are sent only to api.github.com and are never written into cases or reports. A failed search stays in the trail. Without a token, Fossil still follows direct evidence and tries repository searches, but cannot promise code-only discovery. At most 30 HTTP calls, 3 code searches, 3 repository searches, 24 recorded leads, and 1–10 evaluated candidates (default 4) per run. A failed acquisition consumes a candidate slot. `--max-candidates` controls breadth, not evidence thresholds.

## What the investigator actually does

1. **Preserve:** acquire a Git snapshot without checkout hooks/filters, or copy a local working tree/ZIP into the case. Record file hashes, revisions, dirty/shallow state, sampled commit IDs/dates, license notices, direct dependencies, and exclusions.
2. **Hypothesize:** extract fork metadata, contextual repository acknowledgements (including commit-pinned source comments), distinctive symbols, and README terms. Search GitHub with target-derived queries. Rank documentary leads above generic search hits; record the origin of every candidate.
3. **Test:** index 25-token shingles across filenames, shortlist at most 60 file pairs, then examine exact/normalized source or contiguous token blocks. Retain blocks of at least 80 tokens, 16 distinct identifier-like tokens, and 5 lines. Python parsing removes docstrings and normalizes quote style; other languages use a heuristic lexer. Identifiers are preserved.
4. **Assess:** separate raw lexical evidence from scope and direction. Shared commits establish shared history. Fork metadata is a declaration. Source overlap corroborates an affirmative attribution; a source-file/component attribution does not turn into whole-project ancestry. Vendored, generated, test, and example matches remain visible. Negative/instructional statements do not establish derivation.
5. **Remember:** save findings, rejected/unexamined leads, search failures, method parameters and snapshots. Follow-up cases revisit old candidates and summarize changed verdicts without overwriting the original.

The deterministic workflow is the investigator. There is no need for an agent framework, vector database, server, paid model, or web interface in this version. The uncertainty rules and immutable-by-default case history matter more than simulated agent chatter.

### Optional AI advisor

Enable only when you want semantic candidate suggestions and a concise interpretation of collected evidence. An OpenAI-compatible Chat Completions endpoint is supported:

```sh
export FOSSIL_AI_BASE_URL='https://your-provider.example/v1'
export FOSSIL_AI_MODEL='your-model'
export FOSSIL_AI_KEY='your-key'
fossil investigate owner/repo --ai
```

PowerShell uses `$env:VARIABLE='value'`. Default base URL is `https://api.openai.com/v1`; model selection is explicit. Environment variables are not loaded from `.env` automatically. A localhost HTTP endpoint is allowed for local models.

There are at most two model calls (one lead suggestion, one interpretation), each with at most 24,000 input characters and 1,200 requested output tokens. Your provider may charge. Repository excerpts and findings are sent to that configured provider only when `--ai` is enabled. The advisor has no tools, treats repository text as untrusted, and cannot change deterministic verdicts. Suggested repository names are validated and compared like any other lead. AI notes are clearly unverified; the request/response audit is saved without the key. Provider errors leave deterministic findings usable. This optional path has contract tests with a simulated transport; a paid live model was not used for the demonstrations.

## Reports and evidence

Each case contains:

```text
case.json              structured evidence, hypotheses, requests and verdicts
report.md              readable findings, source links and uncertainty
snapshots/target/      preserved analyzed input
snapshots/candidate-N/  preserved candidate inputs
```

GitHub source links use full commit hashes and line ranges. Local/ZIP evidence links point into the preserved case. Reports give examples, overlap fingerprints, observed chronology, license paths, shared dependencies, alternative explanations, confidence labels, and failed/skipped operations. Confidence describes the strength of specific evidence, not a calibrated ancestry probability.

Replay rebuilds snapshot-derived inventories and documentary evidence, checks hashes and method parameters, and recomputes comparisons. It detects modified snapshots or inconsistent claims. It is **not** a cryptographic signature over the editable GitHub metadata/history ledger and cannot certify historical truth or search completeness.

The three real demonstrations and exact revision/evidence links are in [docs/demonstration.md](docs/demonstration.md). Their full replayable cases are bundled in [examples/cases.zip](examples/cases.zip); extract it into the examples directory before running the documented replay commands. Markdown report copies and ledgers remain directly readable alongside the bundle. Third-party source snapshots retain their projects' license/notice files; they are evidence, not Fossil implementation.

## Limits worth knowing

- This is lexical archaeology, not a semantic equivalence prover. Heavy rewrites, translations, short snippets, renamed identifiers, and undocumented conceptual influences can be missed. Provenance language is heuristic, including negation/scope handling; inspect the quoted statement.
- Discovery is bounded, search-index dependent, and not exhaustive. The live demo demonstrates independently discovered **documented** ancestry and a less obvious component attribution; it does not validate reliable hidden-ancestry discovery from code search without acknowledgements.
- Git history is cloned at depth 200; at most 500 reachable commits are sampled. A shallow boundary is not an origin date. Dates can be rewritten; repository creation does not prove code publication. v0.1 does not search every past revision or perform line-by-line historical origin tracing.
- Files over 1 MB are skipped; snapshots are limited to 50 MB/10,000 entries. ZIPs exceeding the total expanded-size/entry limits are rejected. Binary/non-UTF-8 files, common build/dependency directories, and submodules are excluded. Source sampling is capped at 30,000 tokens/file and 200,000 tokens/snapshot, in deterministic path order. These exclusions reduce recall.
- Expensive modified-file diffs are skipped when estimated token-equality work exceeds 500,000. Exact/normalized equality has a fast path. Every skipped pair is recorded. Coverage uses only eligible analyzed application files; it is not percentage of the entire repository copied.
- Dependency extraction covers package.json, pyproject.toml direct dependencies, requirements text, Cargo.toml and go.mod. It does not resolve full dependency graphs or execute setup/build scripts. Vendoring/context labels are heuristic.
- Common credential filenames and Git-ignored local files are excluded. This is not comprehensive secret scanning. Cases still contain source text and may be private; review before sharing.
- Investigated source/build scripts are never run. Git hooks, fsmonitor, and checkout filters are disabled/avoided, but this is not a VM sandbox for hostile Git binaries or parser vulnerabilities. Keep Python/Git updated.

## Development

```sh
python -m unittest discover -s tests -v
```

The suite covers overlap across renames/format changes, restraint, source/component scope, discovery query generation, history/ref handling, failed searches, HTTP cache/offline use, ZIP traversal and scope, local credential exclusion, disabled fsmonitor, token/diff budgets, follow-up memory, AI transport boundaries, tampered evidence and offline replay. No internet or LLM key is needed for the unit suite. Live demonstrations are separate preserved cases.
