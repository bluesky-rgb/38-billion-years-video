import json, base64, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
eps = json.load(open(os.path.join(HERE, '..', 'scripts', 'episodes.json')))
meta = {
 1: ('约 46–44 亿年前', '星云收缩成太阳，地球形成，一次撞击造出月亮'),
 2: ('约 45–44 亿年前', '地球冷却出地壳，火山水汽化作大雨，积成海洋'),
 3: ('约 40 亿年前', '米勒实验与陨石：生命的零件如何自然出现'),
 4: ('约 40 亿年前', 'RNA 既存信息又能催化，学会复制，自然选择开始'),
 5: ('约 40–38 亿年前', '脂类卷成小泡包住 RNA，分裂，共同祖先出现'),
 6: ('约 38–20 亿年前', '细胞变成细菌，蓝细菌放出氧气，臭氧层形成'),
 7: ('约 20 亿年前', '大细胞吞下用氧细菌，线粒体与真核细胞诞生'),
 8: ('约 10–6.4 亿年前', '板块与大陆、超级大陆拼合裂开、冰封又融化'),
 9: ('约 6.4–5.4 亿年前', '细胞粘成群体并分工，海绵与埃迪卡拉生物群'),
 10: ('约 5.6–5.4 亿年前', '爬行带来头、消化道、左右对称和神经索'),
 11: ('约 5.4–5.18 亿年前', '寒武纪大爆发，脊索、肌节、海口鱼与脊椎'),
}
planned = [
 (1, 6, '长出下巴的鱼', '约 4.4 亿年前', '鳃弓变成上下颌，有颌鱼扩张，肉鳍鱼登场', '稿件审核中'),
 (2, 1, '爬上岸的鱼', '约 3.75 亿年前', '鳍变四肢，离开水', '规划'), (2, 2, '带着海水的蛋', '约 3.2 亿年前', '羊膜卵', '规划'),
 (2, 3, '大死亡', '约 2.52 亿年前', '二叠纪大灭绝', '规划'), (2, 4, '恐龙脚下的小老鼠', '约 2 亿年前', '最早的哺乳动物', '规划'),
 (2, 5, '一颗小行星', '6600 万年前', '恐龙灭绝，哺乳动物翻身', '规划'), (2, 6, '爬上树', '约 6000 万年前', '早期灵长类', '规划'),
 (3, 1, '尾巴消失了', '约 2500 万年前', '猿类', '规划'), (3, 2, '站起来', '约 700 万年前', '直立行走', '规划'),
 (3, 3, '第一把石器', '约 250 万年前', '人属出现', '规划'), (3, 4, '火', '约 100 万年前', '用火与更大的大脑', '规划'),
 (3, 5, '走出非洲', '约 30–6 万年前', '智人遍布全球', '规划'), (3, 6, '会讲故事的人', '约 7 万年前', '语言与认知革命', '规划'),
]
SEASON = {0: ('第 0 季', '地球与生命的诞生'), 1: ('第 1 季', '海洋篇'), 2: ('第 2 季', '登陆篇'), 3: ('第 3 季', '人类篇')}
def poster(n):
    p = os.path.join(HERE, 'posters', f'ep{n}.jpg')
    return 'data:image/jpeg;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
def mmss(s):
    s = int(round(s)); return f'{s // 60}:{s % 60:02d}'
