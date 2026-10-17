import math

from reportlab.graphics.shapes import Group

from app.art.primitives import (
    arc_points,
    circle,
    darken,
    ellipse,
    line,
    lighten,
    pline,
    poly,
    rect,
)
from app.art.vocab import HAIR_COLORS, OUTFIT_COLORS, SKIN_TONES

INK = "#2B2024"
MOUTH = "#7A2E2E"
BROW = "#4A3328"
CHEEK = "#F28DA0"

POSE_TABLE = {
    "standing": {"lh": (-33, 72), "rh": (33, 72), "lf": (-11, 6), "rf": (11, 6), "lift": 0},
    "walking": {"lh": (-25, 80), "rh": (31, 86), "lf": (-19, 6), "rf": (20, 13), "lift": 0},
    "reaching": {"lh": (-31, 74), "rh": (58, 132), "lf": (-11, 6), "rf": (13, 6), "lift": 0},
    "wonder": {"lh": (-43, 132), "rh": (43, 132), "lf": (-12, 6), "rf": (12, 6), "lift": 0},
    "jumping": {"lh": (-47, 150), "rh": (47, 150), "lf": (-23, 10), "rf": (23, 10), "lift": 18},
    "pointing": {"lh": (-31, 72), "rh": (66, 114), "lf": (-11, 6), "rf": (11, 6), "lift": 0},
    "waving": {"lh": (-31, 72), "rh": (47, 148), "lf": (-11, 6), "rf": (11, 6), "lift": 0},
}

SHOULDER_Y = 106
SHOULDER_X = 16
HEAD_Y = 138
HEAD_R = 28


def resolve_colors(character):
    return {
        "skin": SKIN_TONES.get(character.skin_tone, SKIN_TONES["tan"]),
        "hair": HAIR_COLORS.get(character.hair_color, HAIR_COLORS["brown"]),
        "outfit": OUTFIT_COLORS.get(character.outfit_color, OUTFIT_COLORS["red"]),
        "accent": OUTFIT_COLORS.get(character.accent_color, OUTFIT_COLORS["yellow"]),
    }


def _back_items(g, character, colors):
    item = character.signature_item
    if item == "cape":
        g.add(
            poly(
                [(-16, 110), (16, 110), (44, 36), (-44, 36)],
                colors["accent"],
                stroke=darken(colors["accent"], 0.25),
                sw=1.2,
            )
        )
    elif item == "backpack":
        pack = "#8A5A36"
        g.add(rect(-27, 62, 54, 48, pack, stroke=darken(pack, 0.3), sw=1.5, rx=10))
        g.add(rect(-15, 66, 30, 17, lighten(pack, 0.15), stroke=darken(pack, 0.3), sw=1.2, rx=4))


def _back_hair(g, character, colors):
    hair = colors["hair"]
    style = character.hair_style
    edge = darken(hair, 0.25)
    if style == "pigtails":
        g.add(circle(0, 140, 31, hair))
        for side in (-1, 1):
            g.add(line(side * 26, 132, side * 36, 118, hair, 12))
            g.add(circle(side * 37, 112, 11, hair, stroke=edge, sw=1))
            g.add(ellipse(side * 31, 124, 5, 3.5, colors["accent"], stroke=darken(colors["accent"], 0.3), sw=1))
    elif style == "bun":
        g.add(circle(0, 140, 31, hair))
        g.add(circle(0, 172, 14, hair, stroke=edge, sw=1))
        g.add(ellipse(0, 162, 11, 3.5, colors["accent"], stroke=darken(colors["accent"], 0.3), sw=1))
    elif style == "ponytail":
        g.add(circle(0, 140, 31, hair))
        g.add(ellipse(-37, 118, 10, 22, hair, stroke=edge, sw=1))
        g.add(ellipse(-31, 136, 4, 6, colors["accent"], stroke=darken(colors["accent"], 0.3), sw=1))
    elif style == "curly":
        g.add(circle(0, 140, 30, hair))
        for angle in range(0, 360, 36):
            rad = math.radians(angle)
            g.add(circle(31 * math.cos(rad), 140 + 31 * math.sin(rad), 11, hair, stroke=edge, sw=1))
    else:
        g.add(circle(0, 140, 31, hair))


def _fringe(g, colors):
    hair = colors["hair"]
    edge = darken(hair, 0.25)
    points = [(29, 136)]
    points += arc_points(0, 139, 29.5, 29.5, 5, 175, 14)
    points += [
        (-29, 136),
        (-26, 147),
        (-19, 153),
        (-11, 149),
        (-3, 154),
        (6, 149),
        (14, 154),
        (22, 148),
    ]
    g.add(poly(points, hair, stroke=edge, sw=1))


