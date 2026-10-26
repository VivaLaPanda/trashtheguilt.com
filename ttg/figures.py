"""Assemble every figure on the page from the numbers module."""

import csv
import importlib.util
import math
from dataclasses import dataclass
from html import escape
from pathlib import Path

from markupsafe import Markup

from ttg import art_bed, art_landfill, art_objects
from ttg.charts import Flow, Row, Step, hbars, ranges, sankey, waterfall
from ttg.numbers import BIN, CLIMATE, LANDFILL, OCEAN, Country
from ttg.svg import circle, el, path, r, rect, svg, text

DATA = Path(__file__).resolve().parent.parent / "data"
WIDE = 720


def variants(narrow: str, wide: str) -> str:
    """Phone and desktop versions of one chart; CSS shows one of them."""
    return narrow.replace('class="fig"', 'class="fig v-narrow"', 1) + wide.replace('class="fig"', 'class="fig v-wide"', 1)


def as_art(svg_markup: str) -> str:
    return svg_markup.replace('class="fig"', 'class="fig art"', 1)


def meijer_countries() -> list[Country]:
    with open(DATA / "meijer2021_countries.csv", newline="") as f:
        return [Country(row["country"], float(row["tonnes"]), float(row["share_pct"])) for row in csv.DictReader(f)]


def _pct(v: float) -> str:
    return f"{v:.2f}%" if v < 1 else f"{v:.1f}%"


def data_table(head: list[str], rows: list[list[str]]) -> Markup:
    th = "".join(f'<th{" class=n" if i else ""}>{escape(h)}</th>' for i, h in enumerate(head))
    trs = "".join(
        "<tr>" + "".join(f'<td{" class=n" if i else ""}>{escape(c)}</td>' for i, c in enumerate(row)) + "</tr>" for row in rows
    )
    return Markup(f'<details class="data"><summary>Data</summary><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></details>')


# Cards


def card_ocean() -> str:
    """The Pasig against every US river, circle areas to scale."""
    o = OCEAN
    big_r = 128
    small_r = big_r * (o.us_tonnes / o.pasig_tonnes) ** 0.5
    base = 284
    cx, sx = 158, 158 + big_r + 44 + small_r
    body = "".join(
        [
            circle(cx, base - big_r, big_r, "s f-deep"),
            circle(sx, base - small_r, small_r, "s f-accent"),
            text(cx, base - big_r - 6, "Pasig River,", "t t-big", anchor="middle"),
            text(cx, base - big_r + 14, "Manila", "t t-big", anchor="middle"),
            text(cx, base - big_r + 40, f"{round(o.pasig_tonnes, -3):,.0f} t a year", "t t-strong", anchor="middle"),
            text(sx, base - 2 * small_r - 30, "Every US", "t t-big", anchor="middle"),
            text(sx, base - 2 * small_r - 12, "river", "t t-big", anchor="middle"),
            text(sx, base + 22, f"{round(o.us_tonnes, -2):,.0f} t", "t t-strong", anchor="middle"),
        ]
    )
    return svg(400, base + 30, body, "Two circles with areas to scale: the Pasig River's plastic is 26 times all US rivers combined")


def card_landfill() -> str:
    fp = LANDFILL.footprint_sq_ft
    s = 1.22
    body = art_bed.bed(1.5, 6, s, (fp.low, fp.high))
    return svg(38 * s + 3, 75 * s + 8, body, "A twin bed seen from above, with a lifetime of buried trash drawn to scale inside it")


def card_climate() -> str:
    return art_objects.card_dog_vs_bag()


# Ocean


def o3() -> tuple[str, Markup]:
    cs = meijer_countries()
    top = cs[:10]
    us = next(c for c in cs if c.name == "United States")
    rows = [Row(c.name, c.share_pct, c.share_pct, _pct(c.share_pct)) for c in top]
    rows.append(Row("United States", us.share_pct, us.share_pct, _pct(us.share_pct), accent=True))
    aria = "Share of global river plastic reaching the ocean, by country; the US is 0.25%"
    chart = variants(hbars(rows, aria, label_w=112, w=360), hbars(rows, aria, label_w=140, w=WIDE))
    table = data_table(["Country", "Tonnes a year", "Share"], [[c.name, f"{c.tonnes:,.0f}", _pct(c.share_pct)] for c in [*top, us]])
    return chart, table


