import numpy as np, math, sys
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep11 import trilobite
from ep14 import permian, lizard

CLEAN = False
rng = np.random.default_rng(151)
yy = np.arange(H, dtype=np.float32)[:, None, None]
xx = np.arange(W, dtype=np.float32)[None, :, None]

def grad(top, bot, y0=0, y1=H):
    k = np.clip((yy - y0) / (y1 - y0), 0, 1)
    return np.clip(np.array(top) * (1 - k) + np.array(bot) * k, 0, 255) * np.ones((1, W, 1))
SPACE = grad((6, 10, 22), (14, 20, 34))
def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * max(k, 0)).astype(np.uint8))

# ---------- globe / Pangaea ----------
GX, GY, GR = 540, 1000, 430
# final x, final y, radius, start x, start y, seed
BLOBS = [(470, 760, 150, 290, 670, 0.3), (640, 740, 140, 780, 630, 1.7), (765, 845, 100, 880, 880, 2.9),
         (430, 960, 140, 350, 1010, 4.1), (480, 1140, 160, 320, 1260, 5.3), (645, 1200, 130, 730, 1310, 0.9)]
def blob_pts(x, y, r, sd, sc=1.0):
    return [(x * sc + r * sc * (1 + 0.16 * math.sin(3 * a + sd) + 0.09 * math.sin(5 * a + 2 * sd)) * math.cos(a),
             y * sc + r * sc * (1 + 0.16 * math.sin(3 * a + sd) + 0.09 * math.sin(5 * a + 2 * sd)) * math.sin(a))
            for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
def blob_pos(k):
    return [(lerp(sx, fx, k), lerp(sy, fy, k), r, sd) for fx, fy, r, sx, sy, sd in BLOBS]

_gcache = {}
HS = 0.5
gy2, gx2 = np.mgrid[0:int(H * HS), 0:int(W * HS)].astype(np.float32)
GMASK = ((gx2 - GX * HS) ** 2 + (gy2 - GY * HS) ** 2) <= (GR * HS) ** 2
def globe_base(k, dk):
    key = (round(k, 3), round(dk, 3))
    if key in _gcache: return _gcache[key]
    m = Image.new('L', (int(W * HS), int(H * HS)), 0); d = ImageDraw.Draw(m)
    for x, y, r, sd in blob_pos(k): d.polygon(blob_pts(x, y, r, sd, HS), fill=255)
    land = np.asarray(m) > 127
    dist = distance_transform_edt(land) / HS
    sh = (np.clip(1 - (((gx2 - (GX - 150) * HS) ** 2 + (gy2 - (GY - 180) * HS) ** 2) ** 0.5) / (GR * HS * 1.9), 0, 1) * 0.55 + 0.45)[..., None]
    ocean = np.array([30, 80, 140], np.float32) * sh
    base_land = np.array([125, 140, 85], np.float32)
    coast = np.array([80, 135, 70], np.float32); desert = np.array([220, 175, 110], np.float32)
    q = np.clip((dist - 25) / 90, 0, 1)[..., None]
    dl = coast * (1 - q) + desert * q
    landc = (base_land * (1 - dk) + dl * dk) * sh
    rgb = np.where(land[..., None], landc, ocean)
    edge = land & (dist < 4 / HS * HS + 1.5)
    rgb[edge] = rgb[edge] * 0.6 + np.array([230, 230, 200]) * 0.4
    out = Image.fromarray(np.where(GMASK[..., None], rgb, 0).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    am = Image.fromarray((GMASK * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    if len(_gcache) > 4: _gcache.clear()
    _gcache[key] = (out, am); return out, am

L_PANG = text_img('盘古大陆', FB, 52, (255, 225, 160), 4)
L_WET = text_img('海边：多雨', FM, 38, (200, 235, 255), 3); L_DRY = text_img('内陆：干旱', FB, 42, (255, 215, 150), 3)
L_SIB = text_img('西伯利亚', FB, 44, (255, 190, 150), 3); L_TETHYS = text_img('海洋', FM, 34, (180, 210, 240), 3)
def cloud(dr, x, y, s, a):
    for dx, dy, r in ((-40, 0, 36), (0, -18, 44), (42, 0, 34), (10, 12, 38)):
        dr.ellipse((x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s), fill=mul((235, 240, 245), a))
def globe(t):
    img = Image.fromarray(SPACE.astype(np.uint8))
    dr = ImageDraw.Draw(img)
    for i in range(70):
        sx, sy = (i * 389) % W, 520 + (i * 571) % (H - 520)
        if (sx - GX) ** 2 + (sy - GY) ** 2 > (GR + 30) ** 2: dr.point((sx, sy), fill=(200, 200, 220))
    k = ss(7.0, 16.0, t); dk = ss(23.4, 27.0, t)
    dr.ellipse((GX - GR - 14, GY - GR - 14, GX + GR + 14, GY + GR + 14), outline=(70, 120, 180), width=10)
    g, am = globe_base(k, dk)
    img.paste(g, (0, 0), am)
    dr = ImageDraw.Draw(img)
    put(img, L_PANG, 520, 960, ss(15.0, 15.8, t) * (1 - ss(22.8, 23.4, t)))
    put(img, L_TETHYS, 770, 1020, ss(15.4, 16.2, t) * (1 - ss(22.8, 23.4, t)))
    if 23.0 < t < 40.4:
        ca = ss(23.4, 24.2, t) * (1 - ss(31.2, 31.8, t))
        for i, (x0, y0, x1, y1) in enumerate(((180, 1250, 320, 1150), (930, 760, 760, 780), (250, 700, 360, 760))):
            q = ((t - 23.4) / 3.2 + i * 0.33) % 1
            cx, cy = lerp(x0, x1, q), lerp(y0, y1, q)
            s = 0.9 * (1 - 0.75 * q)
            cloud(dr, cx, cy, s, ca * (1 - 0.3 * q))
            for j in range(4):
                rx = cx - 30 * s + j * 20 * s
                dr.line((rx, cy + 40 * s, rx - 8, cy + 40 * s + 50 * (1 - q)), fill=mul((170, 210, 255), ca * (1 - q)), width=3)
        put(img, L_WET, 260, 1330, ca); put(img, L_DRY, 520, 1000, ca)
    if t > 40.0:
        a = ss(40.4, 41.2, t); p = 0.5 + 0.5 * math.sin(t * 5)
        x, y = 650, 700
        for r, c in ((60 + 14 * p, (255, 90, 40)), (30, (255, 180, 80))):
            dr.ellipse((x - r, y - r, x + r, y + r), outline=mul(c, a), width=6)
        dr.ellipse((x - 14, y - 14, x + 14, y + 14), fill=mul((255, 220, 120), a))
        put(img, L_SIB, x, y - 110, a)
    return img

# ---------- Permian desert ----------
DESERT_SKY = grad((235, 170, 95), (255, 225, 165), 480, 1100)
L_DIM = text_img('异齿龙 · 背上长帆', FB, 44, (255, 235, 200), 3); L_THER = text_img('兽孔类：腿更直，更像哺乳动物', FB, 40, (255, 235, 200), 3)
def dimetrodon(dr, x, y, s, t, a=1.0):
    walk = math.sin(t * 5)
    sail = [(x - 110 * s + 220 * s * u, y - 30 * s - 150 * s * math.sin(math.pi * u) ** 0.8) for u in np.linspace(0, 1, 24)]
    dr.polygon([(x - 110 * s, y - 20 * s)] + sail + [(x + 110 * s, y - 20 * s)], fill=mul((200, 110, 80), a), outline=mul((120, 60, 45), a))
    for u in np.linspace(0.08, 0.92, 11):
        px = x - 110 * s + 220 * s * u
        dr.line((px, y - 25 * s, px, y - 30 * s - 150 * s * math.sin(math.pi * u) ** 0.8), fill=mul((130, 70, 50), a), width=max(2, int(3 * s)))
    dr.polygon([(x - 130 * s, y - 15 * s), (x - 330 * s, y + 20 * s), (x - 130 * s, y + 20 * s)], fill=mul((140, 110, 80), a))
    dr.ellipse((x - 150 * s, y - 40 * s, x + 150 * s, y + 40 * s), fill=mul((150, 120, 85), a), outline=mul((90, 70, 50), a))
    dr.ellipse((x + 120 * s, y - 45 * s, x + 230 * s, y + 15 * s), fill=mul((150, 120, 85), a), outline=mul((90, 70, 50), a))
    dr.ellipse((x + 185 * s, y - 35 * s, x + 199 * s, y - 21 * s), fill=mul((30, 25, 20), a))
    for i, lx in enumerate((x + 90 * s, x - 90 * s)):
        ph = walk if i == 0 else -walk
        dr.line((lx, y + 20 * s, lx + 40 * s + 20 * s * ph, y + 40 * s), fill=mul((130, 100, 70), a), width=int(16 * s))
        dr.line((lx + 40 * s + 20 * s * ph, y + 40 * s, lx + 30 * s + 20 * s * ph, y + 85 * s), fill=mul((130, 100, 70), a), width=int(14 * s))
def therapsid(dr, x, y, s, t, a=1.0, face=-1):
    walk = math.sin(t * 6)
    dr.polygon([(x - face * 130 * s, y - 10 * s), (x - face * 230 * s, y + 10 * s), (x - face * 130 * s, y + 20 * s)], fill=mul((120, 95, 70), a))
    dr.ellipse((x - 150 * s, y - 50 * s, x + 150 * s, y + 50 * s), fill=mul((135, 105, 75), a), outline=mul((80, 60, 40), a))
    hx = x + face * 170 * s
    dr.ellipse((hx - 70 * s, y - 70 * s, hx + 70 * s, y + 10 * s), fill=mul((140, 110, 80), a), outline=mul((80, 60, 40), a))
    dr.polygon([(hx + face * 40 * s, y - 5 * s), (hx + face * 50 * s, y + 35 * s), (hx + face * 60 * s, y - 5 * s)], fill=mul((245, 240, 225), a))
    dr.ellipse((hx + face * 15 * s - 8 * s, y - 50 * s, hx + face * 15 * s + 8 * s, y - 34 * s), fill=mul((25, 20, 20), a))
    for i, lx in enumerate((x + 95 * s, x - 95 * s)):
        ph = walk if i == 0 else -walk
        dr.line((lx, y + 30 * s, lx + 18 * s * ph, y + 110 * s), fill=mul((115, 90, 65), a), width=int(22 * s))
def desert(t):
    img = Image.fromarray(DESERT_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.ellipse((760, 560, 900, 700), fill=(255, 245, 210))
    dr.polygon([(0, 1050), (250, 960), (520, 1040), (800, 940), (W, 1010), (W, H), (0, H)], fill=(215, 170, 110))
    dr.polygon([(0, 1150), (380, 1090), (760, 1160), (W, 1110), (W, H), (0, H)], fill=(200, 150, 95))
    for i in range(14):
        x0 = (i * 173) % W; y0 = 1250 + (i * 97) % 300
        dr.line((x0, y0, x0 + 60, y0 + 18, x0 + 100, y0 - 6), fill=(160, 115, 70), width=3)
    for x in (120, 960):
        dr.line((x, 1130, x, 1040), fill=(110, 120, 70), width=8)
        for j in range(4): dr.line((x, 1060 + j * 18, x + (-1) ** j * 40, 1040 + j * 18), fill=(110, 130, 70), width=6)
    dimetrodon(dr, lerp(-200, 520, ss(31.8, 36.6, t)), 1260, 1.25, t)
    put(img, L_DIM, 540, 800, ss(32.6, 33.4, t) * (1 - ss(35.8, 36.2, t)))
    if t > 36.0:
        therapsid(dr, lerp(1300, 760, ss(36.0, 39.6, t)), 1420, 0.95, t)
        put(img, L_THER, 540, 800, ss(36.8, 37.6, t))
    return img

# ---------- underground section ----------
SURF = 660
LAYERS = [(SURF, 720, (150, 115, 80), None), (720, 790, (190, 160, 115), None), (790, 860, (30, 28, 28), '煤层（上一集的煤）'),
          (860, 930, (140, 120, 100), None), (930, 1010, (205, 205, 195), '石灰岩'), (1010, 1240, (120, 70, 50), None)]
L_LAYERS = {n: text_img(n, FM, 34, (250, 240, 220), 3) for _, _, _, n in LAYERS if n}
L_MANTLE = text_img('地幔深处', FM, 34, (255, 210, 170), 3); L_PLUME = text_img('地幔柱：一股热流往上升', FB, 40, (255, 200, 120), 3)
L_LAVA = text_img('岩浆涌出地面', FB, 40, (255, 210, 140), 3); L_BASALT = text_img('冷却成一层层黑色岩石', FB, 40, (235, 235, 235), 3)
L_BURN = text_img('煤层被烧着', FB, 40, (255, 200, 120), 3); L_LIME = text_img('石灰岩被烤透', FB, 40, (240, 240, 230), 3)
L_CO2 = text_img('二氧化碳', FB, 40, (235, 235, 240), 3)
SEC_SKY = grad((70, 80, 100), (150, 140, 130), 500, SURF)
def section(t):
    hz = ss(62.0, 70.0, t)
    sky = SEC_SKY * (1 - hz) + grad((120, 70, 50), (210, 120, 70), 500, SURF) * hz
    img = Image.fromarray(sky.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, 1240, W, H), fill=(14, 12, 12))
    for y0, y1, c, n in LAYERS:
        dr.rectangle((0, y0, W, y1), fill=c)
    for y in range(1010, 1240, 6):
        q = (y - 1010) / 230
        dr.line((0, y, W, y), fill=(int(120 + 110 * q), int(70 + 30 * q), int(50 - 20 * q)), width=6)
    # plume
    pk = ss(44.8, 48.6, t)
    if pk > 0:
        hy = lerp(1300, 1060, pk)
        dr.rectangle((470, min(hy, 1240), 610, 1240), fill=(255, 120, 50))
        dr.ellipse((400, hy - 60, 680, hy + 60), fill=(255, 140, 60), outline=(255, 210, 120), width=4)
    # dykes and lava
    dkk = ss(49.0, 51.0, t)
    if dkk > 0:
        for x0, x1 in ((500, 430), (540, 560), (580, 700)):
            yt = lerp(1060, SURF, dkk)
            dr.line((x0, 1060, lerp(x0, x1, dkk), yt), fill=(255, 150, 60), width=12)
    lv = ss(50.6, 53.6, t)
    nb = ss(53.2, 57.0, t)
    if lv > 0:
        for j in range(4):
            if nb * 4 > j:
                th = 22 * min(1, nb * 4 - j)
                y1 = SURF - j * 22
                dr.rectangle((540 - 540 * lv, y1 - th, 540 + 540 * lv, y1), fill=(35, 33, 36) if j < 3 or nb > 0.95 else (60, 40, 35))
                dr.line((540 - 540 * lv, y1 - th, 540 + 540 * lv, y1 - th), fill=(70, 68, 72), width=2)
        ytop = SURF - 22 * min(4, nb * 4)
        hot = (1 - nb) * 0.9 + 0.1
        dr.rectangle((540 - 540 * lv, ytop - 10, 540 + 540 * lv, ytop), fill=mul((255, 120, 40), hot))
    # sills into coal / limestone
    sk = ss(57.6, 59.6, t); lk = ss(61.8, 63.6, t)
    if sk > 0:
        dr.rectangle((540 - 480 * sk, 815, 540 + 480 * sk, 835), fill=(255, 140, 50))
        gl = 0.5 + 0.5 * math.sin(t * 7)
        for i in range(12):
            x = 80 + i * 85
            if abs(x - 540) < 480 * sk:
                dr.ellipse((x - 20, 800 + 10 * gl, x + 20, 840 - 10 * gl), fill=(255, int(150 + 60 * gl), 60))
    if lk > 0:
        dr.rectangle((540 - 480 * lk, 960, 540 + 480 * lk, 980), fill=(255, 150, 60))
    bk = max(ss(58.6, 59.6, t), 0)
    if bk > 0:
        nbub = 10 + int(14 * lk)
        for i in range(nbub):
            q = (t * 0.22 + i / nbub) % 1
            src = 825 if i % 2 == 0 or lk == 0 else 970
            x = 100 + (i * 197) % 880 + 20 * math.sin(t * 2 + i)
            y = lerp(src, 480, q)
            r = 12 + 10 * q
            dr.ellipse((x - r, y - r, x + r, y + r), fill=mul((150, 150, 155), bk * (1 - 0.5 * q)), outline=mul((215, 215, 220), bk * (1 - 0.5 * q)), width=2)
    for y0, y1, c, n in LAYERS:
        if n: put(img, L_LAYERS[n], 200 if n.startswith('煤') else 160, (y0 + y1) / 2, 1 - ss(57.0, 57.6, t) if n.startswith('煤') else 1 - ss(61.2, 61.8, t))
    put(img, L_MANTLE, 900, 1200, 1 - ss(48.0, 48.6, t))
    put(img, L_PLUME, 540, 1170 if pk < 0.5 else 1180, ss(45.4, 46.2, t) * (1 - ss(48.6, 49.0, t)))
    put(img, L_LAVA, 540, 560, ss(50.6, 51.4, t) * (1 - ss(53.0, 53.4, t)))
    put(img, L_BASALT, 540, 560, ss(53.6, 54.4, t) * (1 - ss(57.0, 57.4, t)))
    put(img, L_BURN, 760, 760, ss(58.0, 58.8, t) * (1 - ss(61.4, 61.8, t)))
    put(img, L_LIME, 760, 900, ss(62.2, 63.0, t) * (1 - ss(65.6, 66.0, t)))
    put(img, L_CO2, 540, 560, ss(59.4, 60.2, t) * (1 - ss(65.6, 66.0, t)))
    return img

# ---------- indicator bars ----------
L_B = [text_img(s_, FB, 36, c, 3) for s_, c in (('二氧化碳', (255, 170, 150)), ('温度', (255, 200, 120)), ('海水氧气', (160, 210, 255)))]
L_UP = text_img('升高', FM, 32, (255, 200, 170), 3); L_DN = text_img('下降', FM, 32, (170, 210, 255), 3)
def bars(img, t, a):
    if a <= 0: return
    arr = np.asarray(img, np.float32).copy()
    arr[1250:1500, 40:1040] = arr[1250:1500, 40:1040] * (1 - 0.65 * a) + np.array([10, 14, 20]) * 0.65 * a
    img.paste(Image.fromarray(arr.astype(np.uint8))); dr = ImageDraw.Draw(img)
    vals = [0.22 + 0.68 * ss(58.6, 68.0, t), 0.3 + 0.6 * ss(64.0, 72.0, t), 0.8 - 0.62 * ss(70.4, 78.0, t)]
    cols = [(240, 90, 70), (250, 160, 60), (90, 160, 240)]
    for i, (v, c) in enumerate(zip(vals, cols)):
        y = 1300 + i * 75
        put(img, L_B[i], 160, y, a)
        dr.rounded_rectangle((280, y - 16, 900, y + 16), radius=16, fill=mul((40, 45, 55), a))
        dr.rounded_rectangle((280, y - 16, 280 + 620 * v, y + 16), radius=16, fill=mul(c, a))
    put(img, L_UP, 965, 1300, a * ss(60.0, 61.0, t)); put(img, L_UP, 965, 1375, a * ss(66.0, 67.0, t)); put(img, L_DN, 965, 1450, a * ss(72.0, 73.0, t))

# ---------- ocean ----------
L_SODA = text_img('像温热的汽水：气体留不住', FB, 40, (235, 245, 255), 3)
L_LOWO2 = text_img('缺氧', FB, 44, (200, 220, 255), 3)
L_ACID = text_img('二氧化碳溶进海水 → 海水变酸', FB, 40, (255, 230, 180), 3)
L_SHELL = text_img('贝壳、珊瑚被溶掉', FB, 40, (255, 230, 200), 3)
SEA_A = grad((40, 110, 160), (10, 40, 70), 560, 1250); SEA_B = grad((90, 110, 80), (30, 40, 30), 560, 1250)
FISH = [(rng.random() * W, 650 + rng.random() * 420, 0.7 + rng.random() * 0.6, rng.random() * 6, (1 if rng.random() > 0.5 else -1)) for _ in range(7)]
def fishd(dr, x, y, s, f, c):
    dr.ellipse((x - 50 * s, y - 20 * s, x + 50 * s, y + 20 * s), fill=c)
    dr.polygon([(x - f * 45 * s, y), (x - f * 85 * s, y - 24 * s), (x - f * 85 * s, y + 24 * s)], fill=c)
    dr.ellipse((x + f * 28 * s - 5 * s, y - 8 * s, x + f * 28 * s + 5 * s, y + 2 * s), fill=(20, 20, 25))
def ammonite(dr, x, y, s, a):
    for r in (40, 28, 18, 9):
        dr.ellipse((x - r * s, y - r * s, x + r * s, y + r * s), outline=mul((235, 215, 180), a), width=max(2, int(5 * s)))
def coral(dr, x, y, s, a):
    def br(px, py, ang, L, d):
        if d == 0: return
        ex, ey = px + L * math.cos(ang), py - L * math.sin(ang)
        dr.line((px, py, ex, ey), fill=mul((240, 140, 130), a), width=max(2, int(d * 3 * s)))
        br(ex, ey, ang + 0.45, L * 0.72, d - 1); br(ex, ey, ang - 0.45, L * 0.72, d - 1)
    br(x, y, math.pi / 2, 70 * s, 4)
def ocean(t):
    w = ss(70.2, 86.0, t)
    img = Image.fromarray((SEA_A * (1 - w) + SEA_B * w).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, 500, W, 560), fill=tuple(int(v) for v in lerp(np.array([150, 190, 220]), np.array([220, 150, 100]), w)))
    for x in range(0, W, 60):
        dr.arc((x, 545, x + 60, 575), 180, 360, fill=(220, 235, 245), width=3)
    FL_ = 1180
    dr.rectangle((0, FL_, W, 1250), fill=(110, 95, 75))
    o2 = 1 - ss(70.4, 78.0, t)
    for i in range(26):
        q = (t * 0.35 + i / 26) % 1
        x = (i * 151) % W + 10 * math.sin(t * 3 + i)
        y = lerp(FL_ - 20, 520, q)
        if y < 560 and t > 70.4: continue
        a = o2 if i % 3 else max(o2, 0.25)
        dr.ellipse((x - 7, y - 7, x + 7, y + 7), outline=mul((230, 245, 255), a), width=2)
    for i, (fx, fy, s, ph, f) in enumerate(FISH):
        sick = ss(74.6 + i * 0.4, 77.6 + i * 0.4, t) if i < 5 else 0
        x = (fx + f * (t - 70) * 60 * (1 - 0.8 * sick)) % (W + 200) - 100
        y = fy + 15 * math.sin(t * 2 + ph) + sick * (FL_ - 40 - fy) * ss(77.0, 82.0, t)
        c = tuple(int(v) for v in lerp(np.array([210, 180, 120]), np.array([120, 120, 115]), sick))
        fishd(dr, x, y, s, f, c)
    if t > 78.4:
        ck = ss(78.6, 79.6, t)
        for i in range(14):
            q = (t * 0.3 + i / 14) % 1
            x = 40 + i * 75; y = lerp(560, 1100, q)
            dr.ellipse((x - 10, y - 10, x + 10, y + 10), fill=mul((150, 150, 155), ck * (1 - q)))
    dk_ = 1 - 0.85 * ss(83.0, 86.6, t)
    for x in (140, 420, 700, 950):
        coral(dr, x, FL_, 1.0 * (0.4 + 0.6 * dk_), dk_)
    for x in (280, 560, 830):
        ammonite(dr, x, FL_ - 50, 1.0 * (0.5 + 0.5 * dk_), dk_)
    for x in (60, 360, 640, 900):
        trilobite(dr, x, FL_ - 20, 0.7, 1.0 - 0.4 * ss(75, 80, t))
    put(img, L_SODA, 540, 640, ss(70.8, 71.6, t) * (1 - ss(74.0, 74.5, t)))
    put(img, L_LOWO2, 540, 640, ss(74.8, 75.6, t) * (1 - ss(78.2, 78.6, t)))
    put(img, L_ACID, 540, 640, ss(79.0, 79.8, t) * (1 - ss(82.6, 83.0, t)))
    put(img, L_SHELL, 540, 640, ss(83.2, 84.0, t))
    return img

# ---------- dying forest ----------
L_ACIDR = text_img('酸雨 · 干旱', FB, 44, (240, 240, 200), 3); L_DEAD = text_img('森林大片死去', FB, 44, (240, 220, 190), 3)
DF_SKY = grad((110, 100, 80), (190, 150, 100), 480, 1100)
def deadforest(t):
    img = Image.fromarray(DF_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.polygon([(0, 1130), (W, 1090), (W, H), (0, H)], fill=(140, 110, 80))
    for i in range(10):
        x0 = (i * 157) % W; y0 = 1200 + (i * 71) % 250
        dr.line((x0, y0, x0 + 50, y0 + 20, x0 + 90, y0 - 4), fill=(100, 75, 55), width=3)
    dk = ss(87.4, 90.4, t)
    for i, x in enumerate((110, 300, 500, 700, 900)):
        h = 380 + (i % 3) * 60; base = 1120
        c = tuple(int(v) for v in lerp(np.array([85, 70, 50]), np.array([110, 100, 90]), dk))
        dr.line((x, base, x, base - h), fill=c, width=18)
        for j in range(4):
            yb = base - h * (0.55 + j * 0.12)
            dr.line((x, yb, x + (-1) ** j * 90, yb - 60), fill=c, width=7)
        lc = tuple(int(v) for v in lerp(np.array([70, 120, 60]), np.array([150, 120, 70]), dk))
        if dk < 0.98:
            r = 80 * (1 - dk)
            dr.ellipse((x - r, base - h - r * 0.6, x + r, base - h + r * 0.6), fill=lc)
    for i in range(60):
        q = (t * 1.3 + i / 60) % 1
        x = (i * 97) % W + q * 60; y = lerp(500, 1150, q)
        dr.line((x, y, x + 12, y + 34), fill=(200, 210, 150), width=2)
    put(img, L_ACIDR, 540, 620, ss(87.4, 88.2, t)); put(img, L_DEAD, 540, 700, ss(88.6, 89.4, t))
    return img

# ---------- extinction tally ----------
L_SEA = text_img('海洋物种：约九成消失', FB, 42, (180, 215, 255), 3)
L_LANDV = text_img('陆地脊椎动物：约七成消失', FB, 42, (255, 215, 170), 3)
L_TRI = text_img('三叶虫 · 在海底生活了近 3 亿年', FB, 40, (240, 225, 200), 3); L_GONE = text_img('从此绝迹', FB, 56, (255, 140, 120), 4)
L_WORST = text_img('二叠纪末大灭绝', FB, 56, (255, 200, 160), 4)
def tally(t):
    img = Image.fromarray(grad((16, 14, 20), (34, 20, 18)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 95.6:
        for row in range(2):
            n_dead = 9 if row == 0 else 7
            for i in range(10):
                x = 160 + (i % 5) * 190; y = (730 if row == 0 else 1150) + (i // 5) * 150
                dk = ss(92.4 + i * 0.12 + row * 0.6, 93.4 + i * 0.12 + row * 0.6, t) if i < n_dead else 0
                a = 1 - 0.75 * dk
                if row == 0:
                    if i % 3 == 0 and i < 9: trilobite(dr, x, y, 1.0, a)
                    elif i % 3 == 1 and i < 9: ammonite(dr, x, y, 1.3, a)
                    else: fishd(dr, x, y, 1.1, 1, mul((200, 175, 120), a))
                else:
                    therapsid(dr, x - 10, y - 10, 0.32, 0, a, face=1)
                if dk > 0.5:
                    dr.line((x - 50, y - 50, x + 50, y + 50), fill=mul((220, 70, 60), dk), width=6)
                    dr.line((x - 50, y + 50, x + 50, y - 50), fill=mul((220, 70, 60), dk), width=6)
        put(img, L_SEA, 540, 610, ss(91.6, 92.4, t)); put(img, L_LANDV, 540, 1030, ss(92.4, 93.2, t))
        return img
    if t < 100.0:
        gk = ss(96.6, 99.0, t)
        img = Image.fromarray(grad((30, 60, 80), (12, 26, 36)).astype(np.uint8)); dr = ImageDraw.Draw(img)
        trilobite(dr, 540, 960, 4.0, 1 - 0.55 * gk)
        put(img, L_TRI, 540, 680, ss(95.8, 96.6, t)); put(img, L_GONE, 540, 1260, ss(97.4, 98.2, t))
        return img
    img = Image.fromarray(grad((60, 30, 30), (150, 80, 60), 480, 1100).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.polygon([(0, 1100), (400, 1060), (W, 1110), (W, H), (0, H)], fill=(95, 70, 55))
    for x in (180, 520, 860):
        dr.line((x, 1090, x - 10, 940), fill=(70, 60, 55), width=10); dr.line((x - 5, 1000, x + 50, 960), fill=(70, 60, 55), width=5)
    put(img, L_WORST, 540, 700, ss(100.2, 101.0, t))
    return img

# ---------- survivors ----------
L_SMALL = text_img('个子小', FB, 42, (255, 235, 200), 3); L_DIG = text_img('会挖洞', FB, 42, (255, 235, 200), 3); L_ALL = text_img('什么都吃', FB, 42, (255, 235, 200), 3)
L_LYS = text_img('水龙兽', FB, 46, (255, 225, 160), 3); L_EVERY = text_img('遍布各块大陆', FM, 36, (240, 235, 220), 3)
L_CYN = text_img('犬齿兽', FB, 46, (255, 225, 160), 3)
L_LINE = text_img('犬齿兽 → 哺乳动物 → 你', FB, 46, (255, 225, 160), 4)
L_DINO = text_img('爬行类的一支：恐龙', FB, 42, (210, 235, 200), 3)
TRI_SKY = grad((200, 150, 110), (240, 210, 170), 480, 1100)
GROUND = 1180
def lystro(dr, x, y, s, t, a=1.0, face=1):
    walk = math.sin(t * 6)
    for i, lx in enumerate((x + 60 * s, x - 60 * s)):
        ph = walk if i == 0 else -walk
        dr.line((lx, y + 30 * s, lx + 12 * s * ph, y + 80 * s), fill=mul((120, 95, 70), a), width=int(26 * s))
    dr.ellipse((x - 120 * s, y - 60 * s, x + 120 * s, y + 55 * s), fill=mul((160, 130, 95), a), outline=mul((90, 70, 50), a))
    hx = x + face * 130 * s
    dr.ellipse((hx - 55 * s, y - 55 * s, hx + 55 * s, y + 25 * s), fill=mul((165, 135, 100), a), outline=mul((90, 70, 50), a))
    dr.polygon([(hx + face * 40 * s, y - 10 * s), (hx + face * 75 * s, y + 20 * s), (hx + face * 40 * s, y + 20 * s)], fill=mul((140, 115, 85), a))
    dr.polygon([(hx + face * 25 * s, y + 15 * s), (hx + face * 33 * s, y + 50 * s), (hx + face * 41 * s, y + 15 * s)], fill=mul((245, 240, 225), a))
    dr.ellipse((hx - 6 * s, y - 38 * s, hx + 8 * s, y - 24 * s), fill=mul((25, 20, 20), a))
def cynodont(dr, x, y, s, t, a=1.0, face=1):
    walk = math.sin(t * 9)
    dr.line((x - face * 70 * s, y, x - face * 190 * s, y + 20 * s), fill=mul((110, 85, 65), a), width=int(12 * s))
    for i, lx in enumerate((x + 45 * s, x - 45 * s)):
        ph = walk if i == 0 else -walk
        dr.line((lx, y + 15 * s, lx + 10 * s * ph, y + 50 * s), fill=mul((100, 78, 60), a), width=int(12 * s))
    dr.ellipse((x - 80 * s, y - 28 * s, x + 80 * s, y + 28 * s), fill=mul((125, 95, 72), a))
    hx = x + face * 95 * s
    dr.polygon([(hx - face * 25 * s, y - 30 * s), (hx + face * 50 * s, y), (hx - face * 25 * s, y + 20 * s)], fill=mul((130, 100, 76), a))
    dr.ellipse((hx - 4 * s, y - 18 * s, hx + 6 * s, y - 8 * s), fill=mul((20, 15, 15), a))
    dr.polygon([(hx - face * 18 * s, y - 28 * s), (hx - face * 8 * s, y - 46 * s), (hx, y - 26 * s)], fill=mul((120, 90, 70), a))
    for j in (-1, 1):
        dr.line((hx + face * 42 * s, y, hx + face * 70 * s, y + j * 10 * s), fill=mul((230, 220, 200), a), width=1)
def mini_pangaea(dr, cx, cy, sc, a):
    for x, y, r, sd in blob_pos(1.0):
        dr.polygon([(cx + (px - GX) * sc, cy + (py - GY) * sc) for px, py in blob_pts(x, y, r, sd)], fill=mul((215, 180, 120), a))
def survivors(t):
    img = Image.fromarray(TRI_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.polygon([(0, GROUND - 40), (500, GROUND - 10), (W, GROUND - 50), (W, H), (0, H)], fill=(185, 140, 95))
    for x in (90, 980):
        for j in range(5):
            dr.line((x, GROUND - 30, x + (j - 2) * 30, GROUND - 120 + abs(j - 2) * 20), fill=(110, 130, 80), width=6)
    for bx in (260, 820):
        dr.ellipse((bx - 70, GROUND + 40, bx + 70, GROUND + 100), fill=(70, 50, 35))
    a0 = ss(104.3, 105.2, t)
    put(img, L_SMALL, 230, 620, a0 * (1 - ss(108.0, 108.4, t)))
    put(img, L_DIG, 540, 620, ss(105.4, 106.2, t) * (1 - ss(108.0, 108.4, t)))
    put(img, L_ALL, 850, 620, ss(106.4, 107.2, t) * (1 - ss(108.0, 108.4, t)))
    lx = lerp(-260, 420, ss(104.4, 109.0, t))
    lystro(dr, lx, GROUND + 20, 1.1, t)
    mk = ss(108.6, 109.6, t) * (1 - ss(112.2, 112.7, t))
    if mk > 0:
        cx, cy, sc = 790, 790, 0.42
        dr.rounded_rectangle((cx - 230, cy - 270, cx + 230, cy + 250), radius=24, fill=mul((30, 70, 110), mk), outline=mul((200, 220, 240), mk), width=3)
        mini_pangaea(dr, cx, cy, sc, mk)
        sp = ss(109.0, 112.0, t)
        for i in range(22):
            ang = i * 2.39; rr = (0.15 + 0.85 * ((i * 0.37) % 1)) * sp
            bx, by = BLOBS[i % 6][0], BLOBS[i % 6][1]
            px = cx + (bx - GX + 90 * rr * math.cos(ang)) * sc; py = cy + (by - GY + 90 * rr * math.sin(ang)) * sc
            if sp > i / 22: dr.ellipse((px - 6, py - 6, px + 6, py + 6), fill=mul((200, 60, 50), mk))
        put(img, L_EVERY, cx, cy + 290, mk)
    put(img, L_LYS, lx + 10, GROUND - 120, ss(108.6, 109.4, t) * (1 - ss(112.4, 112.8, t)))
    ck = ss(112.6, 113.4, t)
    if ck > 0:
        cx_ = lerp(820, 700, ss(112.8, 115.0, t)) if t < 124 else 700 + 20 * math.sin(t * 1.5)
        cynodont(dr, cx_, GROUND + 30, 0.95, t if t < 115 else 115, ck, face=-1)
        put(img, L_CYN, 760, GROUND - 90, ck * (1 - ss(116.6, 117.0, t)))
    put(img, L_LINE, 540, 640, ss(117.0, 117.8, t) * (1 - ss(120.8, 121.2, t)))
    dk = ss(121.2, 123.4, t)
    if dk > 0:
        sh = ss(122.0, 125.0, t)
        dr.ellipse((300 - 260 * sh, GROUND + 20, 300 + 260 * sh, GROUND + 90), fill=(150, 110, 75))
        fy = lerp(470, GROUND + 40, ss(123.0, 125.5, t))
        if fy - 60 > 470: dr.rectangle((230, 470, 370, fy - 60), fill=mul((80, 100, 70), dk))
        for j in (-1, 0, 1):
            dr.polygon([(300 + j * 45 - 25, fy - 70), (300 + j * 85, fy + 10), (300 + j * 45 + 25, fy - 70)], fill=mul((80, 100, 70), dk))
            dr.polygon([(300 + j * 85 - 8, fy + 2), (300 + j * 95, fy + 30), (300 + j * 85 + 10, fy)], fill=mul((40, 40, 35), dk))
        put(img, L_DINO, 720, 700, ss(121.4, 122.2, t) * (1 - ss(125.6, 126.0, t)))
    return img

def render(t):
    if t < 6.0: return permian(99.9 + t)
    if t < 31.8: return dim(globe(t), ss(6.0, 6.6, t) * (1 - ss(31.2, 31.8, t)))
    if t < 40.4: return dim(desert(t), ss(31.8, 32.4, t) * (1 - ss(39.8, 40.4, t)))
    if t < 44.6: return dim(globe(t), ss(40.4, 41.0, t) * (1 - ss(44.0, 44.6, t)))
    if t < 70.2: img = dim(section(t), ss(44.6, 45.2, t) * (1 - ss(69.6, 70.2, t)))
    elif t < 87.0: img = dim(ocean(t), ss(70.2, 70.8, t) * (1 - ss(86.4, 87.0, t)))
    elif t < 91.4: img = dim(deadforest(t), ss(87.0, 87.6, t) * (1 - ss(90.8, 91.4, t)))
    elif t < 104.2: return dim(tally(t), ss(91.4, 92.0, t) * (1 - ss(95.2, 95.6, t) if t < 95.6 else ss(95.6, 96.2, t) * (1 - ss(99.6, 100.0, t)) if t < 100.0 else ss(100.0, 100.6, t) * (1 - ss(103.6, 104.2, t))))
    else: return dim(survivors(t), ss(104.2, 104.8, t))
    if 61.8 < t < 91.4:
        k = ss(61.8, 62.6, t) * (1 - ss(90.6, 91.2, t))
        if 69.6 < t < 70.8: k *= 1 - 0.85 * math.sin(math.pi * (t - 69.6) / 1.2)
        if 86.4 < t < 87.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 86.4) / 1.2)
        bars(img, t, k)
    return img

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep15_{ts}.png')
