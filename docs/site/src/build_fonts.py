#!/usr/bin/env python3
"""페이지에 쓰인 글자만 남긴 원티드 산스(Wanted Sans) 웹폰트를 base64 @font-face 로 만든다 → src/fonts.css
사용: python3 build_fonts.py <wanted-sans 패키지 압축 해제 폴더> <index.html>
  npm pack wanted-sans && mkdir ws && tar xzf wanted-sans-*.tgz -C ws   →  폴더 = ws
글꼴 라이선스: SIL Open Font License 1.1
"""
import base64, io, os, sys
from fontTools.ttLib import TTFont
from fontTools import subset

src_dir, page = sys.argv[1], sys.argv[2]
text = open(page, encoding="utf-8").read()
used = {ord(c) for c in text} | set(range(0x20, 0x7F)) | {0x2192, 0x2191, 0x2039, 0x203A, 0x00B7, 0x2013, 0x201C, 0x201D, 0x2713}
base = os.path.join(src_dir, "package/fonts/webfonts/static/complete/woff2")
WEIGHTS = {400: "Regular", 500: "Medium", 600: "SemiBold"}   # 굵은 볼드(700+)는 쓰지 않는다

css, total = [], 0
for weight, name in WEIGHTS.items():
    f = TTFont(os.path.join(base, f"WantedSans-{name}.woff2"))
    keep = used & set(f.getBestCmap())
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "tnum"]
    sub = subset.Subsetter(opts); sub.populate(unicodes=keep); sub.subset(f)
    buf = io.BytesIO(); f.flavor = "woff2"; f.save(buf)
    data = buf.getvalue(); total += len(data)
    css.append(f"@font-face{{font-family:'Wanted Sans';font-style:normal;font-weight:{weight};font-display:swap;"
               f"src:url(data:font/woff2;base64,{base64.b64encode(data).decode()}) format('woff2')}}")
    print(name, len(keep), "chars ->", len(data) // 1024, "KB")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts.css")
open(out, "w").write("/* Wanted Sans (SIL OFL 1.1) — 페이지 글자만 남긴 서브셋 */\n" + "\n".join(css) + "\n")
print(out, total // 1024, "KB")
