# -*- coding: utf-8 -*-
"""Step 2: canonical / meta / OG / JSON-LD / img attrs / related articles / topic hubs / sitemap / robots / 404."""
import os, re, glob, json, subprocess, html as H
from datetime import date
from PIL import Image

os.chdir(r'C:\Users\long_\ascent-sr-site')
BASE = 'https://ascent-sr.jp/'
SITE = 'アセント社労士事務所'
AUTHOR = '長田充博'
TODAY = date.today().isoformat()
LOGO = BASE + 'images/ascent-logo.png'
DEFAULT_OG = BASE + 'images/representative-new.jpg'
EXCLUDE = lambda f: f.startswith('index-before') or f == '404.html'

def read(p):
    return open(p, encoding='utf-8').read()

def write(p, s):
    open(p, 'w', encoding='utf-8', newline='').write(s)

def git_date(f, first=False):
    cmd = ['git', 'log', '--format=%cs'] + (['--diff-filter=A'] if first else ['-1']) + ['--', f]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.split()
    return (out[-1] if first else out[0]) if out else TODAY

def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()

def jsonld(obj):
    return '    <script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + '\n    </script>\n'

def page_url(f):
    if f == 'index.html': return BASE
    if f.endswith('/index.html'): return BASE + f[:-10]
    return BASE + f

def orig_image(src):
    """webp -> original jpg/png for og:image; returns absolute url or None."""
    if not src: return None
    src = src.split('?')[0]
    base, ext = os.path.splitext(src)
    for cand in ([src] if ext.lower() != '.webp' else []) + [base + '.jpg', base + '.png', src]:
        if os.path.exists(cand):
            return BASE + cand
    return None

# ---------------------------------------------------------------- blog metadata
bl = read('blog-list.html')
BLOG = {}
for c in re.findall(r'<article.*?</article>', bl, re.S):
    href = re.search(r'href="(blog-[^"]+)"', c)
    if not href or not os.path.exists(href.group(1)): continue
    d = re.search(r'fa-calendar-alt mr-2"></i>([\d.]+)', c)
    cat = re.findall(r'rounded text-xs">([^<]+)</span>', c)
    img = re.search(r'<img\s+src="([^"]+)"', c)
    BLOG[href.group(1)] = dict(date=d.group(1).replace('.', '-') if d else None, cat=cat[0] if cat else '労務コラム', img=img.group(1) if img else None, listed=True)

for f in sorted(glob.glob('blog-*.html')):
    if f == 'blog-list.html': continue
    h = read(f)
    m = BLOG.setdefault(f, dict(date=None, cat='労務コラム', img=None, listed=False))
    t = re.search(r'<title>([^<]*)</title>', h).group(1)
    m['title'] = re.sub(r'\s*[|｜]\s*アセント社労士事務所\s*$', '', t).strip()
    dm = re.search(r'name="description"\s+content="([^"]*)"', h)
    m['desc'] = dm.group(1) if dm else ''
    if not m['date']:
        od = re.search(r'fa-calendar-alt[^>]*></i>\s*(\d{4})[.年](\d{1,2})[.月](\d{1,2})', h)
        m['date'] = f'{od.group(1)}-{int(od.group(2)):02d}-{int(od.group(3)):02d}' if od else git_date(f, first=True)
    if not m['img']:
        mi = re.search(r'<main.*?<img\s+src="(images/[^"]+)"', h, re.S)
        m['img'] = mi.group(1) if mi else None
    m['mod'] = max(git_date(f), m['date'])

