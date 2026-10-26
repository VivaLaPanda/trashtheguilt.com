"""Knockout scene: a sunrise city with clean power, new housing going up, and a garbage truck at work."""

from dataclasses import dataclass

from ttg.svg import circle, el, line, path, r, rect

W = 800
H = 340
GY = 264  # building base / back of sidewalk
CURB = 276  # front of sidewalk, start of road
LANE = 290  # front edge of the bike lane
WHEEL_Y = 328  # where vehicle wheels touch the road
FLOOR = 21  # storey height
GROUND = 26  # ground-floor (shop) height

SUN = (300, 186, 74)
HALO = 108


@dataclass(frozen=True)
class Block:
    x: float
    w: float
    floors: int  # storeys above the ground floor
    fill: str
    roof: str = "flat"  # flat | solar | garden
    balconies: bool = False
    awning: str = "f-paper"


BLOCKS = [
    Block(376, 76, 5, "f-peach", roof="solar", awning="f-sun"),
    Block(452, 92, 7, "f-cream", roof="garden", balconies=True, awning="f-lime"),
    Block(544, 80, 4, "f-aqua", roof="solar", awning="f-paper"),
    Block(624, 94, 6, "f-brick", roof="solar", awning="f-sun"),
    Block(718, 86, 3, "f-lime", roof="solar", awning="f-paper"),
]


def scene() -> tuple[str, float, float]:
    """Return (svg body, width, height) for the closing illustration."""
    parts = [
        _sky(),
        _hills(),
        _turbines(),
        _houses(),
        _construction(),
        _crane(),
        *(_block(b) for b in BLOCKS),
        _street(),
        _trees(),
        _bins(),
        _birds(),
        _place(_walker("f-peach"), 404, CURB - 3, 1.0),
        _place(_cyclist(), 150, LANE - 3, 1.0),
        _place(_truck(), 436, WHEEL_Y, 1.12),
    ]
    return "".join(parts), W, H


# small shapes


def _poly(pts: list[tuple[float, float]], cls: str) -> str:
    return path("M" + "L".join(f"{r(x)},{r(y)}" for x, y in pts) + "Z", cls)


def _place(body: str, x: float, y: float, k: float = 1) -> str:
    return el("g", body, transform=f"translate({r(x)},{r(y)}) scale({r(k)})")


def _cloud(x: float, y: float, k: float) -> str:
    """Flat-bottomed cloud in a 100 x 40 box, bottom-left at (x, y)."""
    d = "M10,40C1,40 0,27 11,26C11,14 27,9 36,17C42,4 66,3 72,19C84,14 98,22 93,31C100,33 99,40 91,40Z"
    return _place(path(d, "s f-paper"), x, y - 40 * k, k)


def _windows(x: float, y: float, w: float, rows: int, cols: int, seed: int) -> str:
    """A grid of windows across a facade; a few catch the sunrise."""
    ww, wh = 12, 13
    pitch = w / cols
    out = []
    for i in range(rows):
        for j in range(cols):
            lit = (i * 3 + j * 5 + seed) % 7 == 0
            cx = x + pitch * (j + 0.5)
            out.append(rect(cx - ww / 2, y + i * FLOOR, ww, wh, f"s thin {'f-sun' if lit else 'f-water'}"))
    return "".join(out)


# sky and land


def _sky() -> str:
    cx, cy, rad = SUN
    return "".join(
        [
            circle(cx, cy, HALO, "f-cream"),
            circle(cx, cy, rad, "s f-sun"),
            _cloud(26, 58, 0.66),
            _cloud(540, 62, 1.1),
            _cloud(690, 96, 0.72),
        ]
    )


def _hills() -> str:
    back = f"M-4,{GY}V182C40,164 90,160 140,174C180,184 210,192 240,{GY}Z"
    front = f"M-4,{GY}V214C40,200 120,198 190,218C215,226 230,240 236,{GY}Z"
    return path(back, "s f-aqua") + path(front, "s f-grass")


def _turbine(x: float, base: float, h: float, blade: float, angle: float) -> str:
    top = base - h
    wb, wt = max(3.0, h * 0.045), max(1.6, h * 0.02)
    tower = _poly([(x - wb, base), (x - wt, top), (x + wt, top), (x + wb, base)], "s f-paper")
    bw = blade * 0.15
    d = (
        f"M{r(x)},{r(top)}C{r(x + bw)},{r(top - blade * 0.15)} {r(x + bw * 0.7)},{r(top - blade * 0.75)} {r(x)},{r(top - blade)}"
        f"C{r(x - bw * 0.25)},{r(top - blade * 0.6)} {r(x - bw * 0.35)},{r(top - blade * 0.2)} {r(x)},{r(top)}Z"
    )
    blades = "".join(path(d, "s f-paper", transform=f"rotate({r(angle + k * 120)} {r(x)} {r(top)})") for k in range(3))
    nacelle = rect(x - 3, top - 3.5, 9, 7, "s f-paper", rx=2.5)
    hub = circle(x, top, max(2.5, blade * 0.08), "s f-paper")
    return tower + nacelle + blades + hub


