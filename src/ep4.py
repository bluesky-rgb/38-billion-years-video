import numpy as np, math, subprocess, sys
from PIL import Image, ImageDraw
from ep1 import W, H, FPS, ss, lerp, text_img, put, fade_win, FB, FM, FL
from ep3 import SEA, xxg, yyg

DUR = 68.0
BC = {'A': (240, 110, 100), 'U': (240, 200, 90), 'G': (90, 150, 245), 'C': (90, 210, 130)}
PAIR = {'A': 'U', 'U': 'A', 'G': 'C', 'C': 'G'}
LET = {k: text_img(k, FB, 30, (20, 20, 30), 0) for k in BC}
BACK = (200, 225, 230)

def sea(t):
    rays = 0.5 + 0.5 * np.sin(xxg[0, :, 0] * 0.012 + t * 0.4) * np.sin(xxg[0, :, 0] * 0.027 - t * 0.25)
    f = SEA + (rays[None, :] * np.clip(1 - yyg[..., 0] / 1100, 0, 1) * 30)[..., None] * np.array([0.6, 1.0, 1.0])
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(70):
        x = (i * 211 + t * 6) % W; y = (i * 457 - t * 12) % H
        dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(70, 120, 130))
    return img, dr

def mul(c, a): return tuple(int(v * a) for v in c)

def base(img, dr, x, y, b, up=True, a=1.0, s=1.0):
    w, h = 40 * s, 70 * s
    y0, y1 = (y - h, y) if up else (y, y + h)
    dr.rounded_rectangle((x - w / 2, y0, x + w / 2, y1), radius=8 * s, fill=mul(BC[b], a))
    if s > 0.7: put(img, LET[b], x, (y0 + y1) / 2, a)

def strand(img, dr, pts, seq, ups, a=1.0, s=1.0):
    if len(pts) > 1: dr.line(pts, fill=mul(BACK, a), width=int(10 * s), joint='curve')
    for (x, y), b, up in zip(pts, seq, ups): base(img, dr, x, y, b, up, a, s)
    for x, y in pts: dr.ellipse((x - 9 * s, y - 9 * s, x + 9 * s, y + 9 * s), fill=mul((235, 245, 245), a))

def arrow_arc(dr, box, start, end, col, w=6):
    dr.arc(box, start, end, fill=col, width=w)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2; rx, ry = (box[2] - box[0]) / 2, (box[3] - box[1]) / 2
    a = math.radians(end); x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
    tx, ty = -math.sin(a), math.cos(a)
    dr.polygon([(x + tx * 22, y + ty * 22), (x - ty * 14 - tx * 4, y + tx * 14 - ty * 4), (x + ty * 14 - tx * 4, y - tx * 14 - ty * 4)], fill=col)

L_DNA = text_img('DNA', FB, 52, (170, 200, 255), 3)
L_PRO = text_img('蛋白质', FB, 52, (140, 230, 160), 3)
L_INFO = text_img('图纸', FM, 40, (210, 220, 230), 2)
L_HELP = text_img('帮忙', FM, 40, (210, 220, 230), 2)
QM = text_img('?', FB, 220, (255, 225, 150), 8)
L_RNA = text_img('RNA', FB, 64, (255, 225, 150), 4)
L_STORE = text_img('存储信息', FM, 42, (170, 200, 255), 2)
L_CAT = text_img('催化反应', FM, 42, (140, 230, 160), 2)
pr = np.random.default_rng(3)
PROT = [(pr.normal() * 70, pr.normal() * 90, 22 + pr.random() * 10) for _ in range(16)]

def scene_a(t):
    img, dr = sea(t)
    a = ss(6.2, 7.2, t)
    cx, cy = 300, 860; ph = t * 1.5
    seqs = 'AGCUAGGCUAACGU'
    for i in range(14 if a > 0 else 0):
        y = cy - 330 + i * 50
        x1 = cx + 70 * math.sin(i * 0.6 + ph); x2 = cx - 70 * math.sin(i * 0.6 + ph)
        dr.line((x1, y, x2, y), fill=mul(BC[seqs[i]], a * 0.9), width=10)
    for sgn in ((1, -1) if a > 0 else ()):
        pts = [(cx + sgn * 70 * math.sin(i * 0.12 + ph), cy - 330 + i * 10) for i in range(66)]
        dr.line(pts, fill=mul((170, 200, 255), a), width=9)
    put(img, L_DNA, cx, cy + 400, a)
    b = ss(9.8, 10.8, t); px, py = 780, 860
    for x, y, r in (PROT if b > 0 else []):
        x += px + 6 * math.sin(t * 2 + r); y += py + 6 * math.cos(t * 1.7 + r)
        dr.ellipse((x - r, y - r, x + r, y + r), fill=mul((90, 210, 130), b))
        dr.ellipse((x - r * 0.5, y - r * 0.6, x - r * 0.05, y - r * 0.2), fill=mul((140, 245, 175), b))
    put(img, L_PRO, px, cy + 400, b)
    c = ss(14.2, 15.2, t)
    if c > 0:
        arrow_arc(dr, (330, 380, 750, 760), 205, 335, mul((220, 230, 240), c))
        arrow_arc(dr, (330, 960, 750, 1340), 25, 155, mul((220, 230, 240), c))
        put(img, L_INFO, 540, 330, c); put(img, L_HELP, 540, 1390, c)
    q = ss(18.4, 19.2, t)
    if q > 0:
        qs = 1 + 0.06 * math.sin(t * 4)
        put(img, QM, 540, 860, q)
    return img

