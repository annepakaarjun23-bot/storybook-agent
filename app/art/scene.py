import math
import random
from dataclasses import dataclass, field

from reportlab.graphics.shapes import Drawing

from app.art.hero import draw_hero
from app.art.primitives import (
    arc_points,
    circle,
    darken,
    ellipse,
    lighten,
    line,
    mix,
    pline,
    poly,
    rect,
    sparkle,
)
from app.art.vocab import ELEMENTS, SETTINGS, TIMES_OF_DAY

PALETTES = {
    "day": {
        "sky_top": "#7CC8F0",
        "sky_bot": "#EAF8FF",
        "hill_far": "#A9DDB3",
        "hill_near": "#82CB8E",
        "grass": "#6CC070",
        "grass_dark": "#4FA25A",
        "leaf": "#43A85E",
        "leaf_dark": "#2E8750",
        "trunk": "#8B5E3C",
        "wall": "#CDBBA0",
        "path": "#EBDDB5",
        "cloud": "#FFFFFF",
    },
    "dusk": {
        "sky_top": "#8E6FC0",
        "sky_bot": "#FFC9A0",
        "hill_far": "#9CA878",
        "hill_near": "#6F9A63",
        "grass": "#5E9E5C",
        "grass_dark": "#46814A",
        "leaf": "#3F8A52",
        "leaf_dark": "#2B6A41",
        "trunk": "#7A5236",
        "wall": "#C2A98F",
        "path": "#E2CDA2",
        "cloud": "#FFE3D2",
    },
    "night": {
        "sky_top": "#141D4A",
        "sky_bot": "#3E56A0",
        "hill_far": "#2F5A6E",
        "hill_near": "#264C5E",
        "grass": "#2F6B5A",
        "grass_dark": "#245247",
        "leaf": "#2A6A55",
        "leaf_dark": "#1D4F44",
        "trunk": "#4F3A2E",
        "wall": "#7F7A8C",
        "path": "#8C9AAE",
        "cloud": "#5E6FB0",
    },
    "magic": {
        "sky_top": "#B79AEA",
        "sky_bot": "#D9F7E6",
        "hill_far": "#8ED6C0",
        "hill_near": "#6CC7A6",
        "grass": "#5CC28F",
        "grass_dark": "#3FA474",
        "leaf": "#38B07E",
        "leaf_dark": "#2A8F66",
        "trunk": "#7B5A57",
        "wall": "#C9BCCB",
        "path": "#F2E4C4",
        "cloud": "#FFF2FB",
    },
}

FLOWER_COLORS = ["#FF7BAC", "#FFD23F", "#FFFFFF", "#B48CFF", "#FF9A4D", "#6EC8FF"]
FOCAL_SETTINGS = ("wall", "glade", "garden")


@dataclass
class SceneSpec:
    setting: str = "meadow"
    time_of_day: str = "day"
    elements: list = field(default_factory=list)
    hero_pose: str = "standing"
    expression: str = "happy"
    hero_x: float = 0.4


class Ctx:
    def __init__(self, w, h, spec, seed):
        self.w = w
        self.h = h
        self.u = h / 380.0
        self.rng = random.Random(seed)
        self.time = spec.time_of_day if spec.time_of_day in TIMES_OF_DAY else "day"
        self.setting = spec.setting if spec.setting in SETTINGS else "meadow"
        self.pal = PALETTES[self.time]
        self.gy = 78 * self.u
        self.top = 100 * self.u
        hero_frac = min(max(float(spec.hero_x), 0.18), 0.82)
        self.hero_px = hero_frac * w
        self.focal_x = w * 0.74 if hero_frac < 0.5 else w * 0.26

    def pick_x(self, gap, extra_avoid=None, low=0.04, high=0.96):
        for _ in range(40):
            x = self.rng.uniform(low * self.w, high * self.w)
            if abs(x - self.hero_px) < gap:
                continue
            if extra_avoid is not None and abs(x - extra_avoid) < gap * 0.9:
                continue
            return x
        return self.w - self.hero_px