def _turbines() -> str:
    return _turbine(40, 214, 104, 44, 20) + _turbine(100, 196, 72, 31, 75) + _turbine(156, 218, 108, 42, 50)


# housing


def _house(x: float, w: float, wall: str, roof: str) -> str:
    """Two-storey house, long side to us, with a row of solar panels on the roof face."""
    h = 48
    top = GY - h
    rh = 24
    out = [rect(x, top, w, h, f"s {wall}")]
    out.append(_poly([(x - 6, top), (x + 8, top - rh), (x + w - 8, top - rh), (x + w + 6, top)], f"s {roof}"))
    px0, px1 = x + 6, x + w - 6
    out.append(_poly([(px0, top - 4), (px0 + 6, top - rh + 4), (px1 - 6, top - rh + 4), (px1, top - 4)], "s f-solar"))
    for k in (1, 2):
        t = k / 3
        bx = px0 + (px1 - px0) * t
        tx = px0 + 6 + (px1 - px0 - 12) * t
        out.append(line(bx, top - 4, tx, top - rh + 4, "s thin cover"))
    out.append(rect(x + w / 2 - 7, GY - 24, 14, 24, "s f-solar"))
    out.append(rect(x + 7, top + 10, 12, 13, "s thin f-water"))
    out.append(rect(x + w - 19, top + 10, 12, 13, "s thin f-water"))
    return "".join(out)


def _houses() -> str:
    return _house(10, 64, "f-paper", "f-brick") + _house(88, 60, "f-sun", "f-peach")


def _construction() -> str:
    """Mid-rise going up: three finished storeys, two of open timber frame."""
    x, w = 184, 150
    done_top = GY - GROUND - 2 * FLOOR
    frame_top = done_top - 2 * FLOOR
    out = [rect(x, done_top, w, GY - done_top, "s f-cream")]
    out.append(_windows(x + 4, done_top + 6, w - 8, 2, 6, 2))
    out.append(rect(x + 8, GY - 20, w - 16, 20, "s f-aqua"))
    out.append(path("".join(f"M{r(x + 8 + k * (w - 16) / 5)},{GY - 20}V{GY}" for k in range(1, 5)), "s thin ln"))
    for j in range(5):
        cx = x + 3 + j * (w - 6) / 4
        out.append(rect(cx - 3, frame_top, 6, done_top - frame_top, "s f-wood"))
    for k in range(2):
        out.append(rect(x - 2, frame_top + k * FLOOR - 3, w + 4, 6, "s f-wood"))
    out.append(path(f"M{x + 20},{frame_top + FLOOR + 4}L{x + 54},{done_top - 1}M{x + 54},{frame_top + FLOOR + 4}L{x + 20},{done_top - 1}", "s thin ln"))
    return "".join(out)


