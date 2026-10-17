import math

from reportlab.graphics.shapes import Circle, Ellipse, Line, PolyLine, Polygon, Rect
from reportlab.lib.colors import HexColor


def _color(value):
    if value is None:
        return None
    return HexColor(value)


def _fill_kwargs(fill, opacity):
    kwargs = {"fillColor": _color(fill)}
    if opacity is not None:
        kwargs["fillOpacity"] = opacity
    return kwargs


def _stroke_kwargs(stroke, width, opacity=None):
    kwargs = {"strokeColor": _color(stroke)}
    if stroke is not None:
        kwargs["strokeWidth"] = width
        kwargs["strokeLineCap"] = 1
        kwargs["strokeLineJoin"] = 1
        if opacity is not None:
            kwargs["strokeOpacity"] = opacity
    return kwargs


def rect(x, y, w, h, fill, opacity=None, stroke=None, sw=1, rx=0):
    return Rect(
        x, y, w, h, rx=rx, ry=rx, **_fill_kwargs(fill, opacity), **_stroke_kwargs(stroke, sw)
    )


def circle(cx, cy, r, fill, opacity=None, stroke=None, sw=1):
    return Circle(cx, cy, r, **_fill_kwargs(fill, opacity), **_stroke_kwargs(stroke, sw))


def ellipse(cx, cy, rx, ry, fill, opacity=None, stroke=None, sw=1):
    return Ellipse(cx, cy, rx, ry, **_fill_kwargs(fill, opacity), **_stroke_kwargs(stroke, sw))


def poly(points, fill, opacity=None, stroke=None, sw=1):
    flat = [value for point in points for value in point]
    return Polygon(flat, **_fill_kwargs(fill, opacity), **_stroke_kwargs(stroke, sw))


def line(x1, y1, x2, y2, color, width, opacity=None):
    return Line(x1, y1, x2, y2, **_stroke_kwargs(color, width, opacity))


def pline(points, color, width, opacity=None):
    flat = [value for point in points for value in point]
    return PolyLine(flat, **_stroke_kwargs(color, width, opacity))


def arc_points(cx, cy, rx, ry, start_deg, end_deg, steps=16):
    points = []
    for i in range(steps + 1):
        angle = math.radians(start_deg + (end_deg - start_deg) * i / steps)
        points.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
    return points


def mix(color_a, color_b, t):
    a = HexColor(color_a)
    b = HexColor(color_b)
    r = a.red + (b.red - a.red) * t
    g = a.green + (b.green - a.green) * t
    bl = a.blue + (b.blue - a.blue) * t
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(bl * 255))


def darken(color, amount):
    return mix(color, "#000000", amount)


def lighten(color, amount):
    return mix(color, "#FFFFFF", amount)


def sparkle(cx, cy, size, fill, opacity=None):
    k = size * 0.28
    points = [
        (cx, cy + size),
        (cx + k, cy + k),
        (cx + size, cy),
        (cx + k, cy - k),
        (cx, cy - size),
        (cx - k, cy - k),
        (cx - size, cy),
        (cx - k, cy + k),
    ]
    return poly(points, fill, opacity)