def _mound(n: int, cols: int) -> list[tuple[int, int]]:
    """Cells (col, row) for a centered half-ellipse pile of exactly n items, row 0 at the bottom."""
    rows = math.ceil(n / cols * 4 / math.pi)
    widths = [round(cols * math.sqrt(max(0.0, 1 - (rw / rows) ** 2))) for rw in range(rows)]
    excess = sum(widths) - n
    for rw in reversed(range(rows)):
        cut = min(excess, widths[rw])
        widths[rw] -= cut
        excess -= cut
    return [((cols - w) // 2 + c, rw) for rw, w in enumerate(widths) for c in range(w)]


def o4() -> str:
    o = OCEAN
    p: list[str] = []
    clip = "o4clip"
    frac = o.per_american_g / o.bag_g
    p.append(art_objects.bag(70, 8))
    p.append(text(90, 74, f"One grocery bag: {o.bag_g:.0f} g", "t t-strong", anchor="middle"))
    # the American's year: the same bag, filled to 7/8 by height
    bx, by = 270, 8
    p.append(el("clipPath", rect(bx, by + 48 * (1 - frac), 40, 48 * frac, ""), id=clip))
    p.append(art_objects.bag(bx, by))
    p.append(el("g", art_objects.bag(bx, by, cls="f-accent"), clip_path=f"url(#{clip})"))
    p.append(text(290, 74, f"An American's year: {o.per_american_g:.0f} g", "t t-strong", anchor="middle"))
    # the Philippines: one glyph per bag
    n = round(o.philippines_bags)
    cols = 36
    k = 0.22
    gw, gh = 40 * k + 1.3, 48 * k + 1.2
    cells = _mound(n, cols)
    base = 104 + math.ceil(n / cols * 4 / math.pi) * (48 * k + 1.2)
    x0 = (400 - cols * gw) / 2
    glyphs = "".join(art_objects.bag_glyph(x0 + c * gw, base - (rw + 1) * gh, k) for c, rw in cells)
    p.append(el("g", glyphs))
    p.append(path(f"M{r(x0 - 6)},{base}H{r(x0 + cols * gw + 6)}", "s ln"))
    about = round(n, -2)
    kg = f"{o.philippines_kg_per_person:.1f}"
    p.append(text(200, base + 18, f"The Philippines, per person: {kg} kg, about {about} bags", "t t-strong", anchor="middle"))
    return as_art(svg(400, base + 26, "".join(p), f"One 8 g grocery bag; an American's yearly 7 g; and a pile of about {about} bags for the Philippines' {kg} kg per person"))


# Landfills


def l3() -> str:
    lf = LANDFILL
    fp, jp = lf.footprint_sq_ft, lf.japan_footprint_sq_ft
    body, h = art_bed.l3_figure(lf.bed_sq_ft, (fp.low, fp.high), (jp.low, jp.high), lf.doormat_sq_ft)
    return as_art(svg(400, h, body, "A twin bed seen from above with a lifetime of buried trash drawn inside it, and a doormat showing the same trash after incineration"))


def l4() -> str:
    body, h = art_landfill.landfill()
    return as_art(svg(400, h, body, "Modern landfills are sealed, drained and monitored."))


# Climate


def k3() -> tuple[str, Markup]:
    c = CLIMATE
    steps = [
        Step("Make", c.make, f"+{c.make:.1f}", "up"),
        Step("Burn", c.burn_kg_per_kg, f"+{c.burn_kg_per_kg:.2f}", "up"),
        Step("Energy back", -c.energy_back, f"−{c.energy_back:.2f}", "credit"),
        Step("Net", c.net_burned, f"{c.net_burned:.1f}", "total"),
    ]
    chart = waterfall(steps, "Kilograms of CO2e per kilogram of plastic burned: make, burn, energy back, net", 6, [0, 1, 2, 3, 4, 5, 6])
    table = data_table(["Step", "kg CO2 per kg"], [[s.label, s.value_label] for s in steps])
    return chart, table


def k4_rows() -> list[Row]:
    c = CLIMATE
    py = c.plastic_year
    rows = [
        Row("Your plastic, a year", py.low, py.high, f"{_r10(py.low)} to {_r10(py.high)}", accent=True),
        Row("Cheese, a year", c.cheese_year, c.cheese_year, f"{c.cheese_year:,.0f}"),
        Row("A dog, a year", c.dog_kg.low, c.dog_kg.high, f"{c.dog_kg.low:,.0f} to {c.dog_kg.high:,.0f}"),
        Row("5 drives to Tahoe", c.tahoe.low, c.tahoe.high, f"{c.tahoe.low:,.0f} to {c.tahoe.high:,.0f}"),
        Row("London round trip", c.flight_round_trip, c.flight_round_trip, f"{c.flight_round_trip:,.0f}"),
    ]
    return rows


def _r10(v: float) -> int:
    return int(round(v / 10) * 10)


def k4() -> tuple[str, Markup]:
    rows = k4_rows()
    aria = "Kilograms of CO2e a year: your plastic against cheese, a dog, Tahoe drives and a flight"
    ticks = [0, 400, 800, 1200]
    chart = variants(ranges(rows, aria, ticks, label_w=150, w=380), ranges(rows, aria, ticks, label_w=170, w=WIDE))
    table = data_table(["Item", "kg CO2"], [[rw.label, rw.value_label] for rw in rows])
    return chart, table


# In the bin


def r3() -> tuple[str, Markup]:
    b = BIN
    flows = [
        Flow("Landfill", b.landfilled_m, f"{b.landfilled_m:.1f}M tons", accent=True),
        Flow("Burned for energy", b.energy_m, f"{b.energy_m:.1f}M tons"),
        Flow("Recycled", b.recycled_m, f"{b.recycled_m:.1f}M tons"),
    ]
    total = f"{b.plastic_generated_m:.1f}M tons of US plastic, 2018"
    aria = "Three quarters of US plastic goes to landfill."
    chart = sankey(total, flows, aria)
    table = data_table(["Where US plastic went, 2018", "Million tons"], [[f.label, f"{f.value:.1f}"] for f in flows])
    return chart, table


def r4() -> tuple[str, Markup]:
    rows = [Row(name, v, v, f"{v:.1f}%", accent=name.startswith("PET")) for name, v in BIN.recycled_pct_by_resin]
    aria = "Share of each plastic type recycled in the US, 2018; PET is highest at 18.5%"
    chart = variants(hbars(rows, aria, label_w=92, w=360), hbars(rows, aria, label_w=120, w=WIDE))
    table = data_table(["Type", "Recycled, 2018"], [[rw.label, rw.value_label] for rw in rows])
    return chart, table


def can() -> str:
    return svg(48, 68, art_objects.can(), "An aluminum can", cls="fig can")


def scene() -> str | None:
    """The knockout scene, once its module exists."""
    if importlib.util.find_spec("ttg.art_scene") is None:
        return None
    from ttg import art_scene  # optional module

    body, w, h = art_scene.scene()
    return svg(w, h, body, "A sunrise city with wind turbines, solar roofs, new apartments going up and a garbage truck at work")


@dataclass(frozen=True)
class Figures:
    figs: dict[str, Markup]
    tables: dict[str, Markup]


def build() -> Figures:
    o3_svg, o3_t = o3()
    k3_svg, k3_t = k3()
    k4_svg, k4_t = k4()
    r4_svg, r4_t = r4()
    r3_svg, r3_t = r3()
    figs = {
        "c1": card_ocean(),
        "c2": card_landfill(),
        "c3": card_climate(),
        "o3": o3_svg,
        "o4": o4(),
        "l3": l3(),
        "l4": l4(),
        "k3": k3_svg,
        "k4": k4_svg,
        "r3": r3_svg,
        "r4": r4_svg,
        "can": can(),
        "scene": scene(),
    }
    tables = {"o3": o3_t, "k3": k3_t, "k4": k4_t, "r4": r4_t, "r3": r3_t}
    return Figures({k: Markup(v) for k, v in figs.items() if v}, tables)
