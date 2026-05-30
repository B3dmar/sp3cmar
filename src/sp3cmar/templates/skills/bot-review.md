---
description: Read inbound automated PR-review comments (CodeRabbit, Vercel Agent, Copilot, CodeQL), triage each, and report a merge-gate verdict
---

# Bot Review

Read the automated PR-review comments left by review bots, triage every one, and
produce a single explicit **merge-gate verdict**. This is the missing "check the
automatic PR-review comments before merging" step: it closes the loop between a
bot flagging something and a human (or agent) deciding whether the PR is safe to
merge.

This is a **runbook you follow as prose** — do NOT implement a standalone polling
daemon or background service in code. The quiescence loop below is something the
agent executes by re-running `gh` queries, not a program to write.

## Arguments

`$ARGUMENTS` controls behavior:
- *(empty)* — resolve the PR for the current branch and triage it
- `<number>` — triage PR #`<number>` explicitly
- `--no-reply` — triage and report only; do not post any replies to bot comments
- `--no-wait` — skip the quiescence poll; triage whatever exists right now

## Recognized review bots

Filter inbound comments to these automated authors (GitHub login on the left;
match case-insensitively, and treat any `[bot]` suffix as part of the login):

| Bot | Author login | Typical output |
|-----|--------------|----------------|
| CodeRabbit | `coderabbitai` (and `coderabbitai[bot]`) | inline + summary review comments |
| Vercel Agent | `vercel[bot]` | deployment + AI review comments |
| GitHub Copilot | `copilot-pull-request-reviewer` (and `[bot]`) | review suggestions |
| CodeQL / GitHub Advanced Security | `github-advanced-security` (and `[bot]`) | security alerts surfaced on the PR |

Treat any other `*[bot]` author that posts review-style comments as a bot too,
but always include at least the four above. Never triage comments from human
authors here.

## Steps

### 1. Resolve the target PR

```bash
# Explicit number from $ARGUMENTS, else the PR for the current branch:
PR=$(gh pr view --json number --jq .number 2>/dev/null)
# If $ARGUMENTS contains a number, use that instead.
gh pr view "$PR" --json number,title,headRefName,baseRefName,state,url
```

If no PR exists for the current branch, stop and tell the user to open one first.

### 2. Enumerate review threads and comments via gh

Pull every source of bot feedback. Use both the high-level `gh pr view` JSON and
the lower-level REST endpoints so nothing is missed:

```bash
# Reviews + top-level conversation comments
gh pr view "$PR" --json reviews,comments

# Inline review (diff) comments — the "pulls comments" endpoint
gh api "repos/{owner}/{repo}/pulls/$PR/comments" --paginate

# Issue-style PR comments (summary posts land here)
gh api "repos/{owner}/{repo}/issues/$PR/comments" --paginate

# Review threads with their resolved/unresolved state (GraphQL)
gh api graphql -f query='
  query($owner:String!,$repo:String!,$pr:Int!){
    repository(owner:$owner,name:$repo){
      pullRequest(number:$pr){
        reviewThreads(first:100){
          nodes{
            isResolved
            comments(first:50){ nodes{ author{ login } body path } }
          }
        }
      }
    }
  }' -F owner=:owner -F repo=:repo -F pr="$PR"
```

For CodeQL / GitHub Advanced Security findings, also check the code-scanning
alerts surfaced on the PR head ref:

```bash
gh api "repos/{owner}/{repo}/code-scanning/alerts?ref=refs/pull/$PR/head" --paginate 2>/dev/null || true
```

Filter every result to the recognized bot authors from the table above. Record,
per comment: author, file/path, line, body, and the review-thread `isResolved`
state. A thread that is already `isResolved` does not block the gate.

### 3. Triage each comment

For EVERY unresolved bot comment, assign **exactly one** of three triage
outcomes:

| Outcome | What it means | Required action |
|---------|---------------|-----------------|
| **true-positive** | The bot is right; the code needs a change. | Fix it, `git commit` the fix, then **reply to the comment with the fixing commit hash** (e.g. "Fixed in `<sha>`"). |
| **false-positive** | The bot is wrong or the flag does not apply here. | Reply with a brief **won't-fix rationale** (one or two sentences explaining why). |
| **uncertain** | Cannot confidently decide; needs judgment. | **Surface to a human** — do not auto-fix or dismiss. List it in the report under "Needs human review". |

Reply to comments with `gh`:

```bash
# Reply on an inline review comment (in_reply_to = the comment id)
gh api "repos/{owner}/{repo}/pulls/$PR/comments" -f body="Fixed in $SHA" -F in_reply_to=$COMMENT_ID

# Or a general PR comment
gh pr comment "$PR" --body "Won't fix: <one-line reason>"
```

If `--no-reply` is set, skip posting replies but still classify every comment and
record the action you *would* have taken.

### 4. Poll until settled (quiescence window)

Bots post asynchronously and often follow up after a push. Before declaring the
PR **settled**, wait for a quiescence window of approximately **10 minutes** with
no new bot activity:

1. Note the timestamp of the most recent bot comment / review.
2. Re-run the step-2 queries every minute or two.
3. If a new bot comment appears, triage it (step 3) and reset the 10-minute timer.
4. When ~10 minutes elapse with **no new bot comment**, consider the PR settled.

Skip this loop entirely if `--no-wait` is passed. This is a prose poll the agent
performs by re-querying `gh`; do **not** build a background daemon for it.

### 5. Emit the per-comment triage table

Always output a table with one row per triaged bot comment:

```markdown
| # | Bot | File:Line | Tag | Outcome | Action |
|---|-----|-----------|-----|---------|--------|
| 1 | coderabbitai | api/auth.py:42 | security | true-positive | Fixed in a1b2c3d |
| 2 | vercel[bot] | ui/Button.tsx:8 | style | false-positive | Won't fix: intentional spacing |
| 3 | github-advanced-security | db/query.py:19 | bug | uncertain | Surfaced to human |
```

`Tag` is the comment's category: `security`, `bug`, `style`/`nit`, or `other`.
Infer it from the bot's own labeling (CodeRabbit and CodeQL tag severity) or from
the comment body.

### 6. Merge-gate verdict

Produce a single explicit verdict using these rules:

- An **unresolved** bot comment tagged **security** or **bug** → the PR is
  **MERGE-BLOCKING**.
- Comments tagged **style** / **nit** are **advisory only** — they never block.
- `uncertain` items tagged security/bug also block until a human resolves them.
- If every blocking comment has been fixed (true-positive + committed) or
  justified (false-positive), and the PR is settled, the verdict is **CLEAR**.

Output one of:

```markdown
## Merge-gate verdict: MERGE-BLOCKING
Blocking comments: #1 (security, coderabbitai), #3 (bug, github-advanced-security — uncertain, needs human)
```

or

```markdown
## Merge-gate verdict: CLEAR
All security/bug comments resolved; remaining comments are advisory (style/nit).
Settled: no bot activity for >10 min.
```

## Output

Output the per-comment triage table and the merge-gate verdict directly in the
conversation. The only files this skill changes are the source fixes you commit
for true-positive findings — it does not write reports to disk.
