"""L4: cross-section of a modern landfill, in the site's flat line style."""

import math
from itertools import pairwise

from ttg.svg import circle, el, line, path, r, rect, text

Pt = tuple[float, float]

W = 400
H = 366
TRIM = 14  # blank band above the flame and labels, cut from the top
GY = 180  # ground surface
CX = 196  # landfill centre line
CLAY = 9  # compacted clay thickness
CAP = 10  # cap soil thickness
DRAIN = 9  # gravel drainage layer thickness
PIPE = 5  # pipe diameter

# Plastic liner (top of the clay), crest to crest; floor falls to a sump at the centre.
LINER: list[Pt] = [(80, GY), (110, 244), (186, 250), (188, 260), (204, 260), (206, 250), (282, 244), (312, GY)]
# Cap liner (under the cap soil); meets the bottom liner at both crests, so the waste is enclosed.
CAP_LINER: list[Pt] = [(80, GY), (126, 128), (160, 116), (196, 112), (232, 116), (266, 128), (312, GY)]

GAS_X = (140, 196, 252)
GAS_BOTTOM = 210  # wells stop well above the liner
HEADER_Y = 88
FLARE_X = 366
FLARE_TOP = 62
MON_X = (30, 340)  # upgradient, downgradient
WT_L, WT_R = 304, 312  # water table falls left to right: groundwater flows right


def landfill(id_prefix: str = "lf") -> tuple[str, float]:
    """Return (svg body, height) for a 400-wide viewBox; the page draws the title."""
    parts = [
        _ground(),
        _liner(),
        _waste(id_prefix),
        _leachate(),
        _cap(),
        _monitor_wells(),
        _gas(),
        _labels(),
    ]
    return el("g", "".join(parts), transform=f"translate(0,-{TRIM})"), H - TRIM


# geometry


def _offset(pts: list[Pt], d: float) -> list[Pt]:
    """Offset an open polyline by d along its left normal (-dy, dx), mitred."""
    normals = []
    for (x0, y0), (x1, y1) in pairwise(pts):
        n = math.hypot(x1 - x0, y1 - y0)
        normals.append((-(y1 - y0) / n, (x1 - x0) / n))
    out = []
    for i, (x, y) in enumerate(pts):
        if i == 0 or i == len(pts) - 1:
            (nx, ny), k = normals[0 if i == 0 else -1], 1.0
        else:
            (ax, ay), (bx, by) = normals[i - 1], normals[i]
            m = math.hypot(ax + bx, ay + by)
            nx, ny = (ax + bx) / m, (ay + by) / m
            k = 1 / max(0.3, nx * ax + ny * ay)
        out.append((x + nx * d * k, y + ny * d * k))
    return out


def _to_ground(pts: list[Pt]) -> list[Pt]:
    """Slide the end points along their end segments onto the ground line."""
    first = (_x_at(pts[0], pts[1], GY), GY)
    last = (_x_at(pts[-1], pts[-2], GY), GY)
    return [first, *pts[1:-1], last]


def _x_at(a: Pt, b: Pt, y: float) -> float:
    """x on the line through a and b at height y."""
    return a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])


def _y_on(pts: list[Pt], x: float) -> float:
    """y of a polyline at x (first segment that spans x)."""
    for (x0, y0), (x1, y1) in pairwise(pts):
        if min(x0, x1) <= x <= max(x0, x1) and x0 != x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def _d(pts: list[Pt], close: bool = False) -> str:
    s = "M" + "L".join(f"{r(x)},{r(y)}" for x, y in pts)
    return s + "Z" if close else s


def _cap_top() -> list[Pt]:
    return _to_ground(_offset(CAP_LINER, -CAP))


def _clay_bottom() -> list[Pt]:
    return _to_ground(_offset(LINER, CLAY))


def _drain_top() -> list[Pt]:
    """Top of the gravel drainage layer: DRAIN above the floor, meeting the side slopes."""
    toe = LINER[1][1] - DRAIN
    return [(_x_at(LINER[0], LINER[1], toe), toe), (CX, LINER[2][1] - DRAIN), (_x_at(LINER[-1], LINER[-2], toe), toe)]


def _floor_y(x: float) -> float:
    """Liner floor height at x, ignoring the sump."""
    if x < CX:
        return _y_on(LINER[1:3], min(max(x, LINER[1][0]), LINER[2][0]))
    return _y_on(LINER[5:7], max(min(x, LINER[6][0]), LINER[5][0]))


