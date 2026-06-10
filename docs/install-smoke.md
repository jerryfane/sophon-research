# Public Plugin Install Smoke

Last verified: 2026-06-05

This note records the supported public Codex plugin install path for the
`jerryfane/sophon-research` repository.

## Commands

```sh
codex plugin marketplace add jerryfane/sophon-research --ref main
codex plugin add sophon-research --marketplace sophon-research
```

Codex installed the plugin from the public GitHub marketplace into:

```text
/root/.codex/plugins/cache/sophon-research/sophon-research/0.1.1
```

## Verification

The installed plugin was listed as enabled:

```text
sophon-research@sophon-research 0.1.1 installed enabled
```

The installed skill file was present at:

```text
/root/.codex/plugins/cache/sophon-research/sophon-research/0.1.1/skills/sophon-research/SKILL.md
```

The installed CLI passed these smoke checks:

```sh
/root/.codex/plugins/cache/sophon-research/sophon-research/0.1.1/bin/sophon-research --help
/root/.codex/plugins/cache/sophon-research/sophon-research/0.1.1/bin/sophon-research version
/root/.codex/plugins/cache/sophon-research/sophon-research/0.1.1/bin/sophon-research doctor
/root/.codex/plugins/cache/sophon-research/sophon-research/0.1.1/bin/sophon-research search "swe-bench" --limit 3
```

Results:

- Version returned `sophon-research 0.1.1`.
- Doctor returned `ok Sophon API reachable: Sophon public API`.
- Search returned bounded Sophon results for `swe-bench` across eval,
  leaderboard, paper, person, and tool groups.
