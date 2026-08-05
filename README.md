# barber

**Audits and repackages Claude Skills — trims bloat, fixes weak triggers, catches cross-skill duplication.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Install](#install) · [Hermes compatibility](#hermes-compatibility) · [What it does](#what-it-does) · [How it works](#how-it-works) · [Usage](#usage) · [Proof](#proof) · [When to use / when to skip](#when-to-use--when-to-skip) · [License](#license)

---

Skills are always-on context tax: every skill's name + description sits in the model's context window permanently, and its body loads on every trigger. Fat skills, weak triggers, and duplicated logic across skills cost tokens and cause silent misfires forever. Barber audits and cuts.

## Install

Copy `SKILL.md` into your skills directory:

```bash
mkdir -p ~/.claude/skills/barber
curl -o ~/.claude/skills/barber/SKILL.md https://raw.githubusercontent.com/maxkilla/barber/main/SKILL.md
```

Or package as a `.skill` file (zip containing `barber/SKILL.md`) and upload via claude.ai's skill import.

## Hermes compatibility

Drop `SKILL.md` into the same skills directory Hermes reads for Claude Code — no separate packaging needed. Barber's two enhancement PRs to date ([#1](https://github.com/maxkilla/barber/pull/1), [#2](https://github.com/maxkilla/barber/pull/2)) both came directly from Hermes running real audit passes and reporting back what it found missing — that's the intended loop: Hermes runs barber, findings get applied, gaps in barber become PRs here.

**Known quirk:** if Hermes reuses the same feature branch across sessions without deleting it post-merge, that branch's history diverges from `main` after a squash-merge and the next PR shows conflicts even when the diff itself is clean. Branch fresh off current `main` per session, or delete the branch after merge.

## What it does

Runs a 7-part audit, one finding per line, on any SKILL.md — installed, downloaded, or freshly drafted:

1. **Description** — undertriggering, missing "use when" phrasing, collisions with other skills, trigger-phrase coverage gaps between description and body
2. **Body** — redundant instructions, over-explaining, example-density bloat, files that should split into `references/`
3. **Structure** — deterministic work that should be `scripts/`, inline assets that should move to `assets/`, dangling `references/*.md` pointers, generated-file detection (skips edits on files marked `DO NOT EDIT` / `GENERATED`)
4. **Dependency hygiene** — unconditional installs replaced with check-then-install, missing version pins
5. **Safety** — never trims confirmation/authority/stopping-condition language; flags injection-shaped content
6. **Generalization pass** — flags trigger descriptions that are overfit (only match tested phrasings) or overbroad (keyword-match with no scope boundary), per the "weakest correct hypothesis" principle ([Bennett 2023](https://arxiv.org/abs/2301.12987))
7. **Cross-skill dedup & composability** — flags redundant bodies across skills, missing co-load links, and stale "use alongside X" references

## How it works

```
SKILL.md (+ references/, scripts/, assets/)
        │
        ▼
  7-part audit checklist ──► one finding per line
        │
        ▼
  show findings, wait for veto
        │
        ▼
  edit in /tmp/<name>/ ──► repackage <name>.skill
```

## Usage

In a Claude conversation with this skill installed:

- *"comb this skill"* / *"audit my skill"* — full 7-part pass on one skill
- *"why isn't my skill triggering"* — focused pass on section 1/6
- *"which of my skills overlap"* — cross-skill pass (section 7)
- *"tune up my whole skill library"* — cheap description-only pass across all installed skills, reports the 3 worst offenders with estimated always-on token cost

**Flags** (pass in your request, e.g. *"audit this skill, check-only"*):

| Flag | Effect |
|---|---|
| `--check-only` | Findings only — no `/tmp` copy, no edits, no file writes |
| `--max-lines N` | Auto-skip any skill whose body prose is ≤ N lines without a deep read (default full-audit threshold: 500) |
| `--tokens` | Include estimated token cost (~3.3 tok/line of body prose) and projected savings, even on "clean, no cuts" verdicts |

Findings are shown before any edit; nothing is changed without confirmation, and safety-relevant instructions are never trimmed.

## Proof

Real results from Hermes running barber against actual skills, as reported in the merged PRs:

| Skill audited | Before | After | Cut |
|---|---|---|---|
| `last30days` | 1709 lines | 844 lines | 51% ([PR #1](https://github.com/maxkilla/barber/pull/1)) |

PR #2 reports findings from auditing 3 additional skills (example-density and generated-file issues found, no line-count delta reported for those passes).

No automated benchmark suite exists in this repo yet — these numbers are from real dogfooding sessions, not a `bench` script. Treat them as anecdotal until more runs land.

## When to use / when to skip

**Use it if you…**
- maintain more than one Claude Skill and want to catch trigger collisions or duplicated logic between them
- suspect a skill isn't firing when it should (or fires when it shouldn't)
- are about to publish a skill and want a bloat/token-cost pass first

**Skip it if you…**
- have a single small skill that's already lean — barber will just say "clean, no cuts"
- want automated CI-based regression testing — barber is a manual audit pass run by Claude in-conversation, not a test framework or eval harness
- need hard guarantees on token savings — the estimates are a rough per-line heuristic (~3.3 tok/line), not a tokenizer-verified count

## License

MIT — see [LICENSE](LICENSE).
