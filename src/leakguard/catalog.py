"""Catalog loading: read YAML, optionally merge a user override."""

from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class Catalog:
    classes: list = field(default_factory=list)
    ignore_paths: list[str] = field(default_factory=list)


def load_starter_catalog() -> Catalog:
    """Load the catalog shipped with leakguard."""
    text = resources.files("leakguard.data").joinpath("starter-catalog.yaml").read_text()
    return _parse(text)


def load_catalog(path: Path) -> Catalog:
    """Load a catalog from a user-supplied file."""
    return _parse(path.read_text())


def load_with_overrides(user_path: Optional[Path]) -> Catalog:
    """Load starter catalog and merge a user catalog on top (user wins by `id`).
    `ignore_paths` from both are concatenated and deduped."""
    base = load_starter_catalog()
    if user_path is None or not user_path.exists():
        return base
    user = load_catalog(user_path)
    merged_classes = _merge_classes(base.classes, user.classes)
    merged_ignore = list(dict.fromkeys(base.ignore_paths + user.ignore_paths))
    return Catalog(classes=merged_classes, ignore_paths=merged_ignore)


def _parse(text: str) -> Catalog:
    data = yaml.safe_load(text) or {}
    classes = data.get("classes", [])
    ignore_paths = data.get("ignore_paths", [])
    if not isinstance(classes, list):
        raise ValueError("catalog `classes` must be a list")
    if not isinstance(ignore_paths, list):
        raise ValueError("catalog `ignore_paths` must be a list")
    for cls in classes:
        if "id" not in cls or "name" not in cls:
            raise ValueError(f"catalog class missing required field: {cls!r}")
        cls.setdefault("patterns", [])
        cls.setdefault("case_sensitive", False)
    return Catalog(classes=classes, ignore_paths=ignore_paths)


def _merge_classes(base: list, override: list) -> list:
    by_id = {c["id"]: c for c in base}
    for c in override:
        existing = by_id.get(c["id"])
        if existing is None:
            by_id[c["id"]] = c
            continue
        if c.get("replace"):
            by_id[c["id"]] = c
        else:
            merged_patterns = list(dict.fromkeys(existing["patterns"] + c.get("patterns", [])))
            by_id[c["id"]] = {
                **existing,
                **{k: v for k, v in c.items() if k != "patterns"},
                "patterns": merged_patterns,
            }
    return list(by_id.values())
