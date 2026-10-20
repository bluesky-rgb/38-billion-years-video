import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep17 import tree
from ep18 import render as render18

CLEAN = False
rng = np.random.default_rng(191)
SKY = grad((150, 185, 200), (225, 225, 200), 480, 1100)
FUR = (95, 72, 55)
BR = (100, 78, 55)

def branch(dr, y, sag=0.0, x0=0, x1=W, w=20):
    pts = [(x, y + sag * math.sin(math.pi * (x - x0) / (x1 - x0))) for x in np.linspace(x0, x1, 30)]
    dr.line(pts, fill=BR, width=w)
    return pts
def monkey(dr, x, y, s, t, a=1.0, tail=1.0, col=(150, 110, 70)):
    ph = math.sin(t * 8)
    for i, lx in enumerate((x + 40 * s, x - 40 * s)):
        p = ph * (1 if i else -1)
        dr.line((lx, y - 30 * s, lx + 14 * s * p, y), fill=mul(col, a), width=int(10 * s))
    dr.ellipse((x - 60 * s, y - 70 * s, x + 60 * s, y - 25 * s), fill=mul(col, a))
    dr.ellipse((x + 45 * s, y - 95 * s, x + 95 * s, y - 45 * s), fill=mul(col, a))
    dr.ellipse((x + 75 * s, y - 80 * s, x + 85 * s, y - 70 * s), fill=mul((20, 20, 20), a))
    if tail > 0.02:
        dr.arc((x - 60 * s - 140 * s * tail, y - 140 * s * tail - 40 * s, x - 60 * s + 10 * s, y + 40 * s), 90, 250, fill=mul(col, a), width=max(2, int(8 * s)))
def ape_hang(dr, hx, hy, s, t, a=1.0, swing=0.0, tail=0.0, col=FUR):
    # hands at (hx, hy) (lead) ; body hangs below
    sw = swing
    sx, sy = hx + 40 * s * math.sin(sw), hy + 140 * s
    other = (hx - 150 * s * (0.5 + 0.5 * math.cos(t * 3)), hy + 30 * s * (0.5 - 0.5 * math.cos(t * 3)))
    dr.line((hx, hy, sx + 18 * s, sy), fill=mul(col, a), width=int(18 * s))
    dr.line((other[0], other[1], sx - 18 * s, sy), fill=mul(col, a), width=int(18 * s))
    dr.ellipse((sx - 55 * s, sy - 20 * s, sx + 55 * s, sy + 150 * s), fill=mul(col, a))
    dr.ellipse((sx - 38 * s, sy - 75 * s, sx + 38 * s, sy - 5 * s), fill=mul(col, a))
    dr.ellipse((sx - 22 * s, sy - 58 * s, sx + 22 * s, sy - 25 * s), fill=mul((170, 140, 115), a))
    for sg in (-1, 1):
        dr.line((sx + sg * 25 * s, sy + 135 * s, sx + sg * 40 * s, sy + 230 * s), fill=mul(col, a), width=int(16 * s))
    if tail > 0.02:
        dr.arc((sx - 10 * s, sy + 120 * s, sx + 10 * s + 180 * s * tail, sy + 140 * s + 180 * s * tail), 120, 270, fill=mul(col, a), width=max(2, int(10 * s)))
    return sx, sy
def ape_walk(dr, x, y, s, t, a=1.0, col=FUR):
    ph = math.sin(t * 5)
    for i, (lx, ly) in enumerate(((x + 60 * s, y - 120 * s), (x - 60 * s, y - 100 * s))):
        p = ph * (1 if i else -1)
        dr.line((lx, ly, lx + 16 * s * p, y), fill=mul(col, a), width=int(18 * s))
    dr.ellipse((x - 90 * s, y - 160 * s, x + 80 * s, y - 80 * s), fill=mul(col, a))
    dr.ellipse((x + 50 * s, y - 210 * s, x + 120 * s, y - 140 * s), fill=mul(col, a))
    dr.ellipse((x + 75 * s, y - 195 * s, x + 115 * s, y - 160 * s), fill=mul((170, 140, 115), a))
