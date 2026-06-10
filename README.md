# Sophon Research

Sophon Research is a Codex plugin, Agent Skill, and Python CLI for researching
AI evals, benchmarks, models, tools, leaderboards, capabilities,
organizations, people, and papers through Sophon's public catalog.

It is local-first, read-only, and unauthenticated. It uses Sophon's official
JSON and text endpoints rather than scraping pages.

## What It Does

- Search Sophon's catalog across evals, tools, models, papers, leaderboards,
  organizations, people, and capabilities.
- Fetch structured entity metadata, scores, source links, and relationships.
- Preview paper text or safely save paper text/PDF files when Sophon exposes
  them under the source license.
- Fetch `llms.txt` and `llms-full.txt` catalog context for agents.
- Provide an Agent Skills-compatible `sophon-research` skill for research
  workflows and citation discipline.

## Requirements

- Python 3.12 or newer.
- Internet access to `https://sophon.at`.
- Codex plugin support for plugin installation.
- No Sophon API key, OpenAI key, or local secret is required.

## Install

Use from a source checkout:

```sh
git clone https://github.com/jerryfane/sophon-research.git
cd sophon-research
bin/sophon-research --help
```

Install the Python CLI in editable mode if you want `sophon-research` on your
`PATH`:

```sh
python3 -m pip install -e .
sophon-research doctor
```

Install as a Codex plugin from the public repo:

```sh
codex plugin marketplace add jerryfane/sophon-research --ref main
codex plugin add sophon-research --marketplace sophon-research
```

If the marketplace already exists, refresh it before reinstalling:

```sh
codex plugin marketplace upgrade
codex plugin add sophon-research --marketplace sophon-research
```

## CLI Examples

Check reachability and inspect endpoints:

```sh
bin/sophon-research doctor
bin/sophon-research api --json
```

Search and fetch an eval:

```sh
bin/sophon-research search "swe-bench" --limit 3
bin/sophon-research search "swe-bench" --type evals --json
bin/sophon-research search "swe-bench" --type eval --per 3 --sort recent --json
bin/sophon-research get evals swe-bench --json
```

Fetch agent-oriented context:

```sh
bin/sophon-research llms
bin/sophon-research llms --full --json
```

Preview or save paper content:

```sh
bin/sophon-research paper pwc-50106 --text
bin/sophon-research paper pwc-50106 --text --output /tmp/paper.txt
bin/sophon-research paper pwc-50106 --pdf --output /tmp
```

Paper text printed to stdout is bounded. Use `--output` for full paper text.
PDF downloads always require explicit `--output`. Downloads refuse overwrites,
use private file permissions where supported, enforce `--max-bytes`, and print a
receipt with path, byte count, and SHA-256.

## Skill Examples

After the plugin is installed, ask Codex to use the `sophon-research` skill for
tasks like:

```text
Use Sophon Research to compare current SWE-bench-related evals and cite sources.
```

```text
Use Sophon Research to find papers and leaderboards related to tool-using coding agents.
```

The skill tells agents to prefer the local CLI, cite/source Sophon-derived
claims, distinguish inference from direct data, and verify important technical
claims against primary papers or official project documentation.

## Safety

- Do not use internet research tools during benchmark-solving contexts where
  internet access is disallowed.
- Do not commit downloaded papers, generated research outputs, caches,
  credentials, or local plugin build output.
- Treat Sophon as a discovery source. Verify final high-stakes technical claims
  against primary papers, benchmark repositories, model docs, or official tool
  documentation.
- Sophon paper text/PDF endpoints return content only when licensing permits
  redistribution. Respect upstream paper and source licenses.

## Configuration

`SOPHON_BASE` can point the CLI at another Sophon-compatible host:

```sh
SOPHON_BASE=http://localhost:3000 bin/sophon-research api
```

Leave it unset for production `https://sophon.at`.

## Limitations

- The CLI is read-only and does not submit or mutate Sophon data.
- Search relevance and entity relationships are determined by Sophon's catalog.
- Paper text/PDF availability depends on upstream licensing and Sophon's source
  visibility rules.
- The plugin does not include MCP or Go support in v0.

## License

MIT. Catalog content returned by Sophon carries its upstream licenses.