def _sky(d, ctx):
    bands = 18
    band_h = ctx.h / bands
    for i in range(bands):
        color = mix(ctx.pal["sky_bot"], ctx.pal["sky_top"], i / (bands - 1))
        d.add(rect(0, i * band_h, ctx.w, band_h + 1, color))


def _cloud(d, x, y, s, color, opacity):
    for dx, dy, rx, ry in ((0, 0, 34, 15), (-22, -3, 22, 11), (24, -2, 24, 12), (4, 9, 22, 13)):
        d.add(ellipse(x + dx * s, y + dy * s, rx * s, ry * s, color, opacity))


def _sky_objects(d, ctx, elements):
    w, h, u, t = ctx.w, ctx.h, ctx.u, ctx.time
    rng = ctx.rng
    show_stars = t in ("night", "magic") or ("stars" in elements and t != "day")
    if show_stars:
        for _ in range(38):
            x = rng.uniform(0.02 * w, 0.98 * w)
            y = rng.uniform(h * 0.5, h * 0.98)
            d.add(circle(x, y, rng.uniform(1.0, 2.2) * u, "#FFFFFF", 0.9))
        for _ in range(5):
            d.add(sparkle(rng.uniform(0.05 * w, 0.95 * w), rng.uniform(h * 0.6, h * 0.95), rng.uniform(5, 8) * u, "#FFF6C8", 0.95))
    if t == "day":
        sx, sy = w * 0.85, h * 0.83
        for r, o in ((62, 0.12), (48, 0.2)):
            d.add(circle(sx, sy, r * u, "#FFE680", o))
        d.add(circle(sx, sy, 32 * u, "#FFD94A"))
    elif t == "dusk":
        sx, sy = w * 0.16, h * 0.43
        for r, o in ((92, 0.12), (70, 0.2), (52, 0.3)):
            d.add(circle(sx, sy, r * u, "#FFB56B", o))
        d.add(circle(sx, sy, 38 * u, "#FF9A4D"))
    if t == "night" or "moon" in elements:
        if ctx.setting in FOCAL_SETTINGS and ctx.focal_x > w * 0.6:
            mx = w * 0.5
        else:
            mx = w * 0.82 if t != "day" else w * 0.12
        my = h * 0.8
        for r, o in ((50, 0.1), (38, 0.18)):
            d.add(circle(mx, my, r * u, "#FFF6D6", o))
        d.add(circle(mx, my, 26 * u, "#FFF6D6"))
        d.add(circle(mx - 8 * u, my + 6 * u, 5 * u, "#EADFB8"))
        d.add(circle(mx + 9 * u, my - 8 * u, 4 * u, "#EADFB8"))
    if t != "night":
        for _ in range(3):
            _cloud(d, rng.uniform(0.1 * w, 0.9 * w), rng.uniform(h * 0.62, h * 0.9), rng.uniform(0.9, 1.5) * u, ctx.pal["cloud"], 0.85)


def _rainbow(d, ctx):
    colors = ["#FF6B6B", "#FFA94D", "#FFE066", "#8CE99A", "#74C0FC", "#9775FA", "#DA77F2"]
    cx, cy = ctx.w * 0.5, ctx.top + 6 * ctx.u
    for i, color in enumerate(colors):
        r = (262 - i * 10) * ctx.u
        d.add(pline(arc_points(cx, cy, r, r * 0.88, 0, 180, 48), color, 10 * ctx.u, 0.55))


def _hills(d, ctx):
    w, u = ctx.w, ctx.u
    layers = (
        (ctx.top + 76 * u, 28 * u, 1.3, 0.6, ctx.pal["hill_far"]),
        (ctx.top + 34 * u, 22 * u, 1.9, 2.1, ctx.pal["hill_near"]),
    )
    for base, amp, freq, phase, color in layers:
        points = [(0, 0)]
        for i in range(41):
            points.append((w * i / 40, base + amp * math.sin(phase + 2 * math.pi * freq * i / 40)))
        points.append((w, 0))
        d.add(poly(points, color))


