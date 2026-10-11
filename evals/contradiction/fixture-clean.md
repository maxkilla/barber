---
name: commit-messages
description: "Writes commit messages from a staged diff. Use whenever the user asks for a commit message, says 'commit this', or wants a diff summarized for git history."
---

# Commit Messages

## Workflow
1. Read the staged diff.
2. Identify the single main change.
3. Write the message.

## Style
- Subject line under 72 characters, imperative mood.
- For small changes, subject line only.
- For changes touching more than three files, add a short body explaining why.
- Use the repo's existing prefix convention if one is visible in recent history; otherwise none.

## Safety
- Ask before running `git commit`; never amend or force-push.
