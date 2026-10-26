"""Data charts as inline SVG. Grey first, one accent, direct labels, bars from zero."""

from dataclasses import dataclass

from ttg.svg import bar_h, bar_v, circle, el, line, path, r, rect, svg, text

W = 400


@dataclass(frozen=True)
class Row:
    label: str
    low: float
    high: float
    value_label: str
    accent: bool = False

    @property
    def is_range(self) -> bool:
        return self.high != self.low


def _tip(s: str) -> str:
    return el("title", s)


def hbars(rows: list[Row], aria: str, label_w: float = 118, unit: str = "") -> str:
    """Horizontal bars with the value at each tip; rows drawn in the given order."""
    row_h, bar_t, top = 26, 14, 4
    x0 = label_w
    x1 = W - 52
    vmax = max(rw.high for rw in rows)
    h = top + row_h * len(rows) + 4
    parts = [line(x0, 0, x0, h - 4, "base")]
    for i, rw in enumerate(rows):
        y = top + i * row_h + (row_h - bar_t) / 2
        w = (x1 - x0) * rw.high / vmax
        cls = "f-accent" if rw.accent else "f-grey"
        label_cls = "t t-strong" if rw.accent else "t"
        parts.append(text(x0 - 8, y + bar_t - 3, rw.label, label_cls, anchor="end"))
        g = bar_h(x0, y, max(w, 1.5), bar_t, cls) + text(x0 + w + 6, y + bar_t - 3, rw.value_label, f"{label_cls} t-num")
        parts.append(el("g", _tip(f"{rw.label}: {rw.value_label}{unit}") + g + rect(0, y - 5, W, bar_t + 10, "hit")))
    return svg(W, h, "".join(parts), aria)


def ranges(rows: list[Row], aria: str, ticks: list[float], tick_fmt: str = "{:,.0f}", label_w: float = 132) -> str:
    """Point values as bars from zero; ranges as a whisker with a dot at each end."""
    row_h, bar_t, top = 34, 14, 6
    x0, x1 = label_w, W - 70
    vmax = ticks[-1]
    sx = lambda v: x0 + (x1 - x0) * v / vmax  # noqa: E731
    plot_h = top + row_h * len(rows)
    parts: list[str] = []
    for t in ticks:
        parts.append(line(sx(t), 0, sx(t), plot_h, "grid" if t else "base"))
        parts.append(text(sx(t), plot_h + 16, tick_fmt.format(t), "t t-muted t-num", anchor="middle"))
    for i, rw in enumerate(rows):
        cy = top + i * row_h + row_h / 2
        label_cls = "t t-strong" if rw.accent else "t"
        parts.append(text(x0 - 10, cy + 4, rw.label, label_cls, anchor="end"))
        if rw.is_range:
            wcls = "whisker" if rw.accent else "whisker g"
            dcls = "f-accent ring" if rw.accent else "f-grey ring"
            mark = (
                line(sx(rw.low), cy, sx(rw.high), cy, wcls)
                + circle(sx(rw.low), cy, 5, dcls)
                + circle(sx(rw.high), cy, 5, dcls)
            )
            end = sx(rw.high) + 9
        else:
            mark = bar_h(x0, cy - bar_t / 2, sx(rw.high) - x0, bar_t, "f-accent" if rw.accent else "f-grey")
            end = sx(rw.high) + 6
        lab = text(end, cy + 4, rw.value_label, f"{label_cls} t-num")
        parts.append(el("g", _tip(f"{rw.label}: {rw.value_label}") + mark + lab + rect(0, cy - row_h / 2, W, row_h, "hit")))
    return svg(W, plot_h + 24, "".join(parts), aria)


@dataclass(frozen=True)
class Step:
    label: str
    delta: float
    value_label: str
    kind: str  # "up", "credit", "total"


