# AGENTS.md

> Instructions for AI coding agents (Claude Code, Hermes, Codex, Cursor, etc.) working in this repository.

## AI disclosure

This repo's content (barber's own SKILL.md) is developed with AI assistance, including by Hermes running barber against real skills and opening PRs from what it finds. No disclosure footer is needed on commits or PRs — that's the expected workflow here, not an exception.

## Project overview

Barber is a Claude Skill, not an application. There's no build, no runtime, no dependencies to install — `SKILL.md` *is* the product: a set of instructions Claude reads and follows to audit other skills for bloat, weak triggers, missing safety content, and cross-skill duplication.

- **What it is:** a single prompt file (`SKILL.md`) plus a README and logo assets. No code.
- **Stack:** none — Markdown + YAML frontmatter only.
- **Deeper docs:** [README.md](README.md) for install/usage; `SKILL.md` itself is the full spec of what barber does.

## Project structure

```
barber/
├── SKILL.md          # the actual skill — read this before changing behavior
├── README.md         # human-facing install/usage doc, kept in sync with SKILL.md
├── LICENSE           # MIT
├── assets/
│   ├── logo.png      # light-theme logo (black on transparent)
│   └── logo-dark.png # dark-theme logo (white on transparent) — keep in sync with logo.png, same shape
└── .gitignore
```

Don't create new top-level directories (`scripts/`, `references/`, etc.) unless `SKILL.md`'s own content genuinely needs them — most changes here are edits to `SKILL.md` itself.

## Setup & build

None. Clone and edit `SKILL.md` directly.

## Testing

<!-- TODO: no automated test suite or evals/evals.json exists for this repo. SKILL.md itself documents a `--enhance` mode that checks for evals/evals.json on the *skill being audited* — that's a feature barber offers to other skills, not something this repo has for itself yet. Manual verification only: read the diff, confirm YAML frontmatter still parses, confirm the change doesn't silently alter what barber does (see Boundaries below). -->

## Code style & conventions

No linter/formatter — it's prose. Match `SKILL.md`'s existing voice: terse, one finding/rule per line, imperative instructions over explanation (comb-style, per the referenced `comb` skill's own rules).

## Git & PR workflow

- Branch naming (observed): `feat/<short-description>` or `fix/<short-description>`, branched fresh off current `main`.
- Commit format (observed): Conventional Commits — `feat: ...`, `fix: ...`, `docs: ...`, with a longer body explaining the *why*, not just the what.
- **Known failure mode:** reusing a branch across multiple sessions without deleting it after merge causes conflicts on the next PR from that branch — even when the diff is clean — because its history diverges from `main` once a prior PR is squash-merged. Branch fresh per session, or delete the branch after merge.
- PRs are the norm; most await explicit human merge confirmation, though this hasn't been 100% consistent historically (one PR merged automatically without a review request). Prefer opening a PR and waiting for confirmation unless told otherwise.
- No "Generated with `<Agent Name>`" or co-author footers.

## Security & secrets

No secrets, credentials, or `.env` usage anywhere in this repo — it's static prose and two PNGs. If that ever changes, treat any credential the normal way: never commit it, never print it, flag rather than silently "fix" anything that looks like one already committed.

## Boundaries — what not to do

- **Never silently change what barber does** — only how efficiently it says it, unless the user explicitly asks for new capability (e.g. a new mode/section). This is `SKILL.md`'s own core rule (see "Rules" section at the bottom of the file) and applies recursively to editing the file itself.
- Preserve the YAML frontmatter's `name: barber` exactly — tooling and install instructions depend on it.
- If editing `assets/logo.png`, update `assets/logo-dark.png` to match (same shape, inverted color) — the README's `<picture>` element depends on both existing and being visually consistent.
- Before pushing any binary asset (image, etc.) via the GitHub API, verify the base64 round-trips (`base64 -d | md5sum` against the source) — a prior logo upload was silently corrupted mid-transcription and went unnoticed until a user caught it visually.
- Don't add build tooling, a package manifest, or CI — this project has none by design; if that assumption changes, it's a deliberate decision to raise with the user first, not something to add opportunistically.

## When you're unsure

If a change would alter barber's actual audit behavior (not just wording/formatting), stop and show the proposed diff before applying — same rule `SKILL.md` applies to the skills *it* audits.
