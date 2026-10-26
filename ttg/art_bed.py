"""Twin bed and doormat seen from above, with the lifetime trash footprint drawn to scale (s = SVG units per inch)."""

import math
from dataclasses import dataclass

from ttg.svg import circle, el, line, path, r, rect, text

BED_W, BED_H = 38.0, 75.0
MAT_W, MAT_H = 36.0, 24.0
SQ_IN = 144.0
CORNER = 2.5  # mattress corner radius, inches
PILLOW = (7.0, 2.4, 24.0, 9.0)  # x, y, w, h in inches from the mattress top-left
FOLD_Y = 13.2  # turned-down sheet edge, inches from the head
HEAD_CLEAR = PILLOW[1] + PILLOW[3] + 1  # the heap stops this far from the head


@dataclass(frozen=True)
class Item:
    """A piece of trash lying flat, outline in inches around (0, 0), with its bounding box."""

    d: str
    box: tuple[float, float, float, float]


BOTTLE = Item(
    "M-3.6,-1.8H2.8Q4.2,-1.8 4.6,-0.75H5.6V-0.95H6.6V0.95H5.6V0.75H4.6Q4.2,1.8 2.8,1.8H-3.6"
    "Q-5,1.8 -5,0Q-5,-1.8 -3.6,-1.8ZM-1.6,-1.8V1.8M1,-1.8V1.8",
    (-5, -1.8, 6.6, 1.8),
)
BOX = Item("M-5.5,-4H5.5V4H-5.5ZM0,-4V4M-1.4,-4V-1.6H1.4V-4", (-5.5, -4, 5.5, 4))
BAG = Item(
    "M-2.9,5.3Q-3.3,5.3 -3.3,4.9L-3.5,-1.5V-3.5Q-3.5,-3.9 -3.1,-3.9H-2.1Q-1.7,-3.9 -1.7,-3.5V-1.9"
    "Q0,-0.7 1.7,-1.9V-3.5Q1.7,-3.9 2.1,-3.9H3.1Q3.5,-3.9 3.5,-3.5V-1.5L3.3,4.9Q3.3,5.3 2.9,5.3Z"
    "M-1.7,1.4Q0,2.2 1.7,1.4",
    (-3.5, -3.9, 3.5, 5.3),
)
NEWS = Item("M-4,-5H4V5H-4ZM-2.6,-3.2H2.6M-2.6,-1.4H2.6M-2.6,0.4H0.6M-2.6,2.2H2.6", (-4, -5, 4, 5))
CUP = Item("M-2.7,0A2.7,2.7 0 1 0 2.7,0A2.7,2.7 0 1 0 -2.7,0ZM-0.9,-1.5H0.9", (-2.7, -2.7, 2.7, 2.7))
APPLE = Item(
    "M-2.2,-3Q0,-2.2 2.2,-3Q0.7,0 2.2,3Q0,2.3 -2.2,3Q-0.7,0 -2.2,-3ZM0,-2.6V-4.4"
    "M0,-4Q1.5,-5 2.3,-4.1Q1.2,-3.5 0,-4Z",
    (-2.2, -4.9, 2.3, 3),
)
# (item, cx, cy, degrees) in a 38-in-wide heap, measured from its top-left corner
BED_ITEMS = [
    (BOX, 8.5, 7.5, -8), (BOTTLE, 24, 5.2, 10), (CUP, 33.5, 12.5, 0), (NEWS, 20.5, 16.5, 14),
    (APPLE, 6, 20, -20), (BAG, 30.5, 26, 18), (BOTTLE, 12, 30.5, -32), (CUP, 22, 30, 0),
    (BOX, 26, 42, 6), (NEWS, 8, 44, -10), (APPLE, 17.8, 51.2, 25), (BAG, 30, 51.5, -12),
    (BOTTLE, 8, 54.5, 4),
]
# below SMALL_S units per inch: fewer, bigger items so they still read at card size
SMALL_S = 2.0
SMALL_K = 1.45
SMALL_ITEMS = [
    (BOX, 10.5, 9, -6), (BOTTLE, 29, 10.5, 72), (BAG, 9.5, 28.5, -12), (NEWS, 26.5, 30.5, 10),
    (CUP, 8.5, 46, 0), (BOX, 25, 48, 7),
]
MAT_ITEMS = [(BAG, -3.6, 0.2, -10), (CUP, 4.4, -3.4, 0)]  # offsets from the heap center


def _fits(it: Item, cx: float, cy: float, deg: float, w: float, h: float, k: float = 1, pad: float = 0.6) -> bool:
    c, sn = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    x0, y0, x1, y1 = (v * k for v in it.box)
    pts = [(cx + px * c - py * sn, cy + px * sn + py * c) for px in (x0, x1) for py in (y0, y1)]
    return all(pad <= px <= w - pad and pad <= py <= h - pad for px, py in pts)


