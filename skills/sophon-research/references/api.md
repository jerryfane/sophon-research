# Sophon API And CLI Reference

Use this file for concrete command and endpoint details. Prefer the local CLI
because it handles stable JSON output, bounded large text, safe file writes, and
readable exit codes.

## Official Surfaces

Sophon exposes read-only, unauthenticated catalog access:

- `GET /api/v1` - endpoint index.
- `GET /api/v1/search?q={query}` - full-text search across evals, tools,
  models, papers, leaderboards, organizations, people, and capabilities.
- `GET /api/v1/{type}/{slug}` - one entity with metadata, scores, and
  relationships. Supported types are `evals`, `models`, `tools`,
  `leaderboards`, `organizations`, `people`, `capabilities`, and `papers`.
- `GET /api/v1/papers/{slug}/text` - paper text when the upstream license
  permits redistribution.
- `GET /api/v1/papers/{slug}/pdf` - paper PDF when the upstream license permits
  redistribution.
- `GET /llms.txt` and `GET /llms-full.txt` - agent-friendly catalog context.

## CLI Commands

```sh
sophon-research doctor
sophon-research api [--json]
sophon-research search <query> [--type T] [--limit N] [--json]
sophon-research get <type> <slug> [--json]
sophon-research paper <slug> --text [--output PATH_OR_DIR] [--max-bytes N] [--json]
sophon-research paper <slug> --pdf --output PATH_OR_DIR [--max-bytes N] [--json]
sophon-research llms [--full] [--json]
sophon-research version
```

Use plural or singular entity types where supported: `evals`, `models`,
`tools`, `leaderboards`, `organizations`, `people`, `capabilities`, `papers`.

## Output Rules

- Use `--json` for downstream agent/tool parsing.
- Human search output is compact and grouped by Sophon result type.
- Paper text shown on stdout is a bounded preview; use `--output` for full text.
- PDF downloads require explicit `--output`.
- File writes refuse overwrite, use private permissions where supported, and
  print a receipt with path, byte count, and SHA-256.
- `--max-bytes` limits paper text/PDF responses and stops oversized downloads.

## Exit Codes

- `0` success.
- `1` remote/runtime/local file error.
- `2` local usage error, such as invalid entity type, missing `--output`, or
  overwrite refusal.

## Environment

`SOPHON_BASE` can point the client at another Sophon-compatible host. Leave it
unset for production `https://sophon.at`.
