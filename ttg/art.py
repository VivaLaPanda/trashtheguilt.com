"""Illustrations, drawn in code. One flat line style: 2px ink stroke, flat fills, no gradients."""

from ttg.svg import circle, el, line, path, r, rect, text

BAG_W, BAG_H = 40, 48


def bag(x: float, y: float, k: float = 1, cls: str = "f-paper") -> str:
    """T-shirt grocery bag, 40x48 at k=1, top-left at (x, y)."""
    d = (
        "M6,48Q4,48 4,46L3,14V4Q3,2 5,2H10Q12,2 12,4V12Q20,18 28,12V4Q28,2 30,2H35Q37,2 37,4V14"
        "L36,46Q36,48 34,48Z"
    )
    slots = "M6,6H9M31,6H34"
    folds = "M12,26Q20,30 28,26"
    g = path(d, f"s {cls}") + path(slots, "s ln") + path(folds, "s ln thin")
    return el("g", g, transform=f"translate({r(x)},{r(y)}) scale({r(k)})")


def bag_glyph(x: float, y: float, k: float, cls: str = "f-grey") -> str:
    """Bag silhouette without inner lines, for piles of many bags."""
    d = "M6,48Q4,48 4,46L3,14V4Q3,2 5,2H10Q12,2 12,4V12Q20,18 28,12V4Q28,2 30,2H35Q37,2 37,4V14L36,46Q36,48 34,48Z"
    return el("path", d=d, class_=cls, transform=f"translate({r(x)},{r(y)}) scale({r(k)})")


def bed(x: float, y: float, s: float, footprint_sq_ft: tuple[float, float] | None = None) -> str:
    """Twin bed (38 x 75 in) seen from above, head at the top; s = units per inch.

    footprint_sq_ft: (low, high) drawn to scale from the foot of the bed, bed-wide.
    """
    w, h = 38 * s, 75 * s
    parts = [rect(x, y, w, h, "s f-paper", rx=2.5 * s)]
    if footprint_sq_ft:
        lo, hi = footprint_sq_ft
        lo_h = lo * 144 / 38 * s
        hi_h = hi * 144 / 38 * s
        parts.append(rect(x, y + h - hi_h, w, hi_h - lo_h, "f-accent-soft"))
        parts.append(rect(x, y + h - lo_h, w, lo_h, "f-accent"))
        parts.append(rect(x, y, w, h, "s ln", rx=2.5 * s))
    parts.append(rect(x + 6 * s, y + 4 * s, w - 12 * s, 10 * s, "s f-paper", rx=3 * s))
    parts.append(path(f"M{r(x)},{r(y + 20 * s)}H{r(x + w)}", "s ln"))
    parts.append(rect(x - 1.5 * s, y - 3 * s, w + 3 * s, 3 * s, "s f-grey", rx=1.2 * s))
    return "".join(parts)


def doormat(x: float, y: float, s: float, footprint_sq_ft: tuple[float, float] | None = None) -> str:
    """2 x 3 ft doormat, landscape; s = units per inch. Footprint is mat-high, drawn from the left."""
    w, h = 36 * s, 24 * s
    parts = [rect(x, y, w, h, "s f-soft", rx=1.5 * s)]
    if footprint_sq_ft:
        lo, hi = footprint_sq_ft
        lo_w = lo * 144 / 24 * s
        hi_w = hi * 144 / 24 * s
        parts.append(rect(x, y, hi_w, h, "f-accent-soft"))
        parts.append(rect(x, y, lo_w, h, "f-accent"))
    parts.append(rect(x, y, w, h, "s ln", rx=1.5 * s))
    parts.append(rect(x + 2.5 * s, y + 2.5 * s, w - 5 * s, h - 5 * s, "s ln thin", rx=1 * s))
    return "".join(parts)


def dog(x: float, y: float, k: float = 1) -> str:
    """A happy sitting dog facing right, about 100x100 at k=1."""
    parts = [
        # tail, mid-wag
        path("M30,80Q16,74 13,58Q12,50 17,47", "s ln thick"),
        # body and chest
        path("M26,97Q20,72 36,60Q48,52 54,40L74,42Q79,58 77,72L78,97Z", "s f-grey"),
        # haunch
        path("M22,97Q19,80 35,77Q51,76 53,97", "s f-grey"),
        # front legs
        rect(60, 68, 8, 29, "s f-grey", rx=4),
        rect(70, 66, 8, 31, "s f-grey", rx=4),
        # head and snout
        path("M50,34Q50,14 68,14Q82,14 84,28Q96,30 96,38Q96,46 84,46Q76,52 64,50Q50,48 50,34Z", "s f-grey"),
        # ear
        path("M58,19Q47,21 47,34Q47,44 54,44Q60,40 61,28Z", "s f-grey2"),
        # nose and eye
        circle(94.5, 35, 3.2, "f-eye"),
        circle(72, 27, 2.6, "f-eye"),
        # smile and tongue
        path("M78,45Q84,47 90,44", "s ln"),
        path("M81,46Q81,56 85.5,56Q89,56 88,45.5", "s f-tongue"),
        # collar
        path("M57,48Q65,54 75,51", "s ln thick-accent"),
        # ground
        path("M14,97H90", "s ln"),
    ]
    return el("g", "".join(parts), transform=f"translate({r(x)},{r(y)}) scale({r(k)})")


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


