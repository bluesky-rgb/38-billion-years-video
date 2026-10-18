"""Generate the 38 亿年家谱 site from repo data.

Pages: index.html, epNN.html (one per finished episode), notes.html, log.html, review.html.
GitHub Pages serves full documents; _artifact.html is the same index as a fragment for the Claude artifact.
"""
import json, os, html, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
def J(*p): return json.load(open(os.path.join(ROOT, *p), encoding='utf-8'))
EPS = J('scripts', 'episodes.json')
FLOW = J('knowledge', 'flow.json')
NOTES = J('knowledge', 'notes.json')
LOG = J('knowledge', 'log.json')
DEC = J('knowledge', 'decisions.json')
DRAFTS = J('knowledge', 'drafts.json')
VIS = J('knowledge', 'vision.json')
METHOD = J('knowledge', 'method.json')
REV = J('knowledge', 'revisions.json')
e_ = html.escape
SEASON = {0: ('第 0 季', '地球与生命的诞生'), 1: ('第 1 季', '海洋篇'), 2: ('第 2 季', '登陆篇'), 3: ('第 3 季', '人类篇')}
ERA = {1: '约 46–44 亿年前', 2: '约 45–44 亿年前', 3: '约 40 亿年前', 4: '约 40 亿年前', 5: '约 40–38 亿年前', 6: '约 38–20 亿年前',
       7: '约 20 亿年前', 8: '约 10–6.4 亿年前', 9: '约 6.4–5.4 亿年前', 10: '约 5.6–5.4 亿年前', 11: '约 5.4–5.18 亿年前', 12: '约 4.4–4 亿年前'}
PLANNED = [
 (2, 2, '带着海水的蛋', '约 3.2 亿年前', '羊膜卵让动物彻底离开水'), (2, 3, '大死亡', '约 2.52 亿年前', '二叠纪大灭绝'),
 (2, 4, '恐龙脚下的小老鼠', '约 2 亿年前', '最早的哺乳动物'), (2, 5, '一颗小行星', '6600 万年前', '恐龙灭绝，哺乳动物翻身'),
 (2, 6, '爬上树', '约 6000 万年前', '早期灵长类'), (3, 1, '尾巴消失了', '约 2500 万年前', '猿类'),
 (3, 2, '站起来', '约 700 万年前', '直立行走'), (3, 3, '第一把石器', '约 250 万年前', '人属出现'),
 (3, 4, '火', '约 100 万年前', '用火与更大的大脑'), (3, 5, '走出非洲', '约 30–6 万年前', '智人遍布全球'),
 (3, 6, '会讲故事的人', '约 7 万年前', '语言与认知革命')]
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;900&family=Noto+Sans+SC:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">'
NAV_ITEMS = [('index.html', '总览'), ('ep01.html', '剧集'), ('about.html', '项目思路'), ('method.html', '方法论'), ('notes.html', '理解笔记'), ('glossary.html', '概念词典'), ('review.html', '待审核'), ('log.html', '制作日志'),
             ('https://github.com/4jt8jty9sk-cpu/38-billion-years', 'GitHub')]
def nav(cur):
    a = ['<nav class="nav" aria-label="网站导航"><a class="brand" href="index.html">38 亿年家谱</a>']
    for href, lab in NAV_ITEMS:
        on = ' aria-current="page"' if cur == href or (cur.startswith('ep') and href == 'ep01.html') else ''
        a.append(f'<a href="{href}"{on}>{lab}</a>')
    return ''.join(a) + '</nav>'
def mmss(s): s = int(round(s)); return f'{s // 60}:{s % 60:02d}'
def ep_label(e): return f"{SEASON[e['season']][0]} · 第 {e['episode']} 集"
def full(title, body, desc=''):
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e_(title)}</title><meta name="description" content="{e_(desc)}">
{FONTS}<link rel="stylesheet" href="style.css"></head>
<body>{body}</body></html>
'''
def write(name, s): open(os.path.join(HERE, name), 'w', encoding='utf-8').write(s)

# ---------- index ----------
def ep_card(e):
    n = e['id']; f = FLOW[str(n)]
    return f'''<article class="ep">
  <button class="play" type="button" data-src="videos/ep{n:02d}.mp4" data-title="{ep_label(e)}《{e_(e['title'])}》" data-you="{e_(e['theme'])}" aria-label="播放《{e_(e['title'])}》">
    <img src="posters/ep{n}.jpg" alt="" width="360" height="640" loading="lazy"><span class="tri" aria-hidden="true"></span>
  </button>
  <div class="ep-body">
    <p class="ep-no">{ep_label(e)} <span class="dur">{mmss(e['duration_s'])}</span></p>
    <h3><a href="ep{n:02d}.html">{e_(e['title'])}</a></h3>
    <p class="era">{ERA[n]}</p>
    <p class="what">{e_(f['premise'])}</p>
    <p class="you"><span>和你的关系</span>{e_(e['theme'])}</p>
    <a class="more" href="ep{n:02d}.html">看完整因果链与旁白 →</a>
  </div>
