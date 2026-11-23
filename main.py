#!/usr/bin/env python3
"""World news of Saturday 21 November 2026, drawn as one newspaper image.

Pure Python 3.13 standard library. Draws a 1024x1024 front page with an
embedded 8x12 bitmap font (rasterised from DejaVu Sans) and writes a PNG
with a hand-rolled encoder (zlib). No network, no time, no randomness:
two runs write byte-identical files.
"""
import base64
import math
import os
import struct
import zlib

# ---------------------------------------------------------------- palette --
# 22 Nov layout palette; GREY is the polished 21 Nov value (88, 84, 76).
PAPER = (246, 241, 229)
WHITE = (255, 255, 255)
INK = (23, 35, 59)
NAVY = (20, 33, 61)
RED = (193, 39, 45)
TEAL = (15, 118, 110)
GOLD = (183, 121, 31)
BLUE = (29, 78, 216)
GREY = (88, 84, 76)
CREAM = (250, 244, 224)
LIGHT = (232, 184, 75)

# ---------------------------------------------------------------- font ----
# Bitmap font: chars 32..126, regular then bold. Each glyph is 13 bytes:
# one width byte (1..8) + 12 rows of 8 bits. Rasterised from DejaVu Sans.
FONT_B64 = (
'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',
'MDBw4AAACAAAAAAAAABx/44AAA==',
)

_FONT_RAW = base64.b64decode("".join(FONT_B64))
# glyphs[weight][ord-32] = (width, rows tuple of 12 ints)
_GLYPHS = []
for _w in range(2):
    bank = []
    base = _w * 95 * 13
    for _i in range(95):
        off = base + _i * 13
        bank.append((_FONT_RAW[off], tuple(_FONT_RAW[off + 1:off + 13])))
    _GLYPHS.append(bank)

# glyph cache: (weight, ch, scale) -> (width_px, [row bytes]) row bytes are RGB
_GCACHE = {}


def glyph_rows(weight, ch, scale):
    key = (weight, ch, scale)
    hit = _GCACHE.get(key)
    if hit is not None:
        return hit
    width, rows = _GLYPHS[weight][ord(ch) - 32]
    out = []
    for bits in rows:
        line = bytearray()
        for x in range(width):
            on = (bits >> (7 - x)) & 1
            line += b"\x01" * scale if on else b"\x00" * scale
        out.extend([bytes(line)] * scale)
    res = (width * scale, out)
    _GCACHE[key] = res
    return res


def text_width(text, scale, bold=False):
    w = 0
    weight = 1 if bold else 0
    for ch in text:
        if ch == " ":
            w += 4 * scale
        else:
            gw, _ = glyph_rows(weight, ch, scale)
            w += gw + scale
    return w - scale if w else 0


