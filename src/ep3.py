import numpy as np, math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
from ep1 import (W, H, FPS, CX, CY, ss, lerp, rocky, blend, bg, D, text_img, put, fade_win, MN, FB, FM, FL)
from ep2 import earth2, sprite, add_sprite

DUR = 66.0
GLASS = (165, 210, 235)

# ---------- lab geometry ----------
U = (620, 640); UR = 200
L = (330, 1200); LR = 140
TUBE1 = [(330, L[1] - LR + 4), (330, 660), (U[0] - UR + 4, 660)]
TUBE2 = [(620, U[1] + UR - 2), (620, 1290), (470, 1290), (470, L[1] + 10)]
COND = (596, 900, 644, 1060)
EL = [((470, 440), (588, 600)), ((770, 440), (652, 600))]

def path_point(pts, s):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    d = s * sum(seg)
    for i, l in enumerate(seg):
        if d <= l:
            k = d / l; return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k)
        d -= l
    return pts[-1]

def spark_pts(seed):
    r = np.random.default_rng(seed); a, b = EL[0][1], EL[1][1]; pts = [a]
    for i in range(1, 6):
        k = i / 6; pts.append((a[0] + (b[0] - a[0]) * k + (r.random() - 0.5) * 8, a[1] + (r.random() - 0.5) * 40))
    pts.append(b); return pts

LBL = {k: text_img(k, FM, 40, (200, 225, 240), 3) for k in ['大气', '闪电', '海洋', '冷凝']}
GAS = [text_img(k, FM, 38, (230, 230, 210), 2) for k in ['甲烷', '氨', '氢', '水汽']]
AA = text_img('氨基酸', FB, 48, (140, 230, 160), 4)
gr = np.random.default_rng(4)
gas_p = gr.random((4, 2)); gas_ph = gr.random(4) * 6

