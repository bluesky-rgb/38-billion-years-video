import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, CY, ss, lerp, text_img, put, bg, D, blend, rocky, geom, N1, CL, MN, FM, FB, fbm
from ep2 import sprite, add_sprite
from ep4 import sea, mul

CLEAN = False
rng = np.random.default_rng(81)

# ---------- icy earth ----------
def earth_ice(R, rot, ic, clouds=0.4, green=0.0):
    x, y, z, u, v, lam, a = geom(R, rot)
    n1 = N1[v, u]
    land = np.array([110, 92, 78]) * (0.7 + 0.5 * n1[..., None])
    sea_m = np.clip((0.66 - n1) * 12, 0, 1)[..., None]
    sea = lerp(np.array([8, 30, 70]), np.array([22, 72, 125]), (n1 / 0.66).clip(0, 1)[..., None])
    sea = sea * (1 - green) + np.array([20, 95, 105]) * green
    col = land * (1 - sea_m) + sea * sea_m
    ice = np.clip((np.abs(y) + 0.10 * (n1 - 0.5) - (1 - ic * 1.2)) * 9, 0, 1)[..., None]
    col = col * (1 - ice) + np.array([232, 240, 250]) * ice
    col = col * (0.06 + 0.94 * lam[..., None])
    c = CL[v, u]; ca = (np.clip((c - 0.5) * 4, 0, 1) * clouds)[..., None]
    col = col * (1 - ca) + np.array([230, 232, 238]) * (0.12 + 0.88 * lam[..., None]) * ca
    col = col + ((1 - z) ** 3)[..., None] * np.array([150, 180, 240]) * 0.7
    return col, a

def co2_level(t): return float(np.interp(t, [0, 15, 32, 54, 64, 76, 100], [0.7, 0.7, 0.28, 0.22, 0.95, 0.62, 0.62]))
def temp_level(t): return float(np.interp(t, [0, 15, 32, 44, 62, 68, 100], [0.62, 0.62, 0.45, 0.08, 0.08, 0.72, 0.62]))
L_CO2 = text_img('二氧化碳', FM, 34, (215, 215, 220), 2); L_T = text_img('温度', FM, 34, (215, 215, 220), 2)
def gauges(img, t, a):
    if a <= 0: return
    dr = ImageDraw.Draw(img)
    for i, (lab, val, col) in enumerate(((L_CO2, co2_level(t), (190, 190, 200)), (L_T, temp_level(t), None))):
        y = 1360 + i * 70
        put(img, lab, 230, y, a)
        x0, x1 = 320, 900
        dr.rounded_rectangle((x0, y - 14, x1, y + 14), radius=14, fill=mul((25, 30, 40), a), outline=mul((90, 100, 115), a), width=2)
        c = col or tuple(int(v) for v in lerp(np.array([110, 170, 255]), np.array([255, 120, 60]), val))
        dr.rounded_rectangle((x0 + 3, y - 11, x0 + 3 + (x1 - x0 - 6) * val, y + 11), radius=11, fill=mul(c, a))

