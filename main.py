#!/usr/bin/env python3
"""news-image-20261123: draw a 1024x1024 newspaper front page as a PNG.

Pure Python 3.13 standard library only. No network, no clock, no
randomness. Running twice produces byte-identical output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- colours
CREAM = (250, 244, 230)
WHITE = (255, 255, 255)
INK = (18, 28, 52)          # dark ink navy, text and borders
NAVY = (24, 38, 74)         # masthead band
RED = (178, 34, 34)
TEAL = (0, 128, 128)
GOLD = (201, 162, 39)
BLUE = (36, 84, 160)
GREY = (110, 110, 110)
LIGHT_GREY = (200, 200, 200)
CREAM_TEXT = (250, 240, 210)
GOLD_TEXT = (232, 196, 96)

# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def rect(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in (cx - dx, cx + dx - t + 1):
                self.fill_rect(xx, cy + dy, t, 1, c)
        for dx in range(-r, r + 1):
            dy = int((r * r - dx * dx) ** 0.5)
            for yy in (cy - dy, cy + dy - t + 1):
                self.fill_rect(cx + dx, yy, 1, t, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        # Bresenham, square brush of size t.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

# ---------------------------------------------------------------- PNG writer
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

# --------------------------------------------------------------------- font
# Hand-designed 5x7 bitmap font. Each glyph is 7 rows of 5 cells.
# Capitals and digits occupy all 7 rows; lowercase letters sit at
# x-height (rows 2-6) with descenders reaching row 6.
# Glyph rules baked in here:
#   0 is a closed oval with a diagonal slash (never a U);
#   2 and 7 both start with a full flat top bar;
#   c is drawn only in rows 2-6, clearly shorter than capitals.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": ("#####", "....#", "....#", ".###.", "#....", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    "j": (".....", "...#.", ".....", "..##.", "...#.", "...#.", "...#."),
    "k": ("#....", "#....", "#.#..", "#.#..", "##...", "#.#..", "#.#.."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": ("..#..", "..#..", "####.", "..#..", "..#..", "..#..", "..#.."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": (".....", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".###.", "#...#", "#.#..", ".##..", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    ";": (".....", ".....", "..#..", ".....", ".....", ".##..", ".#..."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "..#.#", "####."),
}

GW = 5   # glyph cell width in font units
GH = 7   # glyph cell height in font units


def text_width(text, scale, bold=False, spacing=None):
    sp = scale if spacing is None else spacing
    adv = GW * scale + sp
    if bold:
        adv += scale
    return len(text) * adv - sp


def draw_text(cv, x, y, text, scale, color, bold=False, align="left",
              spacing=None):
    """Draw text with its top-left at (x, y) unless align is center/right."""
    sp = scale if spacing is None else spacing
    w = text_width(text, scale, bold, spacing)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += GW * scale + sp
            continue
        for gy in range(GH):
            row = glyph[gy]
            for gx in range(GW):
                if row[gx] == "#":
                    cv.fill_rect(cx + gx * scale, y + gy * scale,
                                 scale, scale, color)
                    if bold:
                        cv.fill_rect(cx + gx * scale + scale,
                                     y + gy * scale, scale, scale, color)
        cx += GW * scale + sp
        if bold:
            cx += scale
    return x, w


def wrap_text(text, scale, max_w, bold=False, spacing=None):
    """Greedy word wrap; returns a list of lines."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, bold, spacing) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ------------------------------------------------------------------- motifs