def _tree(d, x, base, height, leaf, trunk):
    size = height / 1.06
    d.add(rect(x - 0.05 * size, base, 0.10 * size, 0.55 * size, trunk, rx=0.02 * size))
    blobs = ((0, 0.68, 0.28), (-0.2, 0.56, 0.22), (0.2, 0.56, 0.22), (0, 0.86, 0.2), (-0.14, 0.78, 0.2), (0.14, 0.78, 0.2))
    for dx, dy, r in blobs:
        d.add(circle(x + dx * size, base + dy * size, r * size, leaf))
    d.add(circle(x - 0.1 * size, base + 0.82 * size, 0.1 * size, lighten(leaf, 0.3), 0.35))


def _forest(d, ctx):
    w, u, rng = ctx.w, ctx.u, ctx.rng
    far_leaf = mix(ctx.pal["leaf"], ctx.pal["sky_bot"], 0.35)
    far_trunk = mix(ctx.pal["trunk"], ctx.pal["sky_bot"], 0.3)
    for i in range(-1, 12):
        x = w * i / 10 + rng.uniform(-18, 18) * u
        _tree(d, x, ctx.top + 4 * u, rng.uniform(150, 200) * u, far_leaf, far_trunk)
    d.add(rect(0, ctx.top, w, 70 * u, "#FFFFFF", 0.16))
    for i in range(-1, 8):
        x = w * i / 6.5 + rng.uniform(-24, 24) * u
        _tree(d, x, ctx.top - 8 * u, rng.uniform(230, 300) * u, ctx.pal["leaf_dark"], darken(ctx.pal["trunk"], 0.15))


def _door(d, x, base, s, ctx, glow):
    hw = 42 * s
    rh = 100 * s
    stone = "#B5A89A" if ctx.time != "night" else "#6F6B7E"
    wood = "#7A4B2A" if ctx.time != "night" else "#4D3326"
    outer = [(x + hw + 9 * s, base)] + arc_points(x, base + rh, hw + 9 * s, hw + 9 * s, 0, 180, 24) + [(x - hw - 9 * s, base)]
    d.add(poly(outer, stone, stroke=darken(stone, 0.3), sw=1.5))
    inner = [(x + hw, base)] + arc_points(x, base + rh, hw, hw, 0, 180, 24) + [(x - hw, base)]
    if glow:
        d.add(circle(x, base + rh * 0.8, hw * 2.1, "#FFF3B0", 0.18))
        d.add(poly(inner, "#FFF3B0"))
        d.add(circle(x, base + rh * 0.7, hw * 0.6, "#FFFFFF", 0.55))
        leaf = [(x - hw, base), (x - hw * 0.4, base + 5 * s), (x - hw * 0.4, base + rh - 2 * s), (x - hw, base + rh + 3 * s)]
        d.add(poly(leaf, wood, stroke=darken(wood, 0.3), sw=1.2))
    else:
        d.add(poly(inner, wood, stroke=darken(wood, 0.3), sw=1.2))
        for dx in (-0.5, 0, 0.5):
            top = base + rh + math.sqrt(max(hw * hw - (dx * hw) ** 2, 0)) - 3 * s
            d.add(line(x + dx * hw, base + 2 * s, x + dx * hw, top, darken(wood, 0.3), 1.4))
        d.add(circle(x + 0.58 * hw, base + 0.5 * rh, 4.5 * s, "#E8C15A", stroke="#9C7A2A", sw=1))
    for k in range(5):
        a = 20 + k * 35
        px = x + (hw + 10 * s) * math.cos(math.radians(a))
        py = base + rh + (hw + 10 * s) * math.sin(math.radians(a))
        d.add(circle(px, py, 6 * s, ctx.pal["leaf"], stroke=darken(ctx.pal["leaf"], 0.3), sw=0.8))