def _pipe_y(x: float) -> float:
    """Leachate pipe centre: in the gravel, just clear of the liner."""
    return _floor_y(x) - PIPE / 2 - 2


def _water_y(x: float) -> float:
    return WT_L + (WT_R - WT_L) * x / W


# layers, back to front


def _ground() -> str:
    wl = [(0.0, _water_y(0)), (float(W), _water_y(W))]
    clay = _clay_bottom()
    return "".join(
        [
            rect(0, GY, W, H - GY, "f-soft"),
            path(f"M0,{GY}H{r(clay[0][0])}M{r(clay[-1][0])},{GY}H{W}", "s ln"),
            path(_d([*wl, (W, H), (0, H)], close=True), "f-water"),
            path(_d(wl), "s ln thin"),
            _water_mark(70),
            _flow_arrow(),
        ]
    )


def _water_mark(x: float) -> str:
    """Hydrogeology water-table symbol: inverted triangle on the line, two dashes under it."""
    y = _water_y(x)
    tri = f"M{r(x - 4.5)},{r(y - 8)}H{r(x + 4.5)}L{r(x)},{r(y)}Z"
    dashes = f"M{r(x - 4)},{r(y + 4)}h8M{r(x - 2.5)},{r(y + 7.5)}h5"
    return path(tri, "s thin f-paper") + path(dashes, "s ln thin")


def _flow_arrow() -> str:
    y = _water_y(110) + 26
    return path(f"M84,{r(y)}H136m-6,-4l6,4l-6,4", "s ln thin")


def _liner() -> str:
    clay = _clay_bottom()
    return path(_d(LINER + clay[::-1], close=True), "f-clay") + path(_d(clay), "s ln")


def _waste_outline() -> list[Pt]:
    """Cap liner over the top, bottom liner down the side slopes, drainage layer underneath."""
    return [*CAP_LINER[::-1][:-1], LINER[0], *_drain_top()]


def _waste(id_prefix: str) -> str:
    """Grey cells in lifts; the soil-coloured gaps between them are the daily cover."""
    outline = _d(_waste_outline(), close=True)
    clip_id = f"{id_prefix}-waste"
    h, gap, w, skew = 16.5, 2.6, 40, 5
    cells = []
    yb, row = _drain_top()[1][1] + 4, 0
    while yb > 100:
        x = 60 - (w / 2 + gap) * (row % 2)
        while x < 340:
            cells.append(f"M{r(x)},{r(yb)}L{r(x + skew)},{r(yb - h)}H{r(x + skew + w)}L{r(x + w)},{r(yb)}Z")
            x += w + gap
        yb, row = yb - h - gap, row + 1
    return "".join(
        [
            el("clipPath", el("path", d=outline), id=clip_id),
            path(outline, "f-soft"),
            el("g", path("".join(cells), "f-grey"), clip_path=f"url(#{clip_id})"),
        ]
    )


def _leachate() -> str:
    """Gravel layer on the liner floor with perforated pipes falling to the sump."""
    top = _drain_top()
    out = [path(_d(top + LINER[1:7][::-1], close=True), "f-paper"), path(_d(top), "s ln thin")]
    out.append(_pipe(LINER[1][0] + 10, LINER[3][0] + 1))
    out.append(_pipe(LINER[6][0] - 10, LINER[4][0] - 1))
    out.append(path(_d(LINER), "s ln accent-line"))
    return "".join(out)


def _pipe(x0: float, x1: float) -> str:
    """Perforated pipe lying on the floor from x0 to its open end over the sump at x1."""
    ax, ay, bx, by = x0, _pipe_y(x0), x1, _pipe_y(x1)
    n = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / n, (by - ay) / n
    nx, ny = -uy * PIPE / 2, ux * PIPE / 2
    body = [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)]
    holes = "".join(circle(ax + ux * t, ay + uy * t, 0.9, "f-ink") for t in range(5, int(n) - 2, 6))
    return path(_d(body, close=True), "s f-paper") + holes


def _cap() -> str:
    """Vegetated soil over the cap liner."""
    top = _cap_top()
    grass = []
    for x in range(int(top[0][0]) + 10, int(top[-1][0]) - 6, 11):
        y = _y_on(top, x)
        grass.append(f"M{x},{r(y)}l-2.5,-5M{x},{r(y)}l2,-6")
    return "".join(
        [
            path(_d(top + CAP_LINER[::-1], close=True), "f-cap"),
            path(_d(top), "s ln"),
            path("".join(grass), "s ln thin"),
            path(_d(CAP_LINER), "s ln accent-line"),
        ]
    )


