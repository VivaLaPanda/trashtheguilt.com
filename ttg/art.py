"""Card C1: two circles with areas to scale."""

from ttg.svg import circle, text


def two_circles(w: float, big_t: float, small_t: float, big_label: str, small_label: str) -> str:
    """Two circles with areas to scale, sitting on one baseline, labels underneath."""
    big_r = 46
    small_r = big_r * (small_t / big_t) ** 0.5
    base = 100
    cx_big = w / 2 - 28
    cx_small = cx_big + big_r + 26 + small_r
    return "".join(
        [
            circle(cx_big, base - big_r, big_r, "s f-grey"),
            circle(cx_small, base - small_r, small_r, "s f-accent"),
            text(cx_big, base + 18, big_label, "t", anchor="middle"),
            text(cx_small, base + 18, small_label, "t", anchor="middle"),
        ]
    )
