"""Language-agnostic fingerprints with inspectable, original line numbers."""
from __future__ import annotations

import hashlib
import ast
import io
import os
import tokenize as py_tokenize
import json
import re
import warnings
from pathlib import Path

from .acquire import MAX_FILE, MAX_FILES, MAX_TOTAL, SKIP

MAX_FILE_TOKENS = 30_000
MAX_TOTAL_TOKENS = 200_000

SOURCE = {".py", ".js", ".ts", ".tsx", ".jsx", ".c", ".h", ".cpp", ".hpp", ".cc", ".cs", ".go", ".rs", ".java", ".rb", ".php", ".swift", ".kt", ".scala", ".lua", ".sh", ".ex", ".exs", ".m", ".vue", ".svelte"}
TOKEN = re.compile(r'(?P<comment>/\*[\s\S]*?\*/|//[^\n]*|\#[^\n]*)|(?P<string>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|(?P<token>[A-Za-z_$][\w$]*|\d+(?:\.\d+)?|[^\s])')
URL = re.compile(r"https?://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")


def tokenize(text: str, *, python: bool = False) -> tuple[list[str], list[int]]:
    if python:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)  # old escape sequences in investigated code
            return python_tokens(text)
    return generic_tokens(text)


def python_tokens(text: str) -> tuple[list[str], list[int]]:
    try:
        tree = ast.parse(text)
        spans = set()
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                spans.add((body[0].lineno, body[0].col_offset))
        tokens, lines = [], []
        ignored = {py_tokenize.COMMENT, py_tokenize.NL, py_tokenize.NEWLINE, py_tokenize.INDENT, py_tokenize.DEDENT, py_tokenize.ENDMARKER, py_tokenize.ENCODING}
        for t in py_tokenize.generate_tokens(io.StringIO(text).readline):
            if t.type in ignored or t.start in spans:
                continue
            value = t.string
            if t.type == py_tokenize.STRING:
                try:
                    value = repr(ast.literal_eval(value))
                except (ValueError, SyntaxError):
                    pass
            tokens.append(value)
            lines.append(t.start[0])
        return tokens, lines
    except (SyntaxError, ValueError, py_tokenize.TokenError, RecursionError):
        return generic_tokens(text)  # Python 2/incomplete files retain the generic lexical fallback.


def generic_tokens(text: str) -> tuple[list[str], list[int]]:
    tokens, lines = [], []
    line, pos = 1, 0
    for m in TOKEN.finditer(text):
        line += text[pos:m.start()].count("\n")
        if not m.group("comment"):
            tokens.append(m.group())
            lines.append(line)
        line += m.group().count("\n")
        pos = m.end()
    return tokens, lines


def context(path: str, text: str) -> str:
    parts = set(Path(path).parts)
    if parts & {"vendor", "vendored", "third_party", "third-party", "external", "deps"}:
        return "vendored/external"
    if parts & {"test", "tests", "fixtures", "examples", "example"} or Path(path).name.startswith("test_"):
        return "test/example"
    if ".min." in path or re.search(r"(?:auto.?generated|do not edit)", text[:1000], re.I):
        return "generated"
    return "application"


