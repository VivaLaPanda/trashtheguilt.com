"""Assemble every figure on the page from the numbers module."""

import csv
import math
from dataclasses import dataclass
from html import escape
from pathlib import Path

from markupsafe import Markup

from ttg import art
from ttg.charts import Flow, Row, Step, hbars, ranges, sankey, waterfall
from ttg.numbers import BIN, CLIMATE, LANDFILL, OCEAN, Country
from ttg.svg import bar_v, el, path, r, rect, svg, text

DATA = Path(__file__).resolve().parent.parent / "data"


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
    body = art.two_circles(240, OCEAN.pasig_tonnes, OCEAN.us_tonnes, "Pasig River", "All US rivers")
    return svg(240, 124, body, "Two circles with areas to scale: the Pasig River's plastic is 26 times all US rivers combined")


def card_landfill() -> str:
    fp = LANDFILL.footprint_sq_ft
    s = 1.22
    body = art.bed(0, 6, s, (fp.low, fp.high))
    return svg(38 * s, 75 * s + 8, body, "A twin bed seen from above, with a lifetime of buried trash drawn to scale inside it")


def card_climate() -> str:
    base = 128
    bar_w = 24
    unit = 30
    parts = [art.dog(0, 26, 1.02)]
    x_dog, x_bag = 128, 176
    parts.append(bar_v(x_dog, base, bar_w, unit * 3, "f-grey"))
    parts.append(bar_v(x_bag, base, bar_w, unit, "f-accent"))
    parts.append(art.bag(x_bag + 2, base - unit - 26, 0.5))
    parts.append(text(x_dog + bar_w / 2, base - unit * 3 - 7, "3", "t t-big", anchor="middle"))
    parts.append(text(x_bag + bar_w / 2 + 22, base - unit + 4, "1", "t t-big", anchor="middle"))
    parts.append(path(f"M112,{base}H214", "s ln"))
    return svg(216, 132, "".join(parts), "A happy dog beside a grocery bag; the dog's bar is three times the bag's")


# Ocean


def o3() -> tuple[str, Markup]:
    cs = meijer_countries()
    top = cs[:10]
    us = next(c for c in cs if c.name == "United States")
    rows = [Row(c.name, c.share_pct, c.share_pct, _pct(c.share_pct)) for c in top]
    rows.append(Row("United States", us.share_pct, us.share_pct, _pct(us.share_pct), accent=True))
    chart = hbars(rows, "Share of global river plastic reaching the ocean, by country; the US is 0.25%")
    table = data_table(["Country", "Tonnes a year", "Share"], [[c.name, f"{c.tonnes:,.0f}", _pct(c.share_pct)] for c in [*top, us]])
    return chart, table


def _mound(n: int, cols: int) -> list[tuple[int, int]]:
    """Cells (col, row) for a half-ellipse pile of exactly n items, row 0 at the bottom."""
    rows = math.ceil(n / cols * 4 / math.pi)
    cells: list[tuple[int, int]] = []
    for rw in range(rows):
        width = round(cols * math.sqrt(max(0.0, 1 - (rw / rows) ** 2)))
        start = (cols - width) // 2
        cells.extend((start + c, rw) for c in range(width))
    cells = cells[:n]
    return cells


def o4() -> str:
    o = OCEAN
    p: list[str] = []
    clip = "o4clip"
    frac = o.per_american_g / o.bag_g
    p.append(art.bag(70, 8))
    p.append(text(90, 74, f"One grocery bag: {o.bag_g:.0f} g", "t t-strong", anchor="middle"))
    # the American's year: the same bag, filled to 7/8 by height
    bx, by = 270, 8
    p.append(el("clipPath", rect(bx, by + 48 * (1 - frac), 40, 48 * frac, ""), id=clip))
    p.append(art.bag(bx, by))
    p.append(el("g", art.bag(bx, by, cls="f-accent"), clip_path=f"url(#{clip})"))
    p.append(text(290, 74, f"An American's year: {o.per_american_g:.0f} g", "t t-strong", anchor="middle"))
    # the Philippines: one glyph per bag
    n = round(o.philippines_bags)
    cols = 46
    k = 0.17
    gw, gh = 40 * k + 1.3, 48 * k + 1.2
    cells = _mound(n, cols)
    base = 214
    x0 = (400 - cols * gw) / 2
    glyphs = "".join(art.bag_glyph(x0 + c * gw, base - (rw + 1) * gh, k) for c, rw in cells)
    p.append(el("g", glyphs))
    p.append(path(f"M{r(x0 - 6)},{base}H{r(x0 + cols * gw + 6)}", "s ln"))
    about = round(n, -2)
    kg = f"{o.philippines_kg_per_person:.1f}"
    p.append(text(200, base + 18, f"The Philippines, per person: {kg} kg, about {about} bags", "t t-strong", anchor="middle"))
    return svg(400, base + 26, "".join(p), f"One 8 g grocery bag; an American's yearly 7 g; and a pile of about {about} bags for the Philippines' {kg} kg per person")


