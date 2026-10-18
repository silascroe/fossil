# Fossil: real-repository demonstration

Run date: 2026-10-17T23:39:06.228534+00:00. No LLM was used. The program made its own GitHub HTTP/Git reads. No investigated project was executed or changed.

## Verification

Command: `fossil investigate django-q2/django-q2 --candidate Koed00/django-q --no-discovery --case examples/verification`

The pair was supplied as a known relationship. Result: **corroborated_derivation**, with 49 source-match blocks and 32.23% coverage of eligible analyzed application tokens. Two expensive file-pair diffs were skipped by the work budget, explicitly recorded. The target README's fork declaration and GitHub fork metadata corroborate the matching source. This is specific evidence, not name recognition.

Target revision: `d9814a4d63c0da9446014c5b326cd202f5440422`. Candidate revision: `85baaccd2c3adfe0a414d4237465163e9ff6e5a0`. See [verification report](../examples/verification/report.md) for pinned source/line examples and observed timeline.

## Discovery

Command: `fossil investigate django-q2/django-q2 --max-candidates 3 --case examples/discovery`

**No ancestor/candidate was supplied.** The discovery code contains no project-specific mappings. It inspected the target, extracted fork/reference evidence, generated code-symbol and repository queries, and selected candidates itself. It found:

| Candidate | Finding | Evidence |
|---|---|---|
| Koed00/django-q | corroborated project derivation | fork metadata/declaration plus 49 source matches |
| althonos/pronto at 3384010dfb4fc7c66a219f59276adef3288a886b | corroborated component | multiline attribution in django_q/queues.py plus 85-token contiguous match |
| adamspd/django-appointment | relationship not established | search-generated hypothesis rejected; no qualifying source matches |

The Pronto lead came from a component's source comment, not a supplied candidate or README parent list. Fossil followed its historical commit even though it was not the candidate's current head. Matching code: [target queue](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/django_q/queues.py#L11-L52) and [historical Pronto utility](https://github.com/althonos/pronto/blob/3384010dfb4fc7c66a219f59276adef3288a886b/pronto/utils.py#L186-L244). The source also acknowledges Eli Bendersky's shared-counter explanation; that is a possible earlier influence, not an independently verified GitHub ancestry finding.

This is a successful evidence-led discovery, **not a difficult attribution-free benchmark**: the relationship was documented in the inspected project. GitHub code search returned HTTP 401 because no token was available; the failure is retained. Repository searches were real, returned noisy leads, and one selected lead was rejected. No claim is made that code-only hidden ancestry discovery was validated. A token enables that search path; a controlled query-generation/result-interpretation test covers it, not a live authenticated benchmark.

See [discovery report](../examples/discovery/report.md) and its ledger for all queries, candidate provenance, rejected/unexamined leads, revisions and uncertainty.

## Restraint

Command: `fossil investigate pallets-eco/flask-caching --candidate django-q2/django-q2 --no-discovery --case examples/restraint`

Both are Python/Django-or-Flask ecosystem utilities with cache-related facilities, but the tested evidence does not establish meaningful ancestry. Result: **not_established**, zero qualifying source matches. This is an inconclusive relationship assessment, not proof that no shared upstream or influence exists. [Restraint report](../examples/restraint/report.md).

## Reproduce offline

Unpack `examples/cases.zip` into `examples/`, preserving its verification/discovery/restraint folders. The bundle contains original acquired snapshots, sampled history and ledgers; licenses/notices are retained with the source.

```sh
fossil replay examples/verification
fossil replay examples/discovery
fossil replay examples/restraint
```

All three were replayed successfully with the final implementation. The original Git/HTTP cache is not required. New online runs can yield different search results or heads; the saved reports pin the actual observed revisions. Metadata/history records are editable observations, not signed proof.