def _wall(d, ctx):
    w, u, rng = ctx.w, ctx.u, ctx.rng
    base = ctx.top - 6 * u
    top_y = ctx.top + 205 * u
    color = ctx.pal["wall"]
    brick = darken(color, 0.18)
    d.add(rect(0, base, w, top_y - base, color))
    row_h = 22 * u
    rows = int((top_y - base) / row_h)
    for row in range(rows + 1):
        y = base + row * row_h
        d.add(line(0, y, w, y, brick, 1.2 * u, 0.5))
        x = (row % 2) * 20 * u
        while x < w:
            d.add(line(x, y, x, min(y + row_h, top_y), brick, 1.2 * u, 0.5))
            x += 40 * u
    d.add(rect(0, top_y, w, 12 * u, darken(color, 0.22)))
    for _ in range(34):
        x = rng.uniform(0, w)
        y = rng.uniform(top_y - 70 * u, top_y + 8 * u)
        shade = ctx.pal["leaf"] if rng.random() < 0.6 else ctx.pal["leaf_dark"]
        d.add(circle(x, y, rng.uniform(6, 12) * u, shade))
    for _ in range(10):
        x = rng.uniform(0, w)
        d.add(circle(x, top_y + 10 * u, rng.uniform(8, 14) * u, ctx.pal["leaf_dark"]))
    _door(d, ctx.focal_x, base, 1.25 * ctx.u, ctx, ctx.time == "magic")


def _garden(d, ctx):
    w, u, rng = ctx.w, ctx.u, ctx.rng
    for i in range(-1, 12):
        d.add(circle(w * i / 9 + rng.uniform(-10, 10) * u, ctx.top + 36 * u, rng.uniform(42, 54) * u, ctx.pal["leaf_dark"]))
    for i in range(-1, 14):
        d.add(circle(w * i / 11 + rng.uniform(-10, 10) * u, ctx.top + 18 * u, rng.uniform(30, 40) * u, ctx.pal["leaf"]))
    for _ in range(46):
        d.add(circle(rng.uniform(0, w), ctx.top + rng.uniform(10, 82) * u, rng.uniform(2.5, 4.5) * u, rng.choice(FLOWER_COLORS)))
    fx = ctx.focal_x
    base = ctx.top - 2 * u
    post_h = 118 * u
    arch_r = 62 * u
    for side in (-1, 1):
        d.add(line(fx + side * arch_r, base, fx + side * arch_r, base + post_h, "#F4EBD8", 6 * u))
    arch = arc_points(fx, base + post_h, arch_r, arch_r * 0.9, 0, 180, 30)
    d.add(pline(arch, "#F4EBD8", 6 * u))
    for k, (px, py) in enumerate(arc_points(fx, base + post_h, arch_r, arch_r * 0.9, 0, 180, 12)):
        d.add(circle(px, py, 8 * u, ctx.pal["leaf"]))
        d.add(circle(px, py + 2 * u, 5 * u, FLOWER_COLORS[k % len(FLOWER_COLORS)], stroke="#FFFFFF", sw=0.6))


def _glade(d, ctx):
    u, rng = ctx.u, ctx.rng
    fx = ctx.focal_x
    cy = ctx.top + 150 * u
    for r, color, opacity in ((210, "#FFF0A8", 0.10), (156, "#FFD6F0", 0.13), (104, "#C9F0FF", 0.16)):
        d.add(circle(fx, cy, r * u, color, opacity))
    d.add(poly([(fx - 26 * u, ctx.top - 6 * u), (fx + 26 * u, ctx.top - 6 * u), (fx + 11 * u, ctx.top + 110 * u), (fx - 11 * u, ctx.top + 110 * u)], ctx.pal["trunk"], stroke=darken(ctx.pal["trunk"], 0.3), sw=1.2))
    canopy = []
    for _ in range(11):
        canopy.append((fx + rng.uniform(-85, 85) * u, cy + rng.uniform(-30, 45) * u, rng.uniform(34, 56) * u))
    canopy.append((fx, cy + 10 * u, 60 * u))
    for x, y, r in canopy:
        d.add(circle(x, y, r, ctx.pal["leaf"] if rng.random() < 0.55 else ctx.pal["leaf_dark"]))
    for _ in range(46):
        x = fx + rng.uniform(-110, 110) * u
        y = cy + rng.uniform(-60, 70) * u
        d.add(circle(x, y, rng.uniform(2.5, 5) * u, rng.choice(["#FFB6D5", "#FFE27A", "#FFFFFF"])))
    for _ in range(14):
        d.add(sparkle(fx + rng.uniform(-130, 130) * u, cy + rng.uniform(-80, 100) * u, rng.uniform(4, 8) * u, "#FFF6B0", 0.95))


