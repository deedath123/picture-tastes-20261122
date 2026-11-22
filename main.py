"""One juicy orange slice, cross-section hero.

Stdlib-only PNG program: draws a big orange slice, a half orange
behind it, one mint leaf and juice droplets on a warm cream ground.
Deterministic: fixed geometry, fixed palette, no randomness, no time.
Output: 1024x1024 entry.png in MAKEFUN_OUTPUT_DIR (default /output).
Verified: 247903 bytes, 1024x1024, byte-identical across clean-env runs.
"""
import math
import os
import struct
import zlib

W = 1024
H = 1024
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def clamp(v, lo=0, hi=255):
    return lo if v < lo else hi if v > hi else v


def mix(a, b, t):
    return tuple(clamp(int(round(a[i] + (b[i] - a[i]) * t))) for i in range(3))


def put(buf, x, y, col):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = col[0]
        buf[i + 1] = col[1]
        buf[i + 2] = col[2]


def blend(buf, x, y, col, a):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        for k in range(3):
            buf[i + k] = clamp(int(round(buf[i + k] * (1.0 - a) + col[k] * a)))


def det(x, y, s):
    # Fixed-seed hash in [0, 1): deterministic vesicle / speckle pattern.
    v = (x * 374761393 + y * 668265263 + s * 974634211) & 0xFFFFFFFF
    v ^= v >> 13
    v = (v * 1274126177) & 0xFFFFFFFF
    v ^= v >> 16
    return (v & 0xFFFF) / 65535.0


def ellipse(buf, cx, cy, rx, ry, col, alpha=1.0):
    x0 = max(0, int(cx - rx) - 1)
    x1 = min(W - 1, int(cx + rx) + 1)
    y0 = max(0, int(cy - ry) - 1)
    y1 = min(H - 1, int(cy + ry) + 1)
    for y in range(y0, y1 + 1):
        dy = (y - cy) / ry
        rem = 1.0 - dy * dy
        if rem < 0:
            continue
        dx = rx * math.sqrt(rem)
        for x in range(max(x0, int(cx - dx)), min(x1, int(cx + dx)) + 1):
            if alpha >= 1.0:
                put(buf, x, y, col)
            else:
                blend(buf, x, y, col, alpha)


def circle(buf, cx, cy, r, col, alpha=1.0):
    ellipse(buf, cx, cy, r, r, col, alpha)