# ---------- map: supercontinent breaking ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
MCX, MCY = 540, 820
nz = np.asarray(Image.fromarray((fbm(5, 91, 4)[:, 200:600] * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
dd = np.sqrt((xx - MCX) ** 2 + ((yy - MCY) * 0.9) ** 2)
land = (dd < 330 + 140 * (nz - 0.5)).astype(np.float32)
ang = (np.arctan2(yy - MCY, xx - MCX) + 0.35 + 0.9 * (nz - 0.5)) % (2 * np.pi)
PIECES = []
for k in range(4):
    m = land * ((ang >= k * np.pi / 2) & (ang < (k + 1) * np.pi / 2))
    mid = k * np.pi / 2 + np.pi / 4 - 0.35
    PIECES.append((m, math.cos(mid), math.sin(mid)))
ocean_bg = np.array([25, 80, 140]) * (0.85 + 0.3 * nz[..., None])
land_col = np.array([120, 98, 78]) * (0.75 + 0.5 * nz[..., None])
RAIN = [(rng.random() * W, 380 + rng.random() * 900, rng.random()) for _ in range(260)]
CO2D = [(rng.random() * W, rng.random(), rng.random()) for _ in range(90)]
L_SUP = text_img('超级大陆', FB, 48, (240, 225, 200), 4)

def shifted(m, dx, dy):
    return np.roll(np.roll(m, int(dy), 0), int(dx), 1)

def map_scene(t):
    d = lerp(0, 150, ss(15.6, 21.0, t))
    f = ocean_bg.copy()
    lm = np.zeros((H, W), np.float32)
    for m, cx, cy in PIECES:
        lm = np.maximum(lm, shifted(m, cx * d, cy * d))
    cool = ss(28.0, 32.0, t)
    lc = land_col * (1 - 0.35 * cool) + np.array([200, 210, 225]) * 0.35 * cool
    f = f * (1 - lm[..., None]) + lc * lm[..., None]
    edge = np.clip(lm - np.roll(lm, 4, 0) * np.roll(lm, -4, 0) * np.roll(lm, 4, 1) * np.roll(lm, -4, 1), 0, 1)
    f = f + edge[..., None] * np.array([200, 220, 200]) * 0.5
    f = f * (1 - 0.2 * cool) + np.array([220, 230, 245]) * 0.2 * cool
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    ra = ss(19.6, 20.6, t)
    if ra > 0:
        for x0, y0, ph in RAIN:
            y = 380 + ((y0 - 380 + t * 700 + ph * 900) % 900)
            if lm[int(min(y, H - 1)), int(x0)] > 0.5 or ph < 0.25:
                dr.line((x0, y, x0 - 6, y - 26), fill=mul((200, 215, 235), ra * 0.8), width=2)
    ca = ss(23.6, 24.4, t) * (1 - ss(31.4, 32.2, t))
    if ca > 0:
        for x0, ph, sp in CO2D:
            k = (t * 0.25 * (0.6 + sp) + ph) % 1
            y = lerp(360, 1250, k)
            hit = lm[int(min(y, H - 1)), int(x0)] > 0.5 and k > 0.35
            a = ca * (1 - ss(0.75, 1.0, k))
            if hit or a < 0.5: continue
            dr.ellipse((x0 - 8, y - 8, x0 + 8, y + 8), fill=(175, 175, 185), outline=(225, 225, 235))
    put(img, L_SUP, MCX, MCY, ss(15.0, 15.6, t) * (1 - ss(17.4, 18.2, t)))
    return img

# ---------- snowball with sunlight ----------
def ice_level(t):
    if t < 54: return float(np.interp(t, [32.4, 36.6, 44.0], [0.15, 0.45, 1.0]))
    return float(np.interp(t, [54, 62.6, 66.8, 100], [1.0, 1.0, 0.18, 0.12]))
PUFF = sprite(40)
VOLC = [(-0.5, -0.1), (0.35, 0.45), (0.1, -0.55), (-0.2, 0.6)]
def snowball(t):
    f = bg.copy()
    co = co2_level(t)
    halo = np.array([150, 180, 240]) * (1 - co) + np.array([200, 190, 170]) * co
    f += (np.exp(-np.maximum(D - 340, 0) / (50 + 40 * co)) * (0.3 + 0.2 * co) * (D > 338))[..., None] * halo
    col, a = rocky(92, 0.8, MN, ([60, 58, 56], [165, 160, 152]), 0.0)
    blend(f, col, a, CX - 380, CY + 330)
    green = ss(66.8, 71, t) * 0.6
    col, a = earth_ice(340, 0.8 + t * 0.006, ice_level(t), 0.35, green)
    blend(f, col, a, CX, CY)
    if 54.2 < t < 64:
        pa = ss(54.4, 55.4, t) * (1 - ss(62.6, 64, t))
        for i, (vx, vy) in enumerate(VOLC):
            px, py = CX + vx * 340, CY + vy * 340
            for k in range(5):
                q = (t * 0.5 + k / 5 + i * 0.3) % 1
                add_sprite(f, PUFF, px + vx * 140 * q, py + vy * 140 * q - 30 * q, (140, 135, 130), pa * 0.55 * (1 - q))
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    sa = ss(32.4, 33.4, t) * (1 - ss(44.4, 45.2, t))
    if sa > 0:
        ic = ice_level(t)
        for k in range(6):
            yv = -0.75 + k * 0.3
            hx = CX - 340 * math.sqrt(max(0.0, 1 - yv * yv)) * 0.92; hy = CY + yv * 340
            ph = (t * 0.8 + k * 0.17) % 1
            sx = lerp(-40, hx, min(1.0, ph * 2))
            dr.line((-40, hy, sx, hy), fill=mul((255, 220, 110), sa), width=5)
            if ph > 0.5:
                icy = abs(yv) > 1 - ic * 1.2
                if icy:
                    q = (ph - 0.5) * 2
                    dr.line((hx, hy, lerp(hx, hx - 400, q), lerp(hy, hy - 260 * (1 if yv < 0 else -1), q)), fill=mul((255, 240, 180), sa), width=5)
                else:
                    dr.ellipse((hx - 10, hy - 10, hx + 10, hy + 10), fill=mul((255, 140, 60), sa * (1 - (ph - 0.5) * 2)))
    return img

# ---------- under the ice ----------
CELLS = [(rng.random(), rng.random(), rng.random() * 6) for _ in range(26)]
L_VENT = text_img('海底温泉', FM, 38, (255, 200, 150), 3)
L_ICE = text_img('厚厚的冰层', FB, 44, (60, 90, 120), 0)
def under_ice(t):
    f = np.zeros((H, W, 3), np.float32)
    ky = np.clip((yy - 560) / (H - 560), 0, 1)[..., None]
    f[:] = np.array([12, 40, 60]) * (1 - ky) + np.array([3, 10, 18]) * ky
    ice = ((yy < 560 + 30 * np.sin(xx * 0.01)) & (yy > 300))[..., None]
    f = f * (1 - ice) + (np.array([175, 205, 225]) * (0.75 + 0.3 * nz[..., None])) * ice
    vg = np.exp(-(((xx - 700) / 160) ** 2 + ((yy - 1300) / 220) ** 2))[..., None]
    f = f + vg * np.array([140, 60, 20]) * (0.8 + 0.2 * math.sin(t * 3))
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, 1420, W, H), fill=(28, 24, 22))
    dr.polygon([(650, 1420), (690, 1260), (720, 1260), (760, 1420)], fill=(55, 45, 40))
    for k in range(8):
        q = (t * 0.6 + k / 8) % 1
        add = 30 + 60 * q
        dr.ellipse((705 - add * 0.5 + 20 * math.sin(k + t), 1250 - q * 300 - add * 0.3, 705 + add * 0.5 + 20 * math.sin(k + t), 1250 - q * 300 + add * 0.3), fill=mul((80, 60, 55), 1 - q))
    for i, (u, v, ph) in enumerate(CELLS):
        if i % 2: x, y = 520 + u * 380 + 15 * math.sin(t + ph), 1120 + v * 260 + 10 * math.cos(t + ph)
        else: x, y = u * W + 15 * math.sin(t * 0.6 + ph), 620 + v * 120 + 8 * math.cos(t + ph)
        dr.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(150, 125, 210), outline=(205, 180, 255), width=2)
        dr.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(120, 160, 250))
    put(img, L_VENT, 705, 1480, ss(104.6, 105.4, t))
    put(img, L_ICE, W / 2, 440, ss(100.4, 101.2, t))
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def calm(t):
    from ep2 import earth2
    f = bg.copy()
    f += (np.exp(-np.maximum(D - 340, 0) / 60) * 0.3 * (D > 338))[..., None] * np.array([110, 160, 240])
    col, a = rocky(92, 0.8, MN, ([60, 58, 56], [165, 160, 152]), 0.0); blend(f, col, a, CX - 380, CY + 330)
    col, a = earth_ice(340, 0.8 + t * 0.006, 0.0, 0.45); blend(f, col, a, CX, CY)
    return Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))


