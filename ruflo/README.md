# Ruflo

**Multi-agent AI orchestration harness for Claude Code and Codex** (formerly "Claude Flow").

Ruflo adds coordinated agent swarms, self-learning vector memory, hooks-based task
routing, and an MCP server to Claude Code. After install, you keep using Claude Code
normally — the hooks system routes tasks, learns from successful patterns, and
coordinates agents in the background.

- Upstream: https://github.com/ruvnet/ruflo
- npm: https://www.npmjs.com/package/ruflo

> **Why this is a doc, not a vendored copy:** Ruflo is a published npm package
> (~1,168 transitive deps, native modules, alpha packages) and is meant to be
> installed via npm, not copied into a repo. This folder captures how to install
> and use it so any Claude session can reproduce the setup.

## Prerequisites

- Node.js >= 20 (the package `engines` field requires it)
- npm
- Optional: Claude Code CLI (Ruflo integrates with it but the CLI runs standalone)

## Install

Global install (makes the `ruflo` command available everywhere):

```bash
npm install -g ruflo
ruflo --version      # -> ruflo vX.Y.Z
```

Or run without installing:

```bash
npx -y ruflo --help
```

## Initialize in a project

Run inside the project you want Ruflo to manage. It scaffolds Claude Code
integration (`.claude/`, `.mcp.json`, `CLAUDE.md`) and a runtime (`.claude-flow/`):

```bash
cd your-project
ruflo init --yes          # scaffold; add --start-all to also start daemon+memory+swarm
ruflo memory init         # initialize the vector memory DB (.claude/memory.db)
ruflo doctor              # system diagnostics / health check
ruflo status              # show swarm / agents / tasks / memory state
```

`ruflo init` creates, among other things:

- `.claude/settings.json` — 7 self-learning hook types wired into Claude Code
- `.claude/skills/`, `.claude/commands/`, `.claude/agents/` — bundled skills/commands/agents
- `.mcp.json` — registers the `claude-flow` MCP server (`memory_store`, `swarm_init`, …)
- `.claude-flow/` — config.yaml, data, logs, sessions, learning, metrics

> **Heads up:** `ruflo init` writes into the project's `.claude/` directory. If the
> project already uses `.claude/` (e.g. the Arcads skill pack in this repo), Ruflo's
> files coexist with the existing ones but will add its own `CLAUDE.md`,
> `settings.json`, and 30 bundled skills. Initialize in a throwaway/dedicated
> project first if you want to inspect the output cleanly.

## Common commands

| Command | What it does |
|---|---|
| `ruflo init` | Initialize Ruflo in the current directory |
| `ruflo memory init` / `memory store` / `memory search` | Vector memory (384-dim, HNSW index) |
| `ruflo swarm init` | Initialize an agent swarm |
| `ruflo agent spawn -t coder` | Spawn a typed agent |
| `ruflo daemon start` | Start background workers |
| `ruflo mcp start` | Start the MCP server (stdio) |
| `ruflo doctor` / `ruflo status` | Diagnostics / runtime state |

Run `ruflo <command> --help` for per-command help.

## Notes from setup verification

This was installed and verified working:

- `npm install -g ruflo` → 1,168 packages, `ruflo` on PATH
- `ruflo doctor` → downloads the `all-MiniLM-L6-v2` ONNX embedding model on first run
- `ruflo memory init` → AgentDB ready, verification 6/6 passed
- `ruflo memory store` → entry written as a 384-dim vector, HNSW index active
- `ruflo memory search` applies an internal min-similarity cutoff, so a single-entry
  store may return no results even though the entry is indexed (expected behavior)
