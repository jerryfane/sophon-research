# Sophon Research

Sophon Research is a Codex plugin and local CLI for researching AI evals,
models, tools, leaderboards, capabilities, organizations, people, and papers
through Sophon's public read-only catalog.

The plugin is local-first and requires no Sophon API key. It uses Sophon's
official JSON and text endpoints rather than scraping pages.

## Status

Initial scaffold. The first version will add a tested Python CLI, Agent
Skills-compatible research instructions, safe paper downloads, and Codex plugin
installation docs.

## Usage

```sh
bin/sophon-research --help
```

## Safety

Do not use internet research tools during benchmark-solving contexts where
internet access is disallowed. Do not commit downloaded papers, generated
research outputs, caches, credentials, or local plugin build output.
