# trashtheguilt.com

One static page: where US trash goes, with every number sourced.

## Build

```sh
uv sync
uv run build.py            # writes dist/, renders share images with headless Chromium
uv run build.py --no-og    # skip share images
```

- `ttg/numbers.py`: every input figure and the values derived from it. The build fails if a number written in the copy drifts from the data (`check_copy`).
- `ttg/sources.py`: the source registry; footnotes are numbered by first use.
- `ttg/charts.py`, `ttg/figures.py`, `ttg/art*.py`: inline SVG charts and illustrations.
- `templates/index.html.j2`: the page copy.
- `data/meijer2021_countries.csv`: river plastic to the ocean by country (Meijer et al. 2021, via Our World in Data).

Share images need a Chromium binary; set `CHROME=/path/to/chrome` if it isn't at the Playwright default.

## Deploy

```sh
scripts/deploy.sh          # build and deploy to Cloudflare Pages (production)
scripts/deploy.sh preview  # preview branch
```

The Cloudflare API token is read from `~/.config/cloudflare/token` (or `CF_TOKEN_FILE`) at deploy time and is never stored in the repo.