STRAND = 'AGCUUGACGAUC'
def scene_b(t):
    img, dr = sea(t)
    n = len(STRAND); k = ss(30.6, 33.0, t)
    pts, ups = [], []
    for i in range(n):
        sx, sy = 155 + i * 70, 960 + 18 * math.sin(i * 0.8 + t * 1.5)
        if i < 6: fx, fy, fu = 340 + i * 70, 1040, True
        else: fx, fy, fu = 340 + (11 - i) * 70, 830, False
        if i in (5, 6): fx += 70
        pts.append((lerp(sx, fx, k), lerp(sy, fy, k))); ups.append(True if k < 0.5 else fu)
    vis = [ss(22.8 + i * 0.25, 23.2 + i * 0.25, t) for i in range(n)]
    shown = [i for i in range(n) if vis[i] > 0]
    if shown:
        dr.line([pts[i] for i in shown], fill=BACK, width=10, joint='curve')
        for i in shown:
            base(img, dr, *pts[i], STRAND[i], ups[i], vis[i])
            dr.ellipse((pts[i][0] - 9, pts[i][1] - 9, pts[i][0] + 9, pts[i][1] + 9), fill=(235, 245, 245))
    put(img, L_RNA, 540, 620, ss(23.5, 24.5, t))
    put(img, L_STORE, 300, 1300, ss(27.2, 28, t))
    put(img, L_CAT, 780, 1300, ss(31.2, 32, t))
    if t > 32.8:
        g = ss(32.8, 33.6, t) * (0.6 + 0.4 * math.sin(t * 5))
        for r in (240, 270):
            dr.ellipse((620 - r, 935 - r * 0.55, 620 + r, 935 + r * 0.55), outline=mul((255, 225, 150), g * (300 - r) / 60), width=3)
    return img

TEMP = 'AUGCCGAUAGCU'
fr = np.random.default_rng(7)
FREE = [(fr.random() * W, 300 + fr.random() * 500, fr.random() * 6) for _ in range(12)]
def scene_c(t):
    img, dr = sea(t)
    n = len(TEMP); x0 = 155
    tp = [(x0 + i * 70, 1150) for i in range(n)]
    strand(img, dr, tp, TEMP, [True] * n, ss(35.2, 36, t))
    sep = ss(44.2, 46.6, t) * 260
    placed = []
    for i in range(n):
        tin = 39.6 + i * 0.32
        fx, fy, ph = FREE[i]
        fx += 30 * math.sin(t + ph); fy += 30 * math.cos(t * 0.8 + ph)
        k = ss(tin, tin + 0.6, t)
        tx, ty = tp[i][0], tp[i][1] - 150 - sep
        x, y = lerp(fx, tx, k), lerp(fy, ty, k)
        a = ss(36.5, 37.3, t)
        if k >= 1: placed.append((x, y))
        else:
            base(img, dr, x, y, PAIR[TEMP[i]], False, a)
            dr.ellipse((x - 9, y - 9, x + 9, y + 9), fill=mul((235, 245, 245), a))
    if placed:
        bk = ss(43.0, 43.8, t)
        if bk > 0 and len(placed) == n: dr.line(placed, fill=mul(BACK, bk), width=10)
        for i, (x, y) in enumerate(placed):
            base(img, dr, x, y, PAIR[TEMP[i]], False)
            dr.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(235, 245, 245))
    return img

def mini(dr, x, y, col, a, s=1.0, wob=0.0):
    pts = [(x - 50 * s + i * 12.5 * s, y + 5 * s * math.sin(i * 0.9 + wob)) for i in range(9)]
    dr.line(pts, fill=mul(col, a), width=max(2, int(5 * s)))
    for i, (px, py) in enumerate(pts):
        c = list(BC.values())[i % 4]
        dr.line((px, py, px, py - 18 * s), fill=mul(c, a), width=max(2, int(6 * s)))

