# leakguard

Pre-publish scanner for **narrative-style internal-context leaks** in repos you maintain across a private-to-public boundary.

Gitleaks catches secrets. TruffleHog verifies them against live APIs. Neither catches the prose stuff: phase numbers, internal handoff doc references, "the user pushed back," memory observation IDs, "earlier in this session," your other project's codename slipped into an ADR. That's what leakguard catches.

## Why this exists

If you run multiple projects in the same AI coding agent session (Claude Code, Cursor, OpenClaw, etc.) and one or more of them is public OSS, you accumulate a vocabulary of internal-process framing that leaks across the boundary every time you write prose. The patterns aren't credentials. They're cleanups of internal work that read as natural English ("Phase 6 §3 verification revealed..."). Existing scanners don't see them.

leakguard's starter catalog is a generalization of a real catalog used in production across multiple public OSS repos, including its 15-class taxonomy.

## Install

```sh
pip install leakguard
```

Or run as a `pre-commit` hook (see below).

## Use

```sh
leakguard scan                  # scan current directory
leakguard scan src/ docs/       # scan specific paths
leakguard scan --format json    # machine-readable output
leakguard list-classes          # show all classes in the active catalog
leakguard init                  # write a starter leakguard.yaml into the repo
```

Exit code: `0` if clean, `1` if any findings. Wire it into CI to fail PRs that introduce leaks.

## Pre-commit hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/creatornader/leakguard
    rev: v0.1.0
    hooks:
      - id: leakguard
```

The hook runs on every commit and blocks if a finding is added.

## How it works

leakguard ships a starter catalog with 10 generic leak classes baked in (phase numbering, time-of-day narration, agent-memory IDs, session-state framing, etc.). Three classes ship with empty pattern lists because they need your project's specifics:

- **`cross-project-codenames`**: names of OTHER projects you maintain
- **`operator-paths`**: your local username, beyond the generic `/Users/X/` pattern
- **`private-wrapper-services`**: internal services your public code talks to

Run `leakguard init` to scaffold a `leakguard.yaml` in your repo. Add your codenames. Commit. The next `leakguard scan` merges your overrides on top of the starter and flags any new finding.

## The 15-class taxonomy

leakguard's catalog is derived from a 15-class taxonomy of leak patterns observed across multiple private-to-public flips. See [`docs/leak-classes.md`](docs/leak-classes.md) for the prose explanation of each class.

## Roadmap

This is v0.1.0, a spike. Planned for v0.2:

- **Vale style integration** for prose-level checks (sentence cadence, narrative tense) that go beyond regex
- **LLM semantic layer** ("Layer B"): for each line a regex flags, an LLM second-opinion judges whether it's a real leak vs a false positive in context
- **`leakguard audit-history`**: scan commit messages and full git history, not just the working tree
- **`leakguard audit-issues`**: scan GitHub issue bodies (the place leaks survive force-pushes)
- **More language ecosystems**: ship `.pre-commit-hooks.yaml` patterns for Husky, lefthook, simple-git-hooks

If any of these matter to you before they ship, open an issue.

## What it does NOT do

- Does not encrypt files (use `git-crypt` or `git-secret` for that).
- Does not enforce a mirror-repo structure (that's documentation, not code).
- Does not catch credentials (use `gitleaks` + `trufflehog` for that — leakguard runs alongside them, not instead).
- Does not rewrite git history (use `git-filter-repo` for that, after leakguard catches the prose).

## Related tools

leakguard is one layer of a three-tool stack for maintaining public OSS repos with private context:

| Tool | Concern | When to install |
|---|---|---|
| **leakguard** (this tool) | Narrative-leak detection in file CONTENT (prose patterns, codenames) | Anywhere you write prose that could leak operator-internal context |
| [**oss-twin**](https://github.com/creatornader/oss-twin) | Structural mirror gate — fails if any path declared private exists in the public tree | When you have a `*-internal` mirror repo |
| [**oss-security-scan**](https://github.com/creatornader/oss-security-scan) | Reusable GitHub Actions workflow (typos + gitleaks + trufflehog + osv-scanner) | Every public OSS repo |

For the full stack wire-up pattern (one repo, all three tools), see [`oss-security-scan/examples/full-stack-starter/`](https://github.com/creatornader/oss-security-scan/tree/main/examples/full-stack-starter).

## Note for repos with prose linters

`leakguard.yaml` lists codenames as REGEX PATTERN VALUES (e.g. `- '\bmyproject\b'`). It defines what to catch, not what to mention. If your repo also runs a prose linter (Vale, an LLM-based audit, etc.), exempt `leakguard.yaml` from those scanners — otherwise the linter will flag the pattern strings as if they were narrative leaks. Same applies to [`.oss-twin.yaml`](https://github.com/creatornader/oss-twin).

## License

Apache 2.0. See [LICENSE](LICENSE).
