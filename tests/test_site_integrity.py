from __future__ import annotations

import html.parser
import pathlib
import unittest
from urllib.parse import urljoin, urlsplit


ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://nigamafoundation.org"
SITE_HOSTS = {"nigamafoundation.org", "www.nigamafoundation.org"}


class AnchorParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.anchors.append(href)


def route_exists(path: str) -> bool:
    route = path.rstrip("/")
    if not route:
        return (ROOT / "index.html").is_file()
    relative = route.lstrip("/")
    return any(
        candidate.is_file()
        for candidate in (
            ROOT / relative,
            ROOT / f"{relative}.html",
            ROOT / relative / "index.html",
        )
    )


class SiteIntegrityTests(unittest.TestCase):
    def test_all_same_site_anchor_routes_exist(self) -> None:
        broken: list[str] = []
        for page in sorted(ROOT.glob("*.html")):
            parser = AnchorParser()
            parser.feed(page.read_text(encoding="utf-8"))
            page_url = urljoin(f"{SITE_ORIGIN}/", page.name)
            for href in parser.anchors:
                parsed = urlsplit(urljoin(page_url, href))
                if parsed.scheme not in {"http", "https"}:
                    continue
                if parsed.hostname not in SITE_HOSTS:
                    continue
                if not route_exists(parsed.path):
                    broken.append(f"{page.name}: {href}")

        self.assertEqual([], broken, "Broken same-site links:\n" + "\n".join(broken))

    def test_public_pages_do_not_show_a_stale_copyright_year(self) -> None:
        stale_pages = [
            page.name
            for page in sorted(ROOT.glob("*.html"))
            if "© 2025 Nigama Foundation" in page.read_text(encoding="utf-8")
        ]
        self.assertEqual([], stale_pages)

    def test_donation_amount_promises_are_consistent(self) -> None:
        for filename in ("index.html", "donate.html"):
            content = (ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(page=filename):
                self.assertIn("₹2,000: Uniform + Full Supply Kit", content)
                self.assertIn(
                    'data-amount="2000">₹2,000<span class="amount-label">Supply Kit</span>',
                    content,
                )
                self.assertIn(
                    'data-amount="10000">₹10,000<span class="amount-label">Program Support</span>',
                    content,
                )

    def test_homepage_recent_work_is_newest_first(self) -> None:
        content = (ROOT / "index.html").read_text(encoding="utf-8")
        titles = (
            "Project Parivarthan: Setting the Tone for 2026",
            "Ceipal Cares × Nigama: Classroom Education Drive",
            "Commitment to Youth Well-Being",
        )
        positions = [content.index(title) for title in titles]
        self.assertEqual(sorted(positions), positions)

    def test_site_metadata_uses_the_served_non_www_origin(self) -> None:
        files = [*ROOT.glob("*.html"), ROOT / "sitemap.xml"]
        offenders = [
            path.name
            for path in files
            if "https://www.nigamafoundation.org" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual([], offenders)

    def test_crawler_and_browser_discovery_files_exist(self) -> None:
        self.assertTrue((ROOT / "robots.txt").is_file())
        self.assertTrue((ROOT / "favicon.ico").is_file())
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap: https://nigamafoundation.org/sitemap.xml", robots)

    def test_public_pages_reference_favicon_and_social_image(self) -> None:
        self.assertTrue((ROOT / "images" / "social-share.jpg").is_file())
        missing: list[str] = []
        for page in sorted(ROOT.glob("*.html")):
            content = page.read_text(encoding="utf-8")
            if 'rel="icon" href="/favicon.ico"' not in content:
                missing.append(f"{page.name}: favicon")
            if 'name="robots" content="noindex' not in content:
                if 'property="og:image" content="https://nigamafoundation.org/images/social-share.jpg"' not in content:
                    missing.append(f"{page.name}: og:image")
                if 'name="twitter:card" content="summary_large_image"' not in content:
                    missing.append(f"{page.name}: twitter:card")
        self.assertEqual([], missing)

    def test_donate_page_has_a_real_upi_qr_code(self) -> None:
        content = (ROOT / "donate.html").read_text(encoding="utf-8")
        self.assertTrue((ROOT / "images" / "upi-donation-qr.png").is_file())
        self.assertIn('src="images/upi-donation-qr.png"', content)
        self.assertNotIn("Replace with UPI QR image", content)

    def test_public_pages_do_not_claim_unavailable_payment_methods(self) -> None:
        unavailable_claims = (
            "credit/debit, netbanking accepted",
            "bank transfer below",
            "bank transfer &amp; more ways to give",
        )
        offenders: list[str] = []
        for page in sorted(ROOT.glob("*.html")):
            content = page.read_text(encoding="utf-8")
            for claim in unavailable_claims:
                if claim in content:
                    offenders.append(f"{page.name}: {claim}")
        self.assertEqual([], offenders)
        donate_content = (ROOT / "donate.html").read_text(encoding="utf-8")
        self.assertIn("Donate today using the UPI QR", donate_content)

    def test_upi_donors_are_told_how_to_request_an_80g_receipt(self) -> None:
        content = (ROOT / "donate.html").read_text(encoding="utf-8")
        self.assertIn("UPI transaction ID", content)
        self.assertIn('href="mailto:donate@nigamafoundation.org', content)
        self.assertIn("PAN number if you need an 80G receipt", content)


if __name__ == "__main__":
    unittest.main()