def landfill(clip_id: str = "lf") -> str:
    """Cross-section of a modern landfill; 400 x 300 viewBox, labels in side columns."""
    gy, wt, floor = 150, 252, 236
    cx = 196
    p: list[str] = []
    # soil and groundwater
    p.append(rect(0, gy, 400, 300 - gy, "f-soft"))
    p.append(rect(0, wt, 400, 300 - wt, "f-water"))
    waves = "".join(f"T{x},{wt}" for x in range(40, 401, 20))
    p.append(path(f"M0,{wt}Q10,{wt - 3} 20,{wt}{waves}", "s ln thin"))
    p.append(path(f"M0,{gy}H400", "s ln"))
    # liner: clay band, then the plastic membrane on top of it
    outer = f"M{cx - 90},{gy}L{cx - 66},{floor}H{cx + 66}L{cx + 90},{gy}"
    inner = f"M{cx - 82},{gy}L{cx - 60},{floor - 8}H{cx + 60}L{cx + 82},{gy}"
    p.append(path(outer + "Z", "f-clay"))
    p.append(path(outer, "s ln"))
    # waste body, below and above ground
    mound = f"{inner}L{cx + 74},{gy - 40}Q{cx},{gy - 82} {cx - 74},{gy - 40}Z"
    p.append(el("clipPath", path(mound, ""), id=clip_id))
    p.append(path(mound, "f-grey"))
    cells = "".join(f"M0,{yy}H400" for yy in range(floor - 26, gy - 70, -20))
    cells += "".join(f"M{xx},0V300" for xx in (cx - 44, cx, cx + 44))
    p.append(el("g", path(cells, "s ln cover"), clip_path=f"url(#{clip_id})"))
    p.append(path(inner, "s ln accent-line"))
    # leachate pipes along the floor
    p.append(path(f"M{cx - 60},{floor - 13}H{cx + 60}", "s ln thin"))
    for lx in (cx - 42, cx - 14, cx + 14, cx + 42):
        p.append(circle(lx, floor - 13, 3.4, "s f-paper"))
    # final cap: a soil layer over the mound, with grass
    cap_out = f"M{cx - 88},{gy}L{cx - 80},{gy - 44}Q{cx},{gy - 92} {cx + 80},{gy - 44}L{cx + 88},{gy}"
    cap_in = f"L{cx + 82},{gy}L{cx + 74},{gy - 40}Q{cx},{gy - 82} {cx - 74},{gy - 40}L{cx - 82},{gy}Z"
    p.append(path(cap_out + cap_in, "f-cap"))
    p.append(path(cap_out, "s ln"))
    for gx in range(cx - 66, cx + 67, 12):
        top = _quad_y(gx, cx - 80, cx + 80, gy - 44, gy - 92)
        p.append(path(f"M{gx},{r(top)}l-2.5,-5M{gx},{r(top)}l2,-6", "s ln thin"))
    # gas wells to a header, then to the flare
    head_y = 50
    for gx in (cx - 40, cx, cx + 40):
        p.append(path(f"M{gx},{head_y}V{floor - 46}", "s ln gas"))
    fx = cx + 150
    p.append(path(f"M{cx - 40},{head_y}H{fx}V{gy - 44}", "s ln"))
    p.append(rect(fx - 6, gy - 44, 12, 44, "s f-paper", rx=2))
    p.append(path(f"M{fx},{gy - 46}Q{fx - 8},{gy - 58} {fx},{gy - 72}Q{fx + 8},{gy - 58} {fx},{gy - 46}Z", "s f-flame"))
    # groundwater monitoring wells, one each side, screened below the water table
    for mx in (cx - 104, cx + 104):
        p.append(rect(mx - 3.5, gy - 10, 7, wt + 26 - gy + 10, "s f-paper", rx=1.5))
        p.append(path("".join(f"M{mx - 3.5},{yy}h7" for yy in range(wt + 4, wt + 26, 5)), "s ln thin"))
    # labels
    p.append(_label(["Final cap"], 6, 96, cx - 78, gy - 40))
    p.append(_label(["Gas wells"], cx, 18, cx, head_y, anchor="middle"))
    p.append(_label(["Flare or", "generator"], 396, 20, fx + 4, gy - 64, anchor="end"))
    p.append(_label(["Waste cells", "with daily", "cover"], 6, 172, cx - 44, 190))
    p.append(_label(["Clay and", "plastic liner"], 6, 276, cx - 76, 206))
    p.append(_label(["Leachate pipes"], cx, 292, cx + 14, floor - 13, anchor="middle"))
    p.append(_label(["Groundwater", "monitoring", "wells"], 396, 178, cx + 104, 214, anchor="end"))
    return "".join(p)


def _quad_y(x: float, x0: float, x1: float, y_end: float, y_ctrl: float) -> float:
    """y on a symmetric quadratic from (x0, y_end) to (x1, y_end) with control y_ctrl."""
    t = (x - x0) / (x1 - x0)
    return (1 - t) ** 2 * y_end + 2 * (1 - t) * t * y_ctrl + t**2 * y_end


def _label(lines: list[str], tx: float, ty: float, px: float, py: float, anchor: str = "start") -> str:
    """Multi-line label at (tx, ty) with a leader from the nearest edge of its box to (px, py)."""
    lh = 13.5
    width = max(len(s) for s in lines) * 6.4
    x0 = {"start": tx, "end": tx - width, "middle": tx - width / 2}[anchor] - 3
    x1 = x0 + width + 6
    y0, y1 = ty - 12, ty + lh * (len(lines) - 1) + 4
    lx, ly = min(max(px, x0), x1), min(max(py, y0), y1)
    out = [line(lx, ly, px, py, "leader"), circle(px, py, 2.6, "f-ink")]
    for i, s in enumerate(lines):
        out.append(text(tx, ty + i * lh, s, "t t-strong", anchor=anchor))
    return "".join(out)
