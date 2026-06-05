---
name: sophon-research
description: Research AI evals, benchmarks, models, tools, leaderboards, capabilities, organizations, people, and papers using Sophon's public read-only catalog and local CLI. Use when comparing AI benchmarks, discovering papers, mapping eval/model/tool relationships, or collecting cited AI research context.
license: MIT
compatibility: Requires internet access and the sophon-research CLI.
---

# Sophon Research

Use this skill when the user asks for AI research context from Sophon's public
catalog: evals, benchmarks, models, tools, leaderboards, capabilities,
organizations, people, and papers.

Prefer the local `sophon-research` CLI. If it is not on `PATH` and this skill
is installed as a Codex plugin, resolve the plugin root from this file at
`<plugin-root>/skills/sophon-research/SKILL.md` and use
`<plugin-root>/bin/sophon-research` (`../../bin/sophon-research` relative to
this file). Use `./bin/sophon-research` only after verifying the current
checkout is Sophon Research itself, with `.codex-plugin/plugin.json` name
`sophon-research` and `skills/sophon-research/SKILL.md` present.

Sophon is read-only, unauthenticated, and should be queried through its API/text
endpoints rather than scraped pages.

## Quick Start

Check the CLI and API:

```sh
sophon-research doctor
sophon-research api
```

Search and fetch structured entities:

```sh
sophon-research search "swe-bench" --limit 5
sophon-research search "swe-bench" --type evals --json
sophon-research get evals swe-bench --json
```

Fetch paper context only when Sophon exposes it under the source license:

```sh
sophon-research paper <paper-slug> --text
sophon-research paper <paper-slug> --text --output /tmp/paper.txt
sophon-research paper <paper-slug> --pdf --output /tmp
```

Use `--json` when another tool or agent will consume the result. Human output is
compact and may be truncated; JSON output is stable but still bounded for large
paper text unless `--output` is used.

## When To Use

- Discover evals, benchmarks, datasets, leaderboards, and top scores.
- Compare models, tools, and agents across Sophon entities.
- Find papers related to an eval, model, capability, person, or organization.
- Map relationships across entities before checking primary sources.
- Gather source-linked context for an AI research summary.

## When Not To Use

- Do not use Sophon during benchmark-solving contexts where internet access is
  disallowed.
- Do not scrape Sophon pages when CLI/API endpoints are available.
- Do not treat Sophon as the final authority for high-stakes technical claims.
  Verify important claims against primary papers, official docs, or benchmark
  repositories.
- Do not commit downloaded papers, generated research outputs, caches, or local
  files created during research.

## Workflow

1. Start broad with `search`, then narrow by type when the user asks about a
   specific class of entity.
2. Fetch the best candidate entities with `get <type> <slug> --json`.
3. Follow relationships in the entity JSON: scores, capabilities, publishers,
   papers, tools, organizations, and related models.
4. For papers, preview text with `paper <slug> --text`; use `--output` for full
   text or any PDF.
5. Summaries must include citations or source links from Sophon results and
   note when a claim was inferred from relationships rather than directly
   stated.

## References

- Read [references/api.md](references/api.md) when you need endpoint details,
  CLI flags, JSON mode, or download safety behavior.
- Read [references/research-workflow.md](references/research-workflow.md) when
  producing comparisons, relationship maps, cited summaries, or paper-oriented
  research notes.
