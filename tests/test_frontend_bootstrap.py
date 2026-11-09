from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "static"


def test_spa_bootstrap_is_invoked_after_dom_is_ready():
    script = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "document.addEventListener('DOMContentLoaded', init, { once: true })" in script
    assert "  init();" in script
    assert "window.addEventListener('hashchange', renderRoute)" in script


def test_theme_toggle_updates_accessibility_and_persists_preference():
    script = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "data-action=\"theme\"" in script
    assert "aria-pressed" in script
    assert "localStorage.setItem('algoforge-theme'" in script
    assert "window.monaco.editor.setTheme" in script
    assert "document.documentElement.dataset.theme" in script


def test_first_paint_applies_saved_light_theme_before_app_bootstrap():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert "localStorage.getItem('algoforge-theme')==='light'" in html
    assert html.index("document.documentElement.dataset.theme='light'") < html.index("<body>")
    assert 'class="theme-toggle" data-action="theme"' in html


def test_cookie_disclosure_does_not_cover_page_content():
    css = (STATIC / "styles.css").read_text(encoding="utf-8")
    assert ".cookie-banner{position:relative;left:auto;right:auto;bottom:auto;transform:none" in css


def test_dashboard_does_not_show_fabricated_pattern_progress_percentages():
    script = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "const roadmapCards = [" not in script
    assert "analytics?.pattern_mastery" in script
    assert "based on your recorded progress" in script


def test_workspace_navigation_and_primary_landmarks_are_accessible():
    script = (STATIC / "app.js").read_text(encoding="utf-8")
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert '<nav class="sidebar-nav" aria-label="Workspace navigation">' in script
    assert '<main id="main-content"' in script
    assert '<a class="skip-link" href="#main-content">Skip to content</a>' in html
    assert 'id="toast-region" class="toast-region" aria-live="polite"' in html


def test_static_images_have_alternative_text():
    from html.parser import HTMLParser

    class ImageAltParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.images = []
        def handle_starttag(self, tag, attrs):
            if tag == "img":
                self.images.append(dict(attrs).get("alt"))

    parser = ImageAltParser()
    parser.feed((STATIC / "index.html").read_text(encoding="utf-8"))
    assert all(alt is not None for alt in parser.images)
