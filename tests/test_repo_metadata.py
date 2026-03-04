from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class RepoMetadataTests(unittest.TestCase):
    def test_index_plugin_points_to_public_repo(self) -> None:
        plugin_yaml = Path("/a0/plugins/llm-fallback/plugin.yaml").read_text()
        self.assertIn("github: https://github.com/Nunezchef/a0-llmfallback", plugin_yaml)

    def test_installer_uses_compatibility_check_script(self) -> None:
        install_sh = (REPO_ROOT / "install.sh").read_text()
        self.assertIn('scripts/check-compatibility.sh', install_sh)
        self.assertIn('check_compatibility "${target_root}"', install_sh)
        self.assertIn('trap \'[ -n "${cleanup_root:-}" ] && rm -rf "${cleanup_root}"\' EXIT', install_sh)

    def test_readme_inlines_installation_details(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text()
        self.assertIn("## Installation Details", readme)
        self.assertNotIn("## Trust And Transparency", readme)
        self.assertIn("1. Detects the Agent Zero root automatically", readme)


if __name__ == "__main__":
    unittest.main()
