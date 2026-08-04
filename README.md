# barber

**Audits and repackages Claude Skills — trims bloat, fixes weak triggers, catches cross-skill duplication.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Install](#install) · [What it does](#what-it-does) · [Usage](#usage) · [When to use / when to skip](#when-to-use--when-to-skip) · [License](#license)

---

Skills are always-on context tax: every skill's name + description sits in the model's context window permanently, and its body loads on every trigger. Fat skills, weak triggers, and duplicated logic across skills cost tokens and cause silent misfires forever. Barber audits and cuts.

## Install

Copy `SKILL.md` into your skills directory:

**Claude Code / Claude:**
```bash
mkdir -p ~/.claude/skills/barber
curl -o ~/.claude/skills/barber/SKILL.md https://raw.githubusercontent.com/maxkilla/barber/main/SKILL.md
```

Or package as a `.skill` file (zip containing `barber/SKILL.md`) and upload via claude.ai's skill import.

## What it does

Runs a 7-part audit, one finding per line, on any SKILL.md (installed, downloaded, or freshly drafted):

1. **Description** — undertriggering, missing "use when" phrasing, collisions with other skills
2. **Body** — redundant instructions, over-explaining, files that should split into `references/`
3. **Structure** — deterministic work that should be `scripts/`, inline assets that should move to `assets/`
4. **Dependency hygiene** — unconditional installs replaced with check-then-install, missing version pins
5. **Safety** — never trims confirmation/authority/stopping-condition language; flags injection-shaped content
6. **Generalization pass** — flags trigger descriptions that are overfit (only match tested phrasings) or overbroad (keyword-match with no scope boundary), per the "weakest correct hypothesis" principle ([Bennett 2023](https://arxiv.org/abs/2301.12987))
7. **Cross-skill dedup & composability** — flags redundant bodies across skills, missing co-load links, and stale "use alongside X" references

## Usage

In a Claude conversation with this skill installed:

- *"comb this skill"* / *"audit my skill"* — full 7-part pass on one skill
- *"why isn't my skill triggering"* — focused pass on section 1/6
- *"which of my skills overlap"* — cross-skill pass (section 7)
- *"tune up my whole skill library"* — cheap description-only pass across all installed skills, reports the 3 worst offenders

Findings are shown before any edit; nothing is changed without confirmation, and safety-relevant instructions are never trimmed.

## When to use / when to skip

**Use it if you…**
- maintain more than one Claude Skill and want to catch trigger collisions or duplicated logic between them
- suspect a skill isn't firing when it should (or fires when it shouldn't)
- are about to publish a skill and want a bloat/token-cost pass first

**Skip it if you…**
- have a single small skill that's already lean — barber will just say "clean, no cuts"
- want automated CI-based regression testing — barber is a manual audit pass run by Claude in-conversation, not a test framework or eval harness

## License

MIT — see [LICENSE](LICENSE).
