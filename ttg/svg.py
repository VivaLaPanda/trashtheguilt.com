"""Small helpers for writing inline SVG by hand."""

from html import escape


def attrs(**kw: object) -> str:
    out = []
    for k, v in kw.items():
        if v is None or v is False:
            continue
        name = k.rstrip("_").replace("_", "-")
        out.append(name if v is True else f'{name}="{escape(str(v), quote=True)}"')
    return " ".join(out)


def el(tag: str, body: str = "", **kw: object) -> str:
    a = attrs(**kw)
    head = f"<{tag} {a}" if a else f"<{tag}"
    return f"{head}>{body}</{tag}>" if body else f"{head}/>"


def r(x: float) -> str:
    """Trim coordinates to 2 decimals to keep markup small."""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def path(d: str, cls: str = "ln", **kw: object) -> str:
    return el("path", d=d, class_=cls, **kw)


def rect(x: float, y: float, w: float, h: float, cls: str, rx: float = 0, **kw: object) -> str:
    return el("rect", x=r(x), y=r(y), width=r(w), height=r(h), rx=r(rx) if rx else None, class_=cls, **kw)


def circle(cx: float, cy: float, rad: float, cls: str, **kw: object) -> str:
    return el("circle", cx=r(cx), cy=r(cy), r=r(rad), class_=cls, **kw)


def line(x1: float, y1: float, x2: float, y2: float, cls: str = "ln", **kw: object) -> str:
    return el("line", x1=r(x1), y1=r(y1), x2=r(x2), y2=r(y2), class_=cls, **kw)


def text(x: float, y: float, s: str, cls: str = "t", anchor: str = "start", **kw: object) -> str:
    return el("text", escape(s), x=r(x), y=r(y), class_=cls, text_anchor=anchor if anchor != "start" else None, **kw)


def bar_h(x: float, y: float, w: float, h: float, cls: str, end: float = 4) -> str:
    """Horizontal bar: square at the baseline, rounded data end."""
    if w <= 0:
        return ""
    e = min(end, w, h / 2)
    d = (
        f"M{r(x)},{r(y)}H{r(x + w - e)}Q{r(x + w)},{r(y)} {r(x + w)},{r(y + e)}"
        f"V{r(y + h - e)}Q{r(x + w)},{r(y + h)} {r(x + w - e)},{r(y + h)}H{r(x)}Z"
    )
    return el("path", d=d, class_=cls)


def bar_v(x: float, base: float, w: float, h: float, cls: str, end: float = 4) -> str:
    """Vertical column growing up from `base`: square at the baseline, rounded top."""
    if h <= 0:
        return ""
    e = min(end, h, w / 2)
    top = base - h
    d = (
        f"M{r(x)},{r(base)}V{r(top + e)}Q{r(x)},{r(top)} {r(x + e)},{r(top)}"
        f"H{r(x + w - e)}Q{r(x + w)},{r(top)} {r(x + w)},{r(top + e)}V{r(base)}Z"
    )
    return el("path", d=d, class_=cls)


def svg(view_w: float, view_h: float, body: str, label: str, cls: str = "fig") -> str:
    return (
        f'<svg class="{cls}" viewBox="0 0 {r(view_w)} {r(view_h)}" role="img" '
        f'aria-label="{escape(label, quote=True)}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'
    )