# ---------------------------------------------------------------- topic hubs
HUBS = [
    ('topic-social-insurance-payroll.html', '社会保険・給与計算',
     '社会保険の加入基準、保険料率の改定、随時改定、給与計算の落とし穴など、毎月の手続きで迷いやすい論点をまとめました。',
     '大阪のサービス業では、シフトで働くアルバイトやパートが多く、社会保険の加入・喪失や給与計算の判断が店舗ごとにぶれがちです。ここでは、社会保険と給与計算に関する記事をテーマ別にまとめています。',
     ['social-insurance', 'shift-worker', 'monthly-remuneration', 'payroll', 'minimum-wage', 'employment-insurance', 'health-insurance', 'child-support-fund', 'defined-contribution', 'working-oldage', 'student-part-time', 'maternity', 'employee-count', 'retiree-data', 'proper-resignation', 'store-social'],
     [('pricing.html', '労務顧問・給与計算のサービスと料金を見る')]),
    ('topic-working-hours-work-rules.html', '労働時間・就業規則',
     '残業時間の上限、労働時間の数え方、変形労働時間制、就業規則の作り方と運用など、労働時間と会社のルールに関する記事です。',
     '労働時間の管理と就業規則は、労務トラブルの入口にも出口にもなります。労働基準監督署の指導が変わる中で、サービス業の現場で本当に回るルールの作り方を、記事ごとに解説しています。',
     ['overtime', 'changing-clothes', 'work-rules', 'monthly-variable', 'time-management', 'paid-leave', 'hamasushi', 'side-job', 'labor-law-reform', 'teachers', 'child-safety', 'equal-treatment', 'overseas', 'employment-contract'],
     [('work-rules.html', '就業規則見直しサポートを見る')]),
    ('topic-hiring-resignation-trouble.html', '採用・退職・トラブル対応',
     '初めての採用、退職の手順、雇い止め、ハラスメント対応、労災事故の予防など、人が入るときと辞めるときに起こりやすい問題をまとめました。',
     '人を雇うとき、辞めてもらうとき、そしてトラブルが起きたとき。社長がひとりで抱え込みやすい場面ほど、事前の準備と正しい手順が効きます。採用・退職・トラブル対応に関する記事を集めました。',
     ['first-hire', 'first-employee', 'labor-stability', 'resignation', 'reemployment', 'termination', 'retirement-benefit', 'customer-harassment', 'harassment', 'industrial-accident', 'heatstroke'],
     [('first-hire-lp.html', '採用・労務整備スタートパックを見る'), ('labor-stability-diagnosis.html', '労務安定度 5分診断を受ける')]),
    ('topic-mental-health-workstyle.html', 'メンタルヘルス・働き方改革',
     'メンタル不調の兆候と復職、ストレスチェックの義務化、ワークライフハーモニー、AI活用など、これからの働き方に関する記事です。',
     '社員の心の健康と、会社の働き方は切り離せません。2028年のストレスチェック義務化への備えから、休み方で仕事を変えるワークライフハーモニーの考え方まで、働き方改革に関する記事をまとめています。',
     ['mental-health', 'stress-check', 'work-life', 'worklife', 'flexible-work', 'official-line', 'work-family', 'chatgpt', 'double-license', 'ai-workflow', 'xml-file'],
     [('index.html#services', 'サービス案内を見る')]),
]
HUB_OF = {}
for f in BLOG:
    for hub in HUBS:
        if any(k in f for k in hub[4]):
            HUB_OF[f] = hub; break
unassigned = [f for f in BLOG if f not in HUB_OF]
print('unassigned blogs:', unassigned)
for f in unassigned:
    HUB_OF[f] = HUBS[1]

def bigrams(s):
    s = re.sub(r'[\s、。「」！？!?・（）()【】｜|]', '', s)
    return {s[i:i + 2] for i in range(len(s) - 1)}

def related(f, n=3):
    hub = HUB_OF[f]
    cands = [g for g in BLOG if g != f and HUB_OF[g] is hub and BLOG[g]['listed']]
    bg = bigrams(BLOG[f]['title'])
    cands.sort(key=lambda g: (-len(bg & bigrams(BLOG[g]['title'])), BLOG[g]['date']), reverse=False)
    cands.sort(key=lambda g: -len(bg & bigrams(BLOG[g]['title'])))
    return cands[:n]

# ---------------------------------------------------------------- head fixes
def insert_after(h, pattern, text):
    m = re.search(pattern, h)
    return h[:m.end()] + '\n' + text + h[m.end():] if m else h

