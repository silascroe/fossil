# Fossil investigation

Target: **https://github.com/pallets-eco/flask-caching**

Case `f338b767d111` · Fossil 0.1.0 · 2026-10-17T23:39:07.765115+00:00

## Finding

- **https://github.com/django-q2/django-q2**: `not_established`; confidence: insufficient. Available evidence does not establish a meaningful relationship. Similar descriptions, conventions, licenses, and dependencies do not establish ancestry.

Confidence labels describe evidence strength, not calibrated probabilities. No finding is a plagiarism or legal judgment.

## Scope and timeline

### https://github.com/pallets-eco/flask-caching

70 text files; 32 source files; snapshot `ca5774270c746eb0670cc2dabb055ea4cf6c966c85f880cbeedd9fe143c2b6e1`.
Revision `0d131e699e978db12dfc22e511b79c4e7e1bfc9a`; dirty working tree: False; shallow history: True.
Sampled 265 commits (limit 500): committed dates 2022-05-13T10:51:01-03:00 through 2026-10-06T21:18:27+02:00.
GitHub repository created: 2016-07-04T19:53:57Z. Repository creation is not code publication or authorship.
Dependencies: cachelib, flask.
License/notice evidence: [LICENSE](https://github.com/pallets-eco/flask-caching/blob/0d131e699e978db12dfc22e511b79c4e7e1bfc9a/LICENSE) (`1f3c445faa26eb32d90291228510e2d8594bd1fe15463f5d70c87d44f38872fd`).
License/notice evidence: [docs/license.rst](https://github.com/pallets-eco/flask-caching/blob/0d131e699e978db12dfc22e511b79c4e7e1bfc9a/docs/license.rst) (`7729328f7b1ce664dbf630f077581cdfe97379b58b49e9a4f20c63912a5e5c09`).

### https://github.com/django-q2/django-q2

120 text files; 69 source files; snapshot `06bcfba62a1ecc19381bf123b3bb86956171e6002ff54005add64f44738f96c3`.
Revision `d9814a4d63c0da9446014c5b326cd202f5440422`; dirty working tree: False; shallow history: True.
Sampled 271 commits (limit 500): committed dates 2020-07-13T17:21:32+02:00 through 2026-10-13T16:56:40+02:00.
GitHub repository created: 2022-09-03T22:01:52Z. Repository creation is not code publication or authorship.
Dependencies: asgiref, backports-zoneinfo, django, django-picklefield, importlib-metadata, sphinx-rtd-theme, sqlparse, typing-extensions, tzdata, zipp.
License/notice evidence: [LICENSE](https://github.com/django-q2/django-q2/blob/d9814a4d63c0da9446014c5b326cd202f5440422/LICENSE) (`f1aa85367a2ac13f9798651a429be00ccb8dc11ce76bc2c6092d0b4e5555875c`).

Dates can be rewritten, imported, or inherited. The earliest sampled commit is not automatically an origin date.

## Hypotheses and evidence

### https://github.com/django-q2/django-q2

Hypothesis: a meaningful relationship to the target. Decision: **not_established**.

Available evidence does not establish a meaningful relationship. Similar descriptions, conventions, licenses, and dependencies do not establish ancestry.

Direction: undetermined.

Lead provenance:
- Explicit candidate supplied by operator

Application token coverage: 0.0%; 0 matched application files. This is a bounded lexical measurement, not an ancestry probability.

Shared dependencies (context only): none detected.

No sufficiently distinctive contiguous source match passed the threshold. This rejects this lead under the tested methods; it does not prove unrelatedness.

Alternative explanations: shared upstream sources, templates, vendored modules, and independent implementation remain relevant. Matching identifiers and long contiguous blocks are stronger than shared descriptions, but do not by themselves identify who copied whom.

## Discovery trail

- django-q2/django-q2: not_established; Explicit candidate supplied by operator

## Uncertainty and reproducibility

- Analysis is bounded: 1 MB per file, 50 MB per snapshot, 10,000 files; ignored build/dependency directories and non-UTF-8/binary files are not analyzed.
- Only supported source extensions are compared. Python uses native tokenization, normalizes quote style and removes docstrings; other languages/Python syntax failures use a heuristic lexer.
- Source token limits: 30,000 per file and 200,000 per snapshot. Coverage is measured only within eligible analyzed application files, not the whole repository.
- At most 60 candidate file pairs per repository are selected; pairs exceeding 500,000 estimated token-equality operations are skipped and recorded; heavy rewrites, short code, and cross-language ports may be missed.
- Confidence is a transparent rule-based label, not a statistically calibrated probability.
- Local Git-ignored files and obvious credential filenames are excluded. This is not a comprehensive secret scanner; snapshots may contain private source.
- License files are reported as evidence; no legal conclusion about license compatibility or compliance is made.
- Independent discovery was disabled by the operator.
- https://github.com/pallets-eco/flask-caching: Git history limited to depth 200 and up to 500 sampled commits; cached revision reused unless --refresh is supplied.
- https://github.com/django-q2/django-q2: Git history limited to depth 200 and up to 500 sampled commits; cached revision reused unless --refresh is supplied.

The case contains the acquired text snapshots, SHA-256 file manifest, query/request trail, sampled Git history, comparisons, and algorithm parameters. Run `fossil replay PATH_TO_CASE` to verify snapshot hashes and recompute comparisons offline. Replay verifies this saved sample and recorded method, not authenticity of the editable external metadata/history ledger, completeness of the internet, or historical truth.
