# Discovery benchmark results

Measured 2026-11-01 on Windows 11, Python 3.13, with an authenticated GitHub token and default settings (4 evaluated candidates). Method and pair lists: [README.md](README.md). Raw scores: [results/](results/), where `baseline` is 0.1, `v3` is 0.2, `v5` is 0.3, and `v2`/`v4` are intermediate drafts of 0.2 and 0.3.

**Short version.** On eight pairs that no version had seen (holdout2), with every README, credit, license and attribution line removed, Fossil 0.3 found and confirmed the true upstream in 5 of 8. 0.2 confirmed 4 of 8 on the same pairs, the same day, against the same cached search results. With documentation intact both confirmed 4 of 8. On the pairs used for tuning the gains look much larger (tuning stripped 5 → 7 of 13, first holdout stripped 2 → 5 of 6), and the out-of-sample result says to discount them: one pair of improvement on eight is honest progress, not proof. No run of any version confirmed a repository that did not genuinely share code with the target.

## Counts

"Confirmed" means the upstream was among the evaluated candidates and reached a verdict backed by source overlap. "Found" counts the upstream anywhere in the recorded leads. Renamed repositories count as the same upstream (`kyren/rlua` is `mlua-rs/rlua`, `mishoo/UglifyJS2` is `mishoo/UglifyJS`).

| Set | Condition | 0.1 found / confirmed | 0.2 found / confirmed | 0.3 found / confirmed |
|---|---|---|---|---|
| tuning (13) | intact | 10 / 6 | 12 / 8 | 12 / 8 |
| tuning (13) | stripped | 3 / 1 | 6 / 5 | 7 / 7 |
| holdout (6) | intact | not run | 4 / 3 | 4 / 4 |
| holdout (6) | stripped | not run | 2 / 2 | 5 / 5 |
| **holdout2 (8)** | intact | not run | 7 / 4 | 7 / 4 |
| **holdout2 (8)** | stripped | not run | 6 / 4 | 6 / 5 |

Tuning is in-sample for every version. The first holdout was the honest estimate for 0.2 and is in-sample for 0.3. Holdout2 was committed before any 0.3 code was written and run once, after 0.3 was frozen at commit 1435ee6; 0.2 was run on it from a worktree of commit 10c3562. The 0.3 run reused the 0.2 run's cached searches, so the comparison isolates code changes from changes in GitHub's index.

## Per pair (upstream lead rank and verdict)

A second-hop lead is listed at the position it was evaluated in, which can be past #4 when failed acquisitions or hops reordered the queue.

Holdout2, 0.2 and 0.3:

| Pair | Intact 0.2 | Intact 0.3 | Stripped 0.2 | Stripped 0.3 |
|---|---|---|---|---|
| eza ← ogham/exa | #2 code overlap | #2 code overlap | #1 code overlap | #1 code overlap |
| terser ← mishoo/UglifyJS | #10 not evaluated | #8 not evaluated | #8 not evaluated | #4 code overlap (second hop) |
| golang-jwt ← dgrijalva/jwt-go | #17 not evaluated | #16 not evaluated | not found | not found |
| nextcord ← Rapptz/discord.py | #4 code overlap | #5 code overlap | #4 code overlap | #5 code overlap |
| pycryptodome ← pycrypto/pycrypto | not found | not found | not found | not found |
| angie ← nginx/nginx | #8 not evaluated | #9 not evaluated | #8 not evaluated | #9 not evaluated |
| neovim ← vim/vim | #1 code overlap | #1 code overlap | #1 code overlap | #1 code overlap |
| mysqlclient ← farcepest/MySQLdb1 | #1 corroborated | #1 corroborated | #1 code overlap | #1 code overlap |

Tuning pairs, 0.2 and 0.3:

| Pair | Intact 0.2 | Intact 0.3 | Stripped 0.2 | Stripped 0.3 |
|---|---|---|---|---|
| django-q2 ← Koed00/django-q | #1 corroborated | #1 corroborated | #1 code overlap | #1 code overlap |
| flask-caching ← thadeusb/flask-cache | #1 corroborated | #1 corroborated | not found | not found |
| flask-restx ← noirbizarre/flask-restplus | #1 corroborated | #1 corroborated | #1 code overlap | #1 code overlap |
| niquests ← psf/requests | #20 not evaluated | #20 not evaluated | not found | not found |
| urllib3-future ← urllib3/urllib3 | #21 not evaluated | #21 not evaluated | not found | not found |
| asyncclick ← pallets/click | #1 component | #1 component | #6 not evaluated | #4 code overlap |
| hyfetch ← dylanaraps/neofetch (component) | #19 not evaluated | #19 not evaluated | not found | not found |
| pip ← psf/requests (component) | not found | not found | not found | not found |
| yt-dlp ← ytdl-org/youtube-dl | #2 corroborated | #2 corroborated | not found | #2 code overlap (second hop) |
| valkey ← redis/redis | #3 code overlap | #3 code overlap | #1 code overlap | #1 code overlap |
| lodash ← jashkenas/underscore | #21 not evaluated | #21 not evaluated | not found | not found |
| gitea ← gogs/gogs | #3 code overlap | #3 code overlap | #1 code overlap | #1 code overlap |
| pypdf ← mfenniak/pyPdf | #4 code overlap | #4 code overlap | #4 code overlap | #4 code overlap |

First holdout, 0.2 and 0.3:

| Pair | Intact 0.2 | Intact 0.3 | Stripped 0.2 | Stripped 0.3 |
|---|---|---|---|---|
| searxng ← searx/searx | #1 corroborated | #1 corroborated | not found | #4 code overlap |
| flask-security ← pallets-eco/flask-security-3.0 | not found | not found | not found | not found |
| pillow-simd ← python-pillow/Pillow | #5 not evaluated | #4 code overlap (second hop) | #4 code overlap | #3 code overlap |
| postman-request ← request/request | #1 component | #1 component | #2 code overlap | #2 code overlap |
| bbolt ← boltdb/bolt | not found | not found | not found | #4 code overlap (second hop) |
| mlua ← mlua-rs/rlua | #1 component overlap | #1 component overlap | not found | #6 component overlap (second hop) |

## What changed in 0.3

Each change came from a diagnosed failure on the tuning set or the first holdout:

- **Second hop.** When a candidate confirms overlap, Fossil reads the repositories it names inside the files it shares with the target, or in a relationship statement in its own docs, and evaluates the strongest two next (four per run at most). Copies keep the credits the target lost: a download manager bundling yt-dlp names youtube-dl in five shared files, a Deepin package of bbolt names boltdb/bolt, and on holdout2 GlowScript (VPython in the browser), which bundles uglify-es, names UglifyJS2 in four.
- **Failed acquisitions no longer use a slot.** Repositories with committed virtualenvs often exceed the 10,000-entry ZIP limit; each one used to cost an evaluation (asyncclick). Attempts are capped at twice the budget, and the limit now ignores directories that are never extracted.
- **Bundled hits rank below project source.** A code-search hit inside `site-packages`, `vendor/` or `node_modules`, or in a data or documentation file, ranks below a hit in a project's own source.
- **Go and JS test files are tests; JS function expressions are definitions.** bbolt's queries had been benchmark names, and searxng's JavaScript produced no usable queries.

The first 0.3 draft (`v4`) also followed "based on CPython"-style comments in a copy's source and links in its CI and packaging scripts; in bbolt one of those took the slot boltdb/bolt needed. Source-comment credits now count as plain mentions and support directories are skipped, the same rule already applied to the target's own credits.

## How the second hop did