def _path(d, ctx):
    w, u = ctx.w, ctx.u
    target = ctx.focal_x if ctx.setting in FOCAL_SETTINGS else w * 0.5
    bottom = (target + w * 0.5) / 2
    mid = (target + bottom) / 2 + 14 * u
    points = [
        (bottom - 70 * u, 0),
        (bottom + 70 * u, 0),
        (mid + 36 * u, ctx.top * 0.55),
        (target + 24 * u, ctx.top + 2 * u),
        (target - 24 * u, ctx.top + 2 * u),
        (mid - 36 * u, ctx.top * 0.55),
    ]
    d.add(poly(points, ctx.pal["path"], 0.9))


def _ground(d, ctx):
    w, u = ctx.w, ctx.u
    points = [(0, 0)]
    for i in range(41):
        points.append((w * i / 40, ctx.top + 3 * u * math.sin(i * 0.8)))
    points.append((w, 0))
    d.add(poly(points, ctx.pal["grass"]))
    shade = [(0, 0)]
    for i in range(41):
        shade.append((w * i / 40, 40 * u + 5 * u * math.sin(i * 0.5 + 1)))
    shade.append((w, 0))
    d.add(poly(shade, ctx.pal["grass_dark"], 0.5))


def _flower(d, x, y, size, color, stem):
    d.add(line(x, y, x, y + size * 1.3, stem, max(size * 0.14, 1.2)))
    cy = y + size * 1.3
    for k in range(5):
        a = math.radians(90 + k * 72)
        d.add(circle(x + size * 0.5 * math.cos(a), cy + size * 0.5 * math.sin(a), size * 0.4, color, stroke=darken(color, 0.2), sw=0.5))
    d.add(circle(x, cy, size * 0.32, "#FFD23F" if color != "#FFD23F" else "#FF9A4D"))


def _mushroom(d, x, y, size):
    d.add(rect(x - 0.18 * size, y, 0.36 * size, 0.7 * size, "#F7EFE0", stroke="#CDBFA8", sw=0.8, rx=2))
    cap = arc_points(x, y + 0.65 * size, 0.62 * size, 0.55 * size, 0, 180, 14)
    d.add(poly(cap, "#E5483F", stroke="#A92B25", sw=1))
    for dx, dy, r in ((-0.25, 0.95, 0.1), (0.15, 1.05, 0.12), (0.32, 0.82, 0.08)):
        d.add(circle(x + dx * size, y + dy * size, r * size, "#FFFFFF"))


def _butterfly(d, x, y, s, color):
    for side in (-1, 1):
        d.add(ellipse(x + side * 7 * s, y + 4 * s, 7 * s, 9 * s, color, 0.95, stroke=darken(color, 0.3), sw=0.8))
        d.add(ellipse(x + side * 5 * s, y - 5 * s, 5 * s, 6 * s, lighten(color, 0.25), 0.95, stroke=darken(color, 0.3), sw=0.8))
    d.add(line(x, y - 8 * s, x, y + 9 * s, "#3A2A3A", 2 * s))
    d.add(line(x, y + 9 * s, x - 3 * s, y + 15 * s, "#3A2A3A", 0.9))
    d.add(line(x, y + 9 * s, x + 3 * s, y + 15 * s, "#3A2A3A", 0.9))


