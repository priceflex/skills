# mattpocock/ — Matt Pocock (AI Hero) engineering skill pack

Ported from the open-source repos at aihero.dev on 2026-11-23. Source of record:
`mattpocock/skills` (engineering/ + productivity/ promoted skills). All 24 promoted
skills are here; the in-progress and misc repos' skills were left out.

## What's in here

The main flow, idea to ship:

    setup-matt-pocock-skills (once per repo)
    -> grill-with-docs / grill-me / wait-what / to-questionnaire (align)
    -> prototype / research (optional, when the question needs code)
    -> to-spec -> to-tickets (or wayfinder for fuzzy multi-ticket maps)
    -> implement (TDD, test-first) or implement-spec (parallel subagents)
    -> code-review -> pr -> retro

Supporting reference skills: tdd, diagnosing-bugs, codebase-design,
domain-modeling, improve-codebase-architecture, writing-for-agents,
teach, handoff, ask-matt (router: "which skill for this situation?").

## Three skills NOT installed (name collisions with existing default-profile skills)

- code-review -> existing `software-development/code-review` kept (security-focused review checklist)
- grilling -> existing top-level `grilling` kept (older, 21 lines; the candidate is a 30-line superset — swap it in if you want the newer one)
- wayfinder -> existing top-level `wayfinder` kept (223 lines, richer than the 128-line candidate)

They are functionally near-duplicates; the existing ones already cover the flow.

## Hermes adaptations (the only real deltas)

1. **Issue tracker.** `setup-matt-pocock-skills` configures per-repo where issues live.
   It supports GitHub (default), GitLab, and local-markdown (`.scratch/` files) out of the
   box — the local-markdown option means the whole flow works with zero external tooling.
   The setup skill writes `docs/agents/issue-tracker.md`, `docs/agents/domain.md`,
   and `docs/agents/triage-labels.md` into the target repo; every other skill in this
   category reads those files before acting.
2. **Parallel work.** Where the original says "Claude subagents", use Hermes `delegate_task`
   (batch form, up to 10 parallel). `implement-spec` and `wizard` assume this.
3. **Skill invocation.** The original chains skills via Claude's Skill tool; in Hermes the
   agent loads them via `skill_view(name='mattpocock/...')`. Same behavior, different loader.
4. **Slash commands.** These are skills, not Hermes slash commands. Ask for them by name
   ("run to-spec on this feature", "grill me on this plan").

## Usage

Run `setup-matt-pocock-skills` once per repo before first use of the engineering skills.
Everything else is model-invoked by situation.