</article>'''
def planned_card(s, i, title, era, what, state='规划', href=None):
    t = f'<a href="{href}">{title}</a>' if href else title
    return f'''<article class="ep planned"><div class="ep-body">
  <p class="ep-no">{SEASON[s][0]} · 第 {i} 集 <span class="state {'review' if state != '规划' else ''}">{state}</span></p>
  <h3>{t}</h3><p class="era">{era}</p><p class="what">{what}</p></div></article>'''
def seasons():
    out = ''
    for s in range(4):
        cards = [ep_card(e) for e in EPS if e['season'] == s]
        for d in DRAFTS:
            if d['season'] == s: cards.append(planned_card(s, d['episode'], d['title'], d['era'], '植物先上岸造出土壤，肉鳍鱼长出肺和四肢', d['status'], 'review.html'))
        cards += [planned_card(*p) for p in PLANNED if p[0] == s]
        done = sum(1 for e in EPS if e['season'] == s)
        out += f'<section class="season" id="s{s}"><header><h2>{SEASON[s][0]}<span>{SEASON[s][1]}</span></h2><p class="count">{done} / 6 完成</p></header><div class="grid">{"".join(cards)}</div></section>'
    return out
AGES = [46, 44.5, 40, 40, 39, 30, 20, 7, 6, 5.6, 5.2, 4.4]
def timeline():
    X = lambda a: 40 + (46 - a) / 46 * 920
    s = ['<svg viewBox="0 0 1000 170" role="img" aria-label="已完成各集在 46 亿年时间轴上的位置">',
         '<rect x="40" y="78" width="920" height="6" rx="3" class="tl-bar"/>', f'<rect x="{X(4.4):.1f}" y="66" width="{960 - X(4.4):.1f}" height="30" rx="4" class="tl-zone"/>']
    for a, lab in ((46, '46 亿年前'), (40, '40'), (30, '30'), (20, '20'), (10, '10'), (0, '今天')):
        anc = 'start' if a == 46 else ('end' if a == 0 else 'middle')
        s.append(f'<line x1="{X(a):.1f}" x2="{X(a):.1f}" y1="88" y2="98" class="tl-tick"/><text x="{X(a):.1f}" y="118" text-anchor="{anc}" class="tl-lab">{lab}</text>')
    last, lane = -99, 0
    for i, a in enumerate(AGES[:len(EPS)]):
        x = X(a); lane = lane + 1 if x - last < 14 else 0; last = x
        y = 58 - (lane % 3) * 18
        s.append(f'<a href="ep{i + 1:02d}.html"><circle cx="{x:.1f}" cy="{y}" r="8" class="tl-done"/><text x="{x:.1f}" y="{y + 4}" text-anchor="middle" class="tl-num">{i + 1}</text></a>')
    s.append(f'<text x="{X(4.4) - 6:.1f}" y="150" text-anchor="end" class="tl-note">第 2、3 季的 12 集，都在最后 4.4 亿年里</text>')
    s.append(f'<path d="M{X(4.4) - 2:.1f} 146 L{X(4.4) + 8:.1f} 146 L{X(4.4) + 8:.1f} 100" class="tl-lead"/></svg>')
    return ''.join(s)
def note_html(n, full_ep_link=True):
    ep = n.get('ep'); link = ''
    if ep and ep <= len(EPS): link = f' · <a href="ep{ep:02d}.html">看这一集</a>'
    items = ''.join(f'<li>{e_(x)}</li>' for x in n['a'])
    return f'<article class="note" id="{n["id"]}"><p class="tag">{e_(n["tag"])}{link}</p><h3>{e_(n["title"])}</h3><p class="q">{e_(n["q"])}</p><ul>{items}</ul></article>'
def log_li(l): return f'<li><time>{l["date"]}</time><span class="kind k-{l["kind"]}">{l["kind"]}</span><span>{e_(l["text"])}</span></li>'
def review_block(d, full_page=False):
    ul = lambda xs: '<ol>' + ''.join(f'<li>{e_(x)}</li>' for x in xs) + '</ol>'
    head = f'<p class="col">{SEASON[d["season"]][0]} · 第 {d["episode"]} 集《{e_(d["title"])}》 · {d["era"]} · <span class="state review">{d["status"]}</span></p>'
    if not full_page:
        return head + f'<p class="col">稿子按正向流程写好，确认因果通顺后开始制作。<a href="review.html">阅读完整稿件 →</a></p>'
    return head + f'''<ol class="flow">
  <li><span class="lab">前提</span><h3>陆地先绿了</h3>{ul(d["premise"])}</li>
  <li><span class="lab">形成</span><h3>鱼怎么爬上岸</h3>{ul(d["formation"])}</li>
  <li><span class="lab">影响</span><h3>带来了什么</h3>{ul(d["impact"])}</li>
  <li><span class="lab">概念卡</span><h3>新词</h3><p>{"、".join(d["cards"])}</p></li>
  <li><span class="lab">尺度提示</span><p>{e_(d["scale"])}</p></li>
  <li><span class="lab">和你有什么关系</span><p>{e_(d["you"])}</p></li>
  <li><span class="lab">引出</span><p>下一集《{e_(d["next"])}》</p></li>