def _gas() -> str:
    """Slotted gas wells joined by one header pipe that runs to the flare (one outline, clean tees)."""
    t = PIPE / 2
    xs = sorted(GAS_X)
    d = f"M{r(xs[0] - t)},{r(HEADER_Y - t)}H{r(FLARE_X - 4)}V{r(HEADER_Y + t)}"
    for x in reversed(xs):
        d += f"H{r(x + t)}V{r(GAS_BOTTOM - t)}A{r(t)},{r(t)} 0 0 1 {r(x - t)},{r(GAS_BOTTOM - t)}"
        if x != xs[0]:
            d += f"V{r(HEADER_Y + t)}"
    d += "Z"
    slots = []
    for x in xs:
        y = _y_on(CAP_LINER, x) + 8
        while y < GAS_BOTTOM - 5:
            slots.append(f"M{r(x - t + 1)},{r(y)}H{r(x + t - 1)}")
            y += 6
    return path(d, "s f-paper") + path("".join(slots), "s ln thin") + _flare()


def _flare() -> str:
    x, w = FLARE_X, 12
    ft = FLARE_TOP - 7
    flame = (
        f"M{x},{ft}Q{x - 11},{ft - 4} {x - 6},{ft - 16}Q{x - 3},{ft - 22} {x - 1},{ft - 32}"
        f"Q{x + 6},{ft - 22} {x + 5},{ft - 17}Q{x + 8},{ft - 19} {x + 8},{ft - 23}"
        f"Q{x + 13},{ft - 10} {x},{ft}Z"
    )
    return "".join(
        [
            rect(x - w / 2, FLARE_TOP, w, GY - FLARE_TOP, "s f-paper"),
            rect(x - 12, GY - 7, 24, 7, "s f-grey", rx=1.5),
            rect(x - w / 2 - 2.5, FLARE_TOP - 5, w + 5, 6, "s f-grey", rx=1.5),
            path(flame, "s f-flame"),
        ]
    )


def _monitor_wells() -> str:
    """Cased wells outside the liner, screened across the water table, with a protective top."""
    t = PIPE / 2
    out = []
    for x in MON_X:
        wt = _water_y(x)
        bottom = wt + 30
        slots = "".join(f"M{r(x - t + 1)},{r(wt - 8 + 4 * i)}H{r(x + t - 1)}" for i in range(int((bottom - wt + 4) // 4) + 1))
        out.append(rect(x - t, GY - 6, PIPE, bottom - GY + 6, "s f-paper", rx=t))
        out.append(path(slots, "s ln thin"))
        out.append(rect(x - 5, GY - 14, 10, 16, "s f-grey", rx=1.5))
    return "".join(out)


# labels


def _labels() -> str:
    return "".join(
        [
            _label(["Gas wells"], CX, 56, (CX, HEADER_Y - PIPE / 2), "middle"),
            _label(["Flare or", "generator"], 350, 30, (FLARE_X - 7, FLARE_TOP - 22), "end"),
            _label(["Final cap"], 352, 114, (298, _y_on(_cap_top(), 298) + 4), "end"),
            _label(["Waste cells", "with daily", "cover"], 6, 112, (118, 162), "start"),
            _label(["Clay and", "plastic liner"], 104, 282, (150, _floor_y(150) + CLAY / 2), "start"),
            _label(["Leachate", "pipes"], 222, 282, (246, _pipe_y(246)), "start"),
            _label(["Groundwater", "monitoring wells"], 330, 336, (MON_X[1], 330), "end"),
        ]
    )


def _label(lines: list[str], tx: float, ty: float, target: Pt, anchor: str) -> str:
    """Label at (tx, ty) with a leader from the nearest point of its box to target."""
    lh = 14
    width = max(len(s) for s in lines) * 7.4  # 12px semibold, measured
    x0 = {"start": tx, "end": tx - width, "middle": tx - width / 2}[anchor] - 3
    x1 = x0 + width + 6
    y0, y1 = ty - 12, ty + lh * (len(lines) - 1) + 4
    px, py = target
    lx, ly = min(max(px, x0), x1), min(max(py, y0), y1)
    out = [line(lx, ly, px, py, "leader"), circle(px, py, 2.4, "f-ink")]
    out += [text(tx, ty + i * lh, s, "t t-strong", anchor=anchor) for i, s in enumerate(lines)]
    return "".join(out)
