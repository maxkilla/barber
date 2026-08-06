# barber

<img src="assets/logo.png" alt="barber logo" width="500">

**Audits and repackages Claude Skills and Hermes skills — trims bloat, fixes weak triggers, catches cross-skill duplication, estimates token cost, detects generated files.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Install](#install) · [Hermes compatibility](#hermes-compatibility) · [What it does](#what-it-does) · [How it works](#how-it-works) · [Usage](#usage) · [Proof](#proof) · [When to use / when to skip](#when-to-use--when-to-skip) · [License](#license)

---

Skills are always-on context tax: every skill's name + description sits in the model's context window permanently, and its body loads on every trigger. Fat skills, weak triggers, duplicated logic, and generated-file edits that silently get overwritten cost tokens and cause misfires forever. Barber audits and cuts.

## Install

Copy `SKILL.md` into your skills directory:

```bash
mkdir -p ~/.claude/skills/barber
curl -o ~/.claude/skills/barber/SKILL.md https://raw.githubusercontent.com/maxkilla/barber/main/SKILL.md
```

Or package as a `.skill` file (zip containing `barber/SKILL.md`) and upload via claude.ai's skill import.

## Agent install

**Claude Code:**
```bash
curl -o ~/.claude/skills/barber/SKILL.md \
  https://raw.githubusercontent.com/maxkilla/barber/main/SKILL.md
```

**Hermes:**
```bash
curl -o ~/.hermes/skills/barber/SKILL.md \
  https://raw.githubusercontent.com/maxkilla/barber/main/SKILL.md
```
Both paths work identically — barber detects the runtime (Claude vs Hermes) and routes tool calls (read_file/patch vs hermes file tools) accordingly. No per-platform SKILL.md required.

## What it does

Runs a 7-part audit, one finding per line, on any SKILL.md — installed, downloaded, or freshly drafted:

1. **Description** — undertriggering, missing "use when" phrasing, trigger phrase coverage gaps, collisions with other skills
2. **Body** — redundant instructions, over-explaining, example-dense sections that should split into `references/`, over-500-line threshold (frontmatter excluded)
3. **Structure** — deterministic work that should be `scripts/`, inline assets that should move to `assets/`, dangling references/*.md pointers, generated-file headers (DO NOT EDIT / GENERATED / mirrors)
4. **Dependency hygiene** — unconditional installs replaced with check-then-install, missing version pins
5. **Safety** — never trims confirmation/authority/stopping-condition language; flags injection-shaped content
6. **Generalization pass** — flags trigger descriptions that are overfit (only match tested phrasings) or overbroad (keyword-match with no scope boundary), per the "weakest correct hypothesis" principle ([Bennett 2023](https://arxiv.org/abs/2301.12987))
7. **Cross-skill dedup & composability** — flags redundant bodies across skills, missing co-load links, and stale "use alongside X" references

**Modes:** full audit (default), `--check-only` (findings only, no edits), `--max-lines N` (auto-skip small skills), `--tokens` (estimated context cost + savings).

## Usage

In a Claude conversation with this skill installed:

- *"comb this skill"* / *"audit my skill"* — full 7-part pass on one skill
- *"why isn't my skill triggering"* — focused pass on section 1/6
- *"which of my skills overlap"* — cross-skill pass (section 7)
- *"tune up my whole skill library"* — cheap description-only pass across all installed skills, reports the 3 worst offenders with token estimates

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
- need to rank which skills to audit first (token estimation quantifies the cost)

**Skip it if you…**
- have a single small skill that's already lean — barber will just say "clean, no cuts"
- want automated CI-based regression testing — barber is a manual audit pass run by Claude in-conversation, not a test framework or eval harness
- need hard guarantees on token savings — the estimates are a rough per-line heuristic (~3.3 tok/line), not a tokenizer-verified count

## License

MIT — see [LICENSE](LICENSE).
