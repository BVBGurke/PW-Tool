from __future__ import annotations

from pathlib import Path
import tomllib
import unittest

from version import __version__


class PackageMetadataTests(unittest.TestCase):
    def test_pyproject_matches_central_beta_version(self) -> None:
        project_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
        data = tomllib.loads(project_path.read_text(encoding="utf-8"))

        self.assertEqual("pw-tool", data["project"]["name"])
        self.assertEqual(__version__, data["project"]["version"])
        self.assertEqual("pw:main", data["project"]["scripts"]["pw-tool"])


if __name__ == "__main__":
    unittest.main()
