import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import sea, mul
from ep11 import camb_bg, haikou, FLOOR

CLEAN = False
rng = np.random.default_rng(121)

def armored(dr, x, y, s, t, a=1.0):
    pts = [(x + 110 * s * math.cos(p) * (1 if math.cos(p) > 0 else 1.25), y + 30 * s * math.sin(p) + 5 * s * math.sin(math.cos(p) * 3 - t * 6)) for p in np.linspace(0, 2 * math.pi, 50)]
    dr.polygon(pts, fill=mul((150, 140, 125), a), outline=mul((100, 92, 80), a))
    dr.pieslice((x - 10 * s, y - 42 * s, x + 130 * s, y + 38 * s), 180, 360, fill=mul((120, 105, 90), a), outline=mul((80, 70, 60), a))
    dr.polygon([(x - 130 * s, y), (x - 180 * s, y - 40 * s + 8 * s * math.sin(t * 6)), (x - 175 * s, y + 36 * s + 8 * s * math.sin(t * 6))], fill=mul((140, 128, 112), a))
    for j in range(5):
        dr.ellipse((x + (20 + j * 18) * s, y - 30 * s, x + (32 + j * 18) * s, y - 18 * s), fill=mul((95, 85, 72), a))
    dr.ellipse((x + 92 * s, y - 12 * s, x + 104 * s, y, ), fill=mul((30, 30, 35), a))
    dr.ellipse((x + 116 * s, y + 2 * s, x + 128 * s, y + 14 * s), fill=mul((50, 30, 30), a))

AF = [(rng.random() * W, 820 + rng.random() * 520, 0.8 + rng.random() * 0.5, rng.random() * 6) for _ in range(4)]
def intro(t):
    img, dr = camb_bg(t)
    if t < 10.4:
        m = 0.5 + 0.5 * math.sin(t * 4)
        haikou(dr, 540, 960, 3.0, t, mouth=0.4 + 0.6 * m)
        return img
    k = ss(10.6, 11.6, t)
    for i, (x0, y0, s, ph) in enumerate(AF):
        x = (x0 + (t - 10) * 40 * (1 if i % 2 else -0.7)) % (W + 300) - 150
        armored(dr, x, y0 + 20 * math.sin(t + ph), s * 1.4 * k + 0.01, t + ph)
    return img

# ---------- gill arches become jaws ----------
HX, HY = 300, 960
ARCH_X = [800, 720, 640, 560, 480, 400]
L_ARCH = text_img('鳃弓', FB, 44, (240, 230, 210), 3); L_GILL = text_img('鳃丝（呼吸）', FM, 38, (250, 170, 160), 3)
L_UP = text_img('上颌', FB, 44, (255, 225, 150), 3); L_LO = text_img('下颌', FB, 44, (255, 225, 150), 3)
L_TOOTH = text_img('牙齿', FB, 44, (240, 240, 250), 3)
def head(t):
    img, dr = sea(t + 600)
    pts = []
    for p in np.linspace(math.pi * 0.5, math.pi * 1.5, 30):
        pts.append((HX + 120 * math.cos(p), HY + 230 * math.sin(p)))
    pts += [(HX, HY + 230), (820, HY + 200), (960, HY + 70), (990, HY), (960, HY - 70), (820, HY - 200), (HX, HY - 230)]
    dr.polygon(pts, fill=(185, 165, 145), outline=(225, 205, 185))
    dr.ellipse((850, HY - 150, 900, HY - 100), fill=(30, 30, 35))
    morph = ss(24.0, 30.0, t)
    gape = (0.5 + 0.5 * math.sin((t - 28) * 3)) * ss(28.2, 29.0, t)
    for i, ax in enumerate(ARCH_X):
        if i == 0:
            jx = lerp(ax, 820, morph); sc = lerp(1.0, 1.35, morph)
            up_end = (lerp(ax - 50, 985, morph), lerp(HY - 140, HY - 10 - 70 * gape, morph))
            lo_end = (lerp(ax - 50, 985, morph), lerp(HY + 140, HY + 10 + 70 * gape, morph))
            J = (lerp(ax + 30, 820, morph), HY)
            col = tuple(int(v) for v in lerp(np.array([240, 235, 220]), np.array([255, 220, 140]), morph))
            w = int(lerp(10, 18, morph))
            dr.line((J, up_end), fill=col, width=w); dr.line((J, lo_end), fill=col, width=w)
            dr.ellipse((J[0] - 12, J[1] - 12, J[0] + 12, J[1] + 12), fill=col)
            tk = ss(32.4, 34.0, t)
            if tk > 0:
                for k in range(1, 6):
                    u = k / 6
                    for e, sgn in ((up_end, 1), (lo_end, -1)):
                        px, py = lerp(J[0], e[0], u), lerp(J[1], e[1], u)
                        dr.polygon([(px - 8, py), (px + 8, py), (px, py + sgn * 22 * tk)], fill=(250, 250, 255))
            continue
        a = 1 - 0.0 * morph
        J = (ax + 30, HY)
        dr.line((J, (ax - 50, HY - 140)), fill=(240, 235, 220), width=10)
        dr.line((J, (ax - 50, HY + 140)), fill=(240, 235, 220), width=10)
        dr.ellipse((J[0] - 9, J[1] - 9, J[0] + 9, J[1] + 9), fill=(240, 235, 220))
        for k in range(8):
            u = (k + 1) / 9
            for sgn in (-1, 1):
                px, py = lerp(J[0], ax - 50, u), lerp(HY, HY + sgn * 140, u)
                dr.line((px - 4, py, px - 34, py + 6 * math.sin(t * 3 + k)), fill=(225, 110, 105), width=3)
    if morph < 0.05:
        dr.ellipse((970, HY - 18, 1000, HY + 18), fill=(70, 35, 35))
    put(img, L_ARCH, 600, HY - 300, ss(15.8, 16.6, t) * (1 - ss(23.4, 24.0, t)))
    put(img, L_GILL, 560, HY + 300, ss(20.0, 20.8, t) * (1 - ss(23.4, 24.0, t)))
    put(img, L_UP, 900, HY - 260, ss(28.4, 29.2, t) * (1 - ss(32.0, 32.6, t)))
    put(img, L_LO, 900, HY + 260, ss(28.4, 29.2, t) * (1 - ss(32.0, 32.6, t)))
    put(img, L_TOOTH, 900, HY - 260, ss(32.6, 33.4, t))
    return img

