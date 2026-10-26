"""Object illustrations: dog, grocery bag, bag glyph, can. Flat line style, fills from CSS classes only."""

from ttg.svg import bar_v, el, path, r, svg, text


def _g(body: str, x: float, y: float, k: float) -> str:
    return el("g", body, transform=f"translate({r(x)},{r(y)}) scale({r(k)})")


def _ellipse(cx: float, cy: float, rx: float, ry: float, cls: str) -> str:
    return el("ellipse", cx=r(cx), cy=r(cy), rx=r(rx), ry=r(ry), class_=cls)


# Dog: 100 x 100 box, ground at y=98, facing right.
DOG_TAIL = "M23,81C10,82 3,72 5,61C6,55 9.5,51 14,49.5C11.5,54.5 10.5,58.5 11.5,63C13,70 17,74 24,74Z"
DOG_BODY = (
    "M24,98C18,91 17,77 22,68"  # rump
    "C30,54 42,46 48,38"  # back
    "C46,32 45,24 47,16"  # back of neck
    "C49,8 56,3 64,3C70,3 73,6 75,10"  # skull
    "C77,12 80,12.5 84,13C88,13.5 91,13.5 93,15"  # stop, muzzle
    "C95.5,17 95.5,21 93,23.5C91,26.5 89,28.5 85,29"  # nose, chin
    "C80,30 76,31.5 74,34C73,40 75,46 76,52C77,57 77.2,61 76.7,65"  # throat, chest
    "L75.8,93C76,94.5 79,94.5 80.5,95.5C82,96.5 81.5,98 79,98Z"  # near front paw, then along the ground
)
DOG_LINES = (
    "M31,74C36,66 51,64 57,71C59,76 58,84 54,89C57,90 59.5,91.5 60.5,93.5C61.5,95.5 61,98 58.5,98"  # thigh, rear paw
    "M68,63.5C68.8,65 69,66.5 69,69V98"  # back of near front leg
    "M63,69V98"  # back of far front leg
)
DOG_EAR = "M57,5C51,6 48,12 48.5,19C49,25.5 51.5,29.5 55,29.5C58.5,29.5 60.5,25 61.5,19.5C62.5,13.5 63,8 60.5,5.5Z"
DOG_TONGUE = "M82,23.5C81.5,30.5 83,35 86.5,35C90,35 90.5,30 89.5,23.5Z"
DOG_MOUTH = "M93,22.5C89,25.5 83,25.8 78.5,22.5"
DOG_COLLAR = "M46.5,31.5C55,35 65,37 73.6,36.5L74.3,41C65,41.5 55,39.5 46,36Z"


def dog(x: float, y: float, k: float = 1, ground: bool = True, collar: str = "f-ink") -> str:
    """A happy dog sitting, facing right, in a 100 x 100 box at k=1; paws on y=98."""
    parts = [
        path(DOG_TAIL, "s f-fur"),
        path(DOG_BODY, "s f-fur"),
        path(DOG_LINES, "s ln"),
        path(DOG_EAR, "s f-fur2"),
        path(DOG_COLLAR, f"s {collar}"),
        path(DOG_TONGUE, "s f-tongue"),
        path(DOG_MOUTH, "s ln"),
        # thin ink ring keeps the near-black eye and nose visible on dark grey in dark mode
        _ellipse(91.8, 16.6, 2.7, 2.3, "s thin f-eye"),
        _ellipse(71, 12.5, 1.9, 2.1, "s thin f-eye"),
    ]
    if ground:
        parts.append(path("M12,98H92", "s ln"))
    return _g("".join(parts), x, y, k)


# Bag: 40 x 48 box, standing on y=47.5.
BAG = (
    "M6,47.5C3,47.5 1.5,45.5 1.5,42C1.5,33 2.5,24 4.5,15L5,3.5Q5,1 7.5,1H9.5Q12,1 12,3.5"
    "C12,15 15.8,19.5 20,19.5C24.2,19.5 28,15 28,3.5Q28,1 30.5,1H32.5Q35,1 35,3.5"
    "L35.5,15C37.5,24 38.5,33 38.5,42C38.5,45.5 37,47.5 34,47.5Z"
)
BAG_FOLDS = "M8.5,13L7.2,43M31.5,13L32.8,43"


def bag(x: float, y: float, k: float = 1, cls: str = "f-paper") -> str:
    """Single-use T-shirt grocery bag, 40 x 48 at k=1, top-left at (x, y)."""
    return _g(path(BAG, f"s {cls}") + path(BAG_FOLDS, "s ln thin"), x, y, k)


def bag_glyph(x: float, y: float, k: float, cls: str = "f-grey") -> str:
    """The bag as a filled silhouette with no lines, for piles of hundreds."""
    return el("path", d=BAG, class_=cls, transform=f"translate({r(x)},{r(y)}) scale({r(k)})")


# Can: 48 x 68 box.
CAN_BODY = "M13,8L9,14V60L12,64.5Q24,68.5 36,64.5L39,60V14L35,8Z"
CAN_BAND = "M9,28Q24,32 39,28V45Q24,49 9,45Z"
CAN_DROPS = "M43.8,9C46.3,13 47.3,15.3 47.3,17A3.5,3.5 0 0 1 40.3,17C40.3,15.3 41.3,13 43.8,9ZM44.2,24C45.7,26.5 46.3,27.8 46.3,28.9A2.1,2.1 0 0 1 42.1,28.9C42.1,27.8 42.7,26.5 44.2,24Z"


def can(x: float = 0, y: float = 0, k: float = 1, drops: bool = True) -> str:
    """Aluminum beverage can, 48 x 68 at k=1, top-left at (x, y); accent label band, optional rinse drops."""
    parts = [
        path(CAN_BODY, "s f-metal"),
        path(CAN_BAND, "f-accent"),
        path("M9,28Q24,32 39,28M9,45Q24,49 39,45", "s ln"),
        path("M9,14Q24,18 39,14M9,60Q24,64 39,60", "s ln thin"),
        _ellipse(24, 8, 11, 3.4, "s f-metal"),
        _ellipse(24, 8.3, 8.6, 2.3, "s ln thin"),
        path("M20.5,8.3H27.5", "s ln"),
    ]
    if drops:
        parts.append(path(CAN_DROPS, "s f-water"))
    return _g("".join(parts), x, y, k)


def card_dog_vs_bag() -> str:
    """C3: the dog, then the two bars at 3:1 from one baseline, then the bag."""
    base = 126
    unit = 32
    bw = 26
    x3, x1 = 106, 138
    p = [
        dog(-1, base - 98, 1, ground=False),
        bar_v(x3, base, bw, unit * 3, "f-grey"),
        bar_v(x1, base, bw, unit, "f-accent"),
        bag(172, base - 47.5 * 0.8, 0.8),
        text(x3 + bw / 2, base - unit * 3 - 7, "3x", "t t-big", anchor="middle"),
        text(x1 + bw / 2, base - unit - 7, "1x", "t t-big", anchor="middle"),
        path(f"M8,{base}H210", "s ln"),
    ]
    return svg(216, 132, "".join(p), "A happy dog and a grocery bag; the dog's bar is three times the bag's")