def draw_globe(cv, cx, cy, r, line_c, land_c):
    """Filled circle with ring, vertical + horizontal lines, two land blobs."""
    cv.disc(cx, cy, r, (226, 238, 250))
    cv.ring(cx, cy, r, line_c, 2)
    cv.ring(cx, cy, r + 3, line_c, 2)
    cv.vline(cx, cy - r, 2 * r + 1, line_c, 2)
    cv.hline(cx - r, cy, 2 * r + 1, line_c, 2)
    cv.disc(cx - r // 2, cy - r // 3, max(2, r // 4), land_c)
    cv.disc(cx + r // 3, cy + r // 3, max(2, r // 5), land_c)
    cv.disc(cx + r // 4, cy - r // 2, max(2, r // 6), land_c)
    for dx in (-r * 3 // 5, -r // 5, r * 2 // 5):
        cv.disc(cx + dx, cy, 2, land_c)


def draw_thermometer(cv, x, y, w, h):
    """White tube, ink outline, red fill low, solid red bulb at bottom."""
    tube_w = w // 3
    tx = x + (w - tube_w) // 2
    tube_h = h - w // 2 - 4
    cv.fill_rect(tx, y, tube_w, tube_h, WHITE)
    cv.rect(tx, y, tube_w, tube_h, INK, 2)
    # red fill rising in the lower part of the tube
    fill_h = tube_h * 2 // 5
    cv.fill_rect(tx + 2, y + tube_h - fill_h, tube_w - 4, fill_h - 2, RED)
    bulb_r = w // 2
    bx = x + w // 2
    by = y + tube_h + bulb_r - 2
    cv.disc(bx, by, bulb_r, RED)
    cv.ring(bx, by, bulb_r, INK, 2)
    # join tube to bulb
    cv.fill_rect(tx + 2, y + tube_h - 6, tube_w - 4, 8, RED)


def draw_waves(cv, x, y, w, c, t=3):
    """Two rows of wave humps."""
    for row in range(2):
        yy = y + row * 9
        for xx in range(x, x + w, 16):
            cv.hline(xx, yy + 3, 16, c, t)
            cv.fill_rect(xx, yy, 4, 4, c)
            cv.fill_rect(xx + 12, yy, 4, 4, c)


def draw_ship(cv, x, y, w, h):
    """Ship on waves with a red burst above it."""
    # hull
    hy = y + h - 26
    cv.fill_rect(x + 14, hy, w - 28, 14, INK)
    cv.fill_rect(x + 22, hy + 14, w - 44, 4, INK)
    # mast and sails
    mx = x + w // 2
    cv.vline(mx, hy - 26, 26, INK, 3)
    cv.fill_rect(mx + 3, hy - 26, 26, 22, TEAL)
    cv.fill_rect(mx - 22, hy - 20, 19, 16, BLUE)
    # small red pennant flag flying left from the mast top
    cv.fill_rect(mx - 8, hy - 26, 5, 3, RED)
    cv.fill_rect(mx - 14, hy - 23, 11, 3, RED)
    cv.fill_rect(mx - 8, hy - 20, 5, 3, RED)
    # red burst (star) to the left of the mast, drawn last so it stays
    # visible instead of being covered by the sails
    bx, by = x + 45, y + 10
    for dx, dy in ((0, -8), (0, 8), (-8, 0), (8, 0),
                   (-6, -6), (6, -6), (-6, 6), (6, 6)):
        cv.line(bx, by, bx + dx, by + dy, RED, 3)
    cv.disc(bx, by, 4, RED)
    draw_waves(cv, x, y + h - 14, w, TEAL)


def draw_tanker(cv, x, y, w, h):
    """Oil tanker on waves with a small flame above it."""
    # flame
    fx, fy = x + w // 2, y + 20
    cv.disc(fx, fy, 10, GOLD)
    cv.disc(fx, fy + 4, 6, RED)
    cv.fill_rect(fx - 3, fy - 16, 6, 10, GOLD)
    # wisp of smoke above the flame
    cv.disc(fx + 8, fy - 14, 3, GREY)
    cv.disc(fx + 12, fy - 20, 2, GREY)
    # hull and deck
    hy = y + h - 26
    cv.fill_rect(x + 10, hy, w - 20, 14, INK)
    cv.fill_rect(x + w - 34, hy - 16, 22, 16, INK)
    cv.fill_rect(x + 22, hy - 10, 12, 10, GOLD)
    cv.fill_rect(x + 40, hy - 10, 12, 10, GOLD)
    cv.fill_rect(x + 58, hy - 10, 12, 10, GOLD)
    draw_waves(cv, x, y + h - 14, w, TEAL)


def draw_badge(cv, cx, cy, r):
    """Gold disc with a ring and a small star inside."""
    cv.disc(cx, cy, r, GOLD)
    cv.ring(cx, cy, r, INK, 2)
    cv.ring(cx, cy, r - 6, INK, 2)
    # five-point star, drawn as short spokes from the centre
    sr = r * 2 // 5
    for dx, dy in ((0, -sr), (0, sr), (-sr, 0), (sr, 0),
                   (-sr * 2 // 3, -sr * 2 // 3), (sr * 2 // 3, -sr * 2 // 3),
                   (-sr * 2 // 3, sr * 2 // 3), (sr * 2 // 3, sr * 2 // 3)):
        cv.line(cx, cy, cx + dx, cy + dy, INK, 2)
    cv.disc(cx, cy, 4, INK)
    # second, smaller star below the main one
    sy = cy + r // 2 + 4
    for dx, dy in ((0, -3), (0, 3), (-3, 0), (3, 0),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        cv.line(cx, sy, cx + dx, sy + dy, INK, 2)
    cv.disc(cx, sy, 2, INK)


def draw_arrows(cv, x, y, w):
    """Two opposing horizontal arrows, teal and gold, teal bar below."""
    def tri_right(tx, ty, c):
        # right-pointing triangular head, 18 wide, 24 tall
        for i in range(9):
            cv.fill_rect(tx + i * 2, ty - 12 + i, 2, 24 - 2 * i, c)

    def tri_left(tx, ty, c):
        # left-pointing triangular head, 18 wide, 24 tall
        for i in range(9):
            cv.fill_rect(tx + i * 2, ty - 12 + (8 - i), 2, 24 - 2 * (8 - i), c)

    ay = y + 10
    cv.fill_rect(x + 8, ay - 4, w - 34, 8, TEAL)
    tri_right(x + w - 26, ay, TEAL)
    by = y + 28
    cv.fill_rect(x + 26, by - 4, w - 34, 8, GOLD)
    tri_left(x + 8, by, GOLD)
    # small gold bar above the teal bar
    cv.fill_rect(x + 8, y + 36, w - 16, 4, GOLD)
    cv.fill_rect(x + 8, y + 42, w - 16, 5, TEAL)


def draw_house(cv, x, y, w, h):
    """Small house: red roof, ink walls and door, gold star above."""
    cx = x + w // 2
    # gold star above the house
    sx, sy = cx, y + 4
    for dx, dy in ((0, -4), (0, 4), (-4, 0), (4, 0),
                   (-3, -3), (3, -3), (-3, 3), (3, 3)):
        cv.line(sx, sy, sx + dx, sy + dy, GOLD, 2)
    cv.disc(sx, sy, 2, GOLD)
    # chimney to the right of the roof peak
    cv.fill_rect(cx + 16, y + 10, 6, 10, INK)
    # walls
    wy = y + 22
    cv.fill_rect(cx - 26, wy, 52, 24, WHITE)
    cv.rect(cx - 26, wy, 52, 24, INK, 2)
    # pitched red roof: rows widening from the peak down to the eaves
    for i in range(7):
        cv.fill_rect(cx - 4 - i * 5, wy - 12 + i * 2, 8 + i * 10, 3, RED)
    cv.fill_rect(cx - 34, wy - 2, 68, 4, RED)
    # two small gold windows
    cv.fill_rect(cx - 20, wy + 6, 8, 8, GOLD)
    cv.fill_rect(cx + 12, wy + 6, 8, 8, GOLD)
    cv.rect(cx - 20, wy + 6, 8, 8, INK, 1)
    cv.rect(cx + 12, wy + 6, 8, 8, INK, 1)
    # door
    cv.fill_rect(cx - 7, wy + 8, 14, 16, INK)
    # ground
    cv.hline(x + 8, wy + 24, w - 16, INK, 2)


def draw_courthouse(cv, x, y, w, h):
    """Courthouse/jail front: triangular roof, three columns, gold door."""
    cx = x + w // 2
    # triangular roof: rows widening from the peak down to the eaves
    for i in range(7):
        cv.fill_rect(cx - 6 - i * 10, y + 4 + i * 2, 12 + i * 20, 3, INK)
    cv.fill_rect(cx - 76, y + 18, 152, 3, INK)
    # three vertical columns
    for col_x in (cx - 62, cx - 6, cx + 50):
        cv.fill_rect(col_x, y + 21, 12, 21, INK)
    # small gold door between the middle and right columns
    cv.fill_rect(cx + 12, y + 30, 16, 12, GOLD)
    cv.rect(cx + 12, y + 30, 16, 12, INK, 1)
    # base platform
    cv.fill_rect(cx - 76, y + 42, 152, 4, INK)

# --------------------------------------------------------------------- page
MARGIN = 16
LEFT = MARGIN
RIGHT = W - MARGIN
PAGE_W = RIGHT - LEFT


def draw_masthead(cv):
    y0, y1 = 16, 144
    cv.fill_rect(LEFT, y0, PAGE_W, y1 - y0, NAVY)
    cx = W // 2
    draw_text(cv, cx, y0 + 12, "WORLD NEWS IN ONE IMAGE", 2,
              CREAM_TEXT, align="center")
    draw_text(cv, cx, y0 + 34, "THE WORLD TODAY", 7, CREAM_TEXT,
              bold=True, align="center")
    draw_text(cv, cx, y0 + 104, "MONDAY 23 NOVEMBER 2026", 3,
              GOLD_TEXT, align="center")
    draw_globe(cv, RIGHT - 52, y0 + 64, 30, CREAM_TEXT, TEAL)


def draw_lead(cv):
    y0, y1 = 152, 372
    cv.fill_rect(LEFT, y0, PAGE_W, y1 - y0, WHITE)
    cv.rect(LEFT, y0, PAGE_W, y1 - y0, INK, 2)
    cv.fill_rect(LEFT, y0, 12, y1 - y0, RED)
    tx = LEFT + 32
    draw_text(cv, tx, y0 + 24, "CLIMATE - COP31, ANTALYA", 3, RED, bold=True)
    draw_text(cv, tx, y0 + 58, "COP31 COLLAPSES", 7, INK, bold=True)
    summary = ("UN climate talks in Antalya collapse after more than two "
               "weeks, the longest COP in history and the first failure "
               "since 2009.")
    lines = wrap_text(summary, 2, 760, spacing=1)
    yy = y0 + 118
    for ln in lines:
        draw_text(cv, tx, yy, ln, 2, INK, spacing=1)
        yy += 20
    # thin grey rule, then grey foot line
    ry = yy + 12
    cv.hline(tx, ry, 760, LIGHT_GREY, 2)
    draw_text(cv, tx, ry + 14, "LONGEST COP IN HISTORY - FIRST FAILURE SINCE 2009",
              2, GREY, bold=True)
    # motifs at the right side
    draw_globe(cv, RIGHT - 140, y0 + 78, 44, INK, TEAL)
    draw_thermometer(cv, RIGHT - 84, y0 + 26, 56, 150)


CARDS = [
    ("WAR IN EUROPE", "RUSSIAN WARSHIP SUNK IN LIBYA",
     "Ukrainian sea drones are suspected of sinking the corvette Merkury "
     "at Benghazi. Kyiv and Moscow have not commented.", BLUE, "ship"),
    ("MIDDLE EAST", "GULF CRISIS DEEPENS",
     "Trump dares Iran to test the Hormuz blockade; Bahrain seeks UN "
     "action after Saturday's attacks injured two.", RED, "tanker"),
    ("SCIENCE", "CLAUDE 'PROVES' RIEMANN",
     "Levent Alpoege says he and Claude proved it; Lean and Mathlib "
     "verified it. The Clay Institute still lists it open.", TEAL, "badge"),
    ("ECONOMY", "MARKETS REBOUND AFTER AI ROUT",
     "Nasdaq 100 futures rise nearly 3% after the worst loss in over six "
     "years; Korea's KOSPI falls 5%.", GOLD, "arrows"),
    ("WAR IN UKRAINE", "BOY, 7, PULLED ALIVE",
     "A drone strike on a home in Dimer kills nine. Rescuers save a boy, "
     "7, and a woman, 79, from the rubble.", INK, "house"),
    ("POLITICS", "MAMDANI TO CLOSE RIKERS",
     "New York's mayor unveils a plan to shut the Rikers Island jail "
     "complex.", RED, "courthouse"),
]

BRIEFS = [
    "NATO meets after missiles hit Poland",
    "Democrats win big House majority",
    "UK to host 2035 Women's World Cup",
    "6.5 quake in Vanuatu, 598 km deep",
    "Jeweller Paolo Bulgari dies at 89",
    "Lagarde to leave ECB in Feb 2027",
    "French students plan protests",
    "IG Metall calls 23,000 to walk out",
    "Bolsonaro in hospital, son says",
    "Congo rivals agree to restore ties",
    "Gold rebounds above $3,600",
    "Virginia's first measles death",
]


def tri_down(cv, x, y, c):
    """Small filled triangle pointing down, 9 wide, 10 tall."""
    for i in range(5):
        cv.fill_rect(x + i, y + i * 2, 9 - 2 * i, 2, c)


def tri_up(cv, x, y, c):
    """Small filled triangle pointing up, 9 wide, 10 tall."""
    for i in range(5):
        cv.fill_rect(x + i, y + (4 - i) * 2, 9 - 2 * i, 2, c)


MARKETS = [
    ("S&P 500", "6,910", "-3.7%", False),
    ("NASDAQ", "22,618", "-5.3%", False),
    ("DOW", "48,147", "-1.9%", False),
    ("NIKKEI", "56,437", "-5.1%", False),
    ("KOSPI", "4,587", "-5.8%", False),
    ("FTSE", "10,412", "+0.6%", True),
]


def draw_markets_strip(cv, x, y, w, h):
    """Narrow markets band: red MARKETS label, then six index entries.

    Each entry stacks its bold name above its value plus a small
    triangle and the coloured change, so every entry fits its slot.
    """
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    lw = 112
    cv.fill_rect(x, y, lw, h, RED)
    draw_text(cv, x + lw // 2, y + (h - 14) // 2, "MARKETS", 2, WHITE,
              bold=True, align="center")
    ex = x + lw + 8
    slot = (x + w - ex - 8) // 6
    for i, (name, value, change, up) in enumerate(MARKETS):
        sx = ex + i * slot
        draw_text(cv, sx, y + 5, name, 2, INK, bold=True, spacing=1)
        draw_text(cv, sx, y + 23, value, 2, INK, spacing=1)
        vw = text_width(value, 2, spacing=1)
        tx = sx + vw + 5
        col = TEAL if up else RED
        if up:
            tri_up(cv, tx, y + 25, col)
        else:
            tri_down(cv, tx, y + 25, col)
        draw_text(cv, tx + 12, y + 23, change, 2, col, spacing=1)


def draw_motif(cv, kind, x, y, w, h):
    if kind == "ship":
        draw_ship(cv, x, y, w, h)
    elif kind == "tanker":
        draw_tanker(cv, x, y, w, h)
    elif kind == "badge":
        draw_badge(cv, x + w // 2, y + h // 2, min(w, h) // 2 - 4)
    elif kind == "arrows":
        draw_arrows(cv, x, y, w)
    elif kind == "house":
        draw_house(cv, x, y, w, h)
    elif kind == "courthouse":
        draw_courthouse(cv, x, y, w, h)


def draw_story_card(cv, x, y, w, h, kicker, headline, summary, strip, kind):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    cv.fill_rect(x, y, w, 28, strip)
    draw_text(cv, x + 12, y + 7, kicker, 2, WHITE, bold=True)
    mx, my, mw, mh = x + 12, y + 32, w - 24, 48
    draw_motif(cv, kind, mx, my, mw, mh)
    lines = wrap_text(headline, 3, w - 24, bold=True, spacing=2)
    yy = y + 84
    for ln in lines:
        draw_text(cv, x + 12, yy, ln, 3, INK, bold=True, spacing=2)
        # Headline leading: glyph height at scale 3 is 7*3 = 21 px, so
        # the line step must be larger than 21 or two-line headlines
        # touch and read as one merged band. Step 23 gives 2 px of
        # leading between the lines and 2 px before the summary at y+130.
        yy += 23
    slines = wrap_text(summary, 2, w - 24)
    yy = y + 130
    for ln in slines:
        draw_text(cv, x + 12, yy, ln, 2, INK)
        yy += 14


def draw_briefs_band(cv, x, y, w, h):
    """Full-width briefs band: grey strip, twelve items in two columns."""
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    cv.fill_rect(x, y, w, 26, GREY)
    draw_text(cv, x + 12, y + 6, "ALSO IN BRIEF", 2, WHITE, bold=True)
    col_w = (w - 12) // 2
    for col in range(2):
        cx0 = x + 12 + col * col_w
        for row in range(6):
            item = BRIEFS[col * 6 + row]
            yy = y + 32 + row * 14
            cv.fill_rect(cx0, yy + 3, 8, 8, RED)
            draw_text(cv, cx0 + 14, yy, item, 2, INK, spacing=1)


def build_page():
    cv = Canvas(W, H, CREAM)
    cv.rect(8, 8, W - 16, H - 16, INK, 3)
    draw_masthead(cv)
    draw_lead(cv)
    draw_markets_strip(cv, LEFT, 380, PAGE_W, 44)
    # six cards: two rows of three
    gap = 12
    cw = (PAGE_W - 2 * gap) // 3
    ch = 204
    step = (PAGE_W - cw) // 2
    y_top = 432
    y_bot = y_top + ch + 10
    positions = [(LEFT + i * step, y_top) for i in range(3)]
    positions += [(LEFT + i * step, y_bot) for i in range(3)]
    for i, (kicker, headline, summary, strip, kind) in enumerate(CARDS):
        x, y = positions[i]
        draw_story_card(cv, x, y, cw, ch, kicker, headline, summary,
                        strip, kind)
    draw_briefs_band(cv, LEFT, 858, PAGE_W, 120)
    draw_text(cv, W // 2, 986, "REPORTED ON MONDAY 23 NOVEMBER 2026", 2,
              GREY, align="center")
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build_page()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