def fix_head(f, h):
    url = page_url(f)
    title = re.search(r'<title>([^<]*)</title>', h).group(1).strip()
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
    h1 = strip_tags(h1.group(1)) if h1 else ''

    # title for pages whose title is just the site name
    if title == SITE:
        if f == 'thanks.html':
            title = 'お問い合わせありがとうございます | ' + SITE
        elif h1:
            title = h1 + ' | ' + SITE
        h = re.sub(r'<title>[^<]*</title>', '<title>' + H.escape(title, quote=False) + '</title>', h, count=1)

    # description
    if not re.search(r'name="description"', h):
        if f == 'thanks.html':
            desc = 'アセント社労士事務所へのお問い合わせを受け付けました。内容を確認のうえ、担当者よりご連絡いたします。'
        else:
            body = h[h.find('<main'):] if '<main' in h else h
            ps = [strip_tags(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', body, re.S)]
            ps = [p for p in ps if len(p) > 25]
            desc = (ps[0] if ps else h1)
            desc = (desc[:105] + '…') if len(desc) > 110 else desc
            desc = f'{desc}（{SITE}のお知らせ）' if f.startswith('news-') else desc
        h = insert_after(h, r'<title>[^<]*</title>', f'    <meta name="description" content="{H.escape(desc)}">')
    desc = re.search(r'name="description"\s+content="([^"]*)"', h).group(1)

    # canonical (idempotent)
    if 'rel="canonical"' not in h:
        h = insert_after(h, r'<meta name="viewport"[^>]*>', f'    <link rel="canonical" href="{url}">')

    # robots for thanks
    if f == 'thanks.html' and 'name="robots"' not in h:
        h = insert_after(h, r'<link rel="canonical"[^>]*>', '    <meta name="robots" content="noindex, follow">')

    # OG
    if 'og:title' not in h:
        og_img = DEFAULT_OG
        if f in BLOG and BLOG[f]['img']:
            og_img = orig_image(BLOG[f]['img']) or DEFAULT_OG
        else:
            mi = re.search(r'<main.*?<img\s+src="(images/[^"]+)"', h, re.S)
            if mi and 'logo' not in mi.group(1) and 'qr' not in mi.group(1):
                og_img = orig_image(mi.group(1)) or DEFAULT_OG
        og_type = 'article' if (f in BLOG or f.startswith('news-') or f in ('certified-sr.html', 'festa2025.html', 'seminar-morning.html')) else 'website'
        block = '\n'.join([
            f'    <meta property="og:title" content="{H.escape(title, quote=True)}">',
            f'    <meta property="og:type" content="{og_type}">',
            f'    <meta property="og:url" content="{url}">',
            f'    <meta property="og:image" content="{og_img}">',
            f'    <meta property="og:description" content="{H.escape(desc)}">',
            f'    <meta property="og:site_name" content="{SITE}">',
            f'    <meta property="og:locale" content="ja_JP">',
            f'    <meta name="twitter:card" content="summary_large_image">'])
        h = insert_after(h, r'<meta name="description"[^>]*>', block)
    else:
        # normalise og:url to canonical
        h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), h, count=1)
        if 'og:site_name' not in h:
            h = insert_after(h, r'<meta property="og:url"[^>]*>', f'    <meta property="og:site_name" content="{SITE}">\n    <meta property="og:locale" content="ja_JP">')

    # JSON-LD
    h = re.sub(r'\n?[ \t]*<!-- seo:jsonld -->.*?<!-- /seo:jsonld -->\n?', '\n', h, flags=re.S)  # idempotent
    ld = build_jsonld(f, h, url, title, desc)
    if ld:
        if f == 'index.html':
            h = re.sub(r'[ \t]*<script type="application/ld\+json">.*?</script>\n', '', h, count=1, flags=re.S)
        h = h.replace('</head>', '    <!-- seo:jsonld -->\n' + ld + '    <!-- /seo:jsonld -->\n</head>', 1)
    return h, title, desc

def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

ORG_ID = BASE + '#organization'