def waterfall(steps: list[Step], aria: str, ymax: float, ticks: list[float]) -> str:
    """Waterfall: increases, a credit, and the net total from zero."""
    top, base = 22, 200
    x0 = 34
    col_w = 30
    slot = (W - x0) / len(steps)
    sy = lambda v: base - (base - top) * v / ymax  # noqa: E731
    parts: list[str] = []
    for t in ticks:
        parts.append(line(x0, sy(t), W, sy(t), "grid" if t else "base"))
        parts.append(text(x0 - 6, sy(t) + 4, f"{t:g}", "t t-muted t-num", anchor="end"))
    run = 0.0
    prev_end: tuple[float, float] | None = None
    for i, st in enumerate(steps):
        cx = x0 + slot * i + slot / 2
        x = cx - col_w / 2
        if st.kind == "total":
            lo, hi, cls = 0.0, st.delta, "f-grey"
        elif st.kind == "credit":
            lo, hi, cls = run + st.delta, run, "f-credit"
            run += st.delta
        else:
            lo, hi, cls = run, run + st.delta, "f-accent"
            run += st.delta
        if prev_end is not None:
            parts.append(line(prev_end[0], sy(prev_end[1]), x, sy(prev_end[1]), "leader"))
        if lo == 0:
            mark = bar_v(x, base, col_w, base - sy(hi), cls)
        else:
            mark = rect(x, sy(hi), col_w, sy(lo) - sy(hi), cls, rx=2)
        label_y = sy(hi) - 7
        parts.append(
            el(
                "g",
                _tip(f"{st.label}: {st.value_label}")
                + mark
                + text(cx, label_y, st.value_label, "t t-strong t-num", anchor="middle")
                + text(cx, base + 18, st.label, "t", anchor="middle")
                + rect(cx - slot / 2, top - 20, slot, base - top + 44, "hit"),
            )
        )
        prev_end = (x + col_w, hi if st.kind != "credit" else lo)
    return svg(W, base + 28, "".join(parts), aria)


@dataclass(frozen=True)
class Flow:
    label: str
    value: float
    value_label: str
    accent: bool = False


def sankey(total_label: str, flows: list[Flow], aria: str) -> str:
    """One source splitting into flows, widths to scale; the accent flow carries the point."""
    top, height = 10, 210
    gap = 8
    total = sum(f.value for f in flows)
    k = (height - gap * (len(flows) - 1)) / total
    src_x, src_w = 6, 14
    dst_x, dst_w = 214, 14
    parts = [rect(src_x, top, src_w, total * k + gap * (len(flows) - 1), "f-grey2")]

    sy = top
    dy = top
    min_gap = 30
    last_label = -1e9
    for f in flows:
        h = f.value * k
        cls = "f-accent" if f.accent else "f-grey"
        x_a, x_b = src_x + src_w + 2, dst_x - 2
        mid = (x_a + x_b) / 2
        band = (
            f"M{r(x_a)},{r(sy)}C{r(mid)},{r(sy)} {r(mid)},{r(dy)} {r(x_b)},{r(dy)}"
            f"V{r(dy + h)}C{r(mid)},{r(dy + h)} {r(mid)},{r(sy + h)} {r(x_a)},{r(sy + h)}Z"
        )
        lab_cls = "t t-strong" if f.accent else "t"
        ly = max(dy + h / 2, last_label + min_gap)
        last_label = ly
        parts.append(
            el(
                "g",
                _tip(f"{f.label}: {f.value_label}")
                + path(band, f"{cls} flow")
                + rect(dst_x, dy, dst_w, h, cls)
                + text(dst_x + dst_w + 8, ly - 1, f.label, lab_cls)
                + text(dst_x + dst_w + 8, ly + 13, f.value_label, "t t-muted t-num"),
            )
        )
        sy += h + gap
        dy += h + gap
    parts.append(text(src_x, max(top + height, last_label + 14) + 18, total_label, "t t-strong t-num"))
    bottom = max(top + height, last_label + 14)
    return svg(W, bottom + 26, "".join(parts), aria)