# ================= v2: full causal chain =================
def co2_level(t): return float(np.interp(t, [0, 53.4, 70.2, 78.8, 100, 108.8, 119, 131, 200], [0.75, 0.75, 0.35, 0.3, 0.25, 0.25, 0.95, 0.62, 0.62]))
def temp_level(t): return float(np.interp(t, [0, 70.2, 78.8, 99, 117.2, 121.4, 131, 200], [0.62, 0.62, 0.45, 0.08, 0.08, 0.72, 0.62, 0.62]))
def ice_level(t):
    if t < 104: return float(np.interp(t, [78.8, 81.5, 91.6, 99.0], [0.0, 0.32, 0.62, 1.0]))
    return float(np.interp(t, [104, 117.2, 121.4, 200], [1.0, 1.0, 0.18, 0.12]))

# ---- cross-section: plates on the mantle ----
L_CRUST = text_img('板块（地壳）', FB, 40, (240, 215, 180), 3)
L_MANT = text_img('地幔', FB, 44, (255, 200, 150), 3)
L_CORE = text_img('地核', FB, 44, (255, 240, 180), 3)
XC, YC = 540, 1000
def crosssection(t):
    img = Image.fromarray(np.clip(bg * 1.0, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    for r, c in ((430, (130, 40, 15)), (400, (190, 70, 25)), (300, (215, 100, 35)), (200, (235, 140, 50)), (150, (255, 200, 90)), (90, (255, 235, 150))):
        dr.ellipse((XC - r, YC - r, XC + r, YC + r), fill=c)
    a = ss(19.6, 20.6, t)
    for k in range(4):
        ca = math.radians(k * 90 + 45)
        lx, ly = XC + 275 * math.cos(ca), YC + 275 * math.sin(ca)
        sgn = 1 if k % 2 == 0 else -1
        dr.ellipse((lx - 85, ly - 85, lx + 85, ly + 85), outline=mul((255, 210, 140), a * 0.5), width=3)
        for j in range(3):
            ph = math.radians((sgn * t * 60 + j * 120) % 360)
            px, py = lx + 85 * math.cos(ph), ly + 85 * math.sin(ph)
            tx, ty = -math.sin(ph) * sgn, math.cos(ph) * sgn
            dr.polygon([(px + tx * 22, py + ty * 22), (px - ty * 12, py + tx * 12), (px + ty * 12, py - tx * 12)], fill=mul((255, 240, 190), a))
    off = (t - 15) * 1.2 * ss(23.6, 24.6, t)
    plates = [(0, 85), (95, 175), (185, 265), (275, 355)]
    for k, (s0, s1) in enumerate(plates):
        dir_ = 1 if k % 2 == 0 else -1
        s0 += dir_ * off; s1 += dir_ * off
        dr.arc((XC - 445, YC - 445, XC + 445, YC + 445), s0, s1, fill=(150, 125, 95), width=34)
        dr.arc((XC - 462, YC - 462, XC + 462, YC + 462), s0 + 4, s1 - 4, fill=(110, 140, 90), width=4)
    put(img, L_CORE, XC, YC, ss(15.6, 16.4, t))
    put(img, L_MANT, XC, YC - 250, ss(19.6, 20.4, t))
    put(img, L_CRUST, XC, YC - 530, ss(15.6, 16.4, t))
    return img

# ---- map: assemble, heat up, rift, weather ----
seam = land * (np.minimum(ang % (np.pi / 2), np.pi / 2 - ang % (np.pi / 2)) < 0.035)
heat = np.exp(-(((xx - MCX) / 260) ** 2 + ((yy - MCY) / 260) ** 2))
L_ROD = text_img('罗迪尼亚', FB, 50, (250, 230, 200), 4)
CARB = [(rng.random(), rng.random(), rng.random()) for _ in range(80)]
def map_d(t):
    if t < 44.8: return lerp(430, 0, ss(32.4, 38.6, t))
    return lerp(0, 160, ss(46.2, 52.4, t))
def map_scene(t):
    d = map_d(t)
    f = ocean_bg.copy()
    lm = np.zeros((H, W), np.float32)
    for m, cx, cy in PIECES:
        lm = np.maximum(lm, shifted(m, cx * d, cy * d))
    f = f * (1 - lm[..., None]) + land_col * lm[..., None]
    hk = ss(40.8, 44.0, t) * (1 - ss(47.0, 50.0, t))
    if hk > 0:
        f = f + (heat * lm * hk * (0.7 + 0.3 * math.sin(t * 4)))[..., None] * np.array([200, 60, 10])
    sk = ss(44.9, 45.6, t) * (1 - ss(46.8, 48.0, t))
    if sk > 0:
        f = f + (seam * sk)[..., None] * np.array([255, 170, 60])
    edge = np.clip(lm - np.roll(lm, 4, 0) * np.roll(lm, -4, 0) * np.roll(lm, 4, 1) * np.roll(lm, -4, 1), 0, 1)
    ck = 0.5 + 1.5 * ss(53.6, 54.6, t) * (1 - ss(57.4, 58.4, t)) * (0.6 + 0.4 * math.sin(t * 5))
    f = f + edge[..., None] * np.array([200, 230, 200]) * 0.5 * ck
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    ra = ss(57.8, 58.8, t)
    if ra > 0:
        for x0, y0, ph in RAIN:
            y = 380 + ((y0 - 380 + t * 700 + ph * 900) % 900)
            if lm[int(min(y, H - 1)), int(x0)] > 0.5 or ph < 0.25:
                dr.line((x0, y, x0 - 6, y - 26), fill=mul((200, 215, 235), ra * 0.8), width=2)
    ca = ss(62.0, 62.8, t)
    if ca > 0:
        for x0, ph, sp in CO2D:
            k = (t * 0.25 * (0.6 + sp) + ph) % 1
            y = lerp(360, 1250, k)
            if lm[int(min(y, H - 1)), int(x0)] > 0.5 and k > 0.35: continue
            if k > 0.75: continue
            dr.ellipse((x0 - 8, y - 8, x0 + 8, y + 8), fill=(175, 175, 185), outline=(225, 225, 235))
    cb = ss(66.2, 67.0, t)
    if cb > 0:
        for u, v, ph in CARB:
            q = (t * 0.3 + ph) % 1
            ang2 = u * 6.283; r0 = 120 + v * 120
            r = r0 + q * 380
            x, y = MCX + r * math.cos(ang2), MCY + r * math.sin(ang2) * 1.1
            dr.ellipse((x - 6, y - 6, x + 6, y + 6), fill=mul((235, 235, 225), cb * (1 - q * 0.3)))
    put(img, L_SUP, MCX, MCY - 40, ss(36.8, 37.6, t) * (1 - ss(44.2, 44.8, t)))
    put(img, L_ROD, MCX, MCY + 30, ss(36.8, 37.6, t) * (1 - ss(44.2, 44.8, t)))
    return img

# ---- greenhouse blanket ----
def greenhouse(t):
    f = bg.copy()
    col, a = rocky(92, 0.8, MN, ([60, 58, 56], [165, 160, 152]), 0.0); blend(f, col, a, CX - 380, CY + 330)
    col, a = earth_ice(340, 0.8 + t * 0.006, 0.05, 0.3); blend(f, col, a, CX, CY)
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
    co = co2_level(t)
    th = int(18 + 70 * co)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((CX - 345 - th, CY - 345 - th, CX + 345 + th, CY + 345 + th), outline=(200, 190, 175, 120), width=th)
    base = img.convert('RGBA'); base.alpha_composite(lay); img = base.convert('RGB'); dr = ImageDraw.Draw(img)
    for k in range(12):
        angk = k * 0.5236 + 0.2
        q = (t * 0.6 + k * 0.29) % 1
        blocked = (k / 12) < co
        rb = 345 + th
        if blocked:
            r = 345 + (rb - 345) * (q * 2 if q < 0.5 else (1 - q) * 2)
        else:
            r = 345 + q * 420
        r2 = max(345, r - 90)
        col = (255, 120, 60) if blocked else (255, 170, 120)
        pts = []
        for j in range(8):
            rr = lerp(r2, r, j / 7); wv = 9 * math.sin(j * 1.8 + t * 8)
            pts.append((CX + rr * math.cos(angk) - wv * math.sin(angk), CY + rr * math.sin(angk) + wv * math.cos(angk)))
        dr.line(pts, fill=col, width=7)
    return img

def render_v2(t):
    if t < 14.8: img = dim(calm(t), 1 - ss(14.2, 14.8, t))
    elif t < 32.2: img = dim(crosssection(t), ss(14.8, 15.4, t) * (1 - ss(31.6, 32.2, t)))
    elif t < 70.2: img = dim(map_scene(t), ss(32.2, 32.8, t) * (1 - ss(69.6, 70.2, t)))
    elif t < 78.8: img = dim(greenhouse(t), ss(70.2, 70.8, t) * (1 - ss(78.2, 78.8, t)))
    elif t < 100.0: img = dim(snowball2(t), ss(78.8, 79.4, t) * (1 - ss(99.4, 100.0, t)))
    elif t < 108.6: img = dim(under_ice(t), ss(100.0, 100.6, t) * (1 - ss(108.0, 108.6, t)))
    else: img = dim(snowball2(t), ss(108.6, 109.2, t))
    ga = (ss(53.6, 54.4, t) * (1 - ss(99.4, 100.0, t))) if t < 100 else (ss(108.8, 109.6, t) if t > 108.6 else 0)
    gauges(img, t, ga)
    return img

def snowball2(t):
    f = bg.copy()
    co = co2_level(t)
    halo = np.array([150, 180, 240]) * (1 - co) + np.array([200, 190, 170]) * co
    f += (np.exp(-np.maximum(D - 340, 0) / (50 + 40 * co)) * (0.3 + 0.2 * co) * (D > 338))[..., None] * halo
    col, a = rocky(92, 0.8, MN, ([60, 58, 56], [165, 160, 152]), 0.0)
    blend(f, col, a, CX - 380, CY + 330)
    green = ss(121.4, 125.6, t) * 0.6
    col, a = earth_ice(340, 0.8 + t * 0.006, ice_level(t), 0.35, green)
    blend(f, col, a, CX, CY)
    if 108.8 < t < 119:
        pa = ss(109.0, 110.0, t) * (1 - ss(117.6, 119, t))
        for i, (vx, vy) in enumerate(VOLC):
            px, py = CX + vx * 340, CY + vy * 340
            for k in range(5):
                q = (t * 0.5 + k / 5 + i * 0.3) % 1
                add_sprite(f, PUFF, px + vx * 140 * q, py + vy * 140 * q - 30 * q, (140, 135, 130), pa * 0.55 * (1 - q))
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    sa = ss(83.2, 84.2, t) * (1 - ss(98.6, 99.4, t))
    if sa > 0:
        ic = ice_level(t)
        for k in range(6):
            yv = -0.75 + k * 0.3
            hx = CX - 340 * math.sqrt(max(0.0, 1 - yv * yv)) * 0.92; hy = CY + yv * 340
            ph = (t * 0.8 + k * 0.17) % 1
            sx = lerp(-40, hx, min(1.0, ph * 2))
            dr.line((-40, hy, sx, hy), fill=mul((255, 220, 110), sa), width=5)
            if ph > 0.5:
                if abs(yv) > 1 - ic * 1.2:
                    q = (ph - 0.5) * 2
                    dr.line((hx, hy, lerp(hx, hx - 400, q), lerp(hy, hy - 260 * (1 if yv < 0 else -1), q)), fill=mul((255, 240, 180), sa), width=5)
                else:
                    dr.ellipse((hx - 10, hy - 10, hx + 10, hy + 10), fill=mul((255, 140, 60), sa * (1 - (ph - 0.5) * 2)))
    return img

CAPS_V2 = [(6.4, 10.6, '真核细胞出现后的十几亿年里'), (10.6, 14.6, '生命一直又小又简单'),
        (15.2, 19.4, '地球的外壳，并不是完整的一块'), (19.4, 23.6, '它碎成许多板块，漂在炽热的地幔上'),
        (23.6, 27.8, '地幔翻滚，推着板块每年挪几厘米'), (27.8, 32.0, '几亿年下来，大陆会撞到一起，也会裂开'),
        (32.4, 36.6, '约 10 亿年前，几块大陆撞到了一起'), (36.6, 40.8, '拼成了一块超级大陆，叫罗迪尼亚'),
        (40.8, 44.8, '它像厚被子，捂住了地下的热量'), (45.0, 49.2, '约 7.5 亿年前，热量把它从下面顶裂'),
        (49.2, 53.4, '超级大陆，碎成了好几块'), (53.6, 57.8, '海水涌进裂缝，海岸线变长了'),
        (57.8, 62.0, '海边空气湿润，雨下得更多'), (62.0, 66.2, '雨水溶进二氧化碳，慢慢溶解岩石'),
        (66.2, 70.2, '二氧化碳就这样被冲进海底，锁进石头'), (70.4, 74.6, '二氧化碳像一床棉被，替地球保暖'),
        (74.6, 78.8, '棉被变薄了，热量散走，地球开始变冷'), (79.0, 83.2, '两极，先结了冰'),
        (83.2, 87.4, '白色的冰，把阳光反射回太空'), (87.4, 91.6, '地面吸收的热更少，又结出更多冰'),
        (91.6, 95.8, '冰越多越冷，越冷冰越多'), (95.8, 99.8, '冰一路冻到赤道，地球变成了雪球'),
        (100.2, 104.4, '生命躲在冰层下的海水里'), (104.4, 108.4, '和海底温泉边，熬了过来'),
        (108.8, 113.0, '火山没有停，一直喷出二氧化碳'), (113.0, 117.2, '冰封之下没有雨，它没法被带走'),
        (117.2, 121.4, '棉被越积越厚，几千万年后，冰融化了'), (121.4, 125.6, '融水把大量养分冲进了海洋'),
        (125.8, 129.8, '更复杂的生命，即将登场')]


# ================= v3: how continents formed (inserted at 32.2) =================
INS0, INS = 32.2, 25.2
def slab_pt(q):
    p0, p1, p2 = (560, 760), (790, 790), (930, 1440)
    x = (1 - q) ** 2 * p0[0] + 2 * (1 - q) * q * p1[0] + q * q * p2[0]
    y = (1 - q) ** 2 * p0[1] + 2 * (1 - q) * q * p1[1] + q * q * p2[1]
    return x, y
SLAB_TOP = [(x, 760) for x in range(-20, 561, 20)] + [slab_pt(q / 20) for q in range(1, 21)]
def offset_line(pts, d):
    out = []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; n = math.hypot(tx, ty) or 1
        out.append((x - ty / n * d, y + tx / n * d))
    return out
SLAB_BOT = offset_line(SLAB_TOP, 60)
def along(pts, s_):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    d = s_ * sum(seg)
    for i, l in enumerate(seg):
        if d <= l:
            k = d / l; return pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k
        d -= l
    return pts[-1]
L_OC = text_img('海洋地壳（又薄又重）', FB, 38, (215, 220, 230), 3)
L_SUB = text_img('钻入地幔', FB, 38, (255, 220, 170), 3)
L_WAT = text_img('被带下去的海水', FM, 36, (170, 210, 255), 3)
L_MAG = text_img('较轻的岩浆上冒', FM, 36, (255, 200, 140), 3)
L_ISL = text_img('火山岛', FB, 42, (250, 235, 200), 3)
L_CON = text_img('大陆（轻，浮在上面）', FB, 42, (255, 225, 160), 3)
SEA_Y = 600
def subduction(t):
    img = Image.new('RGB', (W, H), (8, 12, 22)); dr = ImageDraw.Draw(img)
    for i in range(12):
        y0 = 700 + i * 110
        c = (int(150 + 8 * i), int(55 + 4 * i), int(20 + i))
        dr.rectangle((0, y0, W, y0 + 110), fill=c)
    dr.rectangle((0, SEA_Y, W, 760), fill=(25, 75, 130))
    dr.line((0, SEA_Y, W, SEA_Y), fill=(140, 190, 230), width=3)
    mv = ss(40.8, 41.6, t)
    dr.polygon(SLAB_TOP + SLAB_BOT[::-1], fill=(70, 75, 85))
    ph = ((t - 40.8) * 0.035) % 0.05 if t > 40.8 else 0
    for k in range(20):
        q = k * 0.05 + ph
        if q > 1: continue
        a_ = along(SLAB_TOP, q); b_ = along(SLAB_BOT, q)
        dr.line((a_, b_), fill=mul((120, 125, 140), 0.6 + 0.4 * mv), width=3)
    dr.polygon([(560, 740), (W, 740), (W, 830), (600, 830)], fill=(95, 90, 88))
    wa = ss(45.0, 45.8, t)
    if wa > 0:
        for k in range(14):
            q = ((t - 45) * 0.06 + k / 14) % 1
            if q < 0.35: continue
            x, y = along(SLAB_TOP, q)
            fade = 1 - ss(0.82, 0.95, q)
            dr.ellipse((x - 8, y - 18, x + 8, y - 2), fill=mul((120, 190, 255), wa * fade))
        g = ss(46.5, 48.5, t) * (0.7 + 0.3 * math.sin(t * 4))
        if g > 0.02:
            for r, c in ((90, (230, 95, 25)), (55, (255, 150, 50))):
                cc = tuple(int(v) for v in lerp(np.array([178, 69, 24]), np.array(c), g))
                dr.ellipse((800 - r, 1180 - r, 800 + r, 1180 + r), fill=cc)
    isl = ss(49.4, 52.8, t)
    mk = ss(49.2, 49.8, t)
    if mk > 0:
        for k in range(7):
            q = ((t - 49.2) * 0.35 + k / 7) % 1
            x = 800 - 30 * q + 12 * math.sin(k + t); y = lerp(1150, 760, q)
            dr.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(255, 150, 50))
    ih = lerp(0, 230, isl)
    if ih > 0:
        dr.polygon([(680, 742), (840, 742), (770, 742 - ih)], fill=(130, 110, 95))
        dr.polygon([(755, 742 - ih + 20), (785, 742 - ih + 20), (770, 742 - ih)], fill=(255, 130, 50))
    mg = ss(53.4, 56.4, t)
    if t > 53.2:
        x2 = lerp(1150, 900, mg)
        dr.polygon([(x2 - 90, 742), (x2 + 90, 742), (x2, 742 - 200)], fill=(130, 110, 95))
        if mg > 0.6:
            k = ss(55.4, 57.0, t)
            dr.polygon([(660, 742), (1000, 742), (980, 742 - lerp(0, 170, k)), (700, 742 - lerp(0, 170, k))], fill=mul((185, 155, 115), k) if k > 0.05 else None)
    put(img, L_OC, 260, 820, ss(36.8, 37.6, t) * (1 - ss(44.6, 45.2, t)))
    put(img, L_SUB, 700, 1360, ss(41.2, 42.0, t) * (1 - ss(48.8, 49.4, t)))
    put(img, L_WAT, 420, 1060, ss(45.4, 46.2, t) * (1 - ss(48.8, 49.4, t)))
    put(img, L_MAG, 590, 1250, ss(49.6, 50.4, t) * (1 - ss(53.0, 53.6, t)))
    put(img, L_ISL, 770, 460, ss(51.8, 52.6, t) * (1 - ss(55.0, 55.6, t)))
    put(img, L_CON, 830, 480, ss(56.0, 56.8, t))
    return img

def render(t):
    if t < INS0: return render_v2(t)
    if t < INS0 + INS:
        img = subduction(t)
        k = ss(INS0, INS0 + 0.6, t) * (1 - ss(INS0 + INS - 0.6, INS0 + INS, t))
        return dim(img, k)
    return render_v2(t - INS)

CAPS = [c for c in CAPS_V2 if c[0] < INS0] + [
    (32.4, 36.6, '那大陆，最早是怎么来的？'), (36.6, 40.8, '最早的地壳又薄又重，大多沉在海底'),
    (40.8, 45.0, '两个板块相撞，重的那块钻到下面'), (45.0, 49.2, '带下去的海水，让深处的岩石熔化'),
    (49.2, 53.2, '较轻的岩浆往上冒，长出了火山岛'), (53.2, 57.2, '火山岛一次次相撞拼合，长成了大陆')] + \
    [(a + INS, b + INS, x) for a, b, x in CAPS_V2 if a >= INS0]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep8_{ts}.png')