def build_jsonld(f, h, url, title, desc):
    short = re.sub(r'\s*[|｜]\s*アセント社労士事務所\s*$', '', title).strip()
    if f == 'index.html':
        faqs = []
        for d in re.findall(r'<details.*?</details>', h, re.S):
            q = re.search(r'<span>\s*Q\.\s*(.*?)</span>', d, re.S)
            a = re.search(r'<div class="text-gray-600[^"]*">(.*?)</div>', d, re.S)
            if q and a:
                faqs.append({"@type": "Question", "name": strip_tags(q.group(1)),
                             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'^A\.\s*', '', strip_tags(a.group(1)))}})
        org = {
            "@type": ["ProfessionalService", "LocalBusiness"], "@id": ORG_ID,
            "name": SITE, "alternateName": "アセント社会保険労務士事務所",
            "url": BASE, "logo": LOGO, "image": [DEFAULT_OG, LOGO],
            "description": desc,
            "telephone": "+81-6-7878-3790",
            "address": {"@type": "PostalAddress", "streetAddress": "南本町2-3-12 EDGE本町3階",
                        "addressLocality": "大阪市中央区", "addressRegion": "大阪府", "postalCode": "541-0054", "addressCountry": "JP"},
            "geo": {"@type": "GeoCoordinates", "latitude": 34.6824556, "longitude": 135.5046777},
            "email": "nagata@ascent-sr.jp",
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "09:00", "closes": "18:00"}],
            "hasMap": "https://maps.google.com/?cid=5936103874545252663",
            "areaServed": [{"@type": "AdministrativeArea", "name": "大阪府"}, {"@type": "City", "name": "大阪市"}],
            "priceRange": "¥15,000〜",
            "founder": {"@type": "Person", "name": AUTHOR, "jobTitle": "社会保険労務士", "url": BASE + "profile.html"},
            "sameAs": ["https://lin.ee/XAupP0V", "https://maps.google.com/?cid=5936103874545252663"],
            "knowsAbout": ["労務トラブル対応", "就業規則作成", "社会保険手続き", "労働保険手続き", "給与計算", "働き方改革", "サービス業の労務管理"],
            "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "provider": {"@id": ORG_ID}}}
                           for n in ["労務顧問", "就業規則作成・見直し", "社会保険・労働保険手続き", "給与計算", "労務トラブル対応", "スポット相談"]],
        }
        graph = [org, {"@type": "WebSite", "@id": BASE + "#website", "url": BASE, "name": SITE, "publisher": {"@id": ORG_ID}, "inLanguage": "ja"}]
        if faqs:
            graph.append({"@type": "FAQPage", "mainEntity": faqs})
        return jsonld({"@context": "https://schema.org", "@graph": graph})
    if f in BLOG:
        m = BLOG[f]
        hub = HUB_OF[f]
        img = orig_image(m['img']) or DEFAULT_OG
        art = {"@type": "BlogPosting", "@id": url + "#article", "mainEntityOfPage": url,
               "headline": m['title'][:110], "description": desc, "image": [img],
               "datePublished": m['date'], "dateModified": m['mod'],
               "author": {"@type": "Person", "name": AUTHOR, "jobTitle": "社会保険労務士", "url": BASE + "profile.html"},
               "publisher": {"@type": "Organization", "@id": ORG_ID, "name": SITE, "logo": {"@type": "ImageObject", "url": LOGO}},
               "inLanguage": "ja", "articleSection": m['cat'], "isPartOf": {"@id": BASE + "#website"}}
        bc = crumbs([("ホーム", BASE), ("ブログ", BASE + "blog-list.html"), (hub[1], BASE + hub[0]), (m['title'], url)])
        return jsonld({"@context": "https://schema.org", "@graph": [art, bc]})
    if f == 'thanks.html':
        return None
    if f == 'blog-list.html':
        return jsonld({"@context": "https://schema.org", "@graph": [
            {"@type": "CollectionPage", "@id": url, "url": url, "name": short, "description": desc, "isPartOf": {"@id": BASE + "#website"}, "inLanguage": "ja"},
            crumbs([("ホーム", BASE), ("ブログ", url)])]})
    if f.startswith('news-') or f in ('certified-sr.html', 'festa2025.html', 'seminar-morning.html'):
        return jsonld({"@context": "https://schema.org", "@graph": [
            {"@type": "NewsArticle", "@id": url + "#article", "mainEntityOfPage": url, "headline": short, "description": desc,
             "datePublished": git_date(f, first=True), "dateModified": git_date(f),
             "author": {"@type": "Organization", "@id": ORG_ID, "name": SITE},
             "publisher": {"@type": "Organization", "@id": ORG_ID, "name": SITE, "logo": {"@type": "ImageObject", "url": LOGO}}, "inLanguage": "ja"},
            crumbs([("ホーム", BASE), ("お知らせ", BASE + "news.html"), (short, url)])]})
    if f == 'profile.html':
        return jsonld({"@context": "https://schema.org", "@graph": [
            {"@type": "ProfilePage", "@id": url, "url": url, "name": short, "description": desc, "inLanguage": "ja",
             "mainEntity": {"@type": "Person", "name": AUTHOR, "jobTitle": "社会保険労務士", "worksFor": {"@id": ORG_ID}, "url": url,
                            "image": DEFAULT_OG, "memberOf": {"@type": "Organization", "name": "大阪府社会保険労務士会"}}},
            crumbs([("ホーム", BASE), (short, url)])]})
    parent = [("ホーム", BASE)]
    if f == 'news.html':
        return jsonld({"@context": "https://schema.org", "@graph": [crumbs(parent + [(short, url)])]})
    return jsonld({"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": url, "url": url, "name": short, "description": desc, "isPartOf": {"@id": BASE + "#website"}, "about": {"@id": ORG_ID}, "inLanguage": "ja"},
        crumbs(parent + [(short, url)])]})

