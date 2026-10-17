from reportlab.lib.pagesizes import A4, landscape

PAGE_W, PAGE_H = landscape(A4)
MARGIN = 36
ILL_W = PAGE_W - 2 * MARGIN
ILL_H = 372
ILL_X = MARGIN
ILL_Y = PAGE_H - MARGIN - ILL_H
TEXT_TOP = ILL_Y - 24
TEXT_BOTTOM = 62
