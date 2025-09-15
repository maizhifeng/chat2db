# Git history rewrite notice

This repository had a history-rewrite operation performed to remove large build artifacts (frontend/dist, frontend/.angular, frontend/package-lock.json) from the git history.

Why
---
Large committed build artifacts caused excessive repository size and slow clones. The team removed them from history to keep the repo small and maintainable.

Backup
------
A backup branch was created before the rewrite: `backup/frontend-migration-20250915`. If you need the old history, you can fetch it from the remote (if still present) or contact the repository admin.

What changed for collaborators
-----------------------------
After a destructive history rewrite, your local clones will diverge from the remote. To safely update your local clone, follow one of these approaches:

Option A (recommended - reclone):

1. Move your existing local repo copy aside (or delete if you have no local-only changes):

```bash
cd ..
mv chat2db chat2db.backup
```

2. Clone a fresh copy:

```bash
git clone git@github.com:maizhifeng/chat2db.git
cd chat2db
```

Option B (if you have local commits you want to preserve):

1. Create a branch to save your work:

```bash
git checkout -b my-work-save
```

2. Fetch the rewritten remote and reset master (this will rewrite your local history):

```bash
git fetch origin
# Replace local master with remote master
git checkout master
git reset --hard origin/master
```

3. Rebase your saved branch on top of the new master:

```bash
git checkout my-work-save
git rebase master
# resolve any conflicts, then
git checkout master
git merge my-work-save
```

Notes & Support
----------------
- If you relied on release artifacts in the repo (for CI or deployments), switch to a release mechanism (publish artifacts to a registry or attach them to releases).
- If you're unsure how to proceed, contact the repository owner or open an issue in the project.

