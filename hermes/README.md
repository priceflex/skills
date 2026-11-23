# priceflex/skills — fork of [mattpocock/skills](https://github.com/mattpocock/skills)

Remotes: `origin` = this fork, `upstream` = `mattpocock/skills`. `main` tracks upstream untouched.
Branch `hermes-port` adds this `hermes/` directory: a reproducible Hermes Agent port.

## Files

- `port.py` — builds the Hermes skill pack from upstream `skills/engineering` and
  `skills/productivity`. Its transforms (skip / rename / Hermes notes) are declared at the top.
- `category-README.md` — installed as `mattpocock/README.md`; documents the transforms.
- `skills/mattpocock/` — the committed build output (25 skills), identical to what is installed.

## Commands

```bash
./hermes/port.py --check     # fresh build vs installed ~/.hermes/skills/mattpocock (no writes; exit 2 = drift)
./hermes/port.py --install   # rebuild installed copy + skills/mattpocock here
```

## Pulling upstream changes

```bash
git fetch upstream
git checkout main && git reset --hard upstream/main && git push origin main
git checkout hermes-port && git merge main
./hermes/port.py --check      # review what changes
./hermes/port.py --install
git add hermes && git commit -m "hermes: re-port from upstream <sha>" && git push
cd ~/.hermes/skills && git add mattpocock && git commit -m "mattpocock: re-port from upstream <sha>"
```

## Where it runs

`~/.hermes/skills` is the default profile's skill tree. 168 profiles symlink their `skills/`
to it, including every Comms Blitz `cb-*` worker (see `hermes_workspace_service.rb`: "skills ->
symlink to ~/.hermes/skills, live, shared, never cloned"). Those profiles see an install
immediately. Profiles with their own real `skills/` directory (`worker-template`,
`cb-99001-2185`) and profiles made by `hermes profile create --clone` hold a snapshot copy and
do not pick up later changes.
