# Leak classes

The starter catalog ships 13 classes. Three are user-extensible (you provide the patterns); ten are generic and ship with default patterns on. Two more (GitHub PR refs after force-push, GitHub issue body content from prior leak audits) are out-of-band: they aren't file-content patterns and are tracked as v0.2 roadmap items.

Each class below: what it is, why it leaks, an example, and the prevention rule that makes the patterns unnecessary in well-written prose.

## User-extensible classes

### 1. Cross-project codenames

**What it catches**: names of OTHER projects you maintain that should not appear in this public repo.

**Why it leaks**: working across multiple projects in the same AI coding session means cross-project context naturally seeps into ADR prose, commit messages, and inline comments. The temptation to name the actual cross-project consumer is constant because the relationship is real.

**Example**: "ProjectA adopts AKD via the same crate when ProjectB lands. ProjectC's ADR for VRF-blinded mode will reference D034."

**Prevention**: name the relationship abstractly. "Downstream consumers requiring privacy-preserving lookup" instead of "ProjectC."

### 2. Operator name and path patterns

**What it catches**: file paths or usernames that reveal the operator's local filesystem.

**Why it leaks**: stack traces, error messages, debug logs, and tool output get pasted into ADRs. Operator-personal memory paths appear when investigating the local environment.

**Example**: `/Users/alice/repos/foo/bar.py:42`

**Prevention**: never copy-paste raw paths into public docs. Use relative paths or generic placeholders.

### 3. Private wrapper service names

**What it catches**: internal services or wrappers that public code interacts with but should not be named.

**Why it leaks**: scripts and demos reference the wrapper by its actual name. ADR prose describes "the first consumer is `X-bridge`."

**Prevention**: refer to it as "the wrapper service" or "an internal consumer." Record-file paths use neutral names (`records.jsonl`, not `<wrapper-name>-records.jsonl`).

## Generic classes (default-on)

### 4. Internal phase numbering

**What it catches**: implementation-plan phase numbers that anchor public docs to internal planning state.

**Examples**: "Phase 0.6", "Phase 1", "Phase 2", "Phase 6 §3 verification", "Phase-1" (the hyphen variant slips past naive `Phase \d` patterns).

**Prevention**: describe the technical context, not its position in an internal plan. "AP2 cross-spec verification revealed..." not "Phase 6 §3 verification revealed..."

### 5. Internal handoff or planning doc names

**What it catches**: references to internal planning documents like `IMPLEMENTATION-HANDOFF.md` or `thoughts/shared/handoffs/...` paths.

**Why it leaks**: ADR prose references the doc that motivated the decision. "Phase 5 of `IMPLEMENTATION-HANDOFF.md` calls for an end-to-end test."

**Prevention**: name the technical motivation, not the planning artifact. "An end-to-end test exercising the full attribution flow needs a home."

### 6. Agent memory observation IDs

**What it catches**: internal IDs from agent memory systems (claude-mem, persistent memory observations).

**Example**: "memory observation #28586 recorded the final decision."

**Prevention**: cite the underlying evidence, not the memory ID that recorded it.

### 7. Time-of-day and day-relative narration

**What it catches**: timestamps like "3:23 AM," day-relative words like "today" / "tonight" / "yesterday."

**Why it leaks**: late-night operator work can make timestamps the evidence that distinguishes decisions. Day-relative words reveal the writer's frame of reference is the operator's calendar, not the project's history.

**False positives**: legitimate technical uses ("today's typical client," "the next session of the protocol") will trip the patterns. Override on a case-by-case basis.

**Prevention**: "earlier" or "in a prior pass" instead of "at 3:23 AM" or "yesterday."

### 8. User-pushback narration

**What it catches**: "the user pushed back," "the user said X" framings.

**Why it leaks**: ADR prose treats the operator's interventions as part of the decision context. They are, but in operator-private docs.

**Prevention**: present decisions on their own merits. "Direction was to ship the corpus immediately" not "the user pushed for shipping the corpus immediately."

### 9. Agent or subagent actor references

**What it catches**: "primary Claude," "earlier subagent," "prior subagent."

**Why it leaks**: prior search passes were incomplete; ADR prose explains the correction by referencing which agent ran what.

**Prevention**: describe the methodology, not the agent that ran it. "An earlier search pass" / "a prior batch" is enough.

### 10. Session-restart artifacts

**What it catches**: "after a session restart," "the session was interrupted."

**Why it leaks**: AI coding sessions get restarted; ADR prose references the restart as a contextual marker.

**Prevention**: "after a data refresh" or "after the searches were re-run" is sufficient.

### 11. In-this-commit or in-this-session framing

**What it catches**: "shipped in this commit," "earlier in this session," "next session," "current session."

**Why it leaks**: ADR prose self-references the writing context itself, revealing the doc was written from inside an ongoing operator workflow rather than as standalone reference material.

**Note**: legitimate protocol vocabulary like "this protocol session" will trip the regex. Use overrides.

**Prevention**: "Pending work" or "subsequent work" instead of "next session."

### 12. Strategic-process framing and scrub-cleanup language

**What it catches**: "sanity-check session," "private staging," "leak count went from X to Y," "scrub cross-project codename references."

**Why it leaks (the meta-leak)**: commit messages or docs that ANNOUNCE a scrub or describe its cleanup state are themselves leaks. The phrase "leak count went from 12 to 0" tells a public reader the repo had private state worth scrubbing, even when no individual codename remains.

**Prevention**: commit messages describe WHAT changed in technical terms. "Update wording in §4.6 example" not "Scrub cross-project codename references from §4.6 example."

## Out-of-band classes (not file content)

### 13. GitHub PR refs after force-push

`refs/pull/*` survives `git filter-repo` + `git push --force` cycles because GitHub preserves PR refs even after the source branch is deleted. A normal `git clone` doesn't fetch them, but `git fetch refs/pull/*:refs/pull/*` does, and so does any cloud audit routine.

**Detection**: `git ls-remote origin` shows all refs.

**Prevention**: delete and recreate the GitHub repo. Or file a GitHub Support GC ticket. Force-push alone is insufficient.

textleaks does not check this today. Planned for v0.2 as `textleaks audit-refs`.

### 14. GitHub issue body content from prior leak audits

If a cloud audit routine opens an issue when it detects a regression, the issue body contains the leaking lines verbatim. Issue bodies are public-repo content visible at `https://github.com/<owner>/<repo>/issues`.

**Prevention**: close and delete leak-regression issues after fixing the underlying leak. Or have the routine open issues in a private mirror repo instead.

textleaks does not check this today. Planned for v0.2 as `textleaks audit-issues`.

### 15. Speculative cross-project ramification language

Handled by class 1 (cross-project codenames) plus operator review of any prose that describes how this project affects other projects you maintain.

## Why these are the right 15 classes

This taxonomy emerged from three distinct leak-cleanup waves on a real public OSS repo over two months. Each wave caught patterns the previous wave missed:

- Wave 1: literal cross-project codenames.
- Wave 2: internal tooling names + GitHub PR refs surviving force-push.
- Wave 3: internal-process **framing prose** in ADRs and code comments. Phase numbers, handoff doc references, time-of-day timestamps, agent-actor references.

Wave 3 was the surprise. The patterns that caused it were the impetus for textleaks: gitleaks and trufflehog catch nothing in this class, yet the prose leaks are at least as common as credential leaks.
