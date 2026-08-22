# barber

<img src="assets/logo.png" alt="barber logo" width="400">

**Audits and repackages Claude/Hermes skills — trims bloat, fixes weak triggers, catches duplication, fills real gaps, all with your approval.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Install

```bash
mkdir -p ~/.claude/skills/barber
curl -o ~/.claude/skills/barber/SKILL.md https://raw.githubusercontent.com/maxkilla/barber/main/SKILL.md
```

Hermes: same command, swap `~/.claude/skills/` for `~/.hermes/skills/`. Barber detects which runtime it's in automatically.

## What it does

An 8-part audit, one finding per line, on any SKILL.md:

1. **Description** — weak or missing triggers
2. **Body** — bloat, repetition, over-explaining
3. **Structure** — misplaced scripts/assets, broken references, generated files
4. **Dependencies** — unconditional installs, missing version pins
5. **Safety** — never trims confirmation/authority language
6. **Generalization** — triggers that are too narrow or too broad
7. **Cross-skill dedup** — redundant bodies, missing co-load links
8. **Gaps** (opt-in, `--gaps`) — what's dangerously *missing*, not just what's bloated

Every finding is shown before any edit. Nothing changes without approval.

## Usage

- *"audit this skill"* — full pass
- *"why isn't my skill triggering"* — sections 1 & 6
- *"which of my skills overlap"* — section 7
- *"tune up my skill library"* — cheap pass across everything installed
- *"enhance this skill"* (`--enhance`) — bounded audit → approve → fix → retest loop, capped at 3 cycles

Flags: `--check-only`, `--max-lines N`, `--tokens`, `--gaps`, `--enhance`.

## When to skip it

A single small skill that's already lean, or if you want automated CI regression testing — barber is a manual, in-conversation audit, not a test framework.

## License

MIT — see [LICENSE](LICENSE).
