from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class RepoMetadataTests(unittest.TestCase):
    def test_index_plugin_points_to_public_repo(self) -> None:
        plugin_yaml = Path("/a0/plugins/llm-fallback/plugin.yaml").read_text()
        self.assertIn("github: https://github.com/Nunezchef/a0-llmfallback", plugin_yaml)

    def test_repository_does_not_ship_install_scripts(self) -> None:
        self.assertFalse((REPO_ROOT / "install.sh").exists())
        self.assertFalse((REPO_ROOT / "uninstall.sh").exists())
        self.assertFalse((REPO_ROOT / "scripts").exists())

    def test_runtime_files_are_self_contained(self) -> None:
        self.assertTrue(
            (REPO_ROOT / "runtime" / "usr" / "extensions" / "agent_init" / "_20_llm_fallback.py").exists()
        )
        self.assertTrue((REPO_ROOT / "runtime" / "usr" / "helpers" / "llm_fallback.py").exists())
        self.assertTrue(
            (REPO_ROOT / "runtime" / "webui" / "components" / "settings" / "agent" / "llm_fallback.html").exists()
        )

    def test_readme_describes_self_contained_distribution(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text()
        self.assertIn("self-contained plugin repository", readme)
        self.assertNotIn("curl -fsSL", readme)
        self.assertNotIn("install.sh", readme)


if __name__ == "__main__":
    unittest.main()
