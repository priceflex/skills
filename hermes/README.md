# priceflex/skills — fork of [mattpocock/skills](https://github.com/mattpocock/skills)

Fork kept in sync with upstream (`mattpocock/skills` main).

## The `hermes/` directory (branch: `hermes-port`)

A Hermes Agent port of the promoted skill set:

- `hermes/skills/mattpocock/` — the 24 promoted skills (engineering + productivity),
  unchanged from upstream except that they are organized under the `mattpocock/`
  category and validated against Hermes SKILL.md frontmatter.
- `hermes/skills/mattpocock/README.md` — port notes: what was skipped (name
  collisions) and the Hermes-specific adaptations (issue tracker backend,
  `delegate_task` for parallel subagents, `skill_view` for skill chaining).

Installed live at `~/.hermes/skills/mattpocock/` on the TRS Hermes box (committed in
a local git repo at `~/.hermes/skills`).

## Re-porting from upstream

```bash
./hermes/sync.sh
```

Fetches upstream main, diffs it against the installed set, and reports which skills
are new, changed, or removed since the last port. It does NOT auto-apply: review the
diff, then copy changed skill dirs into `~/.hermes/skills/mattpocock/`, and commit
both places (the local skills git repo and this fork's `hermes-port` branch).

## Keeping the fork's main in sync with upstream

```bash
git fetch upstream main && git checkout main && git reset --hard upstream/main && git push origin main
```

Remotes: `origin` = this fork (`priceflex/skills`), `upstream` = `mattpocock/skills`.