COUNT = {n: text_img(f'× {n}', FB, 64, (255, 225, 150), 4) for n in (1, 2, 4, 8, 16, 32, 64)}
def scene_d(t):
    img, dr = sea(t)
    if t < 52.0:
        e = int(max(0, (t - 47.6) / 0.62)); n = min(2 ** e, 64)
        cols = 8; s = 1.0 if n <= 4 else 0.75
        a = ss(47.6, 48.2, t)
        for k in range(n):
            r, c = divmod(k, cols); m = min(n, cols)
            x = 540 + (c - (m - 1) / 2) * 120; y = 600 + r * 110
            mini(dr, x, y, BACK, a * (ss(47.6 + e * 0.62, 47.9 + e * 0.62, t) if k >= n // 2 and n > 1 else 1), s, t * 2 + k)
        put(img, COUNT[n], 540, 1450, a)
        return img
    rows, cols = 8, 6
    g = 1 + 47 / (1 + math.exp(-(t - 58.6) * 1.1)) if t > 54 else 0
    gold = set(int(v) for v in np.random.default_rng(2).permutation(48)[:max(0, int(round(g)))]) if t > 54 else set()
    if 53.0 < t <= 54: gold = {21}
    for k in range(48):
        r, c = divmod(k, cols)
        x = 540 + (c - 2.5) * 160; y = 480 + r * 120
        isg = k in gold
        col = (255, 205, 90) if isg else BACK
        if isg:
            dr.rounded_rectangle((x - 66, y - 34, x + 66, y + 22), radius=14, fill=(70, 62, 30))
        if k == 21 and 53.0 < t < 55:
            fl = 0.5 + 0.5 * math.sin(t * 14)
            dr.ellipse((x - 70, y - 50, x + 70, y + 40), outline=mul((255, 230, 150), fl), width=3)
        mini(dr, x, y, col, 1.0 if isg else 0.75, 1.0, t * (4 if isg else 2) + k)
    return img

CAPS = [(6.4, 10.4, '今天的细胞里，DNA 存储信息'), (10.4, 14.4, '蛋白质负责干活'), (14.4, 18.6, '可它们谁也离不开谁'),
        (18.6, 22.4, '那最早，到底先有谁？'), (22.8, 27.0, '科学家找到了一个两面手：RNA'),
        (27.0, 31.0, '它能像 DNA 一样存储信息'), (31.0, 35.0, '又能像蛋白质一样催化反应'),
        (35.4, 39.6, '一条 RNA，可以当作模板'), (39.6, 43.8, '吸来散落的零件，按规则配对'),
        (43.8, 47.6, '拼出新链，再分开'), (47.8, 51.8, '一变二，二变四，越来越多'),
        (52.2, 56.2, '复制时，偶尔会出错'), (56.2, 60.0, '复制得更快的，后代就更多'),
        (60.0, 63.4, '自然选择，从这一刻开始了')]
cap_imgs = [(a, b, text_img(s, FM, 54)) for a, b, s in CAPS]
ERA = text_img('RNA 世界假说 · 约 40 亿年前', FL, 40, (230, 200, 160), 3)
T_SERIES = text_img('38 亿年家谱', FB, 110, (255, 220, 170), 6)
T_EP = text_img('第 0 季 · 第 4 集', FM, 46, (220, 220, 220), 3)
T_NAME = text_img('会复制的分子', FB, 80, (255, 255, 255), 5)
T_NEXT1 = text_img('下一集', FM, 48, (220, 220, 220), 3)
T_NEXT2 = text_img('第一个细胞', FB, 96, (150, 230, 220), 6)

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

CLEAN = False

def render(t):
    if t < 22.6: img = dim(scene_a(t), (1 if CLEAN else ss(0, 1.2, t)) * (1 - ss(22.0, 22.6, t)))
    elif t < 35.2: img = dim(scene_b(t), ss(22.6, 23.2, t) * (1 - ss(34.6, 35.2, t)))
    elif t < 47.6: img = dim(scene_c(t), ss(35.2, 35.8, t) * (1 - ss(47.0, 47.6, t)))
    else: img = dim(scene_d(t), ss(47.6, 48.0, t) * (1 if CLEAN else (1 - 0.65 * ss(63.4, 64.2, t)) * (1 - ss(66.6, 68, t))))
    if CLEAN: return img
    ta = fade_win(t, 1.0, 6.0, 0.7)
    if t < 6.2:
        img = dim(img, 1 - 0.6 * ta)
    put(img, T_SERIES, W / 2, 760, ta); put(img, T_EP, W / 2, 880, ta)
    put(img, T_NAME, W / 2, 1010, fade_win(t, 2.2, 6.0, 0.7))
    for a, b, im in cap_imgs:
        if a <= t <= b: put(img, im, W / 2, 1660, fade_win(t, a, b, 0.35))
    put(img, ERA, W / 2, 200, fade_win(t, 6.0, 63.4, 0.6))
    na = fade_win(t, 63.8, 68.0, 0.6)
    put(img, T_NEXT1, W / 2, 1500, na); put(img, T_NEXT2, W / 2, 1610, na)
    return img

if __name__ == '__main__':
    if sys.argv[1] == 'stills':
        for ts in sys.argv[2:]: render(float(ts)).save(f'ep4_still_{ts}.png')
    else:
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                              '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
                              '-crf', '20', '-pix_fmt', 'yuv420p', sys.argv[2]], stdin=subprocess.PIPE)
        nf = int(DUR * FPS)
        for i in range(nf):
            p.stdin.write(render(i / FPS).tobytes())
            if i % 300 == 0: print(i, nf, flush=True)
        p.stdin.close(); p.wait(); print('done')
