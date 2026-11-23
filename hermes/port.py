#!/usr/bin/env python3
"""Build the Hermes port of mattpocock/skills from the upstream tree.

  ./hermes/port.py --check            diff a fresh build against the installed set (no writes)
  ./hermes/port.py --install          rebuild ~/.hermes/skills/mattpocock and hermes/skills/mattpocock

The port is deterministic: upstream skill dirs are copied, then exactly these transforms run:
  1. SKIP    skills already provided by a Hermes skill of the same name (kept on purpose).
  2. RENAME  skills whose name collides with an unrelated Hermes skill; references rewritten.
  3. NOTES   a marked "Hermes runtime notes" block appended to SKILL.md files that rely on
             Claude Code mechanics (the Skill tool, sub-agents).
Never hand-edit the installed copy: change this script, re-run --install, commit.
"""
import argparse, filecmp, os, re, shutil, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM_CATS = ["skills/engineering", "skills/productivity"]
INSTALLED = os.path.expanduser(os.environ.get("HERMES_SKILLS_DIR", "~/.hermes/skills/mattpocock"))
FORK_COPY = os.path.join(REPO, "hermes", "skills", "mattpocock")
CATEGORY_README = os.path.join(REPO, "hermes", "category-README.md")

# Existing Hermes skills that already ARE these (older/adapted copies of Matt's own skill).
SKIP = {
    "grilling": "existing top-level `grilling` = Matt's earlier one-question-at-a-time version",
    "wayfinder": "existing top-level `wayfinder` = local-markdown adapted copy",
}
# Upstream name -> Hermes name, where the Hermes name is taken by an unrelated skill.
RENAME = {
    "code-review": "mattpocock-code-review",  # Hermes `code-review` is a generic security checklist
}

BEGIN, END = "<!-- hermes-port:begin -->", "<!-- hermes-port:end -->"
NOTE_SKILL_TOOL = ("- \"Call the Skill tool with X\" means load it with `skill_view(name='X')` "
                   "and follow it.")
NOTE_SUBAGENTS = (
    "- Sub-agents are `delegate_task`. Run parallel ones as ONE call with `tasks: [...]`. Each child\n"
    "  starts with a fresh context and sees only its `goal`/`context`: pass file paths (spec, tickets,\n"
    "  notes) rather than pasted content. Children cannot spawn children, so you (the parent) own\n"
    "  merges and follow-up dispatch. Background children report back between your turns.")


def upstream_skills():
    out = {}
    for cat in UPSTREAM_CATS:
        root = os.path.join(REPO, cat)
        for name in sorted(os.listdir(root)):
            if os.path.isfile(os.path.join(root, name, "SKILL.md")):
                out[name] = os.path.join(root, name)
    return out


def rewrite_refs(text):
    for old, new in RENAME.items():
        text = re.sub(rf"(?<![\w-]){re.escape(old)}(?![\w-])", new, text)
    return text


def notes_for(text):
    notes = []
    if re.search(r"Skill tool", text):
        notes.append(NOTE_SKILL_TOOL)
    if re.search(r"sub-?agent", text, re.I):
        notes.append(NOTE_SUBAGENTS)
    return notes


def build(dest):
    report = []
    for name, src in upstream_skills().items():
        if name in SKIP:
            report.append(f"skip    {name}  ({SKIP[name]})")
            continue
        target = RENAME[name] if name in RENAME else name
        out = os.path.join(dest, target)
        shutil.copytree(src, out)
        for dp, _, files in os.walk(out):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dp, fn)
                orig = open(p, encoding="utf-8").read()
                text = rewrite_refs(orig)
                if fn == "SKILL.md" and dp == out:
                    if name in RENAME:
                        text = re.sub(r"^name:\s*.*$", f"name: {target}", text, count=1, flags=re.M)
                    notes = notes_for(orig)
                    if notes:
                        text = (text.rstrip("\n") + f"\n\n{BEGIN}\n## Hermes runtime notes\n\n"
                                + "\n".join(notes) + f"\n{END}\n")
                if text != orig:
                    open(p, "w", encoding="utf-8").write(text)
        report.append(f"{'rename' if name in RENAME else 'port':7} {name}"
                      + (f" -> {target}" if name in RENAME else ""))
    shutil.copy(CATEGORY_README, os.path.join(dest, "README.md"))
    return report


def diff_trees(a, b):
    """Return (only_in_a, only_in_b, changed) relative paths."""
    def files(root):
        s = set()
        for dp, _, fns in os.walk(root):
            for fn in fns:
                s.add(os.path.relpath(os.path.join(dp, fn), root))
        return s
    fa, fb = files(a), files(b)
    changed = sorted(p for p in fa & fb
                     if not filecmp.cmp(os.path.join(a, p), os.path.join(b, p), shallow=False))
    return sorted(fa - fb), sorted(fb - fa), changed


def replace_tree(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--install", action="store_true")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        built = os.path.join(tmp, "mattpocock")
        os.makedirs(built)
        report = build(built)
        print("\n".join(report))
        print()
        if args.check:
            if not os.path.isdir(INSTALLED):
                print(f"not installed: {INSTALLED}")
                return 1
            new, gone, changed = diff_trees(built, INSTALLED)
            for label, items in (("NEW (would add)", new), ("STALE (would remove)", gone),
                                 ("CHANGED", changed)):
                if items:
                    print(label + ":")
                    print("\n".join("  " + i for i in items))
            if not (new or gone or changed):
                print(f"installed set matches a fresh build ({INSTALLED})")
                return 0
            return 2
        replace_tree(built, INSTALLED)
        replace_tree(built, FORK_COPY)
        print(f"installed -> {INSTALLED}\nfork copy -> {FORK_COPY}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
