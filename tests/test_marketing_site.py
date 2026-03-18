from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "apps" / "site"
INDEX_HTML = SITE_ROOT / "index.html"
STYLES_CSS = SITE_ROOT / "styles.css"
APP_JS = SITE_ROOT / "app.js"
README = REPO_ROOT / "README.md"


class MarketingSiteTests(unittest.TestCase):
    def test_marketing_site_files_exist(self) -> None:
        for path in (INDEX_HTML, STYLES_CSS, APP_JS):
            self.assertTrue(path.exists(), path)

    def test_index_exposes_responsive_marketing_sections(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', html)
        self.assertIn('href="./styles.css"', html)
        self.assertIn('src="./app.js"', html)
        for section_id in (
            "hero",
            "proof",
            "workflow",
            "governance",
            "cta",
        ):
            self.assertRegex(html, rf'<section[^>]+id="{section_id}"')
        self.assertIn("EvCode", html)
        self.assertIn("source-build-first", html)
        self.assertIn("governed runtime", html)

    def test_styles_define_visual_system_and_responsive_rules(self) -> None:
        css = STYLES_CSS.read_text(encoding="utf-8")
        for token in (
            "--page-bg",
            "--panel-bg",
            "--accent",
            "--accent-warm",
            "--shadow-strong",
        ):
            self.assertIn(token, css)
        self.assertIn("@media (max-width: 900px)", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn("linear-gradient", css)
        self.assertIn("animation:", css)

    def test_script_supports_small_progressive_enhancements(self) -> None:
        script = APP_JS.read_text(encoding="utf-8")
        self.assertIn("IntersectionObserver", script)
        self.assertIn("data-reveal", script)
        self.assertIn("matchMedia('(prefers-reduced-motion: reduce)')", script)

    def test_readme_links_to_marketing_surface(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertRegex(readme, re.compile(r"apps/site/index\.html"))
        self.assertIn("Product Preview", readme)


if __name__ == "__main__":
    unittest.main()