def dependencies(path: str, text: str) -> list[str]:
    try:
        if Path(path).name == "package.json":
            data = json.loads(text)
            return sorted(set(data.get("dependencies", {})) | set(data.get("devDependencies", {})))
        if Path(path).name in {"pyproject.toml", "Cargo.toml"}:
            import tomllib
            data = tomllib.loads(text)
            deps = data.get("project", {}).get("dependencies", []) if path.endswith("pyproject.toml") else data.get("dependencies", {})
            return sorted(re.split(r"[<>=!~\[ ;]", x)[0].lower() for x in deps)
        if Path(path).name.startswith("requirements") and path.endswith(".txt"):
            return [m.group(1).lower() for line in text.splitlines() if (m := re.match(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)(?=\s*(?:[<>=!~;\[#]|$))", line))]
        if Path(path).name == "go.mod":
            return re.findall(r"^\s*([\w.-]+/[\w./-]+)\s+v\d", text, re.M)
    except (ValueError, TypeError, AttributeError):
        pass
    return []


def inspect(root: Path) -> dict:
    files, refs, deps, licenses, warnings = [], [], set(), [], []
    total = 0
    paths = []
    for base, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(base) / d).is_symlink())
        paths.extend(Path(base) / name for name in names)
    # Case-sensitive, component-wise order keeps digests identical across operating systems.
    for p in sorted(paths, key=lambda q: q.relative_to(root).parts):
        rel = p.relative_to(root).as_posix()
        if any(part in SKIP for part in p.relative_to(root).parts) or p.is_symlink() or not p.is_file():
            continue
        size = p.stat().st_size
        if size > MAX_FILE or total + size > MAX_TOTAL or len(files) >= MAX_FILES:
            warnings.append("Inventory limit: " + rel)
            continue
        raw = p.read_bytes()
        total += len(raw)
        try:
            text = raw.decode("utf-8")
            if "\x00" in text:
                continue
        except UnicodeDecodeError:
            continue
        suffix = p.suffix.lower()
        # Extensionless scripts (bin/tool, neofetch) are source when they carry a shebang.
        shebang = text[:120].split("\n", 1)[0] if suffix == "" and text.startswith("#!") else ""
        tokens, lines = tokenize(text, python=suffix == ".py" or "python" in shebang) if suffix in SOURCE or shebang else ([], [])
        files.append({"path": rel, "original_tokens": len(tokens), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": size,
                      "text": text, "tokens": tokens, "token_lines": lines, "context": context(rel, text), "source": bool(tokens)})
        deps.update(dependencies(rel, text))
        if re.match(r"(?i)^(licen[cs]e|copying|notice)", p.name):
            licenses.append({"path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "excerpt": text[:700]})
        text_lines = text.splitlines()
        for number, line in enumerate(text_lines, 1):
            for m in URL.finditer(line):
                name = m.group(1).rstrip(".,;)").removesuffix(".git")
                previous_link_end = max((x.end() for x in URL.finditer(line[:m.start()])), default=0)
                start = max(line.rfind(". ", 0, m.start()) + 2, line.rfind("; ", 0, m.start()) + 2, previous_link_end)
                if start == 1:
                    start = 0
                end = line.find(". ", m.end())
                statement = line[start:end if end >= 0 else len(line)]
                if not re.search(r"\b(?:derived|fork|based|inspired|original)\b", statement, re.I) and line[:m.start()].strip() == "":
                    before = " ".join(text_lines[max(0, number-3):number-1])
                    # Only contiguous attribution text immediately above a standalone link.
                    if before.strip() and re.search(r"(?:derived from|fork of|based on|inspired by)\s*$", before, re.I):
                        statement = before + " " + statement
                commit_match = re.match(r"/commit/([0-9a-fA-F]{40})", line[m.end():])
                refs.append({"repository": name, "path": rel, "line": number, "text": line[:700], "statement": statement[:700], "ref": commit_match.group(1) if commit_match else None})
    budget(files, warnings)
    manifest = "\n".join(f["path"] + ":" + f["sha256"] for f in files)
    groups = search_terms(files)
    return {"digest": hashlib.sha256(manifest.encode()).hexdigest(), "files": files, "references": refs,
            "dependencies": sorted(deps), "licenses": licenses, "warnings": warnings,
            "symbols": [s for group in groups for s in group][:12], "search_terms": groups,
            "source_files": sum(f["source"] for f in files)}


def budget(files: list[dict], warnings: list[str]) -> None:
    # Application code gets the snapshot token budget first, so vendored trees
    # that sort early (deps/, _vendor/) cannot starve the project's own source.
    remaining = MAX_TOTAL_TOKENS
    limits = {}
    for f in sorted(files, key=lambda f: f["context"] != "application"):
        limits[f["path"]] = min(MAX_FILE_TOKENS, remaining, len(f["tokens"]))
        remaining -= limits[f["path"]]
    for f in files:
        if len(f["tokens"]) > limits[f["path"]]:
            n = limits[f["path"]]
            warnings.append("Source token limit: " + f["path"] + f" ({n}/{len(f['tokens'])} tokens analyzed)")
            f["tokens"], f["token_lines"], f["source"] = f["tokens"][:n], f["token_lines"][:n], n > 0


SUPPORT_DIRS = {"scripts", "devscripts", "tools", "docs", "doc", "build", "ci", "benchmarks", "bench", ".github"}
SUPPORT_FILES = {"setup.py", "noxfile.py", "conftest.py", "fabfile.py", "build.js", "build.py", "gulpfile.js", "gruntfile.js", "webpack.config.js"}
DEFINITION = re.compile(r"\b(?:def|function|class|func|fn|struct|interface|enum|trait)\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w{11,})")
# C-family top-level functions: a declaration at column 0 whose name is followed by "(".
C_DEFINITION = re.compile(r"^(?!(?:return|else|if|while|for|switch|case|typedef|extern)\b)[A-Za-z_][\w \t\*&:<>,]*?[\s\*&]([A-Za-z_]\w{11,})\s*\([^;]*$", re.M)
C_FAMILY = {".c", ".h", ".cpp", ".hpp", ".cc", ".m"}
SHELL_DEFINITION = re.compile(r"^\s*(?:function\s+)?([A-Za-z_][\w]{11,})\s*\(\)", re.M)


def parts(name: str) -> int:
    return len([p for p in re.split(r"_|(?<=[a-z0-9])(?=[A-Z])", name) if p])


def search_terms(files: list[dict]) -> list[list[str]]:
    """Up to two distinctive defined names per core file, largest files first.

    Names defined in the same file let discovery ask for both at once; copied
    code keeps a file's definitions together, generic vocabulary rarely does.
    """
    core = [f for f in files if f["source"] and f["context"] == "application"
            and not SUPPORT_DIRS & set(Path(f["path"]).parts[:-1]) and Path(f["path"]).name.lower() not in SUPPORT_FILES]
    seen, groups = set(), []
    for f in sorted(core, key=lambda f: (-f["original_tokens"], f["path"])):
        group = []
        suffix = Path(f["path"]).suffix.lower()
        shell = suffix == ".sh" or (suffix == "" and re.match(r"#!.*\b(?:ba|z|k|da)?sh\b", f["text"]))
        pattern = C_DEFINITION if suffix in C_FAMILY else SHELL_DEFINITION if shell else DEFINITION
        for m in pattern.finditer(f["text"]):
            name = m.group(1)
            if name not in seen and parts(name) >= 2 and not name.lower().startswith("test"):
                seen.add(name)
                group.append(name)
                if len(group) == 2:
                    break
        if group:
            groups.append(group)
        if len(groups) == 6:
            break
    return groups
