# Discovery benchmark results

Measured 2026-11-01 on Windows 11, Python 3.13, with an authenticated GitHub token and default settings (4 evaluated candidates). Method and pair lists: [README.md](README.md). Raw scores: [results/](results/), where `baseline` is 0.1, `v3` is 0.2, and `v2` is 0.2 without the vendored-credit fix.

**Short version.** With every README, credit, license and attribution line removed, Fossil 0.2 found and confirmed the true upstream in 5 of 13 tuning pairs (0.1: 1 of 13) and 2 of 6 holdout pairs. With documentation intact it confirmed 8 of 13 and 3 of 6. No run confirmed a repository that did not genuinely share code with the target. The tuning numbers are in-sample, because those pairs were used to find the fixes. The holdout numbers are the honest estimate, and six pairs is a small sample.

## Counts

"Confirmed" means the upstream was among the evaluated candidates and reached a verdict backed by source overlap. Renamed repositories count as the same upstream (`kyren/rlua` is `mlua-rs/rlua`).

| Set | Condition | 0.1 found / confirmed | 0.2 found / confirmed |
|---|---|---|---|
| tuning (13) | intact | 10 / 6 | 12 / 8 |
| tuning (13) | stripped | 3 / 1 | 6 / 5 |
| holdout (6) | intact | not run | 4 / 3 |
| holdout (6) | stripped | not run | 2 / 2 |

"Found" counts the upstream anywhere in the 24 recorded leads; most found-but-unconfirmed leads ranked below the four evaluated slots. The holdout was not run on 0.1: its acquisition code failed outright on two of the six targets (a file name containing `:`, and a snapshot over 50 MB), which is one of the fixes below.

## Per pair (upstream lead rank and verdict)

Tuning pairs, 0.1 and 0.2:

| Pair | Intact 0.1 | Intact 0.2 | Stripped 0.1 | Stripped 0.2 |
|---|---|---|---|---|
| django-q2 ← Koed00/django-q | #1 corroborated | #1 corroborated | not found | #1 code overlap |
| flask-caching ← thadeusb/flask-cache | #1 corroborated | #1 corroborated | not found | not found |
| flask-restx ← noirbizarre/flask-restplus | #1 corroborated | #1 corroborated | #8 not evaluated | #1 code overlap |
| niquests ← psf/requests | #23 not evaluated | #20 not evaluated | not found | not found |
| urllib3-future ← urllib3/urllib3 | not found | #21 not evaluated | not found | not found |
| asyncclick ← pallets/click | #1 component | #1 component | not found | #6 not evaluated |
| hyfetch ← dylanaraps/neofetch (component) | #19 not evaluated | #19 not evaluated | not found | not found |
| pip ← psf/requests (component) | not found | not found | not found | not found |
| yt-dlp ← ytdl-org/youtube-dl | #3 corroborated | #2 corroborated | not found | not found |
| valkey ← redis/redis | not found | #3 code overlap | not found | #1 code overlap |
| lodash ← jashkenas/underscore | #19 not evaluated | #21 not evaluated | not found | not found |
| gitea ← gogs/gogs | #13 not evaluated | #3 code overlap | #6 not evaluated | #1 code overlap |
| pypdf ← mfenniak/pyPdf | #4 code overlap | #4 code overlap | #4 code overlap | #4 code overlap |

Holdout pairs, 0.2 only:

| Pair | Intact | Stripped |
|---|---|---|
| searxng ← searx/searx | #1 corroborated | not found |
| flask-security ← pallets-eco/flask-security-3.0 | not found | not found |
| pillow-simd ← python-pillow/Pillow | #5 not evaluated | #4 code overlap |
| postman-request ← request/request | #1 component | #2 code overlap |
| bbolt ← boltdb/bolt | not found | not found |
| mlua ← mlua-rs/rlua | #1 component overlap | not found |

## What changed between 0.1 and 0.2

Each fix came from a diagnosed tuning failure, not from adjusting thresholds:

- Ties among search hits were broken alphabetically, so flask-restplus, the first result in all three searches, ranked 8th. Hits now keep GitHub's result order, and a repository returned by several independent searches outranks single hits.
- Queries used single names taken from build scripts, docs and imports. They now pair two names *defined* in the same core source file, which copied code keeps together and generic vocabulary rarely matches.
- C definitions and shell functions were not recognized (valkey produced no queries), and extensionless shebang scripts were not read as source.
- Vendored files sorted first could exhaust the 200,000-token budget before application code was read; application files now get the budget first.
- Credits inside `deps/` and `vendor/` READMEs ranked like project acknowledgements, filling all four slots ahead of redis and gogs in the intact runs. This was the one case where documentation made results *worse*; fixed in the last round (gitea and valkey intact went from not evaluated to confirmed, nothing else moved).
- Snapshots with names Windows cannot store, or over 50 MB, were rejected outright. They are now skipped or sampled, with every skip recorded.

## Why the misses missed

**Widely vendored libraries** (niquests and urllib3-future against requests/urllib3, pip, asyncclick and yt-dlp when stripped). Code search returns ten results per query, and for popular libraries they fill up with copies sitting in committed virtualenvs, `site-packages`, and apps that bundle the target. Several of those repositories are too large to acquire (over 10,000 entries), and each failed acquisition still uses one of the four slots. In every such run Fossil confirmed real copies of the target instead of its ancestor, and it correctly left the direction undetermined.

**Evolved forks** (flask-caching, searxng, flask-security when stripped). The largest core files of a long-lived fork are mostly code written after the split. Their defined names did not exist upstream, so searches returned zero to two results.

**Rewrites** (mlua). Everything mlua still shares with rlua is in tests and examples. The intact run found rlua by name and correctly called it component overlap only; with names stripped there was nothing left to search for.

**Component pairs** (hyfetch, pip). Queries come from the target's main code, not from the bundled component, so the component's origin is reachable only through acknowledgements.

**Known gaps found during this benchmark, not yet fixed:**

- Go `*_test.go` files are not classified as tests, so bbolt's queries were benchmark and example function names.
- JavaScript function expressions (`name = function(`) are not recognized as definitions, so lodash produced one query instead of three.

## Other repositories that reached a confirming verdict

Every one was checked by hand (description, matched files, and in three cases the files themselves). None was a spurious match. They fall into three groups:

- **Copies or bundles of the target.** Download-manager add-ons carrying `yt_dlp/`, mlua forks, a SearXNG mirror, apps vendoring flask-restx or asyncclick, pipenv and pigar vendoring pip, bbolt mirrors, a Flask-Security-Too 3.4.5 copy.
- **Copies of, or links in, the upstream's lineage.** yt-dlc (the intermediate fork between youtube-dl and yt-dlp, confirmed as a corroborated derivation), a 2011 PyPDF2 mirror, an annotated Redis 7.0, a detached gogs fork, Pillow packaging.
- **Projects vendoring the same third-party code.** Blender add-ons bundling PIL, a test tool bundling `request`.

Fossil reports all of these as overlap with undetermined direction, which is correct. It cannot yet distinguish an ancestor from a descendant without Git history or an acknowledgement, and with acknowledgements stripped it more often finds descendants than ancestors.

## Limits of this measurement

Nineteen pairs, mostly Python, all public on GitHub. Results depend on GitHub's live code index, which changes. The tuning set was used repeatedly. The holdout was chosen before 0.2 ran on it, and its results did not change any code in 0.2. Its failures were looked at, and the gaps they exposed are listed above for the next round, which needs a fresh holdout.