def wrap_text(text, width, scale, bold=False):
    """Greedy word wrap; returns list of lines."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, bold) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def _row(self, y):
        return y * self.w * 3

    def fill_rect(self, x, y, w, h, color):
        x = max(0, x)
        y = max(0, y)
        w = min(w, self.w - x)
        h = min(h, self.h - y)
        if w <= 0 or h <= 0:
            return
        row = bytes(color) * w
        for yy in range(y, y + h):
            off = self._row(yy) + x * 3
            self.px[off:off + w * 3] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=3, bg=PAPER):
        # 22 Nov fix (b): solid fill -- outer disc in `color`, inner disc
        # in `bg`, so the thermometer bulb stays solid red, not paper.
        self.disc(cx, cy, r, color)
        self.disc(cx, cy, r - thick, bg)

    def border(self, x, y, w, h, color, t=2):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def polygon(self, pts, color):
        # Even-odd scanline fill for simple polygons.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(math.ceil(xs[k])), y,
                               int(math.floor(xs[k + 1])) - int(math.ceil(xs[k])) + 1,
                               1, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        self.polygon([(x0, y0), (x1, y1), (x2, y2)], color)

    def ellipse_outline(self, cx, cy, rx, ry, color, t=2):
        steps = 360
        for k in range(steps):
            a = 2.0 * math.pi * k / steps
            x = int(cx + rx * math.cos(a))
            y = int(cy + ry * math.sin(a))
            self.fill_rect(x - t // 2, y - t // 2, t, t, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def star(self, cx, cy, r, color):
        """8-point starburst."""
        for k in range(8):
            import math
            a = math.pi * k / 4.0
            x1 = cx + int(r * math.cos(a))
            y1 = cy + int(r * math.sin(a))
            self.line(cx, cy, x1, y1, color, 3)
        self.disc(cx, cy, max(2, r // 3), color)

    def draw_text(self, x, y, text, scale, color, bold=False):
        weight = 1 if bold else 0
        cx = x
        for ch in text:
            if ch == " ":
                cx += 4 * scale
                continue
            gw, rows = glyph_rows(weight, ch, scale)
            rgb = bytes(color)
            for i, row in enumerate(rows):
                yy = y + i
                if yy < 0 or yy >= self.h:
                    continue
                off = self._row(yy) + cx * 3
                pos = 0
                for v in row:
                    if v:
                        self.px[off + pos * 3:off + pos * 3 + 3] = rgb
                    pos += 1
            cx += gw + scale
        return cx

    def draw_text_block(self, x, y, text, width, scale, color, bold=False,
                        leading=None):
        """Draw wrapped text; returns y just below the block."""
        lh = 12 * scale + (leading if leading is not None else 4 * scale // 2)
        for line in wrap_text(text, width, scale, bold):
            self.draw_text(x, y, line, scale, color, bold)
            y += lh
        return y


# ------------------------------------------------------------------ png ----
def write_png(canvas, path):
    w, h = canvas.w, canvas.h
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ----------------------------------------------------------------- page ----
W = H = 1024

LEAD_KICKER = "CLIMATE - COP31, ANTALYA"
LEAD_HEADLINE = "COP31 COLLAPSES"
LEAD_SUMMARY = ("UN climate talks in Antalya collapse after more than two "
                "weeks, the longest COP in history and the first failure "
                "since 2009.")
LEAD_FOOT = "LONGEST COP IN HISTORY - FIRST FAILURE SINCE 2009"

BRIEFS = [
    "NATO meets in Brussels after missiles hit Poland",
    "Democrats win largest House majority since 1992",
    "UK set to host 2035 Women's World Cup",
    "6.5 quake in Vanuatu region, 598 km deep",
    "Jeweller Paolo Bulgari dies, aged 89",
    "Lagarde to leave ECB in February 2027",
    "French students plan nationwide protests",
]


# ---------------------------------------------------------------- pictures
def draw_globe(cv, cx, cy, r, ink, teal, bg=PAPER):
    cv.disc(cx, cy, r, teal)
    cv.disc(cx, cy, r - 4, bg)
    cv.ellipse_outline(cx, cy, r - 4, r - 4, ink, 3)
    cv.ellipse_outline(cx, cy, (r - 4) // 2, r - 4, ink, 2)
    cv.line(cx - r + 4, cy, cx + r - 4, cy, ink, 2)
    # two land blobs
    cv.disc(cx - r // 3, cy - r // 3, r // 5, teal)
    cv.disc(cx + r // 4, cy + r // 3, r // 6, teal)


def draw_thermometer(cv, x, y, w, h, red, ink):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, ink, 2)
    cv.fill_rect(x + 3, y + h // 3, w - 6, h - h // 3 - 3, red)
    cv.disc(x + w // 2, y + h, w // 2 + 4, red)
    # solid red bulb with an ink rim: ring's inner fill is red, not paper
    cv.ring(x + w // 2, y + h, w // 2 + 4, ink, 2, bg=red)


def draw_flame(cv, cx, cy, s, red, gold):
    cv.polygon([(cx, cy - 3 * s), (cx + 2 * s, cy + s), (cx + s, cy + 2 * s),
                (cx - s, cy + 2 * s), (cx - 2 * s, cy + s)], red)
    cv.polygon([(cx, cy - s), (cx + s, cy + s), (cx - s, cy + s)], gold)


def draw_tanker(cv, cx, cy, s, ink, red):
    cv.polygon([(cx - 4 * s, cy), (cx + 4 * s, cy), (cx + 3 * s, cy + 2 * s),
                (cx - 3 * s, cy + 2 * s)], ink)
    cv.fill_rect(cx - 2 * s, cy - 2 * s, 2 * s, 2 * s, red)
    cv.line(cx - 5 * s, cy + 3 * s, cx + 5 * s, cy + 3 * s, ink, 2)
    cv.line(cx - 4 * s, cy + 4 * s, cx + 4 * s, cy + 4 * s, ink, 2)


def draw_badge(cv, cx, cy, r, gold, ink, bg=PAPER):
    cv.disc(cx, cy, r, gold)
    cv.disc(cx, cy, r - 4, bg)
    cv.ellipse_outline(cx, cy, r - 4, r - 4, ink, 2)
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rad = r - 10 if k % 2 == 0 else (r - 10) * 0.45
        pts.append((int(cx + rad * math.cos(ang)), int(cy + rad * math.sin(ang))))
    cv.polygon(pts, ink)


def draw_ship_burst(cv, cx, cy, s, blue, red):
    cv.polygon([(cx - 4 * s, cy), (cx + 4 * s, cy), (cx + 3 * s, cy + 2 * s),
                (cx - 3 * s, cy + 2 * s)], blue)
    cv.line(cx, cy, cx, cy - 3 * s, blue, 2)
    cv.triangle(cx, cy - 3 * s, cx + 2 * s, cy - 2 * s, cx, cy - 2 * s, red)
    bx, by = cx, cy - 4 * s
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x0 = int(bx + 2 * s * math.cos(a))
        y0 = int(by + 2 * s * math.sin(a))
        x1 = int(bx + 3 * s * math.cos(a))
        y1 = int(by + 3 * s * math.sin(a))
        cv.line(x0, y0, x1, y1, red, 2)
    cv.disc(bx, by, s // 2, red)


def draw_trade(cv, cx, cy, s, teal, gold):
    cv.line(cx - 4 * s, cy - s, cx + 3 * s, cy - s, teal, 3)
    cv.triangle(cx + 3 * s, cy - s, cx + 4 * s, cy - 2 * s, cx + 4 * s, cy, teal)
    cv.line(cx + 4 * s, cy + s, cx - 3 * s, cy + s, gold, 3)
    cv.triangle(cx - 3 * s, cy + s, cx - 4 * s, cy, cx - 4 * s, cy + 2 * s, gold)
    cv.fill_rect(cx - 2 * s, cy + 2 * s, 4 * s, 2 * s, teal)


def draw_boat(cv, cx, cy, s, ink, blue):
    cv.polygon([(cx - 4 * s, cy), (cx + 4 * s, cy), (cx + 3 * s, cy + 2 * s),
                (cx - 3 * s, cy + 2 * s)], ink)
    cv.line(cx, cy, cx, cy - 3 * s, ink, 2)
    cv.triangle(cx, cy - 3 * s, cx + 3 * s, cy, cx, cy, blue)
    cv.line(cx - 5 * s, cy + 3 * s, cx + 5 * s, cy + 3 * s, blue, 2)
    cv.line(cx - 4 * s, cy + 4 * s, cx + 4 * s, cy + 4 * s, blue, 2)


def draw_house(cv, cx, cy, s, ink, red, gold):
    # home rescued from the rubble: red roof, ink walls and door, gold star
    cv.star(cx + 5 * s, cy - 5 * s, 2 * s, gold)
    cv.polygon([(cx - 4 * s, cy - s), (cx, cy - 4 * s), (cx + 4 * s, cy - s)],
               red)
    cv.rect(cx - 3 * s, cy - s, 6 * s, 4 * s, ink, 2)
    cv.fill_rect(cx - s, cy + s, 2 * s, 2 * s, ink)


# ---------------------------------------------------------------- layout
def card(cv, x, y, w, h, kicker, kcolor, headline, summary, pic):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, INK, 2)
    cv.fill_rect(x, y, w, 30, kcolor)
    cv.draw_text(x + 14, y + 4, kicker, 2, WHITE, True)
    # fix (a): picture below the coloured kicker strip, never overlapping it
    pic(x + w // 2, y + 72)
    hy = y + 104
    end = cv.draw_text_block(x + 14, hy, headline, w - 28, 2, INK, True,
                             leading=4)
    cv.draw_text_block(x + 14, end + 6, summary, w - 28, 1, INK, False,
                       leading=4)


def build():
    cv = Canvas(W, H, PAPER)
    cv.border(16, 16, W - 32, H - 32, INK, 2)

    # masthead
    cv.fill_rect(24, 24, 976, 132, NAVY)
    cv.draw_text(48, 40, "WORLD NEWS IN ONE IMAGE", 2, LIGHT, True)
    cv.draw_text(48, 62, "THE WORLD TODAY", 5, CREAM, True)
    cv.draw_text(48, 128, "MONDAY 23 NOVEMBER 2026", 2, LIGHT, True)
    # fix (c): masthead globe keeps its cream/paper background
    draw_globe(cv, 918, 90, 46, INK, TEAL)
    cv.disc(946, 66, 7, RED)

    # lead story: COP31
    lx, ly, lw, lh = 24, 168, 976, 300
    cv.fill_rect(lx, ly, lw, lh, WHITE)
    cv.border(lx, ly, lw, lh, INK, 2)
    cv.fill_rect(lx, ly, 10, lh, RED)
    cv.draw_text(lx + 28, ly + 18, LEAD_KICKER, 2, RED, True)
    cv.draw_text(lx + 28, ly + 46, LEAD_HEADLINE, 5, INK, True)
    cv.draw_text_block(lx + 28, ly + 140, LEAD_SUMMARY, 620, 2, INK, False,
                       leading=4)
    cv.line(lx + 28, ly + 236, lx + 640, ly + 236, GREY, 2)
    cv.draw_text(lx + 28, ly + 252, LEAD_FOOT, 2, GREY, False)
    # fix (c): lead globe and badge on WHITE, not paper
    draw_globe(cv, 838, 300, 78, INK, TEAL, bg=WHITE)
    draw_thermometer(cv, 928, 268, 16, 74, RED, INK)

    # story cards, 3 + 3
    cw, ch, gap = 314, 236, 16
    xs = [24, 24 + cw + gap, 24 + 2 * (cw + gap)]
    ys = [480, 728]
    card(cv, xs[0], ys[0], cw, ch, "WAR IN EUROPE", BLUE,
         "RUSSIAN WARSHIP SUNK IN LIBYA",
         "Ukrainian sea drones are suspected of sinking the corvette "
         "Merkury at Benghazi. Kyiv and Moscow have not commented.",
         lambda cx, cy: draw_ship_burst(cv, cx, cy - 4, 5, BLUE, RED))
    card(cv, xs[1], ys[0], cw, ch, "MIDDLE EAST", RED,
         "GULF CRISIS DEEPENS",
         "Trump dares Iran to test the Hormuz blockade; Bahrain seeks "
         "UN action after Saturday's attacks injured two.",
         lambda cx, cy: (draw_tanker(cv, cx, cy - 6, 5, INK, RED),
                          draw_flame(cv, cx, cy - 22, 4, RED, GOLD)))
    card(cv, xs[2], ys[0], cw, ch, "SCIENCE", TEAL,
         "CLAUDE 'PROVES' RIEMANN",
         "Levent Alpoege says he and Claude proved it; Lean and "
         "Mathlib verified it. The Clay Institute still lists it open.",
         lambda cx, cy: draw_badge(cv, cx, cy - 8, 30, GOLD, INK, bg=WHITE))
    card(cv, xs[0], ys[1], cw, ch, "ECONOMY", GOLD,
         "MARKETS REBOUND AFTER AI ROUT",
         "Nasdaq 100 futures rise nearly 3% after the worst loss in "
         "over six years; Korea's KOSPI falls 5%.",
         # fix (d): trade arrows enlarged to scale 6
         lambda cx, cy: draw_trade(cv, cx, cy - 8, 6, TEAL, GOLD))
    card(cv, xs[1], ys[1], cw, ch, "WAR IN UKRAINE", INK,
         "BOY, 7, PULLED ALIVE",
         "A drone strike on a home in Dimer kills nine. Rescuers save "
         "a boy, 7, and a woman, 79, from the rubble.",
         lambda cx, cy: draw_house(cv, cx, cy - 4, 4, INK, RED, GOLD))

    # briefs card
    bx, by = xs[2], ys[1]
    cv.fill_rect(bx, by, cw, ch, WHITE)
    cv.border(bx, by, cw, ch, INK, 2)
    cv.fill_rect(bx, by, cw, 30, GREY)
    cv.draw_text(bx + 14, by + 4, "ALSO IN BRIEF", 2, WHITE, True)
    iy = by + 40
    for b in BRIEFS:
        lines = wrap_text(b, cw - 46, 1, False)
        cv.fill_rect(bx + 14, iy + 1, 10, 10, RED)
        for ln in lines:
            cv.draw_text(bx + 32, iy, ln, 1, INK, False)
            iy += 16
        iy += 5
    print("briefs bottom y =", iy, "card bottom =", by + ch)

    # footer
    foot = "REPORTED ON MONDAY 23 NOVEMBER 2026"
    fw = text_width(foot, 2, False)
    cv.draw_text((W - fw) // 2, 976, foot, 2, GREY, False)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print("wrote", path, size, "bytes")


if __name__ == "__main__":
    main()