</ol>'''

PLAYER_JS = open(os.path.join(HERE, 'player.js'), encoding='utf-8').read()
body = open(os.path.join(HERE, 'index_body.html'), encoding='utf-8').read()
total = sum(e['duration_s'] for e in EPS); ncards = sum(len(e['concept_cards']) for e in EPS)
body = (body.replace('{{SEASONS}}', seasons()).replace('{{N_DONE}}', str(len(EPS))).replace('{{TOTAL}}', f'{total / 60:.1f}')
        .replace('{{NCARDS}}', str(ncards)).replace('{{N_NOTES}}', str(len(NOTES))).replace('{{N_LOG}}', str(len(LOG))).replace('{{TIMELINE}}', timeline())
        .replace('{{NOTES_PREVIEW}}', ''.join(note_html(n) for n in NOTES[-3:]))
        .replace('{{REVIEW_PREVIEW}}', ''.join(review_block(d) for d in DRAFTS) or '<p>暂无待审核稿件。</p>')
        .replace('{{DECISIONS}}', ''.join(f'<tr><td class="k">{e_(d["t"])}</td><td>{e_(d["d"])}</td></tr>' for d in DEC))
        .replace('{{LOG_LATEST}}', ''.join(log_li(l) for l in LOG[::-1][:5])))
body = re.sub(r'<script>.*?</script>', '', body, flags=re.S) + f'<script>{PLAYER_JS}</script>'
desc = '《38 亿年家谱》系列的进度、每集因果链、理解笔记、制作日志与下一步。'
write('index.html', full('38 亿年家谱', body.replace('{{NAV}}', nav('index.html')), desc))
write('_artifact.html', f'<title>38 亿年家谱</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n{FONTS}<link rel="stylesheet" href="style.css">\n' + body.replace('{{NAV}}', nav('index.html')))

# ---------- episode pages ----------
for k, e in enumerate(EPS):
    n = e['id']; f = FLOW[str(n)]
    prev = f'<a href="ep{n - 1:02d}.html">← 上一集《{e_(EPS[k - 1]["title"])}》</a>' if k else '<span></span>'
    nxt = f'<a href="ep{n + 1:02d}.html">下一集《{e_(EPS[k + 1]["title"])}》→</a>' if k + 1 < len(EPS) else '<a href="review.html">下一集稿件（待审核）→</a>'
    lines = [(0, x, 'r') for x in e['recap']] + [(round(x['start'] + 7.0, 1), x['text'], '') for x in e['narration']]
    script = ''.join(f'<div class="{c}"><time>{mmss(t) if c == "" else "回顾"}</time><span>{e_(x)}</span></div>' for t, x, c in lines)
    cards = ''.join(f'<span class="chip"><b>{e_(c["term"])}</b>{e_(c["definition"])}</span>' for c in e['concept_cards'])
    rv = REV.get(str(n), [])
    revs = ('<section class="block"><h2>修订记录</h2><p class="cap">审片时发现的问题和补上的内容。</p><ol class="log">' + ''.join(f'<li><time>第 {x[2]} 轮</time><span class="kind k-修正">修正</span><span>{e_(x[x.index("：") + 1:])}</span></li>' for x in rv) + '</ol></section>') if rv else ''
    related = [nn for nn in NOTES if nn.get('ep') == n]
    rel = ('<section class="block"><h2>相关理解笔记</h2><div class="notes">' + ''.join(note_html(x) for x in related) + '</div></section>') if related else ''
    b = f'''<div class="wrap">{nav(f"ep{n:02d}.html")}