def _fountain(d, ctx, x):
    u = ctx.u
    base = ctx.top - 2 * u
    stone = "#CFC8BE" if ctx.time != "night" else "#8A8FA6"
    water = "#8FD3F4"
    d.add(ellipse(x, base + 6 * u, 74 * u, 17 * u, darken(stone, 0.12)))
    d.add(rect(x - 74 * u, base + 6 * u, 148 * u, 16 * u, stone))
    d.add(ellipse(x, base + 22 * u, 74 * u, 17 * u, stone, stroke=darken(stone, 0.2), sw=1))
    d.add(ellipse(x, base + 22 * u, 62 * u, 12 * u, water))
    d.add(rect(x - 8 * u, base + 22 * u, 16 * u, 60 * u, stone, stroke=darken(stone, 0.2), sw=1))
    d.add(ellipse(x, base + 82 * u, 34 * u, 9 * u, stone, stroke=darken(stone, 0.2), sw=1))
    d.add(ellipse(x, base + 83 * u, 28 * u, 6 * u, water))
    for side in (-1, 1):
        arc = arc_points(x, base + 88 * u, 24 * u, 22 * u, 90 - side * 90 + (0 if side > 0 else 0), 90 - side * 8, 8)
        d.add(pline(arc, "#BFE8FF", 3 * u, 0.8))
    d.add(pline([(x, base + 84 * u), (x, base + 112 * u)], "#BFE8FF", 3.5 * u, 0.85))
    d.add(circle(x, base + 116 * u, 5 * u, "#DFF4FF"))


def _draw_back_elements(d, ctx, elements):
    u, rng = ctx.u, ctx.rng
    avoid = ctx.focal_x if ctx.setting in FOCAL_SETTINGS else None
    if "vines" in elements:
        for _ in range(5):
            x = rng.uniform(0.05 * ctx.w, 0.95 * ctx.w)
            length = rng.uniform(70, 140) * u
            points = []
            y = ctx.h
            k = 0
            while y > ctx.h - length:
                points.append((x + 6 * u * math.sin(k * 0.9), y))
                if k % 2 == 0:
                    d.add(circle(x + 6 * u * math.sin(k * 0.9) + 5 * u, y, 5 * u, ctx.pal["leaf"]))
                y -= 12 * u
                k += 1
            d.add(pline(points, ctx.pal["leaf_dark"], 2.6 * u))
    if "lanterns" in elements:
        for _ in range(4):
            x = rng.uniform(0.08 * ctx.w, 0.92 * ctx.w)
            y = rng.uniform(ctx.h * 0.64, ctx.h * 0.84)
            d.add(line(x, ctx.h, x, y + 22 * u, "#5A4A3A", 1.4 * u))
            d.add(circle(x, y, 30 * u, "#FFD37A", 0.22))
            d.add(rect(x - 9 * u, y - 12 * u, 18 * u, 24 * u, "#FFB454", stroke="#5A4A3A", sw=1.4, rx=4 * u))
            d.add(circle(x, y, 4 * u, "#FFF3C4"))
    if "trees" in elements:
        for _ in range(2):
            x = ctx.pick_x(110 * u, avoid)
            _tree(d, x, ctx.top + rng.uniform(-10, 14) * u, rng.uniform(190, 250) * u, ctx.pal["leaf"], ctx.pal["trunk"])
    if "bushes" in elements:
        for _ in range(4):
            x = ctx.pick_x(70 * u, avoid)
            y = ctx.top + rng.uniform(-6, 10) * u
            for dx, dy, r in ((-14, 0, 17), (12, 2, 19), (0, 12, 18)):
                d.add(circle(x + dx * u, y + dy * u, r * u, ctx.pal["leaf_dark"] if dx else ctx.pal["leaf"]))
            for _ in range(4):
                d.add(circle(x + rng.uniform(-20, 20) * u, y + rng.uniform(0, 22) * u, 2.4 * u, "#E5483F"))
    if "door" in elements and ctx.setting != "wall":
        x = ctx.pick_x(120 * u, avoid, low=0.12, high=0.88)
        _door(d, x, ctx.top - 2 * u, 0.9 * u, ctx, ctx.time == "magic")
    if "fountain" in elements:
        _fountain(d, ctx, ctx.pick_x(130 * u, avoid, low=0.14, high=0.86))
    if "flowers" in elements:
        for _ in range(8):
            x = ctx.pick_x(30 * u)
            _flower(d, x, ctx.top + rng.uniform(-2, 24) * u, rng.uniform(7, 10) * u, rng.choice(FLOWER_COLORS), ctx.pal["leaf_dark"])