# ---------- fossils from Chongqing / Guizhou ----------
L_CQ = text_img('重庆', FB, 42, (255, 225, 160), 3); L_GZ = text_img('贵州', FB, 42, (255, 225, 160), 3)
L_FOS = text_img('约 4.36 亿年前的有颌鱼化石', FM, 38, (230, 225, 215), 3)
_sr = np.random.default_rng(7)
SLAB = np.clip(np.array([128, 122, 112]) + _sr.normal(size=(H // 8, W // 8, 1)) * 10, 0, 255)
def fossil(t):
    f = np.asarray(Image.fromarray(SLAB.astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32)
    img = Image.fromarray(f.astype(np.uint8)); dr = ImageDraw.Draw(img)
    k = ss(36.8, 38.4, t)
    cx, cy, s = 540, 1000, 2.6
    col = mul((80, 74, 66), k) if k > 0 else None
    if col:
        c2 = tuple(int(lerp(v, w, k)) for v, w in zip((128, 122, 112), (80, 74, 66)))
        pts = [(cx + 120 * s * math.cos(p), cy + 34 * s * math.sin(p)) for p in np.linspace(0, 2 * math.pi, 50)]
        dr.line(pts + [pts[0]], fill=c2, width=6)
        dr.line((cx - 120 * s, cy, cx - 175 * s, cy - 40 * s), fill=c2, width=6)
        dr.line((cx - 120 * s, cy, cx - 175 * s, cy + 40 * s), fill=c2, width=6)
        dr.line((cx + 70 * s, cy, cx + 122 * s, cy - 12 * s), fill=c2, width=6)
        dr.line((cx + 70 * s, cy, cx + 122 * s, cy + 12 * s), fill=c2, width=6)
        for j in range(12):
            x = cx + (-90 + j * 14) * s
            dr.line((x, cy - 26 * s, x - 8 * s, cy + 26 * s), fill=c2, width=3)
    pk = ss(37.6, 38.6, t)
    if pk > 0:
        for (px, py), lab in (((600, 500), L_CQ), ((470, 660), L_GZ)):
            dr.ellipse((px - 16, py - 16, px + 16, py + 16), fill=mul((230, 80, 60), pk), outline=mul((255, 220, 200), pk), width=3)
            put(img, lab, px, py - 56, pk)
    put(img, L_FOS, 540, 1330, ss(41.0, 41.8, t))
    return img

# ---------- jawed fish rise ----------
def jawfish(dr, x, y, s, t, gape, col=(160, 175, 190), face=1, a=1.0):
    pts = [(x + face * 100 * s * math.cos(p), y + 32 * s * math.sin(p) + 5 * s * math.sin(math.cos(p) * 3 - t * 6)) for p in np.linspace(0, 2 * math.pi, 50)]
    dr.polygon(pts, fill=mul(col, a), outline=mul(tuple(int(v * 0.7) for v in col), a))
    dr.polygon([(x - face * 95 * s, y), (x - face * 150 * s, y - 42 * s + 8 * s * math.sin(t * 6)), (x - face * 145 * s, y + 40 * s + 8 * s * math.sin(t * 6))], fill=mul(col, a))
    jx = x + face * 70 * s
    dr.polygon([(jx, y), (x + face * 112 * s, y - 6 * s - 16 * s * gape), (x + face * 112 * s, y + 6 * s + 16 * s * gape)], fill=mul((60, 35, 35), a))
    dr.line(((jx, y), (x + face * 112 * s, y + 6 * s + 16 * s * gape)), fill=mul((240, 220, 170), a), width=max(2, int(4 * s)))
    dr.ellipse((x + face * 58 * s - 6 * s, y - 16 * s, x + face * 58 * s + 6 * s, y - 4 * s), fill=mul((25, 25, 30), a))

def dunkle(dr, x, y, s, t, gape):
    dr.ellipse((x - 260 * s, y - 70 * s, x + 120 * s, y + 70 * s), fill=(95, 105, 115), outline=(60, 68, 76), width=3)
    dr.polygon([(x - 250 * s, y), (x - 360 * s, y - 90 * s + 10 * math.sin(t * 4)), (x - 340 * s, y + 80 * s)], fill=(90, 100, 110))
    dr.pieslice((x - 40 * s, y - 80 * s, x + 200 * s, y + 80 * s), 180, 360, fill=(70, 72, 78), outline=(40, 42, 46), width=3)
    dr.polygon([(x + 40 * s, y), (x + 200 * s, y - 10 * s - 40 * s * gape), (x + 200 * s, y + 10 * s)], fill=(55, 40, 40))
    dr.polygon([(x + 40 * s, y + 4 * s), (x + 200 * s, y + 14 * s + 40 * s * gape), (x + 60 * s, y + 60 * s)], fill=(70, 72, 78), outline=(230, 225, 210))
    dr.ellipse((x + 90 * s, y - 40 * s, x + 112 * s, y - 18 * s), fill=(250, 245, 230)); dr.ellipse((x + 96 * s, y - 34 * s, x + 106 * s, y - 24 * s), fill=(20, 20, 25))
L_DUNK = text_img('邓氏鱼 · 约 6 米', FB, 44, (240, 230, 220), 3); L_LAM = text_img('七鳃鳗', FB, 42, (230, 220, 200), 3)
SCH = [(rng.random(), rng.random(), rng.random() * 6) for _ in range(12)]
def rise(t):
    img, dr = camb_bg(t)
    if t < 53.6:
        k = ss(45.2, 48.0, t)
        gape = 0.5 + 0.5 * math.sin(t * 5)
        px = lerp(860, 700, k)
        for j in range(6):
            q = (j * 0.618) % 1
            dr.ellipse((px + 40 + j * 22 - 8, 950 + (q - 0.5) * 60 - 8, px + 40 + j * 22 + 8, 950 + (q - 0.5) * 60 + 8), fill=(200, 210, 150)) if t < 47.5 else None
        jawfish(dr, lerp(300, 620, k), 960, 2.0, t, gape)
        if t > 49.4:
            n = int(ss(49.6, 52.6, t) * 12)
            for i, (u, v, ph) in enumerate(SCH[:n]):
                x = (u * W + (t - 49) * 60) % (W + 200) - 100; y = 600 + v * 750
                jawfish(dr, x, y, 0.8, t + ph, 0.5 + 0.5 * math.sin(t * 4 + ph), (150 + i * 6, 170, 190 - i * 4))
        return img
    if t < 57.8:
        k = ss(53.8, 55.4, t)
        dunkle(dr, lerp(-300, 560, k), 960, 1.6, t, 0.5 + 0.5 * math.sin(t * 2.5))
        put(img, L_DUNK, 520, 700, ss(54.4, 55.2, t))
        return img
    for i in range(3):
        a = 1 - ss(58.2 + i * 0.6, 59.4 + i * 0.6, t)
        if a > 0.02:
            armored(dr, 250 + i * 290, 820 + i * 90, 1.0 * a + 0.01, t)
    lx, ly = 540, 1220
    pts = [(lx + 150 * math.cos(p) * (1.0 if math.cos(p) > 0 else 1.1), ly + 18 * math.sin(p) + 6 * math.sin(math.cos(p) * 4 - t * 5)) for p in np.linspace(0, 2 * math.pi, 50)]
    dr.polygon(pts, fill=(120, 100, 90), outline=(80, 66, 58))
    dr.ellipse((lx + 140, ly - 18, lx + 176, ly + 18), fill=(150, 90, 85), outline=(200, 140, 120), width=3)
    for j in range(7):
        dr.ellipse((lx + 60 - j * 14, ly - 6, lx + 66 - j * 14, ly), fill=(60, 45, 40))
    put(img, L_LAM, lx, ly - 90, ss(59.0, 59.8, t))
    return img

# ---------- lobe-finned fish ----------
L_LOBE = text_img('肉鳍鱼', FB, 46, (255, 225, 160), 3); L_BONE = text_img('鳍里的骨头', FM, 40, (240, 240, 250), 3)
def lobe(t):
    img, dr = sea(t + 600)
    x, y, s = 520, 900, 3.0
    pts = [(x + 100 * s * math.cos(p), y + 30 * s * math.sin(p)) for p in np.linspace(0, 2 * math.pi, 60)]
    dr.polygon(pts, fill=(130, 140, 115), outline=(95, 105, 85))
    dr.polygon([(x - 95 * s, y), (x - 140 * s, y - 40 * s), (x - 140 * s, y + 40 * s)], fill=(120, 130, 105))
    dr.ellipse((x + 62 * s, y - 14 * s, x + 74 * s, y - 2 * s), fill=(25, 25, 30))
    sw = 0.25 * math.sin(t * 1.6)
    fx, fy = x + 30 * s, y + 26 * s
    ang = 1.15 + sw
    L = 75 * s
    tipx, tipy = fx + L * math.cos(ang) * -0.4 + L * 0.0, fy + L * math.sin(ang)
    fin = [(fx - 20 * s, fy), (fx + 20 * s, fy), (tipx + 30 * s, tipy), (tipx - 30 * s, tipy + 10 * s)]
    xr = ss(66.6, 68.0, t)
    dr.polygon(fin, fill=(150, 160, 130) if xr < 0.5 else (90, 110, 120), outline=(100, 110, 90))
    if xr > 0:
        def P(u, off=0.0): return (lerp(fx, tipx, u) + off * s, lerp(fy, tipy, u))
        c = mul((245, 245, 255), xr)
        dr.line((P(0.05), P(0.38)), fill=c, width=int(9 * xr) + 1)
        dr.line((P(0.42, -8), P(0.7, -12)), fill=c, width=int(7 * xr) + 1)
        dr.line((P(0.42, 8), P(0.7, 12)), fill=c, width=int(7 * xr) + 1)
        for j in range(5):
            dr.line((P(0.74, -16 + j * 8), P(0.95, -24 + j * 12)), fill=c, width=int(4 * xr) + 1)
    put(img, L_LOBE, x, y - 190, ss(70.8, 71.6, t))
    put(img, L_BONE, tipx + 40, tipy + 110, ss(67.0, 67.8, t))
    if t < 66.4:
        for j in range(8):
            jawfish(dr, (j * 160 + t * 40) % (W + 200) - 100, 1450 + (j % 3) * 70, 0.7, t + j, 0.5)
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def render(t):
    if t < 15.2: return dim(intro(t), 1 - ss(14.6, 15.2, t))
    if t < 36.4: return dim(head(t), ss(15.2, 15.8, t) * (1 - ss(35.8, 36.4, t)))
    if t < 45.0: return dim(fossil(t), ss(36.4, 37.0, t) * (1 - ss(44.4, 45.0, t)))
    if t < 62.0: return dim(rise(t), ss(45.0, 45.6, t) * (1 - ss(61.4, 62.0, t)))
    return dim(lobe(t), ss(62.0, 62.6, t))

CAPS = [(6.4, 10.6, '最早的脊椎动物没有下巴，嘴只是个圆孔'), (10.6, 14.8, '有的披上骨质盔甲来防身，叫甲胄鱼'),
        (15.4, 19.6, '鱼的喉咙两侧，有一排鳃弓'), (19.6, 23.8, '它们是支撑鳃的小骨条，原本用来呼吸'),
        (23.8, 28.0, '科学家认为，最前面那对鳃弓变大、前移'), (28.0, 32.2, '还能上下开合，变成了上颌和下颌'),
        (32.2, 36.2, '嘴边的硬鳞，也可能慢慢变成了牙齿'), (36.6, 40.8, '2022 年，科学家在重庆、贵州'),
        (40.8, 44.8, '发现了约 4.36 亿年前的有颌鱼化石'), (45.2, 49.4, '有了下巴，就能咬住、撕碎猎物'),
        (49.4, 53.6, '能吃的东西，一下子多了'), (53.6, 57.8, '有颌鱼迅速扩张，出现了 6 米长的邓氏鱼'),
        (57.8, 61.8, '没下巴的鱼大多灭绝，只剩七鳃鳗等少数'), (62.2, 66.4, '有颌鱼里，有一支很特别'),
        (66.4, 70.6, '它们的鳍里，长出了骨头和肌肉'), (70.6, 74.6, '叫肉鳍鱼，它们将要爬上陆地')]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep12_{ts}.png')