def _items(
    x: float, y: float, s: float, w: float, h: float, placed: list[tuple[Item, float, float, float]], k: float = 1
) -> str:
    """Item outlines (k times life size) inside a w x h heap (inches) with top-left (x, y); drops any that don't fit."""
    out = []
    for it, cx, cy, deg in placed:
        if _fits(it, cx, cy, deg, w, h, k):
            tf = f"translate({r(x + cx * s)},{r(y + cy * s)}) rotate({r(deg)}) scale({r(s * k)})"
            out.append(path(it.d, "s ln thin", transform=tf))
    return "".join(out)


def _corner_loss(rad: float) -> float:
    """Area cut from a square corner by rounding it with radius rad."""
    return (1 - math.pi / 4) * rad * rad


def _heap_d(x: float, y0: float, w: float, y1: float, rad: float) -> str:
    """Rectangle from y0 to y1 with square top corners and rounded bottom corners."""
    return (
        f"M{r(x)},{r(y0)}H{r(x + w)}V{r(y1 - rad)}A{r(rad)},{r(rad)} 0 0 1 {r(x + w - rad)},{r(y1)}"
        f"H{r(x + rad)}A{r(rad)},{r(rad)} 0 0 1 {r(x)},{r(y1 - rad)}Z"
    )


def _pillow(x: float, y: float, s: float) -> str:
    px, py, pw, ph = (v * s for v in PILLOW)
    x0, y0, x1, y1 = x + px, y + py, x + px + pw, y + py + ph
    b = 0.9 * s  # how far each edge bows inward
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    d = (
        f"M{r(x0)},{r(y0)}Q{r(mx)},{r(y0 + b)} {r(x1)},{r(y0)}Q{r(x1 - b)},{r(my)} {r(x1)},{r(y1)}"
        f"Q{r(mx)},{r(y1 - b)} {r(x0)},{r(y1)}Q{r(x0 + b)},{r(my)} {r(x0)},{r(y0)}Z"
    )
    return path(d, "s f-paper")


def _bed_heap(lo: float, hi: float) -> tuple[float, float, float]:
    """(top of high band, top of low heap, foot) in inches from the head; the heap stands on the foot
    and is as wide as the bed. If it would reach the pillow it overhangs the foot instead."""
    lo_h = (lo * SQ_IN + 2 * _corner_loss(CORNER)) / BED_W
    hi_h = lo_h + max(0.0, hi - lo) * SQ_IN / BED_W
    shift = max(0.0, HEAD_CLEAR - (BED_H - hi_h))
    foot = BED_H + shift
    return foot - hi_h, foot - lo_h, foot


def bed(x: float, y: float, s: float, footprint_sq_ft: tuple[float, float] | None = None) -> str:
    """Twin bed (38 x 75 in) from above, head at the top; top-left of the mattress at (x, y).

    The headboard sits 3.6 in above y, within the bed's width. footprint_sq_ft = (low, high):
    a heap as wide as the bed, standing on the foot, whose area at scale s is exactly low
    (f-accent); the extra up to high is a band above it (f-accent-soft).
    """
    w, h = BED_W * s, BED_H * s
    p = [
        rect(x + 0.6 * s, y - 3.6 * s, w - 1.2 * s, 4.6 * s, "s f-grey", rx=1.4 * s),
        rect(x, y, w, h, "s f-paper", rx=CORNER * s),
        rect(x, y + FOLD_Y * s, w, (BED_H - FOLD_Y - CORNER) * s, "f-soft"),
        path(f"M{r(x)},{r(y + FOLD_Y * s)}H{r(x + w)}", "s ln thin"),
        _pillow(x, y, s),
    ]
    if footprint_sq_ft:
        lo, hi = footprint_sq_ft
        top_hi, top_lo, foot = _bed_heap(lo, hi)
        if hi > lo:
            p.append(rect(x, y + top_hi * s, w, (top_lo - top_hi) * s, "s f-accent-soft"))
        p.append(path(_heap_d(x, y + top_lo * s, w, y + foot * s, CORNER * s), "s f-accent"))
        placed, k = (SMALL_ITEMS, SMALL_K) if s < SMALL_S else (BED_ITEMS, 1.0)
        p.append(_items(x, y + top_lo * s, s, BED_W, foot - top_lo, placed, k))
    p.append(rect(x, y, w, h, "s ln", rx=CORNER * s))
    return "".join(p)


def _mat_heap(area_sq_ft: float, square: bool) -> tuple[float, float]:
    """(width, height) in inches of a footprint of this area: a square, or the mat's 3:2 shape."""
    a = area_sq_ft * SQ_IN
    if square:
        return math.sqrt(a), math.sqrt(a)
    w = math.sqrt(a * MAT_W / MAT_H)
    return w, a / w


