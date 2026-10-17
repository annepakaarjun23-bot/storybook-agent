from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from app.services.illustrator import build_all_drawings
from app.services.layout import (
    ILL_H,
    ILL_W,
    ILL_X,
    ILL_Y,
    MARGIN,
    PAGE_H,
    PAGE_W,
    TEXT_BOTTOM,
    TEXT_TOP,
)

PAPER = "#FFF8EC"
INK = "#4A3B2F"
FRAME = "#E3C99A"
ACCENT = "#C9822B"


def clean_text(value):
    return str(value).replace("\u2011", "-").encode("cp1252", "ignore").decode("cp1252").strip()


def _fit_lines(text, font, max_width, start_size, min_size, max_height, leading=1.35):
    size = start_size
    while True:
        lines = simpleSplit(text, font, size, max_width)
        if len(lines) * size * leading <= max_height or size <= min_size:
            return lines, size
        size -= 1


def _draw_cover(c, drawing, title, hero_name):
    renderPDF.draw(drawing, c, 0, 0)
    title = clean_text(title)
    max_width = PAGE_W - 220
    size = 50
    while True:
        lines = simpleSplit(title, "Times-Bold", size, max_width)
        if len(lines) <= 2 or size <= 28:
            break
        size -= 2
    subtitle = clean_text(f"A story about {hero_name}")
    line_h = size * 1.15
    banner_h = 36 + len(lines) * line_h + 34
    banner_w = PAGE_W - 140
    banner_x = (PAGE_W - banner_w) / 2
    banner_y = PAGE_H - 36 - banner_h

    c.saveState()
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFillAlpha(0.88)
    c.roundRect(banner_x, banner_y, banner_w, banner_h, 22, stroke=0, fill=1)
    c.restoreState()
    c.setStrokeColor(HexColor(FRAME))
    c.setLineWidth(3)
    c.roundRect(banner_x, banner_y, banner_w, banner_h, 22, stroke=1, fill=0)

    c.setFillColor(HexColor(INK))
    c.setFont("Times-Bold", size)
    y = banner_y + banner_h - 24 - size * 0.85
    for line in lines:
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= line_h
    c.setFillColor(HexColor(ACCENT))
    c.setFont("Times-Italic", 20)
    c.drawCentredString(PAGE_W / 2, banner_y + 20, subtitle)
    c.showPage()


def _draw_story_page(c, drawing, text, number, total):
    c.setFillColor(HexColor(PAPER))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    c.saveState()
    clip = c.beginPath()
    clip.roundRect(ILL_X, ILL_Y, ILL_W, ILL_H, 16)
    c.clipPath(clip, stroke=0, fill=0)
    renderPDF.draw(drawing, c, ILL_X, ILL_Y)
    c.restoreState()

    c.setStrokeColor(HexColor(FRAME))
    c.setLineWidth(3.5)
    c.roundRect(ILL_X, ILL_Y, ILL_W, ILL_H, 16, stroke=1, fill=0)

    text = clean_text(text)
    area_h = TEXT_TOP - TEXT_BOTTOM
    lines, size = _fit_lines(text, "Times-Roman", ILL_W - 40, 23, 12, area_h)
    leading = size * 1.35
    block_h = len(lines) * leading
    y = TEXT_TOP - (area_h - block_h) / 2 - size
    c.setFillColor(HexColor(INK))
    c.setFont("Times-Roman", size)
    for line in lines:
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= leading

    footer_y = 34
    c.setFillColor(HexColor(FRAME))
    c.circle(PAGE_W / 2 - 22, footer_y + 4, 2.5, stroke=0, fill=1)
    c.circle(PAGE_W / 2 + 22, footer_y + 4, 2.5, stroke=0, fill=1)
    c.setFillColor(HexColor(ACCENT))
    c.setFont("Times-Bold", 13)
    c.drawCentredString(PAGE_W / 2, footer_y, str(number))
    if number == total:
        c.setFont("Times-BoldItalic", 15)
        c.drawRightString(PAGE_W - MARGIN, footer_y, "The End")
    c.showPage()


def build_pdf(title, character, scenes, output_path, drawings=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if drawings is None:
        drawings = build_all_drawings(character, scenes)
    c = canvas.Canvas(str(output_path), pagesize=(PAGE_W, PAGE_H))
    c.setTitle(clean_text(title))
    c.setAuthor("Storybook Agent")
    c.setSubject("Illustrated children's picture book")
    _draw_cover(c, drawings[0], title, character.name)
    total = len(scenes)
    for index, scene in enumerate(scenes, start=1):
        _draw_story_page(c, drawings[index], scene.text, index, total)
    c.save()
    return str(output_path)