def _crane() -> str:
    mx, mw = 344, 12
    jib_y = 44
    top = 24
    left, right = 196, 420
    out = []
    # mast with a zig-zag lattice
    out.append(rect(mx, jib_y, mw, GY - jib_y, "s f-aqua"))
    zz = "".join(f"L{r(mx + (mw if k % 2 else 0))},{r(jib_y + 8 + k * 14)}" for k in range((GY - jib_y - 8) // 14 + 1))
    out.append(path(f"M{mx},{jib_y + 8}{zz}", "s thin ln"))
    # tower head and pendant lines
    out.append(_poly([(mx, jib_y), (mx + mw / 2, top), (mx + mw, jib_y)], "s f-aqua"))
    out.append(path(f"M{left + 6},{jib_y}L{mx + mw / 2},{top}L{right - 4},{jib_y}", "s thin ln"))
    # jib and counter-jib
    out.append(rect(left, jib_y, right - left, 9, "s f-aqua"))
    zz = "".join(f"L{r(left + 6 + k * 10)},{r(jib_y + (9 if k % 2 else 0))}" for k in range(int((right - left - 12) / 10) + 1))
    out.append(path(f"M{left + 6},{jib_y}{zz}", "s thin ln"))
    out.append(rect(392, jib_y + 9, 24, 14, "s f-metal"))
    out.append(rect(mx + mw, jib_y + 9, 14, 13, "s f-paper", rx=2))
    # trolley, hoist line, load
    tx = 250
    out.append(rect(tx - 6, jib_y + 9, 12, 5, "s f-ink"))
    out.append(line(tx, jib_y + 14, tx, 104, "s thin"))
    out.append(path(f"M{tx},104L{tx - 22},114M{tx},104L{tx + 22},114", "s thin ln"))
    out.append(rect(tx - 28, 114, 56, 10, "s f-wood"))
    return "".join(out)


def _block(b: Block) -> str:
    top = GY - GROUND - b.floors * FLOOR
    out = [rect(b.x, top, b.w, GY - top, f"s {b.fill}")]
    out.append(rect(b.x - 2, top - 5, b.w + 4, 6, f"s {b.fill}"))
    cols = max(2, round(b.w / 27))
    out.append(_windows(b.x, top + 6, b.w, b.floors, cols, int(b.x) % 7))
    if b.balconies:
        for i in range(b.floors):
            y = top + 6 + i * FLOOR + 10
            out.append(rect(b.x + 6, y, b.w - 12, 5, "s thin f-paper"))
    out.append(_shopfront(b))
    out.append(_roof(b, top - 5))
    return "".join(out)


def _shopfront(b: Block) -> str:
    y = GY - GROUND
    out = [rect(b.x + 6, y + 9, b.w * 0.55, GROUND - 9, "s thin f-water")]
    out.append(rect(b.x + b.w - 20, y + 7, 13, GROUND - 7, "s f-solar"))
    aw = b.w * 0.55 + 6
    out.append(path(f"M{r(b.x + 3)},{r(y + 2)}H{r(b.x + 3 + aw)}L{r(b.x + 6 + aw)},{r(y + 9)}H{r(b.x)}Z", f"s {b.awning}"))
    return "".join(out)


def _panel(x: float, y: float) -> str:
    """Tilted rooftop solar panel on a short stand; roof line at y."""
    w, h, lift, skew = 28, 12, 5, 6
    b0 = y - lift
    pts = [(x, b0), (x + w, b0), (x + w + skew, b0 - h), (x + skew, b0 - h)]
    legs = path(f"M{r(x + 5)},{r(y)}V{r(b0)}M{r(x + w - 3)},{r(y)}V{r(b0)}", "s ln")
    cells = "".join(line(x + w * t, b0, x + w * t + skew, b0 - h, "s thin cover") for t in (1 / 3, 2 / 3))
    return legs + _poly(pts, "s f-solar") + cells


def _roof(b: Block, y: float) -> str:
    if b.roof == "solar":
        n = max(1, int((b.w - 4) // 34))
        start = b.x + (b.w - n * 34 + 2) / 2
        return "".join(_panel(start + k * 34, y) for k in range(n))
    if b.roof == "garden":
        return "".join(
            [
                line(b.x + 22, y, b.x + 22, y - 10, "s"),
                circle(b.x + 22, y - 17, 10, "s f-grass"),
                line(b.x + 56, y, b.x + 56, y - 8, "s"),
                circle(b.x + 56, y - 14, 7.5, "s f-lime"),
            ]
        )
    return ""


# street


def _street() -> str:
    out = [rect(-4, GY, W + 8, CURB - GY, "s f-cream")]
    out.append(rect(-4, CURB, W + 8, H - CURB + 4, "s f-metal"))
    out.append(rect(-4, CURB, W + 8, LANE - CURB, "s f-lime"))
    for k in range(10):
        out.append(rect(10 + k * 84, 333, 44, 3.5, "f-paper"))
    return "".join(out)


def _tree(x: float, k: float, fill: str) -> str:
    return line(x, GY + 6, x, GY - 26 * k, "s") + circle(x, GY - 32 * k, 15 * k, f"s {fill}")


def _trees() -> str:
    return _tree(172, 1.0, "f-grass") + _tree(366, 1.1, "f-lime") + _tree(612, 1.15, "f-grass") + _tree(788, 1.1, "f-grass")


def _bin(fill: str) -> str:
    """Wheelie bin, 18 x 28, standing on y=0 with its left edge at x=0."""
    return "".join(
        [
            _poly([(0, -24), (18, -24), (17, 0), (1, 0)], f"s {fill}"),
            rect(-2, -28, 22, 5, f"s {fill}", rx=2),
            circle(4, 0, 3, "s f-ink"),
        ]
    )


def _bins() -> str:
    return _place(_bin("f-lime"), 688, CURB - 3) + _place(_bin("f-aqua"), 714, CURB - 3)


def _cyclist() -> str:
    """Cyclist riding right, wheels on y=0."""
    rw = 11
    a, b = (0, -rw), (38, -rw)
    seat, bar, crank = (13, -32), (32, -34), (18, -rw)
    hip, shoulder = (seat[0] + 1, seat[1] - 2), (seat[0] + 9, seat[1] - 19)
    return "".join(
        [
            circle(*a, rw, "s ln"),
            circle(*b, rw, "s ln"),
            path(f"M{r(a[0])},{r(a[1])}L{r(seat[0])},{r(seat[1] + 4)}L{r(crank[0])},{r(crank[1])}Z", "s ln"),
            path(f"M{r(crank[0])},{r(crank[1])}L{r(bar[0] - 2)},{r(bar[1] + 6)}L{r(b[0])},{r(b[1])}", "s ln"),
            path(f"M{r(seat[0] + 4)},{r(seat[1] + 4)}L{r(bar[0] - 2)},{r(bar[1] + 6)}", "s ln"),
            path(f"M{r(hip[0])},{r(hip[1])}L{r(crank[0] + 6)},{r(crank[1] - 8)}L{r(crank[0] + 3)},{r(crank[1] + 2)}", "s thick ln"),
            path(f"M{r(shoulder[0])},{r(shoulder[1])}L{r(bar[0])},{r(bar[1])}", "s thick ln"),
            _poly([(hip[0] - 4, hip[1] + 2), (shoulder[0] - 5, shoulder[1]), (shoulder[0] + 4, shoulder[1] - 1), (hip[0] + 5, hip[1])], "s f-sun"),
            circle(shoulder[0] + 3, shoulder[1] - 8, 5.5, "s f-wood"),
        ]
    )


def _truck() -> str:
    """Rear-loader facing right, wheels on y=0, tipping a bin into its hopper; a worker rides the back step."""
    rw = 12
    top = -72
    frame = -22
    ribs = "".join(f"M{r(30 + k * 16)},{top + 3}V{frame - 3}" for k in range(1, 7))
    out = [
        rect(4, frame, 196, 9, "s f-ink"),
        _poly([(32, top + 2), (10, top + 12), (2, frame), (32, frame)], "s f-accent"),
        rect(30, top, 114, frame - top, "s f-accent", rx=5),
        path(ribs, "s thin ln"),
        path(f"M148,{frame}V{top + 14}H182L198,{top + 34}V{frame}Z", "s f-accent"),
        path(f"M168,{top + 20}H180L191,{top + 34}H168Z", "s thin f-water"),
        rect(152, top + 20, 12, 14, "s thin f-water"),
        rect(160, top + 8, 10, 6, "s f-sun", rx=3),
        rect(-8, frame + 2, 16, 4, "s f-ink"),
    ]
    for cx in (42, 70, 172):
        out.append(circle(cx, -rw, rw, "s f-ink"))
        out.append(circle(cx, -rw, 4.5, "s thin f-metal"))
    out.append(el("g", _bin("f-aqua"), transform=f"translate(8,{top + 12}) rotate(140)"))
    out.append(_place(_walker("f-sun", step=False), -2, frame + 2, 0.92))
    return "".join(out)


def _walker(shirt: str, step: bool = True) -> str:
    """Standing or walking person facing right, feet on y=0, about 36 tall."""
    hip, neck = (0, -17), (1, -30)
    legs = f"M{hip[0]},{hip[1]}L-5,0M{hip[0]},{hip[1]}L5,0" if step else f"M{hip[0]},{hip[1]}L-2,0M{hip[0]},{hip[1]}L3,0"
    torso = _poly([(-4, hip[1] + 1), (-3.5, neck[1]), (5.5, neck[1]), (5, hip[1] + 1)], f"s {shirt}")
    arm = f"M3,{neck[1] + 3}L7,{hip[1] + 2}" if step else f"M3,{neck[1] + 3}L9,{neck[1] - 4}"
    return path(legs, "s thick ln") + path(arm, "s thick ln") + torso + circle(1, neck[1] - 6, 5, "s f-wood")


def _birds() -> str:
    d = "".join(f"M{x - 7},{y - 3}Q{x - 3},{y - 5} {x},{y}Q{x + 3},{y - 5} {x + 7},{y - 3}" for x, y in ((128, 46), (148, 36), (420, 96)))
    return path(d, "s ln")
