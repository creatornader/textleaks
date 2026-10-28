# Changelog

All notable changes to textleaks (formerly `leakguard`) are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Dropped Python 3.9, which reached end of life in October 2025. `requires-python` is now `>=3.10`, and CI tests 3.10 through 3.13. GitHub's `ubuntu-latest` runner (Ubuntu 26.04) no longer provides Python 3.9.

## [0.2.0] - 2026-05-17

### Changed

- **Renamed `leakguard` → `textleaks`** to avoid a name collision with an unrelated PyPI secret scanner (`adrian-lorenz/leakguard`) and to align with the `gitleaks` naming convention. The two tools are siblings: gitleaks scans for credentials, textleaks scans for narrative leaks in text content.
- Package name: `leakguard` → `textleaks` (Python import, console script, pre-commit hook id all renamed).
- Config file: `leakguard.yaml` → `textleaks.yaml`.
- GitHub repo: `creatornader/leakguard` → `creatornader/textleaks` (the old URL redirects automatically).
- README tagline rewritten to honest positioning: "The text-content companion to gitleaks." rather than the previous reactive framing.

### Migration

If you have an existing `leakguard` wire-up:

1. Update `.pre-commit-config.yaml`: change the repo URL to `creatornader/textleaks`, the hook `id` to `textleaks`, and bump `rev` to `v0.2.0`.
2. Rename `leakguard.yaml` → `textleaks.yaml`.
3. Run `pre-commit autoupdate` to refresh the hook environment, or `pre-commit clean && pre-commit install` to start fresh.

No catalog or scanning logic changed. Findings on the same source files should be identical between v0.1.1 and v0.2.0.

## [0.1.1] - 2026-05-17

### Fixed

- Override catalog files no longer have to duplicate the `name:` field when extending an existing class by `id`. The base catalog's name is inherited automatically; truly-new classes (no matching `id` in the base) default `name` to the `id`. Surfaced when wiring the tool into a real repo whose user catalog extended `cross-project-codenames` with only `id` + `patterns`.

## [0.1.0] - 2026-05-17

### Added

- Initial spike, published as `leakguard`. Python package + console script (`leakguard scan`, `leakguard init`, `leakguard list-classes`).
- YAML catalog format with user override + merge semantics. Override files extend by default; pass `replace: true` to swap the base entry entirely. `ignore_paths` from base + override are concatenated and deduped.
- Starter catalog with 13 leak classes: 10 generic (default-on) and 3 user-extensible (no defaults shipped). See [`docs/leak-classes.md`](docs/leak-classes.md) for the taxonomy.
- `--exclude GLOB` CLI flag stacks with catalog `ignore_paths`.
- Pre-commit framework integration via `.pre-commit-hooks.yaml`.
- 7 smoke tests covering catalog load, scan, ignore, and override-merge paths.
- Apache 2.0 license.

[0.2.0]: https://github.com/creatornader/textleaks/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/creatornader/textleaks/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/creatornader/textleaks/releases/tag/v0.1.0
