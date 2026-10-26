"""Screenshot a local HTML file or URL with headless Chromium: shot.py <src> <out.png> [width] [light|dark] [full|WxH]."""

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME = os.environ.get("CHROME", str(Path.home() / ".cache/ms-playwright/chromium-1243/chrome-linux64/chrome"))


def shoot(src: str, out: str, width: int = 390, scheme: str = "light", mode: str = "full") -> None:
    url = src if "://" in src else Path(src).resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME)
        if "x" in mode:
            w, h = (int(v) for v in mode.split("x"))
            page = browser.new_page(viewport={"width": w, "height": h}, color_scheme=scheme)
        else:
            page = browser.new_page(viewport={"width": width, "height": 800}, color_scheme=scheme, device_scale_factor=2 if width < 500 else 1)
        page.goto(url, wait_until="networkidle")
        page.screenshot(path=out, full_page="x" not in mode)
        browser.close()


if __name__ == "__main__":
    a = sys.argv[1:]
    shoot(a[0], a[1], int(a[2]) if len(a) > 2 else 390, a[3] if len(a) > 3 else "light", a[4] if len(a) > 4 else "full")
