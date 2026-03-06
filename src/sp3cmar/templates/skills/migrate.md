---
description: Codebase migration wrapper — scan, plan, execute, and commit bulk refactors
---

# Migrate

Execute a described codebase migration with inventory, ordered plan, and approval gate.

## Arguments

`$ARGUMENTS` controls behavior:
- `"<description>"` — natural language description of the migration (required)
- `--dry-run` — scan and plan only, do not execute

## Instructions

### Step 1: Parse Migration

Extract the migration intent from the description. Examples:
- "rename UserService to AccountService"
- "move all database queries from handlers to repository layer"
- "replace os.path with pathlib across the codebase"

### Step 2: Scan Affected Locations

Search the codebase for all locations affected by the migration:

```bash
# Example: find all references to the symbol/pattern being migrated
rg "pattern" --files-with-matches
```

Build an inventory:
| # | File | Line(s) | Context |
|---|------|---------|---------|
| 1 | src/api/handler.py | 12, 45 | Import and usage |

### Step 3: Generate Migration Plan

Order the changes to minimize breakage:

1. **Config/types** — shared type definitions, constants, config files
2. **Shared/library** — utility modules, base classes, interfaces
3. **Application** — business logic, handlers, services
4. **Tests** — test files that reference migrated code
5. **Docs** — documentation, README, comments

For each group, generate specific `/batch` instructions.

### Step 4: Approval Gate

Present the full plan:

```markdown
## Migration Plan: "<description>"

Affected files: N
Estimated changes: N locations across N files

### Execution Order
1. Config/types (N files)
2. Shared/library (N files)
3. Application (N files)
4. Tests (N files)
5. Docs (N files)
```

If `--dry-run`: stop here.

### Step 5: Execute

On user approval:

1. Execute each group in order via `/batch`
2. After each group: run lint and type checks
3. If a group fails checks: stop and report — do not proceed to next group
4. Run the full test suite after all groups complete

### Step 6: Commit

If all checks pass:

- Stage all changed files
- Commit with: `refactor(<scope>): <description>`
- Do NOT push — the user can review and push manually
- Output: "Migration committed. Run `git diff HEAD~1` to review, `git push` when ready."

If checks failed:
- Output the failures
- Do NOT commit
- Suggest: "Fix the failures, then run `git add -A && git commit`"
