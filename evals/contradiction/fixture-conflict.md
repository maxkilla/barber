---
name: release-notes
description: "Writes release notes from merged PRs. Use whenever the user asks for release notes, a changelog entry, or a summary of what shipped. Also use when they say 'what changed in this version'."
---

# Release Notes

## Workflow
1. List merged PRs since the last tag.
2. Group them by type: features, fixes, chores.
3. Write one line per PR.

## Style
- Always keep each entry to a single line under 80 characters.
- Include the PR description in full for every feature so readers have context.
- Always address the reader as "you".
- Never use second person; write in neutral third person.

## Output
- Default to Markdown output.
- Default to plain text output with no formatting, since release notes get pasted into email.

## Safety
- Always ask the user to confirm before publishing the notes to GitHub.
- Publish the notes to the GitHub release immediately once drafted; do not wait.
