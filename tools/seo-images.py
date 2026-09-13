# -*- coding: utf-8 -*-
"""Step 1: rename non-ASCII image files, convert referenced raster images to WebP, resize oversized ones.
Updates references in every HTML/CSS file. Originals (jpg/png) are kept for og:image use.
"""
import os, re, glob, json, sys
from PIL import Image

os.chdir(r'C:\Users\long_\ascent-sr-site')
HTML = glob.glob('*.html') + glob.glob('rulebook*/index.html')
CSS = glob.glob('css/*.css')
MAXW = {'hero': 1920, 'default': 1600}

def read(p):
    return open(p, encoding='utf-8').read()

def write(p, s):
    open(p, 'w', encoding='utf-8', newline='').write(s)

# ---- collect references -------------------------------------------------
ref_re = re.compile(r'(?:src|poster|content|href)="(?:https://ascent-sr\.jp/|\.\./)?(images/[^"]+?\.(?:jpg|jpeg|png|webp))"'
                    r'|url\([\'"]?(?:\.\./)?(images/[^\'")]+?\.(?:jpg|jpeg|png|webp))[\'"]?\)', re.I)
refs = {}
for f in HTML + CSS:
    for a, b in ref_re.findall(read(f)):
        p = (a or b).split('?')[0]
        refs.setdefault(p, set()).add(f)

# ---- 1. rename files with non-ASCII / spaces / parens -------------------
def blog_owner(files):
    for f in sorted(files):
        if f.startswith('blog-') and f != 'blog-list.html':
            return f[:-5]
    return None

rename = {}
used = set()
for p in sorted(refs):
    if not os.path.exists(p):
        continue
    if re.search(r'[^\x21-\x7e]|[\s()]', p):
        ext = os.path.splitext(p)[1].lower().replace('jpeg', 'jpg')
        owner = blog_owner(refs[p])
        if owner:
            base = owner
        else:
            base = 'img-' + re.sub(r'[^a-z0-9]+', '-', p.lower()).strip('-')[:40]
        new = f'images/{base}{ext}'
        i = 2
        while new in used or (os.path.exists(new) and new != p):
            new = f'images/{base}-{i}{ext}'; i += 1
        used.add(new)
        rename[p] = new

for old, new in rename.items():
    os.rename(old, new)
    print('renamed', old, '->', new)

# apply renames in files (both raw and with ../ prefix in css)
for f in HTML + CSS:
    s = read(f); o = s
    for old, new in rename.items():
        s = s.replace(old, new)
    if s != o:
        write(f, s)

# refresh refs with new names
refs = {rename.get(k, k): v for k, v in refs.items()}

# ---- 2. WebP conversion + resize ----------------------------------------
webp_of = {}
dims = {}
for p in sorted(refs):
    if not os.path.exists(p) or p.lower().endswith('.webp'):
        continue
    if os.path.getsize(p) == 0 or 'qr' in p.lower():
        continue
    if os.path.exists(os.path.splitext(p)[0] + '.webp'):
        out = os.path.splitext(p)[0] + '.webp'; webp_of[p] = out; dims[out] = Image.open(out).size; dims[p] = Image.open(p).size; continue
    try:
        im = Image.open(p)
    except Exception as e:
        print('skip', p, e); continue
    maxw = MAXW['hero'] if 'hero' in p else MAXW['default']
    w, h = im.size
    if w > maxw:
        im = im.resize((maxw, round(h * maxw / w)), Image.LANCZOS)
    has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
    if has_alpha:
        im = im.convert('RGBA')
    else:
        im = im.convert('RGB')
    out = os.path.splitext(p)[0] + '.webp'
    im.save(out, 'WEBP', quality=82, method=6)
    webp_of[p] = out
    dims[out] = im.size
    dims[p] = Image.open(p).size
    print(f'webp {p} {os.path.getsize(p)//1024}KB -> {out} {os.path.getsize(out)//1024}KB {im.size}')

# ---- 3. swap <img src>, poster=, css url() to webp; keep og:image/meta ----
def swap_in_html(s):
    def img_sub(m):
        tag = m.group(0)
        def src_sub(mm):
            src = mm.group(2)
            return mm.group(1) + webp_of.get(src, src) + mm.group(3)
        return re.sub(r'(src=")([^"]+)(")', src_sub, tag)
    s = re.sub(r'<img\b[^>]*>', img_sub, s)
    s = re.sub(r'(poster=")([^"]+)(")', lambda m: m.group(1) + webp_of.get(m.group(2), m.group(2)) + m.group(3), s)
    s = re.sub(r"(url\(['\"]?)(images/[^'\")]+)(['\"]?\))", lambda m: m.group(1) + webp_of.get(m.group(2), m.group(2)) + m.group(3), s)
    return s

for f in HTML:
    s = read(f); o = swap_in_html(s)
    if o != s:
        write(f, o)
for f in CSS:
    s = read(f)
    o = re.sub(r"(url\(['\"]?\.\./)(images/[^'\")]+)(['\"]?\))", lambda m: m.group(1) + webp_of.get(m.group(2), m.group(2)) + m.group(3), s)
    if o != s:
        write(f, o)


print('done. renamed', len(rename), 'webp', len(webp_of))