# Landfills


def l3() -> str:
    lf = LANDFILL
    fp, jp = lf.footprint_sq_ft, lf.japan_footprint_sq_ft
    s = 2.3
    p: list[str] = [art.bed(24, 26, s, (fp.low, fp.high))]
    bed_w, bed_h = 38 * s, 75 * s
    tx = 24 + bed_w + 22
    p.append(text(tx, 50, f"Twin bed: {lf.bed_sq_ft:.0f} sq ft", "t t-strong"))
    p.append(rect(tx, 62, 12, 12, "f-accent", rx=2))
    p.append(text(tx + 18, 72, "A lifetime of trash,", "t"))
    p.append(text(tx + 18, 86, f"buried: {fp.low:.0f} to {fp.high:.0f} sq ft", "t"))
    p.append(rect(tx, 98, 12, 12, "f-accent-soft", rx=2))
    p.append(text(tx + 18, 108, "Range of the estimate", "t t-muted"))
    # inset: the doormat at the same scale, linked to the burning objection
    my = 26 + bed_h - 24 * s
    inset = art.doormat(tx, my, s, (jp.low, jp.high))
    inset += text(tx, my - 24, f"Doormat: {lf.doormat_sq_ft:.0f} sq ft", "t t-strong")
    inset += text(tx, my - 10, "with Japan-style incineration", "t")
    p.append(el("a", inset, href="#burning", class_="open-objection"))
    p.append(text(tx, 26 + bed_h + 18, f"Burned: {jp.low:.1f} to {jp.high:.1f} sq ft", "t t-muted"))
    return svg(400, 26 + bed_h + 28, "".join(p), "A twin bed seen from above with a lifetime of buried trash drawn inside it, and a doormat showing the same trash after incineration")


def l4() -> str:
    return svg(400, 300, art.landfill(), "Modern landfills are sealed, drained and monitored.")


# Climate


def k3() -> tuple[str, Markup]:
    c = CLIMATE
    steps = [
        Step("Make", c.make, f"+{c.make:.1f}", "up"),
        Step("Burn", c.burn_kg_per_kg, f"+{c.burn_kg_per_kg:.2f}", "up"),
        Step("Energy back", -c.energy_back, f"−{c.energy_back:.2f}", "credit"),
        Step("Net", c.net_burned, f"{c.net_burned:.1f}", "total"),
    ]
    chart = waterfall(steps, "Kilograms of CO2 per kilogram of plastic burned: make, burn, energy back, net", 6, [0, 1, 2, 3, 4, 5, 6])
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
    chart = ranges(rows, "Kilograms of CO2 a year: your plastic against cheese, a dog, Tahoe drives and a flight", [0, 400, 800, 1200])
    table = data_table(["Item", "kg CO2"], [[rw.label, rw.value_label] for rw in rows])
    return chart, table


# In the bin


def r3() -> str:
    b = BIN
    flows = [
        Flow("Landfill", b.landfilled_m, f"{b.landfilled_m:.1f}M tons", accent=True),
        Flow("Burned for energy", b.energy_m, f"{b.energy_m:.1f}M tons"),
        Flow("Recycled", b.recycled_m, f"{b.recycled_m:.1f}M tons"),
    ]
    return sankey(f"{b.plastic_generated_m:.1f}M tons of US plastic, 2018", flows, "Three quarters of US plastic goes to landfill.")


def r4() -> tuple[str, Markup]:
    rows = [Row(name, v, v, f"{v:.1f}%", accent=name.startswith("PET")) for name, v in BIN.recycled_pct_by_resin]
    chart = hbars(rows, "Share of each plastic type recycled in the US, 2018; PET is highest at 18.5%", label_w=96)
    table = data_table(["Type", "Recycled, 2018"], [[rw.label, rw.value_label] for rw in rows])
    return chart, table


def can() -> str:
    body = (
        path("M8,10Q8,6 12,5H36Q40,6 40,10V58Q40,62 36,63H12Q8,62 8,58Z", "s f-paper")
        + path("M8,16H40M8,54H40", "s ln")
        + rect(8, 24, 32, 22, "f-accent")
        + path("M8,24H40M8,46H40", "s ln")
        + path("M18,8H30", "s ln thick")
    )
    return svg(48, 68, body, "An aluminum can", cls="fig can")


@dataclass(frozen=True)
class Figures:
    figs: dict[str, Markup]
    tables: dict[str, Markup]


def build() -> Figures:
    o3_svg, o3_t = o3()
    k3_svg, k3_t = k3()
    k4_svg, k4_t = k4()
    r4_svg, r4_t = r4()
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
        "r3": r3(),
        "r4": r4_svg,
        "can": can(),
    }
    tables = {"o3": o3_t, "k3": k3_t, "k4": k4_t, "r4": r4_t}
    return Figures({k: Markup(v) for k, v in figs.items()}, tables)
