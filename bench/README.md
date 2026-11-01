# Discovery benchmark

Fossil's demonstrations found ancestry that the target documented itself. This benchmark asks the harder question: **can Fossil find a known upstream from the code alone?**

## Method

[pairs.json](pairs.json) lists 13 targets whose upstream is documented (fork metadata, README declaration, or a vendoring manifest). Eleven are whole-project derivations; two are component cases (pip vendoring requests, hyfetch bundling neofetch). Targets are pinned to exact commits. Long-diverged pairs (gitea/gogs, valkey/redis, lodash/underscore, pypdf/pyPdf) are pinned near the split, so the shared code really is present. These pairs were used to find and fix weaknesses, so results on them are in-sample.

[holdout.json](holdout.json) lists six more pairs (searxng, flask-security, pillow-simd, postman-request, bbolt, mlua) chosen and pinned *before* the improved version was run on them. They are the honest estimate.

Each target is investigated twice, both times as a **local snapshot with no Git history and no GitHub metadata**. That removes fork metadata and shared commits, the two strongest signals in a normal run.

- **intact** keeps every file, so README acknowledgements, license headers and source comments are still available.
- **stripped** deletes READMEs, docs, changelogs, and license, credit and author files. It then blanks every remaining line that contains a GitHub/GitLab URL, attribution phrasing (forked, based on, derived from, inspired by, originally, copied/adapted from, ported), the upstream owner, or its authors' names. Lines are blanked rather than deleted so line numbers still match.

Stripping cannot rename code. Where the package or identifiers still carry the upstream's name, `pairs.json` records it under `leaks`. The target's own repository is passed to `--exclude` so code search cannot "discover" the target itself. Runs use default settings (4 evaluated candidates) with a GitHub token, because code search is the path being measured.

## Scoring

For each run, `score` records whether the true upstream appeared among the discovered leads and at what rank, the verdict if it was evaluated, any other leads from the upstream's fork network (relatives), and any other repository that reached a confirming verdict, labelled by fork network where possible.

## Reproduce

```sh
python bench/run.py prepare [--set holdout]                 # fetch pinned targets, build intact/stripped subjects
GITHUB_TOKEN=... python bench/run.py run --tag v3 [--set holdout]
GITHUB_TOKEN=... python bench/run.py score --tag v3 [--set holdout]   # writes bench/results/v3-<set>.json
```

`--tag` keeps runs from different Fossil versions apart. Runs pause 25 seconds between investigations for the code-search rate limit; reruns within 24 hours reuse cached searches, so a lower `--pause` is safe then.

The working directory defaults to `~/.cache/fossil-bench`. Search results depend on GitHub's live index, so reruns can differ; the saved cases record every query and response digest.

Findings are in [RESULTS.md](RESULTS.md).
