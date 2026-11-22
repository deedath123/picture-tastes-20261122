#!/usr/bin/env python3
"""The picture that tastes of one ingredient — make.fun probe.

One giant glossy strawberry, centre frame, stdlib only (no PIL, no
fonts, no network). Writes entry.png (1024x1024, 299499 bytes) into
$MAKEFUN_OUTPUT_DIR (default /output). Deterministic: fixed geometry,
fixed palette, zlib level 9, no timestamps anywhere in the file.
"""
import os
import struct
import zlib
from math import sqrt, sin, cos, radians, pi

W = H = 1024
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")

buf = bytearray(W * H * 3)


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def lerp(a, b, t):
    return a + (b - a) * t


def lerp3(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def smooth(a, b, x):
    t = clamp((x - a) / (b - a))
    return t * t * (3 - 2 * t)


def set_px(x, y, col):
    i = (y * W + x) * 3
    buf[i] = int(col[0])
    buf[i + 1] = int(col[1])
    buf[i + 2] = int(col[2])


def blend_px(x, y, col, alpha):
    if alpha <= 0.0:
        return
    i = (y * W + x) * 3
    if alpha >= 1.0:
        buf[i] = int(col[0])
        buf[i + 1] = int(col[1])
        buf[i + 2] = int(col[2])
        return
    buf[i] = int(buf[i] + (col[0] - buf[i]) * alpha)
    buf[i + 1] = int(buf[i + 1] + (col[1] - buf[i + 1]) * alpha)
    buf[i + 2] = int(buf[i + 2] + (col[2] - buf[i + 2]) * alpha)


# ---------- background: warm cream, gentle radial light falloff ----------
BG_CENTRE = (253, 247, 233)
BG_EDGE = (232, 212, 182)
BCX, BCY = 512.0, 460.0
for y in range(H):
    dy = y - BCY
    row = y * W * 3
    for x in range(W):
        dx = x - BCX
        d = sqrt(dx * dx + dy * dy) / 760.0
        t = clamp(d * d * 0.9 + d * 0.15)
        r = lerp(BG_CENTRE[0], BG_EDGE[0], t)
        g = lerp(BG_CENTRE[1], BG_EDGE[1], t)
        b = lerp(BG_CENTRE[2], BG_EDGE[2], t)
        i = row + x * 3
        buf[i] = int(r)
        buf[i + 1] = int(g)
        buf[i + 2] = int(b)


def soft_ellipse(cx, cy, rx, ry, col, peak):
    """Soft dark/light ellipse blended with smooth falloff."""
    x0 = max(0, int(cx - rx))
    x1 = min(W - 1, int(cx + rx) + 1)
    y0 = max(0, int(cy - ry))
    y1 = min(H - 1, int(cy + ry) + 1)
    for y in range(y0, y1 + 1):
        ny = (y - cy) / ry
        for x in range(x0, x1 + 1):
            nx = (x - cx) / rx
            e = nx * nx + ny * ny
            if e >= 1.0:
                continue
            a = peak * (1.0 - e) * (1.0 - e)
            blend_px(x, y, col, a)


# soft shadow under the fruit
soft_ellipse(530, 884, 330, 50, (110, 70, 40), 0.30)


# ---------- strawberry body ----------
def half_width(yn, rx):
    """Superellipse profile (p=2.6, flat-ish top) with a tapered point."""
    a = abs(yn)
    if a >= 1.0:
        return 0.0
    hw = rx * (1.0 - a ** 2.6) ** (1.0 / 2.6)
    if yn > 0.3:
        hw *= 1.0 - 0.5 * ((yn - 0.3) / 0.7) ** 1.5
    return hw


def draw_strawberry(cx, cy, rx, ry, bright, deep, seed_col, gloss):
    """Body + seeds + gloss. bright/deep are the radial gradient ends."""
    lx, ly = cx - rx * 0.45, cy - ry * 0.55  # light point, upper left
    y0 = max(0, int(cy - ry))
    y1 = min(H - 1, int(cy + ry) + 1)
    for y in range(y0, y1 + 1):
        yn = (y - cy) / ry
        hw = half_width(yn, rx)
        if hw < 1.0:
            continue
        x0 = max(0, int(cx - hw))
        x1 = min(W - 1, int(cx + hw) + 1)
        for x in range(x0, x1 + 1):
            nx = (x - cx) / hw
            rn = sqrt(nx * nx + yn * yn)
            if rn > 1.0:
                continue
            dx = x - lx
            dy = y - ly
            t = clamp(sqrt(dx * dx + dy * dy) / (rx * 2.1))
            col = lerp3(bright, deep, t ** 1.15)
            # vertical darkening toward the tip
            col = lerp3(col, (col[0] * 0.78, col[1] * 0.72, col[2] * 0.75),
                        0.42 * max(0.0, yn))
            # faint vertical ribs
            rib = 1.0 + 0.045 * sin(x * 0.085 + y * 0.012)
            col = (col[0] * rib, col[1] * rib, col[2] * rib)
            # rounded 3-D edge falloff
            edge = 1.0 - 0.24 * smooth(0.72, 1.0, rn)
            set_px(x, y, (col[0] * edge, col[1] * edge, col[2] * edge))
    # seeds: neat rows, pale dots with a soft darker pit above each
    row = 0
    y = int(cy - ry + 42)
    while y < cy + ry - 30:
        hw = half_width((y - cy) / ry, rx) - 22
        if hw > 10:
            off = 26 if row % 2 else 0
            x = int(cx - hw) + off
            while x < cx + hw:
                # pit shadow, then pale seed
                soft_ellipse(x + 2, y + 3, 8, 11, deep, 0.35)
                soft_ellipse(x, y, 6.5, 9.5, seed_col, 0.95)
                x += 52
        row += 1
        y += 46
    if gloss:
        soft_ellipse(cx - rx * 0.48, cy - ry * 0.52, rx * 0.34, ry * 0.16,
                     (255, 255, 255), 0.55)
        soft_ellipse(cx - rx * 0.30, cy - ry * 0.34, rx * 0.16, ry * 0.07,
                     (255, 255, 255), 0.45)
        soft_ellipse(cx + rx * 0.55, cy + ry * 0.10, rx * 0.20, ry * 0.09,
                     (255, 220, 200), 0.16)
        # juice sheen: soft pale-pink highlight arc along lower-left curve
        soft_ellipse(cx - rx * 0.62, cy + ry * 0.35, rx * 0.22, ry * 0.10,
                     (255, 190, 175), 0.18)


# smaller strawberry behind-left, for depth (muted, less gloss)
draw_strawberry(335, 470, 145, 185, (205, 55, 55), (120, 18, 28),
                (238, 220, 185), gloss=False)


# ---------- mint leaf, bottom right ----------
def draw_leaf(ox, oy, angle_deg, length, half_w, c_base, c_tip, vein=True):
    a = radians(angle_deg)
    ca, sa = cos(a), sin(a)
    x0 = max(0, int(ox - length))
    x1 = min(W - 1, int(ox + length) + 1)
    y0 = max(0, int(oy - length))
    y1 = min(H - 1, int(oy + length) + 1)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx, dy = x - ox, y - oy
            u = dx * ca + dy * sa
            v = -dx * sa + dy * ca
            if u < 0.0 or u > length:
                continue
            s = u / length
            w = half_w * (1.0 - (2.0 * s - 1.0) ** 2) ** 0.6
            if abs(v) > w:
                continue
            col = lerp3(c_base, c_tip, s)
            if vein and abs(v) < 2.5 and 0.08 < s < 0.95:
                col = lerp3(col, (28, 88, 42), 0.55)
            # serrated-ish edge shading
            edge = 1.0 - 0.18 * smooth(0.75, 1.0, abs(v) / max(w, 1.0))
            blend_px(x, y, (col[0] * edge, col[1] * edge, col[2] * edge), 1.0)


draw_leaf(742, 838, -38, 150, 42, (52, 138, 66), (96, 186, 104))


# ---------- hero strawberry ----------
draw_strawberry(545, 555, 265, 300, (238, 72, 62), (148, 14, 26),
                (252, 238, 205), gloss=True)


# ---------- calyx: fresh green leaves fanning over the top ----------
# short stem first (behind the leaves)
for y in range(212, 268):
    for x in range(538, 554):
        blend_px(x, y, (96, 124, 62), 1.0)
for ang in (-158, -132, -108, -90, -72, -48, -22):
    draw_leaf(545, 292, ang, 150, 30, (34, 104, 44), (74, 158, 74),
              vein=False)
# leaf veins on the calyx: darker centre lines
for ang in (-132, -90, -48):
    a = radians(ang)
    for s in range(12, 140, 4):
        x = int(545 + cos(a) * s)
        y = int(292 + sin(a) * s)
        blend_px(x, y, (24, 78, 34), 0.7)
        blend_px(x, y + 1, (24, 78, 34), 0.5)


# ---------- stdlib PNG encoder (zlib + struct, filter 0, level 9) ----------
def chunk(kind, data):
    c = struct.pack(">I", len(data)) + kind + data
    c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return c


raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += buf[y * W * 3:(y + 1) * W * 3]

png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
png += chunk(b"IEND", b"")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "wb") as f:
    f.write(png)
print("saved", OUT, len(png), "bytes")
