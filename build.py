"""Build the static site into dist/: uv run build.py [--no-og]."""

import argparse
import hashlib
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup, escape
from playwright.sync_api import sync_playwright

from ttg import figures
from ttg.numbers import check_copy
from ttg.sources import Notes

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
SITE = "https://trashtheguilt.com"
DESCRIPTION = "Modern disposal is contained and far from the ocean, so trash is not where your environmental worry should go."
CHROME = os.environ.get("CHROME", str(Path.home() / ".cache/ms-playwright/chromium-1243/chrome-linux64/chrome"))

SHARE_ICON = Markup(
    '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 10V2M5 4.5 8 1.5l3 3M3 7.5V14h10V7.5" '
    'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


@dataclass(frozen=True)
class Share:
    slug: str
    label: str
    num: str
    line: str
    fig: str
    band: str

    @property
    def text(self) -> str:
        return f"{self.num} {self.line}"


SHARES = [
    Share("26x", "26x", "26x.", "One river in Manila puts 26 times more plastic into the ocean than every US river combined.", "c1", "aqua"),
    Share("twin-bed", "Twin bed", "Twin bed.", "Your lifetime of trash, buried, takes up less floor space than a twin bed.", "c2", "lime"),
    Share("3x", "3x", "3x.", "Your dog has 3 times the climate footprint of your plastic. You don't sweat the kibble. Don't sweat the bag.", "c3", "sun"),
]


@dataclass(frozen=True)
class Meta:
    title: str
    og_title: str
    url: str
    image: str
    description: str = DESCRIPTION


def fingerprint(src: Path, dest_dir: Path) -> str:
    digest = hashlib.sha256(src.read_bytes()).hexdigest()[:10]
    name = f"{src.stem}.{digest}{src.suffix}"
    shutil.copyfile(src, dest_dir / name)
    return f"assets/{name}"


def labelled(figs: figures.Figures):
    """Template helper: a figure's SVGs with aria-label set to the chart title (rule V8)."""

    def fig_svg(key: str, title: str) -> Markup:
        body, n = re.subn(r'aria-label="[^"]*"', f'aria-label="{escape(title)}"', str(figs.figs[key]))
        if not n:
            raise ValueError(f"figure {key} has no aria-label")
        return Markup(body)

    return fig_svg


def render_pages(env: Environment, figs: figures.Figures, css: str, js: str) -> None:
    tpl = env.get_template("index.html.j2")
    pages = [(DIST / "index.html", Meta("Garbage in, guilt out.", "Garbage in, guilt out.", f"{SITE}/", "site"))]
    for s in SHARES:
        pages.append((DIST / s.slug / "index.html", Meta("Garbage in, guilt out.", s.text, f"{SITE}/{s.slug}/", s.slug)))
    for out, meta in pages:
        out.parent.mkdir(parents=True, exist_ok=True)
        html = tpl.render(
            meta=meta, site=SITE, css=css, js=js, figs=figs.figs, tables=figs.tables,
            n=Notes(), shares=SHARES, share_icon=SHARE_ICON, fig_svg=labelled(figs),
        )
        out.write_text(html)


def render_og(env: Environment, figs: figures.Figures) -> None:
    # fonts load relative to dist/, so render from a temporary file there
    css = (ROOT / "static/style.css").read_text().replace('url("/fonts/', 'url("fonts/')
    tpl = env.get_template("og.html.j2")
    cards = [(s.slug, s.num, s.line, figs.figs[s.fig], s.band) for s in SHARES]
    cards.append(("site", "Garbage in,<br>guilt out.", "", figs.figs["c3"], "cream"))
    out_dir = DIST / "og"
    out_dir.mkdir(exist_ok=True)
    tmp = DIST / "_og.html"
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1200, "height": 630}, color_scheme="light")
        for slug, num, line, art, band in cards:
            tmp.write_text(tpl.render(css=Markup(css), num=num, line=line, art=art, band=band))
            page.goto(tmp.as_uri())
            page.evaluate("document.fonts.ready")
            page.screenshot(path=str(out_dir / f"{slug}.png"))
        browser.close()
    tmp.unlink()


HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: interest-cohort=()
  Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self' https://static.cloudflareinsights.com; connect-src 'self' https://cloudflareinsights.com; base-uri 'none'; form-action 'none'; frame-ancestors 'none'
/assets/*
  Cache-Control: public, max-age=31536000, immutable
/og/*
  Cache-Control: public, max-age=3600
/fonts/*
  Cache-Control: public, max-age=2592000
"""

NOT_FOUND = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Not found</title><link rel="stylesheet" href="/{css}"><body><header class="wrap hero"><h1>Not found.</h1>
<p><a href="/">trashtheguilt.com</a></p></header></body></html>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-og", action="store_true", help="skip rendering share images")
    ap.add_argument("--allow-drift", action="store_true", help="warn instead of failing on copy/data mismatches")
    args = ap.parse_args()

    problems = check_copy()
    if problems and args.allow_drift:
        print("warning: " + "; ".join(problems), file=sys.stderr)
    elif problems:
        sys.exit("copy numbers drifted from the data:\n" + "\n".join(problems))

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    css = fingerprint(ROOT / "static/style.css", DIST / "assets")
    js = fingerprint(ROOT / "static/site.js", DIST / "assets")
    shutil.copyfile(ROOT / "static/favicon.svg", DIST / "favicon.svg")
    shutil.copytree(ROOT / "static/fonts", DIST / "fonts")

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html", "j2"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    figs = figures.build()
    render_pages(env, figs, css, js)
    (DIST / "404.html").write_text(NOT_FOUND.format(css=css))
    (DIST / "_headers").write_text(HEADERS)
    (DIST / "_redirects").write_text("/3-to-1/ /3x/ 301\n/3-to-1 /3x/ 301\n")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    (DIST / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE}/</loc></url></urlset>\n'
    )
    if not args.no_og:
        render_og(env, figs)
    print(f"built {sum(1 for _ in DIST.rglob('*') if _.is_file())} files into {DIST}")


if __name__ == "__main__":
    main()
