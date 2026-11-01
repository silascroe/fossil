# Fossil design and execution record

The user's brief is the specification: a persistent, evidence-driven CLI investigator with real verification, independent discovery, and restraint demonstrations. External repositories are read-only.

Python 3.11+ and Git; standard library at runtime. Inspect → discover → compare → assess → report. Token shingles shortlist source pairs; contiguous token matches and exact hashes provide examples. Vendored/test/generated material is separate. Documentary statements, shared commits, and fork metadata corroborate ancestry; similarity alone has no direction. Dates are observations, not proof of authorship. Dependencies and licenses never establish ancestry.

Each case preserves a JSON ledger, Markdown report, content-addressed snapshots, requests, queries, rejected hypotheses, revisions, file hashes, parameters, and limitations. A reusable HTTP/Git cache avoids repeated downloads. Discovery begins only from the target: fork metadata, contextual references, then bounded GitHub code searches for pairs of names defined together in the largest core source files, and repository searches from documentation. Credits inside vendored, test or generated files rank below code-search hits, since they describe bundled code rather than the target, and hits inside bundled copies or data files rank below hits in a project's own source. A candidate that confirms overlap can nominate up to two further leads: repositories it names inside the files it shares with the target, or in a relationship statement. Measured in [bench/RESULTS.md](../bench/RESULTS.md). Optional OpenAI-compatible AI can propose leads or interpret evidence, but cannot upgrade deterministic verdicts.

## Native implementation plan (test first)

- [x] Acquisition/inventory/comparison/report vertical slice: local Git projects and ZIPs; traversal/symlink/size protection; exact and modified matches; restraint; pinned portable evidence.
- [x] GitHub discovery/history/cache: bounded read-only requests/clones; source-derived queries; rejected hypotheses; partial histories and failures surfaced; offline replay.
- [x] Optional AI: explicitly enabled, configurable provider, bounded inputs, untrusted repository text treated as data; proposed leads verified before use.
- [x] Demonstrations: known-related pair, target-only independent discovery, unrelated pair; actual network runs, pinned revisions, inspected reports.
- [x] Review/install/docs: regression suite; isolated install and CLI smoke test; fresh whole-branch review; local package without pushing.

## Process decisions

User delegated architecture and requested proportionate process and delivery. Use this concise design/plan and proceed without repeated design gates. Fresh README-only clone, new local branch; no worktree needed to protect an empty checkout. Initial commit 096f632. GitHub connector and read-only HTTP/Git available.

## Progress

Repository inspection complete; no existing application/tests.


Final review: a fresh reviewer reproduced seven important issues (fsmonitor execution, copied credentials, negated/instructional attribution, component scope, unbounded repetitive diff, ledger-trusting replay, ZIP scope). All were fixed with failing regression tests followed by a green full suite. Python-native normalization was added after the real historical queue lead initially had too-short lexical matches. Pair/token budgets intentionally reduce recall and are disclosed. No deferred review findings remain.

Process rulings: use a single deterministic stateful investigator with an optional advisor; no paid live AI call without a supplied model key. Documented ancestry/component discovery was the first benchmark; code-only discovery is measured separately in [bench/](../bench/README.md) on tuning and holdout pairs. Conservative thresholds intentionally reject weak matches; false negatives are preferable to invented ancestry.
