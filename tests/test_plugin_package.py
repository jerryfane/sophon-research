from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "sophon-research"

SYNCED_PATHS = [
    ".codex-plugin/plugin.json",
    "LICENSE",
    "README.md",
    "assets/sophon-research-logo.svg",
    "bin/sophon-research",
    "pyproject.toml",
    "skills/sophon-research/SKILL.md",
    "skills/sophon-research/references/api.md",
    "skills/sophon-research/references/research-workflow.md",
    "src/sophon_research/__init__.py",
    "src/sophon_research/cli.py",
    "src/sophon_research/files.py",
    "src/sophon_research/formatting.py",
    "src/sophon_research/sophon.py",
]


class PluginPackageTests(unittest.TestCase):
    def test_marketplace_points_to_materialized_plugin_package(self) -> None:
        marketplace = json.loads(
            (REPO_ROOT / ".agents" / "plugins" / "marketplace.json").read_text()
        )

        self.assertEqual(marketplace["name"], "sophon-research")
        [entry] = marketplace["plugins"]
        self.assertEqual(entry["name"], "sophon-research")
        self.assertEqual(entry["source"]["source"], "local")
        self.assertEqual(entry["source"]["path"], "./plugins/sophon-research")
        self.assertTrue((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").is_file())
        self.assertTrue((PLUGIN_ROOT / "bin" / "sophon-research").is_file())
        self.assertTrue((PLUGIN_ROOT / "skills" / "sophon-research" / "SKILL.md").is_file())

    def test_plugin_package_copy_stays_in_sync(self) -> None:
        for relative_path in SYNCED_PATHS:
            with self.subTest(path=relative_path):
                root_file = REPO_ROOT / relative_path
                package_file = PLUGIN_ROOT / relative_path
                self.assertTrue(root_file.is_file(), root_file)
                self.assertTrue(package_file.is_file(), package_file)
                self.assertEqual(package_file.read_bytes(), root_file.read_bytes())

    def test_plugin_manifest_is_read_only_and_points_to_public_repo(self) -> None:
        manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())

        self.assertEqual(manifest["name"], "sophon-research")
        self.assertEqual(manifest["repository"], "https://github.com/jerryfane/sophon-research")
        self.assertEqual(manifest["interface"]["capabilities"], ["Read"])
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(
            manifest["interface"]["composerIcon"],
            "assets/sophon-research-logo.svg",
        )


if __name__ == "__main__":
    unittest.main()