def _legs(g, character, colors, pose):
    skin = colors["skin"]
    shoe = darken(colors["accent"], 0.35)
    for side, foot in ((-1, pose["lf"]), (1, pose["rf"])):
        hip_x = side * 9
        if character.outfit == "tunic":
            g.add(line(hip_x, 66, foot[0], foot[1] + 6, colors["accent"], 12))
        else:
            g.add(line(hip_x, 60, foot[0], foot[1] + 6, skin, 10))
        g.add(ellipse(foot[0] + side * 1.5, foot[1], 11, 6, shoe, stroke=darken(shoe, 0.3), sw=1))


def _body(g, character, colors):
    outfit = colors["outfit"]
    accent = colors["accent"]
    edge = darken(outfit, 0.28)
    g.add(rect(-6, 106, 12, 12, colors["skin"]))
    if character.outfit == "tunic":
        g.add(poly([(-16, 112), (16, 112), (22, 66), (-22, 66)], outfit, stroke=edge, sw=1.2))
        g.add(poly([(-20.5, 74), (20.5, 74), (21.3, 68), (-21.3, 68)], accent))
        g.add(rect(-4, 68, 8, 6, darken(accent, 0.3), rx=1.5))
    else:
        g.add(poly([(-16, 112), (16, 112), (32.86, 53), (-32.86, 53)], outfit, stroke=edge, sw=1.2))
        g.add(poly([(-30.86, 60), (30.86, 60), (32.86, 53), (-32.86, 53)], accent))
        for x in (-18, -6, 6, 18):
            g.add(circle(x, 80 - abs(x) * 0.15, 2.6, lighten(outfit, 0.45)))


def _arms(g, colors, pose):
    outfit = colors["outfit"]
    skin = colors["skin"]
    for side, hand in ((-1, pose["lh"]), (1, pose["rh"])):
        sx, sy = side * SHOULDER_X, SHOULDER_Y
        hx, hy = hand
        mx = sx + (hx - sx) * 0.4
        my = sy + (hy - sy) * 0.4
        g.add(line(sx, sy, hx, hy, skin, 8))
        g.add(line(sx, sy, mx, my, outfit, 11))
        g.add(circle(hx, hy, 5.5, skin))


def _scarf(g, colors):
    accent = colors["accent"]
    edge = darken(accent, 0.3)
    g.add(poly([(-18, 114), (18, 114), (19, 104), (-19, 104)], accent, stroke=edge, sw=1.2))
    g.add(poly([(6, 106), (19, 104), (27, 80), (14, 79)], accent, stroke=edge, sw=1.2))
    g.add(line(11, 98, 22, 96, lighten(accent, 0.5), 2.5))
    g.add(line(13, 90, 24, 88, lighten(accent, 0.5), 2.5))


def _face(g, expression, colors):
    skin = colors["skin"]
    g.add(circle(-HEAD_R, 136, 5, skin, stroke=darken(skin, 0.15), sw=0.8))
    g.add(circle(HEAD_R, 136, 5, skin, stroke=darken(skin, 0.15), sw=0.8))
    g.add(circle(0, HEAD_Y, HEAD_R, skin, stroke=darken(skin, 0.18), sw=1.2))
    g.add(circle(-17, 127, 5.2, CHEEK, opacity=0.5))
    g.add(circle(17, 127, 5.2, CHEEK, opacity=0.5))

    eye_y = 135
    if expression == "joyful":
        for side in (-1, 1):
            g.add(pline(arc_points(side * 10, eye_y - 1, 5, 4.5, 20, 160, 8), INK, 2.4))
    else:
        rx, ry = (4.2, 5.6) if expression == "surprised" else (3.5, 4.8)
        for side in (-1, 1):
            g.add(ellipse(side * 10, eye_y, rx, ry, INK))
            g.add(circle(side * 10 + 1.2, eye_y + 1.8, 1.3, "#FFFFFF"))

    if expression == "surprised":
        g.add(pline([(-15, 146), (-10, 149), (-5, 146)], BROW, 2))
        g.add(pline([(5, 146), (10, 149), (15, 146)], BROW, 2))
        g.add(ellipse(0, 123, 4, 5.5, MOUTH))
    elif expression == "curious":
        g.add(pline([(-15, 145), (-10, 149), (-5, 148)], BROW, 2))
        g.add(pline([(5, 144), (10, 145), (15, 144)], BROW, 2))
        g.add(pline(arc_points(3, 128, 5, 4, 215, 325, 8), MOUTH, 2))
    elif expression == "determined":
        g.add(pline([(-16, 148), (-5, 144)], BROW, 2.4))
        g.add(pline([(5, 144), (16, 148)], BROW, 2.4))
        g.add(pline([(-6, 124.5), (-3, 123), (3, 123), (6, 124.5)], MOUTH, 2))
    elif expression == "joyful":
        g.add(pline([(-15, 145), (-10, 148), (-5, 145)], BROW, 2))
        g.add(pline([(5, 145), (10, 148), (15, 145)], BROW, 2))
        mouth = arc_points(0, 127, 8, 8, 180, 360, 12)
        g.add(poly(mouth, "#8E2F3A", stroke=MOUTH, sw=1))
        g.add(ellipse(0, 121.5, 4, 2.2, "#F59AA8"))
    else:
        g.add(pline([(-15, 144), (-10, 146.5), (-5, 144)], BROW, 2))
        g.add(pline([(5, 144), (10, 146.5), (15, 144)], BROW, 2))
        g.add(pline(arc_points(0, 129, 8, 6, 205, 335, 10), MOUTH, 2.2))