# ---------------------------------------------------------------- img attributes
DIMS = {}
def dims(src):
    src = src.split('?')[0]
    if src in DIMS: return DIMS[src]
    d = None
    if src.startswith('images/') and os.path.exists(src) and os.path.getsize(src) > 0 and not src.endswith('.svg'):
        try: d = Image.open(src).size
        except Exception: d = None
    DIMS[src] = d
    return d

def fix_imgs(h):
    main_pos = h.find('<main')
    first = [None]
    def sub(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if not src: return tag
        s = src.group(1)
        d = dims(s)
        if d and not re.search(r'\swidth=', tag):
            tag = tag.replace('<img', f'<img width="{d[0]}" height="{d[1]}"', 1)
        is_lcp = False
        if m.start() > main_pos and first[0] is None and 'logo' not in s:
            first[0] = m.start(); is_lcp = True
        if 'logo' not in s and not is_lcp and 'loading=' not in tag:
            tag = tag.replace('<img', '<img loading="lazy" decoding="async"', 1)
        if is_lcp and 'fetchpriority' not in tag:
            tag = tag.replace('<img', '<img fetchpriority="high"', 1)
        return tag
    return re.sub(r'<img\b[^>]*>', sub, h)

# ---------------------------------------------------------------- related articles
MARK = '<div class="mt-16 pt-8 border-t border-gray-100 text-center">'

def card(g, small=True):
    m = BLOG[g]
    d = dims(m['img']) if m['img'] else None
    wh = f' width="{d[0]}" height="{d[1]}"' if d else ''
    img = f'<img src="{m["img"]}" alt=""{wh} loading="lazy" decoding="async" class="w-28 h-[4.5rem] object-cover rounded-lg flex-shrink-0 bg-gray-100">' if m['img'] else ''
    return (f'<li><a href="{g}" class="flex gap-4 items-center group">{img}'
            f'<span><span class="block text-xs text-gray-500 mb-1">{m["date"].replace("-", ".")}</span>'
            f'<span class="font-bold text-navy-900 group-hover:text-accent-500 transition leading-snug">{H.escape(m["title"], quote=False)}</span></span></a></li>')

def related_block(f):
    hub = HUB_OF[f]
    items = '\n'.join('                            ' + card(g) for g in related(f))
    return f'''                    <aside id="related-articles" class="mt-12 pt-8 border-t border-gray-100">
                        <h2 class="text-xl font-bold text-navy-900 mb-6">関連記事</h2>
                        <ul class="space-y-5">
{items}
                        </ul>
                        <p class="mt-6 text-sm"><a href="{hub[0]}" class="text-accent-500 font-bold hover:underline">「{hub[1]}」の記事をもっと読む &rarr;</a></p>
                    </aside>
'''

# ---------------------------------------------------------------- process pages
report = {}
for f in sorted(glob.glob('*.html')) + ['rulebook/index.html', 'rulebook2/index.html']:
    if EXCLUDE(f): continue
    h = read(f)
    h, title, desc = fix_head(f, h)
    h = fix_imgs(h)
    if f in BLOG and 'id="related-articles"' not in h:
        if MARK in h:
            h = h.replace(MARK, related_block(f) + '                    ' + MARK, 1)
        else:
            print('NO MARK', f)
    write(f, h)
    report[f] = (title, desc)

# ---------------------------------------------------------------- blog-list theme nav
bl = read('blog-list.html')
if 'id="topic-nav"' not in bl:
    links = '\n'.join(f'                    <a href="{hub[0]}" class="inline-flex items-center bg-white border border-gray-200 hover:border-accent-500 hover:text-accent-500 text-navy-900 font-bold text-sm px-5 py-2.5 rounded-full shadow-sm transition">{hub[1]}</a>' for hub in HUBS)
    nav = f'''
        <nav id="topic-nav" aria-label="テーマ別に読む" class="bg-gray-50 border-b border-gray-200 py-6">
            <div class="container mx-auto px-4 md:px-8">
                <p class="text-center text-sm text-gray-500 mb-3">テーマ別に読む</p>
                <div class="flex flex-wrap justify-center gap-3">
{links}
                </div>
            </div>
        </nav>
'''
    i = bl.find('</section>') + len('</section>')
    bl = bl[:i] + nav + bl[i:]
    write('blog-list.html', bl)

# ---------------------------------------------------------------- topic hub pages + 404
tpl = read('blog-list.html')
head_tpl = tpl[tpl.find('<head>'):tpl.find('</head>')]
head_tpl = re.sub(r'<title>.*?</title>', '<title>__TITLE__</title>', head_tpl, flags=re.S)
head_tpl = re.sub(r'<meta name="description"[^>]*>', '<meta name="description" content="__DESC__">', head_tpl)
head_tpl = re.sub(r'<link rel="canonical"[^>]*>', '<link rel="canonical" href="__URL__">', head_tpl)
head_tpl = re.sub(r'<meta property="og:title"[^>]*>', '<meta property="og:title" content="__TITLE__">', head_tpl)
head_tpl = re.sub(r'<meta property="og:type"[^>]*>', '<meta property="og:type" content="website">', head_tpl)
head_tpl = re.sub(r'<meta property="og:url"[^>]*>', '<meta property="og:url" content="__URL__">', head_tpl)
head_tpl = re.sub(r'<meta property="og:description"[^>]*>', '<meta property="og:description" content="__DESC__">', head_tpl)
head_tpl = re.sub(r'\n?[ \t]*<!-- seo:jsonld -->.*?<!-- /seo:jsonld -->\n?', '\n__JSONLD__', head_tpl, flags=re.S)
head_tpl = re.sub(r'[ \t]*<style>.*?</style>\n', '', head_tpl, flags=re.S)
top_tpl = tpl[tpl.find('<body'):tpl.find('<main')]
tail_tpl = tpl[tpl.find('</main>') + len('</main>'):]

def build_page(f, title, desc, ld, body):
    head = head_tpl.replace('__TITLE__', H.escape(title, quote=False)).replace('__DESC__', H.escape(desc)).replace('__URL__', page_url(f)).replace('__JSONLD__', ld)
    return '<!DOCTYPE html>\n<html lang="ja" class="scroll-smooth">\n\n' + head + '</head>\n\n' + top_tpl + '<main class="pt-20">\n' + body + '\n    </main>' + tail_tpl

for hub in HUBS:
    f, name, desc, lead, keys, links = hub
    posts = sorted([g for g in BLOG if HUB_OF[g] is hub], key=lambda g: BLOG[g]['date'], reverse=True)
    cards = []
    for g in posts:
        m = BLOG[g]; d = dims(m['img']) if m['img'] else None
        wh = f' width="{d[0]}" height="{d[1]}"' if d else ''
        img = f'<img src="{m["img"]}" alt=""{wh} loading="lazy" decoding="async" class="w-full aspect-[16/9] object-cover bg-gray-100">' if m['img'] else '<div class="w-full aspect-[16/9] bg-gray-100"></div>'
        cards.append(f'''                        <a href="{g}" class="block bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition">
                            {img}
                            <div class="p-5">
                                <span class="text-xs text-gray-500"><i class="far fa-calendar-alt mr-1"></i>{m["date"].replace("-", ".")}</span>
                                <span class="ml-2 bg-navy-900 text-white px-2 py-0.5 rounded text-xs">{m["cat"]}</span>
                                <h2 class="font-bold text-navy-900 mt-2 leading-snug">{H.escape(m["title"], quote=False)}</h2>
                            </div>
                        </a>''')
    others = ' ／ '.join(f'<a href="{o[0]}" class="text-accent-500 font-bold hover:underline">{o[1]}</a>' for o in HUBS if o is not hub)
    svc = '\n'.join(f'                            <a href="{u}" class="inline-flex items-center justify-center bg-white text-navy-900 font-bold py-3 px-6 rounded-full shadow transition hover:bg-gray-100">{t} <i class="fas fa-arrow-right ml-2 text-sm"></i></a>' for u, t in links)
    body = f'''        <section class="bg-navy-900 text-white py-16">
            <div class="container mx-auto px-4 md:px-8 text-center">
                <nav aria-label="パンくずリスト" class="text-xs text-gray-400 mb-4">
                    <a href="index.html" class="hover:text-white">ホーム</a> &rsaquo; <a href="blog-list.html" class="hover:text-white">ブログ</a> &rsaquo; <span class="text-gray-200">{name}</span>
                </nav>
                <h1 class="text-2xl md:text-3xl font-bold leading-tight">{name}の記事一覧</h1>
                <p class="mt-4 text-gray-300 max-w-3xl mx-auto">{desc}</p>
            </div>
        </section>

        <section class="py-16">
            <div class="container mx-auto px-4 md:px-8">
                <div class="max-w-5xl mx-auto">
                    <p class="text-gray-700 leading-relaxed mb-10 max-w-3xl">{lead}</p>
                    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
{chr(10).join(cards)}
                    </div>

                    <div class="mt-16 bg-navy-900 text-white rounded-2xl p-8 md:p-12 text-center shadow-xl">
                        <h2 class="text-2xl font-bold mb-4">{name}で困ったら、大阪・本町の社労士へ</h2>
                        <p class="mb-8 text-gray-300">アセント社労士事務所は、大阪市中央区を拠点にサービス業の労務を支援しています。記事を読んで気になったことは、そのままご相談ください。</p>
                        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
{svc}
                            <a href="index.html#contact-form-anchor" class="inline-flex items-center justify-center bg-accent-500 hover:bg-accent-600 text-white font-bold py-3 px-6 rounded-full shadow-lg transition"><i class="fas fa-envelope mr-2" aria-hidden="true"></i>お問い合わせ</a>
                        </div>
                    </div>

                    <p class="mt-12 text-sm text-gray-600 text-center">ほかのテーマ： {others}</p>
                    <div class="mt-8 text-center">
                        <a href="blog-list.html" class="text-navy-900 font-bold hover:text-accent-500 transition">&larr; ブログ一覧に戻る</a>
                    </div>
                </div>
            </div>
        </section>
'''
    url = page_url(f)
    ld = jsonld({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url, "url": url, "name": f'{name}の記事一覧', "description": desc, "isPartOf": {"@id": BASE + "#website"}, "inLanguage": "ja",
         "hasPart": [{"@type": "BlogPosting", "headline": BLOG[g]['title'][:110], "url": BASE + g, "datePublished": BLOG[g]['date']} for g in posts]},
        crumbs([("ホーム", BASE), ("ブログ", BASE + "blog-list.html"), (name, url)])]})
    write(f, build_page(f, f'{name}の記事一覧 | {SITE}', desc, ld, body))
    print('hub', f, len(posts))

