import tempfile
import unittest
from pathlib import Path

from meta_agent.validator import check_markdown_links


class MarkdownLinkValidationTest(unittest.TestCase):
    def run_link_check(self, files):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for relative_path, content in files.items():
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            errors = []
            check_markdown_links(root, errors)
            return errors

    def test_valid_relative_link_passes(self):
        errors = self.run_link_check({
            "README.md": "See [guide](docs/GUIDE.md).",
            "docs/GUIDE.md": "# Guide\n",
        })
        self.assertEqual(errors, [])

    def test_missing_relative_link_fails(self):
        errors = self.run_link_check({"README.md": "See [guide](docs/MISSING.md)."})
        self.assertTrue(any("missing file" in error for error in errors))

    def test_external_links_are_ignored(self):
        errors = self.run_link_check({"README.md": "See [site](https://example.com)."})
        self.assertEqual(errors, [])

    def test_anchor_links_are_ignored(self):
        errors = self.run_link_check({"README.md": "See [section](#section)."})
        self.assertEqual(errors, [])

    def test_file_with_anchor_passes_when_file_exists(self):
        errors = self.run_link_check({
            "README.md": "See [guide](docs/GUIDE.md#section).",
            "docs/GUIDE.md": "# Section\n",
        })
        self.assertEqual(errors, [])

    def test_outside_project_link_fails(self):
        errors = self.run_link_check({"docs/nested/GUIDE.md": "See [outside](../../../outside.md)."})
        self.assertTrue(any("outside project" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
