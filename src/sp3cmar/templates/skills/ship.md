---
description: Lint, commit, push, and create PR in one step
---

Ship the current changes. Run quality checks, verify docs are updated, commit, push, and optionally create a PR.

## Arguments

`$ARGUMENTS` controls behavior:
- *(empty)* — lint, commit, push, create PR to staging
- `commit` — lint and commit only (no push, no PR)
- `main` — create PR to main (use when on staging branch)
- `--no-lint` — skip lint checks (use sparingly)
- `--no-simplify` — skip the /simplify pass

## Steps

### 1. Pre-flight checks

- Run `git status` to see all changed files
- Run `git diff --stat` to gauge change size
- Identify the current branch name and base branch
- If on `main` or `staging`, STOP — do not commit directly to protected branches

### 2. Quality gate (skip if `--no-lint`)

Detect the project's lint tooling and run checks on changed files only:

- **Python** (if `pyproject.toml` with ruff/mypy config exists):
  ```
  ruff check <changed-python-files>
  ruff format --check <changed-python-files>
  mypy <changed-python-files>
  ```
- **TypeScript/JavaScript** (if `package.json` with eslint config exists):
  ```
  npx eslint <changed-ts-files>
  npx tsc --noEmit
  ```
- **Both** (monorepo): run each in its subdirectory
- **Generated types** (if a `generate:api-types` script exists in `package.json`):
  ```
  npm run generate:api-types
  ```
  If the generated file changed, stage it automatically alongside other changes.

If any check fails, fix the issues and re-run. Do NOT skip failures.

### 3. Simplify pass (skip if `--no-lint` or `--no-simplify`)

Run `/simplify` on all changed files to clean up reuse, quality, and efficiency issues:

- Collect the list of changed files from Step 1
- Run `/simplify` targeting those files
- If `/simplify` made changes: re-stage the affected files and re-run the lint checks from Step 2
- If no changes: proceed

### 4. Documentation check

Review the changed files and determine if documentation updates are needed:

- **What to check**: README, API docs, config references, inline doc comments, CLAUDE.md project instructions, skill descriptions, or any docs that describe behavior being changed
- **Triggers requiring doc updates**:
  - New or renamed CLI commands, skills, or public API endpoints
  - Changed configuration options, environment variables, or defaults
  - Modified user-facing behavior or workflows
  - New dependencies or changed system requirements
- **If docs need updating**: make the doc changes now, before committing. Keep updates minimal and in the canonical location (don't create new docs when an existing one covers the topic).
- **If no docs are affected**: proceed — not every change needs doc updates.

### 5. Commit

- Stage changed files (prefer specific files over `git add -A`)
- Do NOT stage files that look like secrets (.env, credentials, tokens)
- Draft a conventional commit message: `<type>(<scope>): <subject>`
  - 50 char subject, imperative mood, no period
  - Add body for complex changes explaining what/why
  - Reference issues where relevant
- Create the commit with `Co-Authored-By: Claude <noreply@anthropic.com>` trailer

If `$ARGUMENTS` is `commit`, stop here.

### 6. Push

- Push to remote with `-u` flag to set upstream tracking
- If push fails due to divergence, inform the user — do NOT force push

### 7. Create PR

- Determine base branch:
  - If current branch is `staging` and `$ARGUMENTS` is `main`: base = `main`
  - Otherwise: base = `staging`
- Determine issue-linking keywords based on base branch:
  - If base = `staging`: use `Relates to #N` or `Part of #N` for linked issues.
    Do NOT use `Fixes`, `Closes`, or `Resolves` — these prematurely close issues on staging merge.
  - If base = `main`: use `Fixes #N` or `Closes #N` so GitHub auto-closes on merge.
- Create PR using `gh pr create`:
  - Title: short, under 70 chars
  - Body: summary bullets, test plan, linked issues (with correct keywords per above)
- Output the PR URL

### 8. CI status check

After push/PR creation, check CI status:

- Run `gh run list --branch <branch> --limit 1 --json status,conclusion`
- Report CI status inline:
  - **PENDING**: "CI running — check back shortly"
  - **PASS**: "CI passed"
  - **FAIL**: Show failed run summary with `gh run view <id> --log-failed | tail -30`
- This is informational only — does not block the ship
