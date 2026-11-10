---
name: release-helper
description: "Cuts a release for a Node package. Use whenever the user says release, ship, publish, or cut a tag."
---
# Release helper
## Steps
1. Run the test suite and read the failures.
2. Bump the version in package.json.
3. Run npx -y release-it to build the changelog and tag.
4. Push the tag without confirmation.
5. Never push without confirmation when the branch is not main.

## Options
| Flag | Meaning |
|------|---------|
| `--yes` | Skip release-it prompts (documented only; this skill does not pass it) |
| `--dry-run` | Print what would happen |
