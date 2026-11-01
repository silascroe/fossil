"""Bounded read-only acquisition. Never execute investigated project code."""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

MAX_FILE = 1_000_000
MAX_TOTAL = 50_000_000
MAX_FILES = 10_000
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".fossil", ".tox", ".next", "dist", "build", ".cache", ".ssh", ".aws", ".gnupg"}
REPO_RE = re.compile(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$")


def sensitive(path: Path) -> bool:
    name = path.name.lower()
    return (name in {".env", ".npmrc", ".pypirc", ".netrc", "id_rsa", "id_ed25519", "credentials", "credentials.json", "service-account.json"}
            or (name.startswith(".env.") and name not in {".env.example", ".env.sample", ".env.template"})
            or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"})


class AcquisitionError(ValueError):
    pass


def repo_name(value: str) -> str | None:
    value = value.strip().removeprefix("https://github.com/").removesuffix(".git").rstrip("/")
    if REPO_RE.fullmatch(value) and all(x not in {".", ".."} for x in value.split("/")):
        return value
    return None


def git(path: Path, *args: str, timeout: int = 60) -> str:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0", GIT_CONFIG_NOSYSTEM="1")
    # Ignore user filters, hooks, credentials and arbitrary URL rewrites for analysis.
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    # Fossil never checks out a work tree, so NTFS path guards only block archiving on Windows;
    # extract_zip applies its own path checks to everything written.
    cmd = ["git", "-c", "core.hooksPath=" + os.devnull, "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false", "-c", "protocol.file.allow=never",
           "-c", "core.protectNTFS=false", "-C", str(path), *args]
    try:
        p = subprocess.run(cmd, env=env, capture_output=True, timeout=timeout, check=True)
        return p.stdout.decode("utf-8", errors="replace")
    except (subprocess.SubprocessError, OSError) as e:
        detail = getattr(e, "stderr", b"") or b""
        raise AcquisitionError("Git read failed: " + detail.decode(errors="replace")[:500]) from e


def extract_zip(archive: Path, destination: Path) -> list[str]:
    warnings = []
    total = 0
    with zipfile.ZipFile(archive) as z:
        if len(z.infolist()) > MAX_FILES:
            raise AcquisitionError("ZIP exceeds 10,000 entries")
        # Validate all names before writing anything.
        for info in z.infolist():
            name = PurePosixPath(info.filename.replace("\\", "/"))
            if name.is_absolute() or ".." in name.parts or (name.parts and re.fullmatch(r"[A-Za-z]:", name.parts[0])):
                raise AcquisitionError("Unsafe ZIP path: " + info.filename)
        destination.mkdir(parents=True, exist_ok=True)
        for info in z.infolist():
            name = PurePosixPath(info.filename.replace("\\", "/"))
            if info.is_dir() or any(p in SKIP for p in name.parts):
                continue
            if any(re.search(r'[:<>"|?*\x00-\x1f]', p) for p in name.parts):
                # Legal in Git, unwritable (or an alternate data stream) on Windows; skip, do not fail the snapshot.
                warnings.append("Skipped name not portable to all filesystems: " + str(name))
                continue
            if sensitive(Path(str(name))):
                warnings.append("Skipped credential-like filename: " + str(name))
                continue
            if info.file_size > MAX_FILE:
                warnings.append("Skipped per-file limit: " + str(name))
                continue
            if stat.S_ISLNK(info.external_attr >> 16):
                warnings.append("Skipped archive symlink: " + str(name))
                continue
            # Sample up to the snapshot budget rather than discarding a large repository outright.
            # Reads are capped, so a header that understates a member's size cannot exceed the limits.
            if total + info.file_size > MAX_TOTAL:
                warnings.append("Acquisition limit: " + str(name))
                continue
            with z.open(info) as source:
                data = source.read(MAX_FILE + 1)
            if len(data) > MAX_FILE or total + len(data) > MAX_TOTAL:
                warnings.append("Acquisition limit: " + str(name))
                continue
            total += len(data)
            p = destination.joinpath(*name.parts)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
    return warnings


def copy_snapshot(source: Path, destination: Path, *, allowed: set[str] | None = None) -> list[str]:
    warnings, total, count = [], 0, 0
    destination.mkdir(parents=True, exist_ok=True)
    for base, dirs, files in os.walk(source, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(base) / d).is_symlink())
        for name in sorted(files):
            p = Path(base) / name
            rel = p.relative_to(source)
            if sensitive(p):
                warnings.append("Skipped credential-like filename: " + str(rel))
                continue
            if allowed is not None and rel.as_posix() not in allowed:
                warnings.append("Skipped Git-ignored file: " + str(rel))
                continue
            if p.is_symlink() or not p.is_file():
                warnings.append("Skipped symlink/special file: " + str(rel))
                continue
            size = p.stat().st_size
            count += 1
            if size > MAX_FILE or total + size > MAX_TOTAL or count > MAX_FILES:
                warnings.append("Acquisition limit: " + str(rel))
                continue
            total += size
            dst = destination / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dst)
    return warnings


def history(path: Path, revision: str = "HEAD") -> dict:
    try:
        root = Path(git(path, "rev-parse", "--show-toplevel").strip()).resolve()
        if root != path.resolve():
            return {"available": False, "note": "Input is not a Git repository root; enclosing repository history was excluded."}
        sha = git(path, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}").strip()
    except AcquisitionError:
        return {"available": False}
    rows = git(path, "log", "-n", "500", "--format=%H%x09%aI%x09%cI%x09%s", sha).splitlines()
    commits = []
    for row in rows:
        parts = row.split("\t", 3)
        if len(parts) == 4:
            commits.append(dict(zip(("sha", "authored", "committed", "subject"), parts)))
    shallow = git(path, "rev-parse", "--is-shallow-repository").strip() == "true"
    return {"available": True, "head": sha, "shallow": shallow, "log_limit": 500,
            "dirty": bool(git(path, "status", "--porcelain")), "commits": commits,
            "note": "Dates are author-controlled observations; the earliest sampled commit is not necessarily the project's origin."}


def acquire_local(value: str, destination: Path) -> dict:
    source = Path(value).expanduser().resolve()
    if source.is_dir():
        if destination.resolve().is_relative_to(source):
            raise AcquisitionError("Case/cache directory must be outside the investigated source directory")
        info = history(source)
        try:
            allowed = set(git(source, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0"))
        except AcquisitionError:
            allowed = None
        warnings = copy_snapshot(source, destination, allowed=allowed)
        if not info.get("available") and info.get("note"):
            warnings.insert(0, info["note"])
        return {"input": str(source), "kind": "directory", "git": info, "warnings": warnings}
    if source.is_file() and zipfile.is_zipfile(source):
        warnings = extract_zip(source, destination)
        return {"input": str(source), "kind": "zip", "archive_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "git": {"available": False}, "warnings": warnings + ["ZIP has no trusted Git history."]}
    raise AcquisitionError("Expected a directory, ZIP, or GitHub owner/repository")
