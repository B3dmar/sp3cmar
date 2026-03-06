# Contributing to sp3cmar

## Setup

```bash
git clone https://github.com/b3dmar/sp3cmar.git
cd sp3cmar
uv sync --group dev
```

## Adding a Skill

1. Create `src/sp3cmar/templates/skills/{name}.md` with `description` frontmatter
2. Add to `SKILLS` and `skill_info` in `constants.py`
3. If Cowork-compatible (pure analysis, no terminal/git dependency), add to `COWORK_SKILLS`
4. Run `uv run pytest` (template alignment tests catch missing entries)
5. Run `uv run sp3cmar build-plugin` to regenerate `cowork-plugin/`
6. Commit template + regenerated plugin files together

## Adding a Cowork-Only Skill

1. Create `src/sp3cmar/templates/skills/{name}.md`
2. Add to `COWORK_ONLY_SKILLS` in `constants.py`
3. Run tests and regenerate plugin

## Adding a 3ngram Extension

1. Create `src/sp3cmar/templates/engram/{name}.md`
2. Add to `ENGRAM_SKILLS` in `constants.py`
3. Copy to `extensions/3ngram/skills/`
4. Run tests

## Checks

```bash
uv run pytest                # tests
uv run ruff check            # lint
uv run ruff format --check   # format
uv run mypy --strict src/    # type check
```

## Cowork Plugin Sync

The `cowork-plugin/` directory is git-tracked. After changing templates:

```bash
uv run sp3cmar build-plugin
# Verify sync
diff -r cowork-plugin <(uv run sp3cmar build-plugin --output /dev/stdout 2>/dev/null)
```

CI will fail if the committed plugin is stale.

## Pull Requests

- Keep PRs under 200 lines
- All checks must pass (ruff, mypy, pytest, plugin sync)
- Commit messages: `<type>(<scope>): <subject>`