def main():
    buf = bytearray(W * H * 3)
    # Warm cream background with gentle radial falloff, light top-left.
    lx, ly = 300.0, 220.0
    for y in range(H):
        for x in range(W):
            d = math.sqrt((x - lx) ** 2 + (y - ly) ** 2) / 1150.0
            t = min(1.0, d)
            base = mix((255, 248, 230), (236, 214, 176), t * t)
            edge = math.sqrt((x - 512.0) ** 2 + (y - 512.0) ** 2) / 724.0
            if edge > 0.92:
                base = mix(base, (226, 200, 160), (edge - 0.92) * 3.0)
            put(buf, x, y, base)

    # Soft shadow under the fruit, darker toward its centre.
    ellipse(buf, 512, 872, 330, 62, (150, 105, 60), 0.16)
    ellipse(buf, 512, 866, 270, 46, (140, 95, 52), 0.20)
    ellipse(buf, 512, 860, 200, 32, (130, 88, 48), 0.18)

    # ---- Half orange behind, upper right, for depth ----
    hx, hy, hr = 712, 330, 235
    circle(buf, hx, hy, hr, (214, 106, 8))
    for y in range(hy - hr, hy + hr):
        for x in range(hx - hr, hx + hr):
            dx, dy = x - hx, y - hy
            r = math.sqrt(dx * dx + dy * dy)
            if r > hr:
                continue
            t = r / hr
            light = clamp(1.0 - (dx + dy) / 700.0, 0.55, 1.25)
            col = mix((255, 150, 30), (176, 82, 6), t)
            col = tuple(clamp(int(c * light)) for c in col)
            if det(x, y, 3) > 0.93:
                col = mix(col, (150, 70, 5), 0.5)
            put(buf, x, y, col)
    # Cut face of the half orange: pale pith ring + flesh dome.
    circle(buf, hx, hy, hr - 16, (250, 238, 200))
    circle(buf, hx, hy, hr - 34, (252, 138, 18))
    for y in range(hy - hr, hy + hr):
        for x in range(hx - hr, hx + hr):
            dx, dy = x - hx, y - hy
            r = math.sqrt(dx * dx + dy * dy)
            if r > hr - 36:
                continue
            t = r / (hr - 36)
            col = mix((255, 190, 70), (240, 120, 10), t)
            if det(x, y, 7) > 0.90:
                col = mix(col, (255, 215, 120), 0.6)
            put(buf, x, y, col)
    # Segment spokes on the half orange.
    for k in range(9):
        a = k * 2.0 * math.pi / 9.0 + 0.3
        for s in range(20, hr - 40):
            x = int(hx + math.cos(a) * s)
            y = int(hy + math.sin(a) * s)
            blend(buf, x, y, (255, 232, 190), 0.55)
            blend(buf, x + 1, y, (255, 232, 190), 0.35)

    # ---- Hero slice: centre frame, cross-section ----
    cx, cy, R = 500, 545, 305
    circle(buf, cx, cy, R, (196, 92, 6))
    circle(buf, cx, cy, R - 10, (238, 122, 18))
    circle(buf, cx, cy, R - 22, (253, 244, 224))
    flesh_r = R - 40
    n_seg = 10
    for y in range(cy - flesh_r, cy + flesh_r + 1):
        for x in range(cx - flesh_r, cx + flesh_r + 1):
            dx, dy = x - cx, y - cy
            r = math.sqrt(dx * dx + dy * dy)
            if r > flesh_r:
                continue
            ang = math.atan2(dy, dx)
            if ang < 0:
                ang += 2.0 * math.pi
            seg = ang / (2.0 * math.pi) * n_seg
            frac = seg - math.floor(seg)
            edge_d = min(frac, 1.0 - frac) * (2.0 * math.pi * r / n_seg)
            t = r / flesh_r
            col = mix((255, 196, 74), (242, 118, 8), t * 0.85)
            light = 1.0 + clamp(-(dx + dy) / 2600.0, -0.08, 0.10)
            col = tuple(clamp(int(c * light)) for c in col)
            if edge_d < 4.5:
                col = mix(col, (255, 238, 200), 0.75 * (1.0 - edge_d / 4.5))
            elif edge_d < 8.0:
                col = mix(col, (255, 220, 160), 0.25 * (1.0 - (edge_d - 4.5) / 3.5))
            if 0.15 < t < 0.95 and det(x // 3, y // 3, 11) > 0.988:
                col = mix(col, (255, 226, 140), 0.55)
            elif det(x // 5, y // 5, 5) > 0.996:
                col = mix(col, (255, 240, 190), 0.4)
            if r < 26:
                col = mix(col, (255, 240, 205), 1.0 - r / 26.0)
            put(buf, x, y, col)
    # Segment tips: small pale notches at the rim of each segment.
    for k in range(n_seg):
        a = (k + 0.5) * 2.0 * math.pi / n_seg
        tx = cx + math.cos(a) * (flesh_r - 8)
        ty = cy + math.sin(a) * (flesh_r - 8)
        circle(buf, int(tx), int(ty), 7, (255, 226, 150), 0.55)

    # Glossy highlight sweeping the upper-left of the slice (softened:
    # the first render showed a flat pale oval, so lower alphas).
    ellipse(buf, 392, 420, 150, 62, (255, 255, 255), 0.10)
    ellipse(buf, 400, 428, 96, 36, (255, 255, 255), 0.14)
    ellipse(buf, 372, 402, 42, 18, (255, 255, 255), 0.25)
    # Fresh juice sheen along the lower rim.
    ellipse(buf, 560, 800, 150, 26, (255, 214, 120), 0.18)

    # ---- Mint leaf, lower right, overlapping the rind ----
    mx, my = 762, 782
    ellipse(buf, mx, my, 92, 42, (46, 138, 62))
    ellipse(buf, mx - 18, my - 6, 70, 34, (62, 162, 78))
    ellipse(buf, mx + 28, my + 4, 48, 26, (34, 116, 52))
    ellipse(buf, mx + 92, my - 2, 16, 10, (46, 138, 62))
    for s in range(0, 46):
        put(buf, mx + 88 + s, my + 2 + s // 3, (40, 110, 55))
    # Centre vein + side veins, lighter green.
    for s in range(-84, 86):
        x = mx + s
        y = my - s // 6
        blend(buf, x, y, (190, 230, 170), 0.8)
        if s % 22 == 0:
            for v in range(1, 14):
                blend(buf, x - v // 2, y - v, (170, 215, 150), 0.55)
                blend(buf, x - v // 2, y + v, (170, 215, 150), 0.45)
    # Leaf gloss.
    ellipse(buf, mx - 22, my - 14, 44, 12, (220, 245, 200), 0.30)

    # ---- Juice droplets on the cream ground ----
    drops = [(300, 830, 16), (338, 862, 11), (688, 884, 14),
             (724, 852, 9), (252, 700, 10), (812, 640, 12)]
    for dx0, dy0, dr in drops:
        circle(buf, dx0, dy0, dr, (255, 176, 60), 0.85)
        circle(buf, dx0, dy0, dr - 3, (255, 205, 110), 0.9)
        circle(buf, dx0 - dr // 3, dy0 - dr // 3, max(2, dr // 4),
               (255, 255, 255), 0.85)

    # ---- PNG encode (stdlib zlib + struct, no timestamps) ----
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "entry.png"), "wb") as f:
        f.write(bytes(png))


if __name__ == "__main__":
    main()