def doormat(x: float, y: float, s: float, footprint_sq_ft: tuple[float, float] | None = None) -> str:
    """2 x 3 ft doormat (36 x 24 in, landscape), top-left at (x, y).

    footprint_sq_ft = (low, high): a heap centered on the mat with area exactly low (f-accent),
    and a concentric one out to high (f-accent-soft). Square while it fits, else the mat's shape.
    """
    w, h = MAT_W * s, MAT_H * s
    cx, cy = x + w / 2, y + h / 2
    p = [
        rect(x, y, w, h, "s f-grey", rx=1.6 * s),
        rect(x + 2.2 * s, y + 2.2 * s, w - 4.4 * s, h - 4.4 * s, "s ln thin", rx=0.8 * s),
    ]
    if footprint_sq_ft:
        lo, hi = footprint_sq_ft
        square = math.sqrt(max(lo, hi) * SQ_IN) <= MAT_H - 3
        if hi > lo:
            hw, hh = _mat_heap(hi, square)
            p.append(rect(cx - hw * s / 2, cy - hh * s / 2, hw * s, hh * s, "s f-accent-soft"))
        lw, lh = _mat_heap(lo, square)
        x0, y0 = cx - lw * s / 2, cy - lh * s / 2
        p.append(rect(x0, y0, lw * s, lh * s, "s f-accent"))
        placed = [(it, lw / 2 + dx, lh / 2 + dy, deg) for it, dx, dy, deg in MAT_ITEMS]
        p.append(_items(x0, y0, s, lw, lh, placed))
    return "".join(p)


def _sq_ft(lo: float, hi: float, fmt: str) -> str:
    a, b = f"{lo:{fmt}}", f"{hi:{fmt}}"
    return f"{a} sq ft" if a == b else f"{a} to {b} sq ft"


def _leader(tx: float, ty: float, px: float, py: float) -> str:
    return line(tx, ty, px, py, "leader") + circle(px, py, 2.6, "f-ink")


def l3_figure(
    bed_sq_ft: float, footprint: tuple[float, float], japan: tuple[float, float], doormat_sq_ft: float
) -> tuple[str, float]:
    """L3 body for a 400-wide viewBox: the bed with the buried footprint, and the doormat inset
    (burned footprint) linked to the burning objection. Returns (svg_body, height)."""
    s = 2.7
    bx, by = 18.0, 24.0
    bw = BED_W * s
    lo, hi = footprint
    top_hi, top_lo, foot = _bed_heap(lo, hi)
    floor = by + foot * s
    p = [bed(bx, by, s, footprint)]
    x0 = bx + bw + 28
    p.append(text(x0, by + 12, f"Twin bed: {bed_sq_ft:.0f} sq ft", "t t-strong"))
    p.append(_leader(x0 - 4, by + 8, bx + 34.5 * s, by + 8))
    ty = by + (top_hi + 4.5) * s
    p.append(text(x0, ty + 4, f"A lifetime of trash, buried: {_sq_ft(lo, hi, '.0f')}", "t t-strong"))
    p.append(_leader(x0 - 4, ty, bx + 34.5 * s, by + (top_lo + 4.5) * s))
    # inset: the doormat at the same scale, standing on the bed's floor line
    mw, mh = MAT_W * s, MAT_H * s
    mx, my = x0, floor - mh
    jl, jh = japan
    burned = f"Burned: {_sq_ft(jl, jh, '.1f')}"
    beside = mx + mw + 14 + len(burned) * 6.8 <= 396
    gap = 0 if beside else 22  # room under the mat when the label can't fit beside it
    my -= gap
    inset = [
        rect(x0 - 12, my - 48, 400 - x0 + 8, mh + 58 + gap, "f-paper grid", rx=10),
        text(x0, my - 28, f"Doormat: {doormat_sq_ft:.0f} sq ft", "t t-strong"),
        text(x0, my - 13, "with Japan-style incineration", "t"),
        text(388, my - 28, "\u2193", "t t-strong", anchor="end"),
        doormat(mx, my, s, japan),
    ]
    dot_x, dot_y = mx + mw / 2 + 4.6 * s, my + mh / 2 + 4.6 * s  # empty spot in the burned heap, below the cup
    if beside:
        inset += [text(mx + mw + 14, dot_y + 4, burned, "t t-strong"), _leader(mx + mw + 10, dot_y, dot_x, dot_y)]
    else:
        inset += [text(mx, floor + 4, burned, "t t-strong"), _leader(mx + mw * 0.75, floor - 8, dot_x, dot_y)]
    p.append(el("a", "".join(inset), href="#burning", class_="open-objection"))
    return "".join(p), floor + 12