# 404 (root-absolute paths so it works from any URL depth)
body404 = '''        <section class="py-24 bg-white">
            <div class="container mx-auto px-4 md:px-8 text-center max-w-2xl">
                <p class="text-accent-500 font-bold text-6xl mb-4">404</p>
                <h1 class="text-2xl md:text-3xl font-bold text-navy-900 mb-6">お探しのページが見つかりませんでした</h1>
                <p class="text-gray-600 leading-relaxed mb-10">URLが変更されたか、ページが削除された可能性があります。下のリンクから目的のページをお探しください。</p>
                <div class="flex flex-col sm:flex-row flex-wrap items-center justify-center gap-4 mb-12">
                    <a href="/" class="inline-flex items-center justify-center bg-navy-900 hover:bg-navy-800 text-white font-bold py-3 px-8 rounded-full shadow-lg transition">トップページへ</a>
                    <a href="/blog-list.html" class="inline-flex items-center justify-center bg-white border border-gray-300 hover:border-accent-500 text-navy-900 font-bold py-3 px-8 rounded-full transition">ブログ一覧へ</a>
                    <a href="/#contact-form-anchor" class="inline-flex items-center justify-center bg-accent-500 hover:bg-accent-600 text-white font-bold py-3 px-8 rounded-full shadow-lg transition"><i class="fas fa-envelope mr-2" aria-hidden="true"></i>お問い合わせ</a>
                </div>
                <p class="text-sm text-gray-500 mb-3">テーマ別に記事を読む</p>
                <div class="flex flex-wrap justify-center gap-3">
''' + '\n'.join(f'                    <a href="/{hub[0]}" class="inline-flex items-center bg-white border border-gray-200 hover:border-accent-500 hover:text-accent-500 text-navy-900 font-bold text-sm px-5 py-2.5 rounded-full shadow-sm transition">{hub[1]}</a>' for hub in HUBS) + '''
                </div>
            </div>
        </section>
'''
p404 = build_page('404.html', f'ページが見つかりません | {SITE}', 'お探しのページは見つかりませんでした。トップページやブログ一覧から目的のページをお探しください。', '', body404)
p404 = p404.replace('<link rel="canonical" href="https://ascent-sr.jp/404.html">', '<meta name="robots" content="noindex, follow">')
p404 = re.sub(r'\s*<meta property="og:[^"]*"[^>]*>', '', p404)
p404 = re.sub(r'\s*<meta name="twitter:card"[^>]*>', '', p404)
p404 = re.sub(r'(src|href)="(?!https?:|/|#|tel:|mailto:)([^"]+)"', r'\1="/\2"', p404)
write('404.html', p404)

