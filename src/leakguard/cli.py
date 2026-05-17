"""leakguard CLI."""

import argparse
import json
import sys
from importlib import resources
from pathlib import Path

from leakguard import __version__
from leakguard.catalog import load_with_overrides
from leakguard.scanner import scan_paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="leakguard",
        description="Pre-publish scanner for narrative-style internal-context leaks.",
    )
    parser.add_argument("--version", action="version", version=f"leakguard {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    scan_p = sub.add_parser("scan", help="Scan files or directories for narrative leaks")
    scan_p.add_argument("paths", nargs="*", default=["."], help="Paths to scan (default: current directory)")
    scan_p.add_argument(
        "--catalog",
        type=Path,
        default=Path("leakguard.yaml"),
        help="User catalog path (default: ./leakguard.yaml; merged on top of starter)",
    )
    scan_p.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="Glob pattern of files to skip (repeatable). Stacks with `ignore_paths` from the catalog.",
    )
    scan_p.add_argument("--format", choices=["text", "json"], default="text")
    scan_p.add_argument("--quiet", action="store_true", help="Suppress summary line")

    init_p = sub.add_parser("init", help="Write a starter leakguard.yaml into the current directory")
    init_p.add_argument("--force", action="store_true", help="Overwrite existing leakguard.yaml")

    list_p = sub.add_parser("list-classes", help="Print the classes in the active catalog")
    list_p.add_argument("--catalog", type=Path, default=Path("leakguard.yaml"))

    args = parser.parse_args(argv)

    if args.cmd == "scan":
        return _cmd_scan(args)
    if args.cmd == "init":
        return _cmd_init(args)
    if args.cmd == "list-classes":
        return _cmd_list(args)
    return 1


def _cmd_scan(args) -> int:
    catalog = load_with_overrides(args.catalog)
    paths = [Path(p) for p in args.paths]
    ignore_patterns = list(catalog.ignore_paths) + list(args.exclude)
    findings = scan_paths(paths, catalog.classes, ignore_patterns=ignore_patterns)

    if args.format == "json":
        out = [
            {
                "path": f.path,
                "line": f.line_no,
                "text": f.line,
                "class_id": f.class_id,
                "class_name": f.class_name,
                "pattern": f.pattern,
            }
            for f in findings
        ]
        print(json.dumps(out, indent=2))
    else:
        for f in findings:
            snippet = f.line.strip()
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            print(f"{f.path}:{f.line_no} [{f.class_id}] {snippet}")
        if not args.quiet:
            file_count = len({f.path for f in findings})
            print(f"\n{len(findings)} finding(s) across {file_count} file(s)", file=sys.stderr)

    return 1 if findings else 0


def _cmd_init(args) -> int:
    target = Path("leakguard.yaml")
    if target.exists() and not args.force:
        print(f"{target} already exists. Use --force to overwrite.", file=sys.stderr)
        return 1
    text = resources.files("leakguard.data").joinpath("template.yaml").read_text()
    target.write_text(text)
    print(f"Wrote {target}. Edit it to add your project's codenames and operator-private terms.")
    return 0


def _cmd_list(args) -> int:
    catalog = load_with_overrides(args.catalog)
    for cls in catalog.classes:
        n = len(cls.get("patterns", []))
        marker = " (no patterns)" if n == 0 else f" ({n} pattern{'s' if n != 1 else ''})"
        print(f"{cls['id']}: {cls['name']}{marker}")
    if catalog.ignore_paths:
        print(f"\nignore_paths: {len(catalog.ignore_paths)} pattern(s)")
        for p in catalog.ignore_paths:
            print(f"  - {p}")
    return 0