def lab(t):
    img = Image.new('RGB', (W, H), (8, 12, 18))
    a = np.asarray(img, np.float32).copy()
    yy = np.arange(H, dtype=np.float32)[:, None]
    a += (np.exp(-((yy - 900) / 700) ** 2) * 18)[..., None] * np.array([0.5, 0.8, 1.0])
    img = Image.fromarray(a.astype(np.uint8))
    glow = Image.new('RGB', (W // 2, H // 2), (0, 0, 0)); gd = ImageDraw.Draw(glow)
    dr = ImageDraw.Draw(img)
    brown = ss(22.5, 28.5, t)
    wc = tuple(int(v) for v in lerp(np.array([40, 95, 170]), np.array([125, 82, 40]), brown))
    dr.chord((L[0] - LR, L[1] - LR, L[0] + LR, L[1] + LR), 20, 160, fill=wc)
    gc = tuple(int(v) for v in lerp(np.array([22, 30, 40]), np.array([45, 36, 28]), brown))
    dr.ellipse((U[0] - UR, U[1] - UR, U[0] + UR, U[1] + UR), fill=gc)
    for i in range(4):
        ang = gas_ph[i] + t * 0.4
        x = U[0] + (i - 1.5) * 85 + math.cos(ang) * 18
        y = U[1] + 95 + (i % 2) * 45 + math.sin(ang * 1.3) * 14
        put(img, GAS[i], x, y, ss(8, 10, t) * 0.85)
    for (x0, y0, x1, y1) in [(L[0] - LR, L[1] - LR, L[0] + LR, L[1] + LR), (U[0] - UR, U[1] - UR, U[0] + UR, U[1] + UR)]:
        dr.ellipse((x0, y0, x1, y1), outline=GLASS, width=4)
        gd.ellipse((x0 / 2, y0 / 2, x1 / 2, y1 / 2), outline=(60, 110, 140), width=4)
    for p in (TUBE1, TUBE2):
        dr.line(p, fill=GLASS, width=6, joint='curve')
        gd.line([(x / 2, y / 2) for x, y in p], fill=(60, 110, 140), width=5)
    dr.rectangle(COND, outline=GLASS, width=3)
    for e in EL:
        dr.line(e, fill=(210, 210, 200), width=6)
    # flame
    fl = 0.8 + 0.2 * math.sin(t * 23) * math.sin(t * 7)
    for k, (dx, h) in enumerate([(-30, 60), (0, 85), (30, 60)]):
        hh = h * fl * (1 + 0.15 * math.sin(t * 17 + k))
        dr.polygon([(L[0] + dx - 18, L[1] + LR + 70), (L[0] + dx + 18, L[1] + LR + 70), (L[0] + dx, L[1] + LR + 70 - hh)], fill=(90, 150, 255))
        gd.polygon([((L[0] + dx - 18) / 2, (L[1] + LR + 70) / 2), ((L[0] + dx + 18) / 2, (L[1] + LR + 70) / 2), ((L[0] + dx) / 2, (L[1] + LR + 70 - hh) / 2)], fill=(40, 80, 200))
    # bubbles in lower flask
    for k in range(14):
        ph = (t * 0.9 + k * 0.071) % 1
        bx = L[0] - 90 + (k * 37) % 180; by = L[1] + 100 - ph * 120
        dr.ellipse((bx - 6, by - 6, bx + 6, by + 6), outline=(200, 220, 240), width=2)
    # droplets along tubes
    for k in range(10):
        for path, off in ((TUBE1, 0), (TUBE2, 0.05)):
            s = (t * 0.12 + k / 10 + off) % 1
            x, y = path_point(path, s)
            c = (220, 230, 240) if path is TUBE1 else tuple(int(v) for v in lerp(np.array([170, 200, 230]), np.array([200, 150, 90]), brown))
            dr.ellipse((x - 5, y - 5, x + 5, y + 5), fill=c)
    # sparks
    if t > 18.6:
        sp = (int(t * 30) % 5) < 3
        if sp:
            pts = spark_pts(int(t * 30))
            dr.line(pts, fill=(255, 255, 255), width=4)
            gd.line([(x / 2, y / 2) for x, y in pts], fill=(170, 160, 255), width=10)
    glow = glow.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    img = Image.fromarray(np.clip(np.asarray(img, np.float32) + np.asarray(glow, np.float32) * 1.6, 0, 255).astype(np.uint8))
    la = ss(8, 9.5, t)
    put(img, LBL['大气'], 900, 640, la); put(img, LBL['闪电'], 620, 400, la * ss(18.6, 19.2, t))
    put(img, LBL['海洋'], 110, 1200, la); put(img, LBL['冷凝'], 730, 980, la)
    # inset amino acid
    ia = ss(27.6, 28.6, t)
    if ia > 0:
        a = np.asarray(img, np.float32).copy()
        cy0 = 1000; rr = 250
        yy, xx = np.ogrid[0:H, 0:W]
        m = (((xx - 540) ** 2 + (yy - cy0) ** 2) < rr ** 2)[..., None] * ia
        a = a * (1 - m * 0.88) + np.array([6, 14, 12]) * m * 0.88
        img = Image.fromarray(a.astype(np.uint8)); dr = ImageDraw.Draw(img)
        dr.ellipse((540 - rr, cy0 - rr, 540 + rr, cy0 + rr), outline=tuple(int(v * ia) for v in (140, 230, 160)), width=4)
        rot = (t - 28) * 0.5
        atoms = [(-110, 0, 'N', (90, 120, 240), 34), (-20, -10, 'C', (150, 150, 150), 34), (70, 0, 'C', (150, 150, 150), 34),
                 (120, -70, 'O', (230, 70, 60), 32), (130, 60, 'O', (230, 70, 60), 32),
                 (-150, -60, 'H', (235, 235, 235), 20), (-150, 60, 'H', (235, 235, 235), 20),
                 (-30, -90, 'H', (235, 235, 235), 20), (-30, 75, 'H', (235, 235, 235), 20), (195, 80, 'H', (235, 235, 235), 20)]
        P = [(540 + x * math.cos(rot) * 1.0 - 0 * y, cy0 - 30 + y + x * math.sin(rot) * 0.15) for x, y, *_ in atoms]
        for i, j in [(0, 1), (1, 2), (2, 3), (2, 4), (0, 5), (0, 6), (1, 7), (1, 8), (4, 9)]:
            dr.line((P[i], P[j]), fill=tuple(int(v * ia) for v in (200, 200, 200)), width=8)
        for (x, y), (_, _, _, c, r) in zip(P, atoms):
            c = tuple(int(v * ia) for v in c)
            dr.ellipse((x - r, y - r, x + r, y + r), fill=c)
            dr.ellipse((x - r * 0.5, y - r * 0.6, x - r * 0.05, y - r * 0.2), fill=tuple(min(255, int(v * 1.4)) for v in c))
        put(img, AA, 540, cy0 + 170, ia)
    return img

# ---------- meteors ----------
METS = [(33.6, 0.3), (35.0, -0.25), (36.3, 0.55), (37.4, 0.05), (38.5, -0.45)]
GLOW = sprite(60)
def meteors(t):
    f = bg.copy()
    rot = 2.3 + t * 0.012
    f += (np.exp(-np.maximum(D - 340, 0) / 60) * 0.3 * (D > 338))[..., None] * np.array([110, 160, 240])
    col, a = earth2(340, rot, 1.0, 0.5)
    blend(f, col, a, CX, CY)
    seg = []
    for t0, ang in METS:
        k = (t - t0) / 1.3
        if 0 <= k <= 1.0:
            ex, ey = CX + 340 * math.sin(ang) * 0.95, CY - 340 * math.cos(ang) * 0.95
            sx, sy = ex + 1100, ey - 1000
            hx, hy = lerp(sx, ex, k ** 1.3), lerp(sy, ey, k ** 1.3)
            add_sprite(f, GLOW, hx, hy, (255, 220, 150), 0.9)
            seg.append((hx, hy, sx, sy))
        if 1.0 < k < 1.6:
            ex, ey = CX + 340 * math.sin(ang) * 0.95, CY - 340 * math.cos(ang) * 0.95
            add_sprite(f, GLOW, ex, ey, (255, 240, 200), math.exp(-(k - 1) * 5))
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    for hx, hy, sx, sy in seg:
        for j in range(12):
            k0, k1 = j / 12, (j + 1) / 12
            b = int(255 * (1 - k0) ** 2)
            dr.line((lerp(hx, sx, k0 * 0.35), lerp(hy, sy, k0 * 0.35), lerp(hx, sx, k1 * 0.35), lerp(hy, sy, k1 * 0.35)),
                    fill=(b, int(b * 0.85), int(b * 0.6)), width=max(1, 8 - j // 2))
    return img

rk_r = np.random.default_rng(9)
SPK = [(rk_r.normal() * 0.45, rk_r.normal() * 0.35, rk_r.random() * 6, rk_r.integers(0, 2)) for _ in range(45)]
ROCKN = text_img('默奇森陨石', FM, 44, (230, 210, 180), 3)
def rock(t):
    f = bg.copy() * 0.6
    col, a = rocky(300, 0.4 + t * 0.03, MN, ([35, 30, 28], [120, 105, 92]), 0.0)
    im = np.concatenate([np.clip(col, 0, 255), a[..., None] * 255], 2).astype(np.uint8)
    im = Image.fromarray(im, 'RGBA').resize((640, 470), Image.BILINEAR)
    base = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).convert('RGBA')
    base.alpha_composite(im, (CX - 320, CY - 235))
    img = base.convert('RGB'); dr = ImageDraw.Draw(img)
    sa = ss(42, 43.5, t)
    for x, y, ph, c in SPK:
        if abs(x) < 0.85 and abs(y) < 0.8:
            tw = (0.5 + 0.5 * math.sin(t * 3 + ph)) * sa
            px, py = CX + x * 300, CY + y * 210
            cc = (110, 240, 150) if c else (240, 220, 110)
            r = 4 + 4 * tw
            dr.ellipse((px - r, py - r, px + r, py + r), fill=tuple(int(v * tw) for v in cc))
    put(img, ROCKN, W / 2, CY - 330, ss(40.6, 41.4, t))
    return img

# ---------- molecules ----------
TYPES = [((90, 210, 130), '氨基酸'), ((90, 150, 245), '核苷酸'), ((240, 200, 90), '糖'), ((235, 120, 165), '脂类')]
LEG = [text_img(n, FM, 36, c, 2) for c, n in TYPES]
mr = np.random.default_rng(13)
NM = 46
mol = [(mr.random() * W, 500 + mr.random() * 1100, mr.integers(0, 4), 16 + mr.random() * 10, mr.random() * 6) for _ in range(NM)]
CHAINS = [(160, 760, 0.25, [0, 0, 1, 0, 0, 1, 0, 0]), (300, 1080, -0.1, [1, 1, 1, 1, 1, 1, 1, 1]), (120, 1360, 0.15, [0, 2, 0, 0, 2, 0, 0, 1])]
yyg = np.arange(H, dtype=np.float32)[:, None, None]
xxg = np.arange(W, dtype=np.float32)[None, :, None]
SEA = (np.array([12, 70, 95]) * (1 - yyg / H) + np.array([3, 18, 30]) * (yyg / H)).repeat(W, 1)

def molecules(t):
    lt = t - 46.6
    rays = 0.5 + 0.5 * np.sin(xxg[0, :, 0] * 0.012 + lt * 0.4) * np.sin(xxg[0, :, 0] * 0.027 - lt * 0.25)
    f = SEA + (rays[None, :] * np.clip(1 - yyg[..., 0] / 1100, 0, 1) * 30)[..., None] * np.array([0.6, 1.0, 1.0])
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(80):
        x = (i * 211 + lt * 6) % W; y = (i * 457 - lt * 12) % H
        dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(70, 120, 130))
    def bead(x, y, r, c, a=1.0):
        c = tuple(int(v * a) for v in c)
        dr.ellipse((x - r, y - r, x + r, y + r), fill=c)
        hl = tuple(min(255, int(v * 1.35)) for v in c)
        dr.ellipse((x - r * 0.55, y - r * 0.6, x - r * 0.05, y - r * 0.2), fill=hl)
    for x0, y0, ty, r, ph in mol:
        x = (x0 + 35 * math.sin(lt * 0.5 + ph) + lt * 8) % (W + 60) - 30
        y = y0 + 30 * math.cos(lt * 0.4 + ph * 1.7)
        bead(x, y, r, TYPES[ty][0], 0.85)
    for ci, (x0, y0, tilt, seq) in enumerate(CHAINS):
        pts = []
        for i, ty in enumerate(seq):
            start = 51.0 + ci * 0.6 + i * 0.45
            if t < start: break
            px = x0 + i * 82 + 10 * math.sin(lt * 0.6 + ci)
            py = y0 + i * 82 * tilt + 26 * math.sin(i * 0.9 + lt * 0.9 + ci)
            pts.append((px, py, ty, ss(start, start + 0.4, t)))
        for (x1, y1, _, a1), (x2, y2, _, a2) in zip(pts, pts[1:]):
            dr.line((x1, y1, x2, y2), fill=tuple(int(v * a2) for v in (190, 230, 220)), width=6)
        glowc = ss(55.6, 57, t) if ci == 1 else 0
        for x, y, ty, a in pts:
            if glowc: dr.ellipse((x - 40, y - 40, x + 40, y + 40), outline=tuple(int(v * glowc) for v in (180, 220, 255)), width=3)
            bead(x, y, 28, TYPES[ty][0], a)
    la = ss(47.5, 48.5, t)
    for i, im in enumerate(LEG):
        cx = 300 + (i % 2) * 480; cy = 300 + (i // 2) * 70
        bead(cx - 90, cy, 16, TYPES[i][0], la)
        put(img, im, cx + 10, cy, la)
    return img

# ---------- text ----------
CAPS = [(6.4, 10.4, '生命的零件，最初是从哪来的？'), (10.4, 14.8, '1953 年，学生米勒做了一个著名实验'),
        (14.8, 19.2, '他把早期地球的气体和水封进玻璃瓶'), (19.2, 23.4, '再用电火花模拟闪电'),
        (23.4, 27.8, '一周后，瓶里的水变成了褐色'), (27.8, 32.4, '里面出现了氨基酸，蛋白质的基本零件'),
        (33.0, 37.2, '天上，也在给地球送原料'), (37.2, 41.8, '1969 年，一颗陨石坠落在澳大利亚'),
        (41.8, 46.2, '科学家在里面找到了几十种氨基酸'), (47.0, 51.2, '这些小分子在海水里漂荡、相遇'),
        (51.2, 55.6, '有些开始手拉手，连成长链'), (55.6, 61.6, '离一个会复制自己的分子，只差一步了')]
cap_imgs = [(a, b, text_img(s, FM, 54)) for a, b, s in CAPS]
ERAS = [(6.0, 32.6, text_img('1953 年 · 芝加哥大学', FL, 40, (230, 200, 160), 3)),
        (32.6, 40.3, text_img('约 40 亿年前', FL, 40, (230, 200, 160), 3)),
        (40.3, 46.6, text_img('1969 年 · 澳大利亚', FL, 40, (230, 200, 160), 3)),
        (46.6, 61.8, text_img('约 40 亿年前 · 原始海洋', FL, 40, (230, 200, 160), 3))]
T_SERIES = text_img('38 亿年家谱', FB, 110, (255, 220, 170), 6)
T_EP = text_img('第 0 季 · 第 3 集', FM, 46, (220, 220, 220), 3)
T_NAME = text_img('生命的原料', FB, 80, (255, 255, 255), 5)
T_NEXT1 = text_img('下一集', FM, 48, (220, 220, 220), 3)
T_NEXT2 = text_img('会复制的分子', FB, 96, (200, 180, 255), 6)

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

CLEAN = False

def render(t):
    if t < 6.0:
        f = bg.copy()
        col, a = earth2(340, 2.2, 1.0, 0.5); blend(f, col, a, CX, CY)
        img = dim(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)), (1 if CLEAN else ss(0, 1.2, t)) * (1 - ss(5.3, 6.0, t)))
    elif t < 32.6: img = dim(lab(t), ss(6.0, 6.8, t) * (1 - ss(31.9, 32.6, t)))
    elif t < 40.3: img = dim(meteors(t), ss(32.6, 33.3, t) * (1 - ss(39.7, 40.3, t)))
    elif t < 46.6: img = dim(rock(t), ss(40.3, 40.9, t) * (1 - ss(46.0, 46.6, t)))
    else: img = dim(molecules(t), ss(46.6, 47.3, t) * (1 if CLEAN else (1 - 0.6 * ss(61.8, 62.6, t)) * (1 - ss(64.6, 66, t))))
    if CLEAN: return img
    ta = fade_win(t, 1.0, 6.0, 0.7)
    put(img, T_SERIES, W / 2, 760, ta); put(img, T_EP, W / 2, 880, ta)
    put(img, T_NAME, W / 2, 1010, fade_win(t, 2.2, 6.0, 0.7))
    for a, b, im in cap_imgs:
        if a <= t <= b: put(img, im, W / 2, 1660, fade_win(t, a, b, 0.35))
    for a, b, im in ERAS:
        if a <= t <= b: put(img, im, W / 2, 200, fade_win(t, a, b, 0.5))
    na = fade_win(t, 62.2, 66.0, 0.6)
    put(img, T_NEXT1, W / 2, 1500, na); put(img, T_NEXT2, W / 2, 1610, na)
    return img

if __name__ == '__main__':
    if sys.argv[1] == 'stills':
        for ts in sys.argv[2:]: render(float(ts)).save(f'ep3_still_{ts}.png')
    else:
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                              '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
                              '-crf', '20', '-pix_fmt', 'yuv420p', sys.argv[2]], stdin=subprocess.PIPE)
        nf = int(DUR * FPS)
        for i in range(nf):
            p.stdin.write(render(i / FPS).tobytes())
            if i % 300 == 0: print(i, nf, flush=True)
        p.stdin.close(); p.wait(); print('done')