def _front_items(g, character, colors, pose):
    item = character.signature_item
    accent = colors["accent"]
    if item == "hat":
        straw = "#E3B55C"
        g.add(ellipse(0, 158, 44, 9, straw, stroke=darken(straw, 0.3), sw=1.2))
        dome = arc_points(0, 159, 27, 23, 0, 180, 16)
        g.add(poly(dome, lighten(straw, 0.15), stroke=darken(straw, 0.3), sw=1.2))
        g.add(poly([(-26.5, 160), (26.5, 160), (25, 168), (-25, 168)], accent))
    elif item == "flower_crown":
        palette = [accent, "#FFD76A", "#FF9EC4", "#FFFFFF", accent]
        for index, angle in enumerate((25, 55, 90, 125, 155)):
            rad = math.radians(angle)
            x = 30 * math.cos(rad)
            y = 139 + 30 * math.sin(rad)
            g.add(circle(x, y, 6, palette[index], stroke=darken(palette[index], 0.25), sw=0.8))
            g.add(circle(x, y, 2.2, "#FFF1B5" if palette[index] != "#FFD76A" else "#F08A32"))
    elif item == "lantern":
        hx, hy = pose["rh"]
        metal = "#5A4A3A"
        g.add(circle(hx, hy - 24, 24, "#FFE9A0", opacity=0.35))
        g.add(line(hx, hy - 2, hx, hy - 14, metal, 1.8))
        g.add(poly([(hx - 8, hy - 14), (hx + 8, hy - 14), (hx, hy - 20)], metal))
        g.add(rect(hx - 7, hy - 36, 14, 17, "#FFD76A", stroke=metal, sw=1.6, rx=2))
        g.add(rect(hx - 8, hy - 38, 16, 3, metal, rx=1))
        g.add(circle(hx, hy - 27, 3, "#FFF6D0"))
    elif item == "backpack":
        strap = darken("#8A5A36", 0.1)
        g.add(line(-10, 111, -13, 70, strap, 4))
        g.add(line(10, 111, 13, 70, strap, 4))


def draw_hero(character, pose_name, expression, cx, ground_y, scale=1.0, flip=False):
    colors = resolve_colors(character)
    pose = POSE_TABLE.get(pose_name, POSE_TABLE["standing"])

    outer = Group()
    outer.add(ellipse(0, 0, 32, 6, "#000000", opacity=0.16))

    inner = Group()
    _back_items(inner, character, colors)
    _back_hair(inner, character, colors)
    _legs(inner, character, colors, pose)
    _body(inner, character, colors)
    _arms(inner, colors, pose)
    if character.signature_item == "scarf":
        _scarf(inner, colors)
    if character.signature_item == "backpack":
        _front_items(inner, character, colors, pose)
    _face(inner, expression, colors)
    _fringe(inner, colors)
    if character.signature_item in ("hat", "flower_crown", "lantern"):
        _front_items(inner, character, colors, pose)
    inner.translate(0, pose["lift"])

    outer.add(inner)
    outer.translate(cx, ground_y)
    outer.scale(-scale if flip else scale, scale)
    return outer