<header class="page-head"><p class="kicker">{ep_label(e)} · {ERA[n]} · {mmss(e['duration_s'])}</p><h1>{e_(e['title'])}</h1></header>
<div class="detail">
  <div class="side"><video controls playsinline preload="metadata" poster="posters/ep{n}.jpg" src="videos/ep{n:02d}.mp4"></video>
  <p class="cap">720p 预览版 · 临时配音</p></div>
  <ol class="flow">
    <li><span class="lab">1 · 前提</span><h3>当时的世界</h3><p>{e_(f['premise'])}</p></li>
    <li><span class="lab">2 · 形成</span><h3>一步步怎么来的</h3><ol>{''.join(f'<li>{e_(x)}</li>' for x in f['formation'])}</ol></li>
    <li><span class="lab">3 · 变化</span><h3>原因到结果</h3><p>{e_(f['change'])}</p></li>
    <li><span class="lab">4 · 概念</span><h3>{len(e['concept_cards'])} 张概念卡</h3><div class="chips">{cards}</div></li>
    <li><span class="lab">5 · 影响</span><h3>和你有什么关系</h3><p>{e_(f['impact'])}</p></li>
    <li><span class="lab">6 · 引出</span><h3>通向下一集</h3><p>{e_(f['leads'])}</p></li>
  </ol>
