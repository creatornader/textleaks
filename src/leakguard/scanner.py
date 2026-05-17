"""Core scanner: walk paths, match catalog patterns line-by-line, return findings."""

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SKIP_DIRS = frozenset({
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".env",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".remember",
    ".claude",
    "target",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
})

SKIP_DIR_SUFFIXES = frozenset({".egg-info"})

SKIP_SUFFIXES = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg",
    ".pdf", ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z",
    ".lock", ".woff", ".woff2", ".ttf", ".otf",
    ".mp3", ".mp4", ".mov", ".webm", ".wav", ".ogg",
    ".so", ".dylib", ".dll", ".exe", ".bin", ".o", ".a",
})


@dataclass(frozen=True)
class Finding:
    path: str
    line_no: int
    line: str
    class_id: str
    class_name: str
    pattern: str


def _should_skip(path: Path) -> bool:
    parts = path.parts
    if any(part in SKIP_DIRS for part in parts):
        return True
    if any(part.endswith(suffix) for part in parts for suffix in SKIP_DIR_SUFFIXES):
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    return False


def _matches_ignore(path: Path, patterns: list[str]) -> bool:
    """True if `path` matches any glob pattern (matched against the path
    relative to cwd, falling back to the absolute path, and against the
    basename for simple-name patterns)."""
    if not patterns:
        return False
    cwd = Path.cwd().resolve()
    try:
        rel = path.resolve().relative_to(cwd).as_posix()
    except ValueError:
        rel = path.as_posix()
    name = path.name
    for pat in patterns:
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(name, pat):
            return True
    return False


def _iter_files(paths: Iterable[Path], ignore_patterns: list[str]) -> Iterable[Path]:
    for p in paths:
        if p.is_file():
            if not _should_skip(p) and not _matches_ignore(p, ignore_patterns):
                yield p
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and not _should_skip(f) and not _matches_ignore(f, ignore_patterns):
                    yield f


def _compile_classes(classes: list) -> list:
    """Pre-compile regex patterns, attach back to class dicts as `_compiled`."""
    compiled = []
    for cls in classes:
        flags = 0 if cls.get("case_sensitive") else re.IGNORECASE
        cls_compiled = {
            **cls,
            "_compiled": [re.compile(p, flags) for p in cls.get("patterns", [])],
        }
        compiled.append(cls_compiled)
    return compiled


def scan_file(path: Path, compiled_classes: list) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for cls in compiled_classes:
            for pat, source in zip(cls["_compiled"], cls.get("patterns", [])):
                if pat.search(line):
                    findings.append(Finding(
                        path=str(path),
                        line_no=lineno,
                        line=line,
                        class_id=cls["id"],
                        class_name=cls["name"],
                        pattern=source,
                    ))
                    break  # one finding per (class, line)
    return findings


def scan_paths(
    paths: Iterable[Path],
    classes: list,
    ignore_patterns: Iterable[str] = (),
) -> list[Finding]:
    compiled = _compile_classes(classes)
    ignore_list = list(ignore_patterns)
    out: list[Finding] = []
    for f in _iter_files(paths, ignore_list):
        out.extend(scan_file(f, compiled))
    return out
