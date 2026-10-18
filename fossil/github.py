"""Read-only GitHub transport, bounded HTTP cache and pinned Git snapshots."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .acquire import AcquisitionError, copy_snapshot, extract_zip, git, history, repo_name


def split_repository(value: str) -> tuple[str, str | None]:
    base, sep, ref = value.partition("@")
    name = repo_name(base)
    if not name or (sep and (not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_./-]{0,199}", ref) or ".." in ref)):
        raise AcquisitionError("Invalid GitHub repository or revision; use owner/repo[@commit-or-tag]")
    return name, ref if sep else None


class GitHub:
    def __init__(self, cache: Path, *, offline: bool = False, refresh: bool = False):
        self.cache, self.offline, self.refresh = cache, offline, refresh
        self.cache.mkdir(parents=True, exist_ok=True)
        self.trail = []
        self.calls = 0
        self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    def get(self, route: str) -> dict:
        if not route.startswith(("/repos/", "/search/")) or ".." in route or "\\" in route:
            raise AcquisitionError("Only read-only GitHub repository/search endpoints are allowed")
        url = "https://api.github.com" + route
        key = hashlib.sha256(url.encode()).hexdigest()
        path = self.cache / "http" / (key + ".json")
        now = datetime.now(timezone.utc).isoformat()
        if path.exists() and (self.offline or (not self.refresh and time.time() - path.stat().st_mtime < 86400)):
            cached = json.loads(path.read_text())
            self.trail.append({"url": url, "status": "cached", "observed_at": cached["observed_at"], "used_at": now, "response_sha256": cached["sha256"]})
            return cached["data"]
        if self.offline:
            raise AcquisitionError("Offline cache miss: " + route)
        if self.calls >= 30:
            raise AcquisitionError("GitHub HTTP request budget (30) exhausted")
        self.calls += 1
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "fossil-investigator/0.1", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        try:
            with urlopen(Request(url, headers=headers), timeout=25) as response:
                raw = response.read(8_000_001)
            if len(raw) > 8_000_000:
                raise AcquisitionError("GitHub response exceeds 8 MB")
            data = json.loads(raw)
        except HTTPError as e:
            self.trail.append({"url": url, "status": "HTTP " + str(e.code), "observed_at": now})
            raise AcquisitionError(f"GitHub HTTP {e.code} for {route}; code search needs a token, and rate limits may apply") from e
        except (URLError, TimeoutError, OSError) as e:
            raise AcquisitionError("GitHub network request failed: " + str(e)) from e
        digest = hashlib.sha256(raw).hexdigest()
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"observed_at": now, "sha256": digest, "data": data}))
        tmp.replace(path)
        self.trail.append({"url": url, "status": "fetched", "observed_at": now, "response_sha256": digest})
        return data

    def acquire(self, value: str, destination: Path) -> dict:
        name, requested_ref = split_repository(value)
        warnings = []
        try:
            meta = self.get("/repos/" + name)
            # Follow canonical renames in the returned GitHub metadata.
            name = repo_name(meta.get("full_name", name)) or name
        except AcquisitionError as e:
            meta = {}
            warnings.append(str(e))
        repo = self.cache / "git" / name.replace("/", "--")
        repo.parent.mkdir(parents=True, exist_ok=True)
        if not repo.exists():
            if self.offline:
                raise AcquisitionError("Offline Git cache miss: " + name)
            with tempfile.TemporaryDirectory(dir=repo.parent) as tmp:
                tmp_path = Path(tmp)
                git(tmp_path, "clone", "--depth", "200", "--no-checkout", "--", "https://github.com/" + name + ".git", "repo", timeout=180)
                shutil.move(str(tmp_path / "repo"), repo)
        elif self.refresh and not self.offline:
            git(repo, "fetch", "--depth", "200", "origin", timeout=180)
            # Fetch a default-branch HEAD even if the branch name changed.
            git(repo, "fetch", "--depth", "200", "origin", "HEAD", timeout=180)
            git(repo, "update-ref", "HEAD", "FETCH_HEAD")
        try:
            revision = git(repo, "rev-parse", "--verify", "--end-of-options", (requested_ref or "HEAD") + "^{commit}").strip()
        except AcquisitionError:
            if self.offline or not requested_ref:
                raise AcquisitionError("Requested revision unavailable in Git cache")
            git(repo, "fetch", "--depth", "200", "origin", requested_ref, timeout=180)
            revision = git(repo, "rev-parse", "FETCH_HEAD").strip()
        # git archive only reads the object database; no checkout filters/hooks execute.
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "snapshot.zip"
            git(repo, "archive", "--format=zip", "--output=" + str(archive), revision, timeout=120)
            warnings.extend(extract_zip(archive, destination))
        h = history(repo, revision)
        h["dirty"] = False  # no working tree was checked out; snapshot is exactly HEAD
        selected = {k: meta[k] for k in ("full_name", "html_url", "created_at", "pushed_at", "description", "fork", "default_branch") if k in meta}
        for key in ("parent", "source"):
            if meta.get(key):
                selected[key] = {k: meta[key][k] for k in ("full_name", "html_url") if k in meta[key]}
        warnings.append("Git history limited to depth 200 and up to 500 sampled commits; cached revision reused unless --refresh is supplied.")
        return {"input": "https://github.com/" + name + ("@" + requested_ref if requested_ref else ""), "requested_ref": requested_ref, "repository": name, "kind": "github", "metadata": selected, "git": h, "warnings": warnings}