def _draw_front_elements(d, ctx, elements):
    u, rng = ctx.u, ctx.rng
    if "flowers" in elements:
        for _ in range(14):
            x = ctx.pick_x(46 * u)
            _flower(d, x, rng.uniform(6, 56) * u, rng.uniform(8, 13) * u, rng.choice(FLOWER_COLORS), ctx.pal["leaf_dark"])
    if "mushrooms" in elements:
        for _ in range(4):
            x = ctx.pick_x(55 * u)
            _mushroom(d, x, rng.uniform(8, 50) * u, rng.uniform(16, 26) * u)
    if "butterflies" in elements:
        for color in rng.sample(["#FF7BAC", "#B48CFF", "#FFB454", "#6EC8FF", "#FFD23F"], 4):
            x = ctx.pick_x(50 * u)
            _butterfly(d, x, rng.uniform(ctx.top + 70 * u, ctx.h - 60 * u), rng.uniform(0.9, 1.3) * u, color)
    if "fireflies" in elements:
        for _ in range(18):
            x = rng.uniform(0.03 * ctx.w, 0.97 * ctx.w)
            y = rng.uniform(ctx.top + 10 * u, ctx.h - 40 * u)
            d.add(circle(x, y, 7 * u, "#FFF29A", 0.25))
            d.add(circle(x, y, 2.4 * u, "#FFF8C4"))
    magic_sparkles = "sparkles" in elements or ctx.time == "magic"
    if magic_sparkles:
        for _ in range(12):
            d.add(sparkle(rng.uniform(0.04 * ctx.w, 0.96 * ctx.w), rng.uniform(ctx.top + 20 * u, ctx.h - 24 * u), rng.uniform(5, 10) * u, "#FFF3B0", 0.95))
    for _ in range(16):
        x = rng.uniform(0, ctx.w)
        y = rng.uniform(2, 30) * u
        blade = ctx.pal["grass_dark"]
        s = rng.uniform(8, 14) * u
        d.add(poly([(x - s * 0.5, y), (x - s * 0.3, y + s), (x - s * 0.05, y)], blade))
        d.add(poly([(x - s * 0.15, y), (x + s * 0.05, y + s * 1.3), (x + s * 0.3, y)], blade))
        d.add(poly([(x + s * 0.15, y), (x + s * 0.4, y + s), (x + s * 0.55, y)], blade))


def compose_scene(spec, character, w, h, seed=0, hero_scale=1.0):
    d = Drawing(w, h)
    ctx = Ctx(w, h, spec, seed)
    elements = []
    for name in spec.elements:
        if name in ELEMENTS and name not in elements:
            elements.append(name)

    _sky(d, ctx)
    _sky_objects(d, ctx, elements)
    if "rainbow" in elements:
        _rainbow(d, ctx)
    _hills(d, ctx)
    if ctx.setting == "forest":
        _forest(d, ctx)
    elif ctx.setting == "wall":
        _wall(d, ctx)
    elif ctx.setting == "garden":
        _garden(d, ctx)
    elif ctx.setting == "glade":
        _glade(d, ctx)
    _ground(d, ctx)
    _path(d, ctx)
    _draw_back_elements(d, ctx, elements)

    target = ctx.focal_x if ctx.setting in FOCAL_SETTINGS else w * 0.5
    d.add(
        draw_hero(
            character,
            spec.hero_pose,
            spec.expression,
            ctx.hero_px,
            ctx.gy,
            scale=1.15 * ctx.u * hero_scale,
            flip=ctx.hero_px > target,
        )
    )
    _draw_front_elements(d, ctx, elements)
    return d
