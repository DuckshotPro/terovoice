# Plan: Fix Git Push Secret Scanning Blocks

GitHub blocked the push to `dev-sync` because of a Twilio secret exposed in the history (commit `c8eba70`). To fix this, we need to remove the offending file from the git history.

## Steps

1.  **Rewrite History**: Use `git filter-branch` to completely remove `powers/twilio-phone-management/POWER.md` from the current branch history.
    *   Command: `git filter-branch --force --index-filter "git rm --cached --ignore-unmatch powers/twilio-phone-management/POWER.md" --prune-empty --tag-name-filter cat HEAD`
2.  **Verify Removal**: Ensure the file is gone from history.
3.  **Push Branch**: Force push the cleaned `dev-sync` branch to GitHub.