total = sum(e['duration_s'] for e in eps)
ncards = sum(len(e['concept_cards']) for e in eps)
cards_html = {0: [], 1: [], 2: [], 3: []}
for e in eps:
    era, what = meta[e['id']]
    cards_html[e['season']].append(f'''<article class="ep">
  <button class="play" type="button" data-src="videos/ep{e['id']:02d}.mp4" data-title="{SEASON[e['season']][0]} · 第 {e['episode']} 集《{html.escape(e['title'])}》" data-you="{html.escape(e['theme'])}" aria-label="播放《{html.escape(e['title'])}》">
    <img src="{poster(e['id'])}" alt="" width="360" height="640" loading="lazy"><span class="tri" aria-hidden="true"></span>
  </button>
  <div class="ep-body">
    <p class="ep-no">{SEASON[e['season']][0]} · 第 {e['episode']} 集 <span class="dur">{mmss(e['duration_s'])}</span></p>
    <h3>{html.escape(e['title'])}</h3>
    <p class="era">{era}</p>
    <p class="what">{what}</p>
    <p class="you"><span>和你的关系</span>{html.escape(e['theme'])}</p>
    <p class="terms">{len(e['concept_cards'])} 张概念卡 · {' · '.join(html.escape(c['term']) for c in e['concept_cards'][:4])}</p>
  </div>
</article>''')
for s, i, title, era, what, st in planned:
    cards_html[s].append(f'''<article class="ep planned">
  <div class="ep-body">
    <p class="ep-no">{SEASON[s][0]} · 第 {i} 集 <span class="state {'review' if st != '规划' else ''}">{st}</span></p>
    <h3>{title}</h3>
    <p class="era">{era}</p>
    <p class="what">{what}</p>
  </div>
</article>''')
seasons = ''
for s in range(4):
    done = sum(1 for e in eps if e['season'] == s)
    seasons += f'''<section class="season" id="s{s}">
  <header><h2>{SEASON[s][0]}<span>{SEASON[s][1]}</span></h2><p class="count">{done} / 6 完成</p></header>
  <div class="grid">{''.join(cards_html[s])}</div>
</section>'''
AGES = [46, 44.5, 40, 40, 39, 30, 20, 7, 6, 5.6, 5.2, 4.4, 3.75, 3.2, 2.52, 2.0, 0.66, 0.6, 0.25, 0.07, 0.025, 0.01, 0.003, 0.0007]
X = lambda a: 40 + (46 - a) / 46 * 920
svg = ['<svg viewBox="0 0 1000 170" role="img" aria-label="24 集在 46 亿年时间轴上的位置">']
svg.append('<rect x="40" y="78" width="920" height="6" rx="3" class="tl-bar"/>')
svg.append(f'<rect x="{X(4.4):.1f}" y="66" width="{960 - X(4.4):.1f}" height="30" rx="4" class="tl-zone"/>')
for a, lab in ((46, '46 亿年前'), (40, '40'), (30, '30'), (20, '20'), (10, '10'), (0, '今天')):
    svg.append(f'<line x1="{X(a):.1f}" x2="{X(a):.1f}" y1="88" y2="98" class="tl-tick"/><text x="{X(a):.1f}" y="118" text-anchor="{"start" if a == 46 else ("end" if a == 0 else "middle")}" class="tl-lab">{lab}</text>')
last = -99; lane = 0
for i, a in enumerate(AGES):
    x = X(a)
    lane = lane + 1 if x - last < 14 else 0
    last = x
    y = 81 - 22 - lane * 0 if i < 11 else 81
    cls = 'tl-done' if i < 11 else 'tl-plan'
    if i < 11:
        svg.append(f'<circle cx="{x:.1f}" cy="{58 - (lane % 3) * 18:.1f}" r="8" class="{cls}"/><text x="{x:.1f}" y="{62 - (lane % 3) * 18:.1f}" text-anchor="middle" class="tl-num">{i + 1}</text>')
svg.append(f'<text x="{X(4.4) - 6:.1f}" y="150" text-anchor="end" class="tl-note">第 1 季第 6 集起的 13 集，都在最后 4.4 亿年里</text>')
svg.append(f'<path d="M{X(4.4) - 2:.1f} 146 L{X(4.4) + 8:.1f} 146 L{X(4.4) + 8:.1f} 100" class="tl-lead"/>')
svg.append('</svg>')
TIMELINE = ''.join(svg)
tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
out = tpl.replace('{{SEASONS}}', seasons).replace('{{N_DONE}}', str(len(eps))).replace('{{TOTAL}}', f'{total / 60:.1f}').replace('{{NCARDS}}', str(ncards)).replace('{{TIMELINE}}', TIMELINE)
open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(out)
print('ok', len(out) // 1024, 'KB')