</div>
<section class="block"><h2>完整旁白</h2><p class="cap">时间为成片中的位置；"回顾"为开头 7 秒的上集回顾。</p><div class="script">{script}</div></section>
{revs}{rel}
<nav class="pager" aria-label="翻页">{prev}{nxt}</nav>
</div>'''
    write(f'ep{n:02d}.html', full(f'{e["title"]} · 38 亿年家谱', b, f['premise']))

# ---------- notes / log / review ----------
nb = f'''<div class="wrap">{nav("notes.html")}<header class="page-head"><p class="kicker">理解笔记 · {len(NOTES)} 条</p><h1>我们的理解</h1>
<p class="lede">每条笔记来自制作中的一个问题。先弄懂，再写进片子里。</p></header><div class="notes">{"".join(note_html(x) for x in NOTES)}</div></div>'''
write('notes.html', full('理解笔记 · 38 亿年家谱', nb, '制作中提出的每个问题和答案。'))
lb = f'''<div class="wrap">{nav("log.html")}<header class="page-head"><p class="kicker">制作日志 · {len(LOG)} 步</p><h1>每一步</h1>
<p class="lede">从一个想法到现在，项目做过的每一件事。最新的在最上面。</p></header><ol class="log">{"".join(log_li(l) for l in LOG[::-1])}</ol></div>'''
write('log.html', full('制作日志 · 38 亿年家谱', lb, '项目从想法到现在的每一步。'))
rb = f'''<div class="wrap">{nav("review.html")}<header class="page-head"><p class="kicker">待审核稿件</p><h1>下一集的稿子</h1>
<p class="lede">按正向流程写好，确认因果通顺、没有跳步后才开始制作。</p></header>{"".join(f'<section class="block" style="border-top:0;margin-top:0;padding-top:16px"><h2>《{e_(d["title"])}》</h2>{review_block(d, True)}</section>' for d in DRAFTS) or '<p>暂无待审核稿件。</p>'}</div>'''
write('review.html', full('待审核稿件 · 38 亿年家谱', rb, '下一集的稿子。'))

def sec(title, inner, lead=''):
    return f'<section class="block"><h2>{title}</h2>{f"<p class=col>{lead}</p>" if lead else ""}{inner}</section>'
def table(heads, rows):
    return '<div class="tbl"><table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in heads) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td{" class=k" if i == 0 else ""}>{e_(c)}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows) + '</tbody></table></div>'
def ulist(xs, tag='ul'): return f'<{tag} class="plain">' + ''.join(f'<li>{e_(x)}</li>' for x in xs) + f'</{tag}>'
V = VIS
two = '<div class="tbl"><table class="lines"><thead><tr><th>时间</th><th>合作：谁和谁组成整体</th><th>信息：靠什么记住和传递</th><th>在哪一集</th></tr></thead><tbody>' + ''.join(
    f'<tr{" class=gene" if i == 4 else ""}><td class="k">{e_(l["era"])}</td><td>{e_(l["coop"])}</td><td>{e_(l["info"])}</td><td class="muted">{e_(l["ep"])}</td></tr>' for i, l in enumerate(V['lines'])) + '</tbody></table></div><p class="cap">从 7 万年前那一行开始，变化从靠基因改为靠文化，速度从几亿年缩短到几百年。</p>'
prod = '<div class="cards3">' + ''.join(f'<div><p class="ep-no">{e_(p["s"])}</p><h3>{e_(p["n"])}</h3><p>{e_(p["d"])}</p></div>' for p in V['products']) + '</div>'
qual = '<div class="three">' + ''.join(f'<div><h3>{e_(q["n"])}</h3><p>{e_(q["d"])}</p></div>' for q in V['quality']) + '</div>'
ab = f"""<div class="wrap">{nav("about.html")}<header class="page-head"><p class="kicker">项目思路</p><h1>为什么做，做成什么样</h1>
<p class="lede">{e_(V['thesis'])}</p></header>
{sec('两条主线', two, '每一次跃迁都同时发生两件事：原本独立的单位合作成更大的整体，信息有了新的存储和传递方式。')}
{sec('终点：社会的本质', ulist(V['society']), '这个系列最初的问题是"人类群体是怎么演变来的"。往回追到生命起源，是为了让这个答案有根。')}
{sec('系列方案', table(['事项', '方案'], [(p['n'], p['d']) for p in V['plan']]))}
{sec('产品矩阵', prod, '一个核心叙事，用不同形态反复讲。先用短视频验证，再延伸。')}
{sec('质感评估', qual)}
{sec('声音方案', ulist(V['voice']))}
{sec('英文版与海外', ulist(V['overseas']))}
{sec('发布后看什么', table(['指标', '看什么', '偏低时怎么改'], [(m['n'], m['w'], m['f']) for m in V['metrics']]), '先用前两季在国内平台测试，每周 2–3 集，观察 2–3 周数据再调整。')}
{sec('待决定', '<ul class="todo">' + ''.join(f'<li>{e_(x)}</li>' for x in V['pending']) + '</ul>')}
</div>"""
write('about.html', full('项目思路 · 38 亿年家谱', ab, V['thesis']))
M = METHOD
steps = '<ol class="steps">' + ''.join(f'<li><b>{i + 1}</b><strong>{a}</strong><span>{e_(b)}</span></li>' for i, (a, b) in enumerate(M['steps'])) + '</ol>'
mb = f"""<div class="wrap">{nav("method.html")}<header class="page-head"><p class="kicker">方法论</p><h1>正向流程</h1>
<p class="lede">每一集、每一个新出现的事物，都按这六步讲完，不允许凭空出现、不允许跳步。这套方法是在一次次"没看懂"里总结出来的。</p></header>
{steps}
{sec('从修订中学到的', table(['审片时的问题', '学到的规则'], M['lessons']))}
{sec('写稿自查', ulist(M['selfcheck'], 'ol'))}
{sec('引导装置', table(['装置', '作用', '片中的例子'], M['devices']))}
{sec('制作流程', table(['步骤', '谁来做', '在哪里'], M['pipeline']), '每一步都提交到 GitHub 仓库，网页随之更新。')}
{sec('成片检查清单', '<ul class="todo">' + ''.join(f'<li>{e_(x)}</li>' for x in M['checklist']) + '</ul>')}
</div>"""
write('method.html', full('方法论 · 38 亿年家谱', mb, '正向流程六步、引导装置、制作流程与检查清单。'))
gl = ''
nterms = 0
for e in EPS:
    if not e['concept_cards']: continue
    nterms += len(e['concept_cards'])
    gl += f'<section class="gloss"><h2><a href="ep{e["id"]:02d}.html">{ep_label(e)} · {e_(e["title"])}</a></h2><dl>' + ''.join(f'<div><dt>{e_(c["term"])}</dt><dd>{e_(c["definition"])}</dd></div>' for c in e['concept_cards']) + '</dl></section>'
gb = f"""<div class="wrap">{nav("glossary.html")}<header class="page-head"><p class="kicker">概念词典 · {nterms} 个词</p><h1>每个新词，一句白话</h1>
<p class="lede">片中每个新词第一次出现时都会弹出概念卡。这里按出现顺序全部收录，看完就是一份从星云到有颌鱼的词汇表。</p></header>{gl}</div>"""
write('glossary.html', full('概念词典 · 38 亿年家谱', gb, '片中全部概念卡，按出现顺序。'))
print('built', 6 + len(EPS) + 1, 'pages')

