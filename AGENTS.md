# Fossil agent notes

Python 3.11+ CLI, standard library only at runtime. Entry point `fossil/cli.py`; pipeline is acquire → inventory → discovery → compare → assess → report (`fossil/case.py` ties it together).

- Tests: `python -m unittest discover -s tests`. No network or keys needed.
- Bundled cases must keep replaying: extract `examples/cases.zip` somewhere outside the repo and run `python -m fossil replay <case>` on each.
- Anything that changes inventories or verdicts changes replay; bump `__version__` (fossil/__init__.py and pyproject.toml) when it does.
- Discovery quality is measured in `bench/` (see bench/README.md). It needs `GITHUB_TOKEN`; pass it via the environment, never write it to files. Record new numbers in bench/RESULTS.md, and use a fresh holdout set for each round of tuning.
- Never execute investigated code, follow symlinks, or let a case path escape its directory.

Deeper docs: [README.md](README.md), [docs/implementation.md](docs/implementation.md), [docs/demonstration.md](docs/demonstration.md), [bench/RESULTS.md](bench/RESULTS.md).