Across every 0.3 run, hops backed by shared files led to the upstream in four of seven distinct cases (Pillow, youtube-dl, boltdb/bolt, UglifyJS; the misses were python/cpython and python/mypy from pip copies, and curl, never evaluated). Hops backed only by a relationship statement in a copy's docs led to the upstream once in seven (mlua → rlua, in-sample). The other six were a changelog template "adapted from pytest", a tengine feature list, a bundled Lua module's README, a "projects using bolt" entry, and two neovim links. On holdout2 they took slots in angie, nextcord and neovim without costing a confirmation, because nginx was out of reach in both versions and discord.py and vim were confirmed anyway. That is luck, not design; it is the first thing to fix.

## Why the misses missed

**Fork-only vocabulary** (niquests, urllib3-future, flask-caching, flask-security). Queries use names defined in the target's largest core files. In a long-lived fork those files are mostly code written after the split: niquests searches for `AsyncSession` and `AsyncSOCKSProxyManager`, flask-caching for `RedisSentinelCache`, none of which exist upstream. The results are committed virtualenvs carrying the *target*, and the upstream is absent at any result count; asking for 50 results instead of 10, or excluding bundled paths, does not help. 0.2's diagnosis ("vendored copies crowd out the upstream") was wrong.

**Credits outranking code search when docs are intact** (bbolt, terser). Snippet comments in source ("Based on: mmap-go", "Copied from etcd"), polyfill and Unicode-data credits, and a README list of projects using bolt ("reef-pi ... based on a Raspberry Pi") rank above code-search hits and fill the slots. In both pairs the stripped run did better than the intact one.

**Ubiquitous upstreams** (angie). nginx code is in thousands of repositories; nginx/nginx ranked 8th–9th behind tengine and an annotated nginx tree, both of which Fossil confirmed.

**Borrowed cores** (pycryptodome). Its largest C files are cipher implementations pycrypto itself took from older public-domain code, so their names lead to libtomcrypt, the PSP SDK and Komodo, none of which overlapped enough to confirm.

**Renamed copies with no credits** (golang-jwt). Three repositories carrying jwt-go as an internal package were confirmed, but none names dgrijalva/jwt-go in the shared files, so there was nothing to hop to.

**Component pairs** (hyfetch, pip): queries come from the target's own code, not from the bundled component, and find only the target. **lodash** at its pinned commit is essentially one file and yields a single query, whose hits are old app bundles that did not confirm.

## Next round

In rough order of expected value: drop or down-weight relation-only hops; rank snippet credits in the target's source below code-search hits (as already done for copies); pick some queries from files more likely to predate a fork rather than only the largest ones; then the component and direction problems. Each needs a fresh holdout.

## Other repositories that reached a confirming verdict

Every one was checked by hand (description and matched files). None was a spurious match.

- **Copies or bundles of the target.** Download-manager and Kodi add-ons carrying `yt_dlp/`, mlua forks, a TypeScript port of terser, apps vendoring flask-restx, asyncclick or jwt-go as internal packages, pipenv vendoring pip, bbolt packaging, a Flask-Security-Too copy.
- **Copies of, or links in, the upstream's lineage.** yt-dlc (the intermediate fork between youtube-dl and yt-dlp), a PyPDF2 mirror, exa forks, annotated Redis and nginx trees, tengine, a detached gogs fork, disnake and qq.py (discord.py forks), MySQL-for-Python-3 and moist, vim.wasm, Pillow packaging.
- **Projects vendoring the same third-party code.** Blender add-ons bundling PIL, a test tool bundling `request`, GlowScript bundling uglify-es.

Fossil reports all of these as overlap with undetermined direction, which is correct. It cannot yet tell an ancestor from a descendant without Git history or an acknowledgement, and with acknowledgements stripped it more often finds descendants than ancestors.

## Limits of this measurement

Twenty-seven pairs, now spanning Python, Go, Rust, JavaScript and C, all public on GitHub. Holdout2 has eight pairs, so a one-pair difference is suggestive at best. Results depend on GitHub's live code index, which changes. The tuning set and first holdout have been used repeatedly and overstate what the next unseen pairs will show.
