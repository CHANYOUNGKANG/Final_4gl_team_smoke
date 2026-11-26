#!/usr/bin/env python3
"""페이지에 쓰인 글자만 남긴 웹폰트를 base64 @font-face 로 만든다 → src/fonts.css
사용: python3 build_fonts.py <fontsource 압축 해제 폴더> <index.html 또는 template.html>
폰트: Gasoek One(한글 제목) · Unbounded(영문 제목·숫자) · IBM Plex Sans KR(본문) — 모두 SIL OFL 1.1
"""
import base64, glob, io, os, re, sys
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.merge import Merger
import tempfile

src_dir, page = sys.argv[1], sys.argv[2]
text = open(page, encoding="utf-8").read()
used = {ord(c) for c in text} | set(range(0x20, 0x7F)) | {0x2192, 0x2191, 0x2039, 0x203A, 0x00B7, 0x2013, 0x201C, 0x201D, 0x2713}

FACES = [  # (family, glob pattern, weight)
    ("Gasoek One", "fontsource-gasoek-one-*/package/files/gasoek-one-*-400-normal.woff2", 400),
    ("Unbounded", "fontsource-unbounded-*/package/files/unbounded-latin-600-normal.woff2", 600),
    ("Unbounded", "fontsource-unbounded-*/package/files/unbounded-latin-800-normal.woff2", 800),
] + [("IBM Plex Sans KR", f"fontsource-ibm-plex-sans-kr-*/package/files/ibm-plex-sans-kr-*-{w}-normal.woff2", w) for w in (400, 500, 700)]

def ranges(cps):
    cps = sorted(cps); out = []; start = prev = cps[0]
    for c in cps[1:]:
        if c == prev + 1: prev = c; continue
        out.append((start, prev)); start = prev = c
    out.append((start, prev))
    return ", ".join(f"U+{a:X}" if a == b else f"U+{a:X}-{b:X}" for a, b in out)

css, total = [], 0
tmp = tempfile.mkdtemp()
for family, pat, weight in FACES:
    parts, covered = [], set()
    for path in sorted(glob.glob(os.path.join(src_dir, pat))):
        cmap = TTFont(path).getBestCmap()
        keep = (used & set(cmap)) - covered   # 같은 글자가 두 조각에 있으면 한 번만
        if not keep:
            continue
        covered |= keep
        opts = subset.Options(); opts.layout_features = []; opts.name_IDs = ["*"]; opts.notdef_outline = True
        f = TTFont(path)
        sub = subset.Subsetter(opts); sub.populate(unicodes=keep); sub.subset(f)
        f.flavor = None
        out_p = os.path.join(tmp, f"{len(parts)}-{weight}-{family.replace(' ','')}.ttf"); f.save(out_p); parts.append(out_p)
    merged = Merger().merge(parts) if len(parts) > 1 else TTFont(parts[0])
    merged.flavor = "woff2"; buf = io.BytesIO(); merged.save(buf)
    data = buf.getvalue(); total += len(data)
    css.append(f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};font-display:swap;"
               f"src:url(data:font/woff2;base64,{base64.b64encode(data).decode()}) format('woff2');unicode-range:{ranges(covered)}}}")
    print(family, weight, len(parts), "slices ->", len(data)//1024, "KB")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts.css")
open(out, "w").write("/* Gasoek One · Unbounded · IBM Plex Sans KR — SIL Open Font License 1.1, 페이지 글자만 남긴 서브셋 */\n" + "\n".join(css) + "\n")
print(out, len(css), "faces,", total // 1024, "KB woff2")
