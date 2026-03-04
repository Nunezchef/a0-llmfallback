from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check-compatibility.sh"


class CheckCompatibilityTests(unittest.TestCase):
    def test_accepts_current_anchor_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "run_ui.py").write_text("")
            (root / "python" / "helpers").mkdir(parents=True)
            (root / "webui" / "components" / "settings" / "agent").mkdir(parents=True)

            (root / "python" / "helpers" / "settings.py").write_text(
                textwrap.dedent(
                    """
                    browser_model_kwargs: dict[str, Any]
                    browser_http_headers: dict[str, Any]

                    def convert_out(settings):
                        # normalize certain fields
                        pass

                    def _get_api_key_field(settings: Settings, provider: str, title: str) -> SettingsField:
                        pass

                    def convert_in(settings):
                        current[key] = value

                    browser_http_headers=get_default_value("browser_http_headers", {}),
                    """
                ).strip()
                + "\n"
            )
            (root / "webui" / "components" / "settings" / "agent" / "agent-settings.html").write_text(
                textwrap.dedent(
                    """
                                  <li>
                                    <a href="#section-memory">
                                  <div id="section-memory" class="section">
                    """
                ).strip()
                + "\n"
            )

            result = subprocess.run(
                [
                    "bash",
                    "-lc",
                    f'die() {{ echo "$1" >&2; exit 91; }}; . "{SCRIPT}"; check_compatibility "{root}"',
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