def ape_stand(dr, x, y, s, a=1.0, col=FUR):
    dr.ellipse((x - 50 * s, y - 230 * s, x + 50 * s, y - 80 * s), fill=mul(col, a))
    dr.ellipse((x - 36 * s, y - 300 * s, x + 36 * s, y - 225 * s), fill=mul(col, a))
    dr.ellipse((x - 20 * s, y - 285 * s, x + 20 * s, y - 250 * s), fill=mul((170, 140, 115), a))
    for sg in (-1, 1):
        dr.line((x + sg * 40 * s, y - 200 * s, x + sg * 70 * s, y - 70 * s), fill=mul(col, a), width=int(16 * s))
        dr.line((x + sg * 25 * s, y - 95 * s, x + sg * 40 * s, y), fill=mul(col, a), width=int(18 * s))

# ---------- A: monkey vs ape in the trees ----------
L_TAILB = text_img('尾巴：像平衡杆', FB, 42, (255, 235, 200), 3)
L_APE = text_img('猿：个子更大', FB, 46, (255, 225, 160), 3); L_BEND = text_img('细树枝撑不住', FB, 42, (255, 225, 200), 3)
L_HANG = text_img('吊在树枝下，手臂交替往前荡', FB, 40, (255, 235, 200), 3)
L_UPR = text_img('身体竖直：尾巴帮不上忙', FB, 42, (255, 225, 200), 3)
def trees_scene(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(9):
        cx = (i * 147) % W; cy = 520 + (i % 3) * 30
        dr.ellipse((cx - 160, cy - 80, cx + 160, cy + 80), fill=(70 + 6 * i, 120, 70))
    dr.rectangle((0, GROUND, W, H), fill=(110, 125, 75))
    for x in (60, 1020): dr.line((x, GROUND, x, 560), fill=BR, width=40)
    if t < 19.0:
        branch(dr, 960)
        x = lerp(-120, 620, ss(6.4, 14.6, t)) if t < 14.6 else 620
        monkey(dr, x, 950, 1.5, t if t < 14.6 else 14.6)
        if t > 14.6:
            g = ss(14.8, 15.6, t) * (0.6 + 0.4 * math.sin(t * 4))
            dr.arc((x - 90 - 210, 950 - 250, x - 90 + 15, 950 + 60), 90, 250, fill=mul((255, 220, 120), g), width=6)
        put(img, L_TAILB, 540, 1120, ss(15.0, 15.8, t))
        return img
    if t < 27.4:
        sag = 120 * ss(23.4, 25.0, t)
        pts = branch(dr, 960, sag, w=14)
        x = lerp(-150, 540, ss(19.2, 23.2, t))
        yb = 960 + sag * math.sin(math.pi * max(0, min(1, x / W)))
        ape_walk(dr, x, yb - 8, 1.1, t if t < 23.2 else 23.2)
        put(img, L_APE, 540, 1120, ss(19.4, 20.2, t) * (1 - ss(23.0, 23.4, t)))
        put(img, L_BEND, 540, 1120, ss(23.6, 24.4, t))
        return img
    branch(dr, 700, 0, w=22)
    k = (t - 27.4) / 4.0
    hx = lerp(200, 760, ss(27.6, 35.6, t))
    tl = 1.0 - ss(40.4, 43.6, t) if t > 36 else 1.0
    if t < 36.0:
        sx, sy = ape_hang(dr, hx, 700, 1.2, t, swing=0.4 * math.sin(t * 3), tail=0.0)
        put(img, L_HANG, 540, 1300, ss(28.0, 28.8, t))
    else:
        sx, sy = ape_hang(dr, 760, 700, 1.2, 35.6, swing=0.15 * math.sin(t * 2), tail=0.9 * tl)
        g = ss(36.2, 37.0, t)
        dr.line((sx, sy - 90, sx, sy + 200), fill=mul((255, 220, 120), g), width=3)
        put(img, L_UPR, 540, 1300, ss(36.2, 37.0, t))
    return img

# ---------- B: tails shrink over generations ----------
L_GEN = text_img('一代代：尾巴越来越短', FB, 42, (255, 225, 160), 3)
L_SAME = text_img('没了尾巴，荡得一样灵活', FB, 40, (255, 235, 200), 3)
def gens(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(9):
        cx = (i * 147) % W; cy = 520 + (i % 3) * 30
        dr.ellipse((cx - 160, cy - 80, cx + 160, cy + 80), fill=(70 + 6 * i, 120, 70))
    branch(dr, 760, 0, w=20)
    for i, tl in enumerate((1.0, 0.6, 0.3, 0.0)):
        a = ss(44.6 + i * 0.8, 45.4 + i * 0.8, t)
        if a > 0: ape_hang(dr, 160 + i * 250, 760, 0.85, 44 + i, swing=0.1 * math.sin(t * 2 + i), tail=tl, a=a)
    put(img, L_GEN, 540, 1300, ss(44.6, 45.4, t) * (1 - ss(48.2, 48.6, t)))
    put(img, L_SAME, 540, 1300, ss(48.6, 49.4, t))
    return img

# ---------- C: jumping gene ----------
L_GENE = text_img('控制尾巴发育的基因', FB, 40, (200, 230, 255), 3)
L_JUMP = text_img('插进一段跳跃基因', FB, 42, (255, 200, 140), 3)
L_MOUSE = text_img('放进老鼠体内：尾巴也变短了', FB, 40, (255, 235, 200), 3)
def helix(dr, y, x0, x1, t, gap=None, ins=0.0):
    for x in range(x0, x1, 14):
        ph = x / 60 + t * 0.6
        y1 = y + 60 * math.sin(ph); y2 = y - 60 * math.sin(ph)
        inside = gap and gap[0] <= x <= gap[1]
        c1 = (90, 170, 240) if not inside else (255, 170, 90)
        if inside and ins < 0.98: continue
        dr.ellipse((x - 7, y1 - 7, x + 7, y1 + 7), fill=c1); dr.ellipse((x - 7, y2 - 7, x + 7, y2 + 7), fill=(150, 210, 250) if not inside else (255, 210, 140))
        if x % 28 == 0: dr.line((x, y1, x, y2), fill=(200, 210, 220), width=2)
def mouse(dr, x, y, s, tail, a=1.0):
    c = (170, 160, 150)
    dr.ellipse((x - 70 * s, y - 35 * s, x + 70 * s, y + 30 * s), fill=mul(c, a))
    dr.polygon([(x + 50 * s, y - 25 * s), (x + 120 * s, y + 5 * s), (x + 50 * s, y + 25 * s)], fill=mul(c, a))
    dr.ellipse((x + 40 * s, y - 55 * s, x + 70 * s, y - 25 * s), fill=mul((220, 180, 180), a))
    dr.ellipse((x + 85 * s, y - 12 * s, x + 93 * s, y - 4 * s), fill=mul((20, 20, 20), a))
    L = 200 * s * tail
    if L > 4: dr.arc((x - 70 * s - L, y - 10 * s, x - 70 * s + 10 * s, y + L * 0.5), 180, 300, fill=mul((210, 170, 170), a), width=max(2, int(6 * s)))
def gene(t):
    img = Image.fromarray(grad((14, 20, 40), (8, 12, 24)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 61.2:
        ins = ss(57.4, 59.6, t)
        helix(dr, 960, -20, W + 20, t, gap=(470, 610) if t > 57.2 else None, ins=1.0 if ins > 0.98 else 0)
        if 57.2 < t and ins < 0.98:
            y = lerp(700, 960, ins)
            for x in range(470, 610, 14):
                dr.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 170, 90))
        g = ss(53.0, 54.0, t)
        dr.rounded_rectangle((300, 860, 780, 1060), radius=20, outline=mul((200, 230, 255), g), width=3)
        put(img, L_GENE, 540, 1120, g); put(img, L_JUMP, 540, 650, ss(57.4, 58.2, t))
        return img
    k = ss(62.4, 64.4, t)
    mouse(dr, 300, 1000, 1.4, 1.0)
    mouse(dr, 780, 1000, 1.4, 1.0 - 0.8 * k)
    put(img, L_MOUSE, 540, 650, ss(61.6, 62.4, t))
    return img

# ---------- D: shoulders and chest ----------
L_SHO = text_img('肩膀：能往各个方向转', FB, 42, (255, 225, 160), 3)
L_CHEST = text_img('胸廓变宽变扁 · 手臂变长', FB, 42, (255, 235, 200), 3)
def body(t):
    img = Image.fromarray(grad((30, 34, 44), (16, 18, 24)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    cx, cy = 540, 980
    wk = ss(70.0, 72.6, t)
    cw = lerp(130, 200, wk); ch = lerp(200, 170, wk)
    dr.ellipse((cx - cw, cy - ch, cx + cw, cy + ch), outline=(230, 225, 215), width=6)
    for j in range(5):
        yy_ = cy - ch * 0.7 + j * ch * 0.35
        dr.arc((cx - cw * 0.95, yy_ - 30, cx + cw * 0.95, yy_ + 30), 0, 180, fill=(200, 195, 185), width=4)
    dr.line((cx, cy - ch - 120, cx, cy + ch + 40), fill=(230, 225, 215), width=8)
    dr.ellipse((cx - 50, cy - ch - 230, cx + 50, cy - ch - 120), outline=(230, 225, 215), width=6)
    arm = lerp(330, 420, wk)
    for sg in (-1, 1):
        sx, sy = cx + sg * (cw + 10), cy - ch + 40
        ang = -math.pi / 2 + sg * (0.3 + 1.0 * (0.5 + 0.5 * math.sin(t * 1.8 + (sg > 0) * 1.5)))
        ex, ey = sx + arm * math.cos(ang) * sg * sg, sy + arm * math.sin(ang)
        ex = sx + sg * abs(arm * math.cos(ang));
        dr.line((sx, sy, ex, ey), fill=(230, 225, 215), width=10)
        dr.ellipse((sx - 22, sy - 22, sx + 22, sy + 22), outline=(255, 220, 120), width=5)
        g = ss(66.0, 67.0, t)
        dr.arc((sx - 110, sy - 110, sx + 110, sy + 110), 0, 360, fill=mul((255, 220, 120), 0.5 * g), width=2)
    put(img, L_SHO, 540, 640, ss(65.8, 66.6, t) * (1 - ss(69.6, 70.0, t)))
    put(img, L_CHEST, 540, 640, ss(70.0, 70.8, t))
    return img

# ---------- E: fossils, mother & child ----------
L_PRO = text_img('原康修尔猿 · 肯尼亚 · 没有尾巴', FB, 40, (255, 225, 160), 3)
L_LU = text_img('禄丰古猿 · 云南', FB, 44, (255, 225, 160), 3)
L_SLOW = text_img('个子大、寿命长、孩子长得慢', FB, 40, (255, 235, 200), 3)
L_LEARN = text_img('跟着妈妈更久：学会更多本领', FB, 40, (255, 235, 200), 3)
L_BRAIN = text_img('大脑继续变大', FB, 44, (255, 215, 190), 3)
def fossils(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(9):
        cx = (i * 147) % W; cy = 520 + (i % 3) * 30
        dr.ellipse((cx - 160, cy - 80, cx + 160, cy + 80), fill=(70 + 6 * i, 120, 70))
    dr.rectangle((0, GROUND, W, H), fill=(110, 125, 75))
    if t < 82.8:
        branch(dr, 1000, 0, w=26)
        if t < 78.4:
            ape_walk(dr, lerp(1200, 560, ss(74.2, 77.6, t)), 990, 1.2, t if t < 77.6 else 77.6)
            put(img, L_PRO, 540, 1160, ss(74.4, 75.2, t))
        else:
            ape_hang(dr, 560, 1000 - 400, 1.1, t, swing=0.2 * math.sin(t * 2), col=(120, 85, 60))
            branch(dr, 600, 0, w=22)
            put(img, L_LU, 540, 1160, ss(78.6, 79.4, t))
        return img
    dr.line((0, 1060, W, 1040), fill=BR, width=30)
    mx = 480
    ape_walk(dr, mx, 1045, 1.3, 83)
    bk = ss(83.0, 83.8, t)
    if bk > 0:
        dr.ellipse((mx - 40, 1045 - 150, mx + 40, 1045 - 95), fill=mul((120, 92, 70), bk))
        dr.ellipse((mx - 10, 1045 - 185, mx + 40, 1045 - 135), fill=mul((120, 92, 70), bk))
    if t > 87.0:
        k = ss(87.2, 89.0, t)
        bx = lerp(mx, 780, k)
        ape_walk(dr, bx, 1045, 0.55, t if t < 89 else 89)
        for i in range(3):
            dr.ellipse((700 + i * 40, 1010, 724 + i * 40, 1034), fill=(150, 110, 60))
    put(img, L_SLOW, 540, 1200, ss(83.0, 83.8, t) * (1 - ss(86.8, 87.2, t)))
    put(img, L_LEARN, 540, 1200, ss(87.2, 88.0, t) * (1 - ss(91.0, 91.4, t)))
    put(img, L_BRAIN, 540, 1200, ss(91.4, 92.2, t))
    return img

# ---------- F: family tree ----------
L_FT = [text_img(s_, FB, 40, c, 3) for s_, c in (('猿', (255, 225, 160)), ('长臂猿', (230, 230, 240)), ('猩猩', (230, 230, 240)), ('大猩猩', (230, 230, 240)), ('黑猩猩', (230, 230, 240)), ('人', (255, 215, 150)))]
def family(t):
    img = Image.fromarray(grad((30, 40, 36), (16, 22, 20)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    rx, ry = 540, 1380
    put(img, L_FT[0], rx, ry + 50, 1.0)
    ends = [(150, 1180), (330, 1030), (520, 900), (720, 800), (900, 700)]
    for i, (ex, ey) in enumerate(ends):
        k = ss(95.8 + i * 0.6 if i < 2 else 100.0 + (i - 2) * 0.6, 96.8 + i * 0.6 if i < 2 else 101.0 + (i - 2) * 0.6, t)
        if k <= 0: continue
        col = (255, 215, 150) if i == 4 else (200, 190, 170)
        dr.line((rx, ry, lerp(rx, ex, k), lerp(ry, ey + 40, k)), fill=col, width=7 if i == 4 else 5)
        put(img, L_FT[i + 1], ex, ey, ss(0.8, 1.0, k))
    return img

# ---------- G: coccyx ----------
L_COC = text_img('尾骨：消失的尾巴', FB, 46, (255, 225, 160), 4)
L_YOUSP = text_img('你的脊柱末端', FM, 38, (235, 235, 240), 3)
def coccyx(t):
    img = Image.fromarray(grad((24, 28, 38), (14, 16, 22)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    cx = 540
    for j in range(9):
        y = 600 + j * 62
        dr.rounded_rectangle((cx - 70, y, cx + 70, y + 46), radius=12, fill=(225, 215, 195))
    dr.polygon([(cx - 170, 1160), (cx + 170, 1160), (cx + 90, 1300), (cx - 90, 1300)], fill=(215, 205, 185))
    g = ss(108.6, 109.6, t) * (0.6 + 0.4 * math.sin(t * 4))
    for j in range(4):
        y = 1300 + j * 34; w = 40 - j * 8
        dr.rounded_rectangle((cx - w, y, cx + w, y + 26), radius=8, fill=(240, 200, 140), outline=mul((255, 225, 160), g), width=4)
    put(img, L_YOUSP, 540, 540, ss(104.4, 105.2, t)); put(img, L_COC, 820, 1360, ss(108.6, 109.4, t))
    return img

# ---------- H: forests shrink, down to the ground ----------
L_AFR = text_img('约 700 万年前 · 非洲：森林继续变少', FB, 38, (255, 235, 200), 3)
L_DOWN = text_img('通往人的那一支，下到了地面', FB, 40, (255, 225, 160), 3)
def ground(t):
    k = ss(113.0, 116.0, t)
    img = Image.fromarray((SKY * (1 - k) + grad((170, 190, 205), (240, 220, 170), 480, 1100) * k).astype(np.uint8)); dr = ImageDraw.Draw(img)
    gc = tuple(int(v) for v in lerp(np.array([110, 125, 75]), np.array([190, 170, 105]), k))
    dr.rectangle((0, GROUND, W, H), fill=gc)
    for i, x in enumerate((90, 260, 430, 620, 820, 990)):
        gone = ss(113.4 + i * 0.4, 115.0 + i * 0.4, t) if i > 1 else 0
        if gone < 0.98: tree(dr, x, GROUND, 560 if i < 2 else 480, 1 - gone)
    for i in range(40):
        x = (i * 31) % W
        if x > 360: dr.line((x, GROUND, x + 4, GROUND - (16 + (i % 4) * 7) * k), fill=(160, 145, 80), width=3)
    if t < 117.0:
        ape_hang(dr, 230, 620, 0.9, t, swing=0.15 * math.sin(t * 2))
        dr.line((90, 620, 330, 600), fill=BR, width=16)
    else:
        d = ss(117.2, 119.6, t)
        if d < 0.98:
            ape_hang(dr, 230, lerp(620, GROUND - 330, d), 0.9, t)
        else:
            ape_stand(dr, lerp(250, 420, ss(119.8, 121.6, t)), GROUND + 30, 1.0)
        dr.line((90, 620, 330, 600), fill=BR, width=16)
    put(img, L_AFR, 540, 1300, ss(113.2, 114.0, t) * (1 - ss(116.8, 117.2, t)))
    put(img, L_DOWN, 540, 1300, ss(117.2, 118.0, t))
    return img

def render(t):
    if t < 6.0: return render18(132.9 + t)
    if t < 44.2:
        k = ss(6.0, 6.6, t) * (1 - ss(43.6, 44.2, t))
        for a in (18.6, 27.0):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(trees_scene(t), k)
    if t < 52.6: return dim(gens(t), ss(44.2, 44.8, t) * (1 - ss(52.0, 52.6, t)))
    if t < 65.6:
        k = ss(52.6, 53.2, t) * (1 - ss(65.0, 65.6, t))
        if 60.8 < t < 61.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 60.8) / 0.8)
        return dim(gene(t), k)
    if t < 74.0: return dim(body(t), ss(65.6, 66.2, t) * (1 - ss(73.4, 74.0, t)))
    if t < 95.6:
        k = ss(74.0, 74.6, t) * (1 - ss(95.0, 95.6, t))
        for a in (78.0, 82.4):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(fossils(t), k)
    if t < 104.2: return dim(family(t), ss(95.6, 96.2, t) * (1 - ss(103.6, 104.2, t)))
    if t < 112.8: return dim(coccyx(t), ss(104.2, 104.8, t) * (1 - ss(112.2, 112.8, t)))
    return dim(ground(t), ss(112.8, 113.4, t))

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep19_{ts}.png')