# ---------------------------------------------------------------- sitemap + robots + gitignore
urls = [(BASE, TODAY, '1.0')]
for f in sorted(glob.glob('*.html')):
    if f in ('index.html', 'thanks.html') or EXCLUDE(f): continue
    if f in BLOG:
        urls.append((BASE + f, BLOG[f]['mod'], '0.7'))
    else:
        pri = '0.9' if f in ('pricing.html', 'work-rules.html', 'profile.html', 'blog-list.html', 'service-lp.html', 'first-hire-lp.html') else '0.6'
        urls.append((BASE + f, TODAY, pri))
urls.append((BASE + 'rulebook/', git_date('rulebook/index.html'), '0.6'))
urls.append((BASE + 'rulebook2/', git_date('rulebook2/index.html'), '0.6'))
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, d, p in urls:
    sm.append(f'  <url>\n    <loc>{H.escape(u)}</loc>\n    <lastmod>{d}</lastmod>\n    <priority>{p}</priority>\n  </url>')
sm.append('</urlset>\n')
write('sitemap.xml', '\n'.join(sm))
write('robots.txt', 'User-agent: *\nAllow: /\nDisallow: /index-before-\nDisallow: /tmp_doc/\nDisallow: /thanks.html\n\nSitemap: https://ascent-sr.jp/sitemap.xml\n')
gi = read('.gitignore') if os.path.exists('.gitignore') else ''
if 'index-before-' not in gi:
    write('.gitignore', gi.rstrip('\n') + '\n# local backups of old top pages (never deploy)\nindex-before-*.html\n')


print('sitemap urls', len(urls))
