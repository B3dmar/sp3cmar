---
description: Create a GitHub issue with full hygiene — template, labels, parent sub-issue, project board, milestone
---

Create a GitHub issue end-to-end in one step. Render the right template, validate labels, set milestone, link to a parent epic as a sub-issue, add to the default project board, and (optionally) record a 3ngram commitment. Eliminates the 3-4 prompt sequence of `gh issue create` → label fix → parent link → project add.

## Arguments

`$ARGUMENTS` controls behavior. Parse the user's prompt for the following fields. If any required field is missing, ASK — do NOT silently default. Labels matter and a wrong default poisons the backlog.

Required:
- `title` — short imperative title, under 70 chars
- `type` — one of `bug | task | feature | spike | epic`. Maps to `.github/ISSUE_TEMPLATE/<type>.yml`
- `priority` — one of `p0 | p1 | p2 | p3`
- `area` — domain label, e.g. `mcp`, `memory`, `frontend`, `ops`, `auth`, `billing`, `infra`. Repo-specific.

Optional:
- `--parent <N>` — parent issue number; when present the new issue is linked as a sub-issue of `#N`
- `--milestone <name>` — milestone title to attach (must exist)
- `--assignee <user>` — defaults to the current `gh auth` user when unspecified
- `--no-project` — skip adding to the default project board
- `--no-commit` — skip the 3ngram commitment write
- `--dry-run` — print the rendered body and the exact `gh` invocation without creating anything

## Steps

### 1. Resolve repo + collect args

```bash
gh repo view --json nameWithOwner,defaultBranchRef
```

Parse `$ARGUMENTS` into the fields above. If anything required is missing, prompt the user with a one-shot question listing the missing fields. Do not assume.

### 2. Locate the issue template

Look for `.github/ISSUE_TEMPLATE/<type>.yml` in the repo root.

- If found: render it, filling form fields from the user's prompt and asking once for any free-text section that has no obvious value.
- If not found: format a minimal Markdown body with `## Summary`, `## Acceptance criteria`, `## Notes` sections. Do NOT invent a template path that doesn't exist.

### 3. Validate labels exist

```bash
gh label list --limit 200 --json name | jq -r '.[].name'
```

Required labels for any issue:
- `type:<type>` (e.g. `type:bug`, `type:feature`)
- `priority:<priority>` (e.g. `priority:p1`)
- `area:<area>` (e.g. `area:mcp`)

If a label does NOT exist, surface that to the user and offer the closest existing labels. Do NOT auto-create labels — label taxonomy is curated.

### 4. Create the issue

Write the rendered body to a temp file (`/tmp/sp3cmar-issue-<timestamp>.md`) and invoke:

```bash
gh issue create \
  --title "<title>" \
  --body-file <tmpfile> \
  --label "type:<type>,priority:<priority>,area:<area>" \
  $( [[ -n "$milestone" ]] && echo "--milestone \"$milestone\"" ) \
  $( [[ -n "$assignee" ]] && echo "--assignee $assignee" )
```

Capture the returned issue number from stdout (typically `https://github.com/<owner>/<repo>/issues/<N>`).

### 5. Verify the issue

Per the global CLAUDE.md guideline, never reference an issue number you haven't verified.

```bash
gh issue view <N> --json number,title,labels,milestone,state
```

Confirm: number matches, title matches, all three labels are attached, milestone is set if requested.

### 6. Link as sub-issue (if `--parent <N>` was given)

GitHub sub-issue links require GraphQL — not exposed via `gh issue` flags.

```bash
# Fetch node IDs for parent and child
parent_id=$(gh api graphql -f query='
  query($owner:String!,$repo:String!,$num:Int!){
    repository(owner:$owner,name:$repo){issue(number:$num){id}}
  }' -F owner=<owner> -F repo=<repo> -F num=<parent_N> --jq '.data.repository.issue.id')

child_id=$(gh api graphql -f query='
  query($owner:String!,$repo:String!,$num:Int!){
    repository(owner:$owner,name:$repo){issue(number:$num){id}}
  }' -F owner=<owner> -F repo=<repo> -F num=<new_N> --jq '.data.repository.issue.id')

# Link
gh api graphql -f query='
  mutation($parent:ID!,$child:ID!){
    addSubIssue(input:{issueId:$parent,subIssueId:$child}){
      subIssue{number}
    }
  }' -F parent=$parent_id -F child=$child_id
```

Verify the link via `gh issue view <parent_N> --json subIssuesSummary` (or by re-fetching the parent's sub-issue list).

### 7. Add to default project board (skip if `--no-project`)

```bash
owner=$(gh repo view --json owner --jq '.owner.login')
gh project list --owner "$owner" --format json --jq '.projects[] | {number,title}'
```

Pick the default project (typically `B3dmar/projects/1` for B3dmar repos — confirm by title if multiple). Then:

```bash
gh project item-add <project_number> --owner "$owner" --url <issue_url>
```

Set status, type, priority, and area fields if the project schema exposes them — use `gh project field-list` to discover field IDs and `gh project item-edit` to set values.

### 8. Save 3ngram commitment (skip if `--no-commit`)

If 3ngram MCP is connected, persist a commitment so future sessions surface this issue:

```
mcp__3ngram__remember(
  text="Created issue #<N>: <title> (<type>/<priority>/<area>)",
  classification="commitment",
  scope="work"
)
```

If 3ngram is unavailable, skip silently with a one-line note.

### 9. Summarize

Output:

```
## Issue #<N> created

- Title: <title>
- URL: <url>
- Labels: type:<type>, priority:<priority>, area:<area>
- Milestone: <name or none>
- Parent: #<N> (sub-issue linked) | none
- Project: added to <project_title> | skipped
- 3ngram commitment: <memory_id> | skipped
```

If `--dry-run`, output the rendered body, the exact `gh` invocation, and stop before step 4.
