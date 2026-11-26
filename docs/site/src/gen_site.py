#!/usr/bin/env python3
"""㈜스모크 기업 홈페이지 생성기 — 장면 SVG(원근 계산)를 만들어 단일 index.html 로 출력."""
import random, sys

random.seed(7)
OUT = sys.argv[1]

def lerp(a, b, t): return a + (b - a) * t

# ---------- 장면 1: 올려다본 유리 타워 (보안 네트워크) ----------
def scene_tower():
    W, H = 1600, 800
    s = [f'<symbol id="sc-tower" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
         '<defs><linearGradient id="tw-sky" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#17305e"/><stop offset=".55" stop-color="#3f74b3"/><stop offset="1" stop-color="#a9cdea"/></linearGradient>'
         '<linearGradient id="tw-l" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1b2d4f"/><stop offset="1" stop-color="#34507e"/></linearGradient>'
         '<linearGradient id="tw-r" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6d96c6"/><stop offset=".5" stop-color="#9cc0e2"/><stop offset="1" stop-color="#4a6e9c"/></linearGradient>'
         '<linearGradient id="tw-b2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a4774"/><stop offset="1" stop-color="#5f86b8"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#tw-sky)"/>']
    # 먼 건물 (왼쪽)
    s.append('<polygon points="80,800 330,800 300,170 140,230" fill="#203b66" opacity=".75"/>')
    for i in range(1, 14):
        t = i / 14
        y = lerp(800, 200, t ** 0.8)
        s.append(f'<line x1="{lerp(80,140,t**.8):.0f}" y1="{y:.0f}" x2="{lerp(330,300,t**.8):.0f}" y2="{y-10:.0f}" stroke="#7aa3d2" stroke-opacity=".25"/>')
    # 주 타워: 아래가 넓고 위로 갈수록 한 점으로 모인다
    bl, bc, br = (520, 820), (900, 820), (1180, 820)
    tl, tc, tr = (760, -20), (860, -20), (960, -20)
    s.append(f'<polygon points="{bl[0]},{bl[1]} {bc[0]},{bc[1]} {tc[0]},{tc[1]} {tl[0]},{tl[1]}" fill="url(#tw-l)"/>')
    s.append(f'<polygon points="{bc[0]},{bc[1]} {br[0]},{br[1]} {tr[0]},{tr[1]} {tc[0]},{tc[1]}" fill="url(#tw-r)"/>')
    def face(b0, b1, t0, t1, cols, stroke, op):
        for i in range(1, cols):
            u = i / cols
            s.append(f'<line x1="{lerp(b0[0],b1[0],u):.1f}" y1="820" x2="{lerp(t0[0],t1[0],u):.1f}" y2="-20" stroke="{stroke}" stroke-opacity="{op}" stroke-width="{1.6 if i%3==0 else .8}"/>')
        for j in range(1, 34):
            v = (j / 34) ** 1.7   # 위로 갈수록 층 간격이 좁아진다
            y = lerp(820, -20, 1 - (1 - v))
            y = 820 - (840 * (1 - (1 - j / 34) ** 1.9))
            k = (820 - y) / 840
            x0 = lerp(b0[0], t0[0], k); x1 = lerp(b1[0], t1[0], k)
            s.append(f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{stroke}" stroke-opacity="{op}" stroke-width=".9"/>')
    face(bl, bc, tl, tc, 18, "#9fc0e6", .35)
    face(bc, br, tc, tr, 14, "#e9f3ff", .45)
    # 반사광
    s.append(f'<polygon points="980,820 1100,820 935,-20 905,-20" fill="#fff" opacity=".12"/>')
    s.append(f'<line x1="{bc[0]}" y1="820" x2="{tc[0]}" y2="-20" stroke="#dfeeff" stroke-width="2" stroke-opacity=".7"/>')
    # 오른쪽 건물
    s.append('<polygon points="1300,820 1640,820 1640,90 1420,150" fill="url(#tw-b2)"/>')
    for j in range(1, 22):
        y = 820 - 700 * (1 - (1 - j / 22) ** 1.6)
        s.append(f'<line x1="1300" y1="{y:.0f}" x2="1640" y2="{y - 40*(1-(820-y)/700):.0f}" stroke="#cfe2f7" stroke-opacity=".28"/>')
    for i in range(1, 9):
        x = lerp(1300, 1640, i / 9)
        s.append(f'<line x1="{x:.0f}" y1="820" x2="{lerp(1420,1640,i/9):.0f}" y2="{lerp(150,90,i/9):.0f}" stroke="#cfe2f7" stroke-opacity=".2"/>')
    # 망 연결선(민트) — 건물 사이의 분리된 경로
    s.append('<g stroke="#5ff0c2" stroke-width="2" fill="none" opacity=".8"><path d="M905 210 C 980 190, 1010 250, 1060 300"/><path d="M1060 300 C 1200 280, 1320 260, 1460 320" stroke-dasharray="6 7"/></g>')
    for x, y in [(905, 210), (1060, 300), (1460, 320)]:
        s.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#5ff0c2"/><circle cx="{x}" cy="{y}" r="14" fill="#5ff0c2" opacity=".25"/>')
    s.append('</symbol>')
    return ''.join(s)

# ---------- 장면 2: 서버실 통로 ----------
def scene_racks():
    W, H, vx, vy = 1600, 800, 820, 360
    s = [f'<symbol id="sc-racks" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
         '<defs><linearGradient id="rk-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1430"/><stop offset=".5" stop-color="#1a2552"/><stop offset="1" stop-color="#0b1026"/></linearGradient>'
         '<radialGradient id="rk-glow" cx=".51" cy=".45" r=".35"><stop offset="0" stop-color="#bfe9ff" stop-opacity=".9"/><stop offset="1" stop-color="#bfe9ff" stop-opacity="0"/></radialGradient>'
         '<linearGradient id="rk-fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4a80"/><stop offset="1" stop-color="#121a3a"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#rk-bg)"/>']
    s.append(f'<polygon points="0,800 1600,800 {vx+60},{vy+40} {vx-60},{vy+40}" fill="url(#rk-fl)"/>')
    # 바닥 타일선
    for i in range(-10, 11):
        s.append(f'<line x1="{vx + i*160}" y1="800" x2="{vx + i*6}" y2="{vy+40}" stroke="#7e90d0" stroke-opacity=".18"/>')
    for k in [0.15, 0.3, 0.45, 0.6, 0.75]:
        y = lerp(800, vy + 40, k)
        s.append(f'<line x1="0" y1="{y:.0f}" x2="1600" y2="{y:.0f}" stroke="#7e90d0" stroke-opacity=".12"/>')
    # 랙 벽: 깊이별 세로 칸
    def wall(side):
        sx = 0 if side < 0 else 1600
        for d in range(9):
            t0 = 1 - 0.78 ** d; t1 = 1 - 0.78 ** (d + 1)
            x0 = lerp(sx, vx + side * 70, t0); x1 = lerp(sx, vx + side * 70, t1)
            top0 = lerp(40, vy - 60, t0); top1 = lerp(40, vy - 60, t1)
            bot0 = lerp(800, vy + 40, t0); bot1 = lerp(800, vy + 40, t1)
            shade = 0.55 + 0.05 * d
            s.append(f'<polygon points="{x0:.0f},{top0:.0f} {x1:.0f},{top1:.0f} {x1:.0f},{bot1:.0f} {x0:.0f},{bot0:.0f}" fill="#1e2a5a" fill-opacity="{shade:.2f}" stroke="#4d5ea0" stroke-opacity=".5"/>')
            rows = 10
            for r in range(1, rows):
                yy0 = lerp(top0, bot0, r / rows); yy1 = lerp(top1, bot1, r / rows)
                s.append(f'<line x1="{x0:.0f}" y1="{yy0:.0f}" x2="{x1:.0f}" y2="{yy1:.0f}" stroke="#30407a" stroke-opacity=".8"/>')
                if random.random() < .8:
                    c = random.choice(["#5ff0c2", "#5ff0c2", "#7fa2ff", "#ffffff"])
                    xm = lerp(x0, x1, .2); ym = lerp(yy0, yy1, .2) - (bot0 - top0) / rows * .45
                    rr = max(1.2, 4.5 * (0.8 ** d))
                    s.append(f'<circle cx="{xm:.0f}" cy="{ym:.0f}" r="{rr:.1f}" fill="{c}"/>')
    wall(-1); wall(1)
    # 천장 조명
    s.append(f'<polygon points="0,0 1600,0 {vx+70},{vy-60} {vx-70},{vy-60}" fill="#0f1738"/>')
    for k in range(9):
        t0 = 1 - 0.78 ** k; t1 = t0 + (1 - 0.78 ** (k + 1) - t0) * .55
        for side in (-1, 1):
            xa = lerp(vx + side * 420, vx + side * 14, t0); xb = lerp(vx + side * 420, vx + side * 14, t1)
            xa2 = lerp(vx + side * 380, vx + side * 12, t0); xb2 = lerp(vx + side * 380, vx + side * 12, t1)
            ya = lerp(0, vy - 60, t0); yb = lerp(0, vy - 60, t1)
            s.append(f'<polygon points="{xa:.0f},{ya:.0f} {xa2:.0f},{ya:.0f} {xb2:.0f},{yb:.0f} {xb:.0f},{yb:.0f}" fill="#e6f7ff" opacity=".85"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#rk-glow)"/>')
    s.append('</symbol>')
    return ''.join(s)

# ---------- 장면 3: 구름 위 두 가용 영역 ----------
def scene_cloud():
    W, H = 1600, 800
    s = [f'<symbol id="sc-cloud" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
         '<defs><linearGradient id="cl-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f3f7a"/><stop offset=".5" stop-color="#5f93cf"/><stop offset=".78" stop-color="#e8c3a2"/><stop offset="1" stop-color="#f3dcc4"/></linearGradient>'
         '<radialGradient id="cl-sun" cx=".78" cy=".62" r=".35"><stop offset="0" stop-color="#fff2d6"/><stop offset=".4" stop-color="#ffe3b8" stop-opacity=".5"/><stop offset="1" stop-color="#ffe3b8" stop-opacity="0"/></radialGradient>'
         '<filter id="cl-soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>'
         '<linearGradient id="cl-puff" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#c9d6ea"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#cl-sky)"/><rect width="{W}" height="{H}" fill="url(#cl-sun)"/>']
    # 높은 새털구름
    for (cx, cy, rx) in [(1080, 150, 260), (1380, 230, 200), (900, 260, 140)]:
        s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx*.09:.0f}" fill="#fff" opacity=".35" filter="url(#cl-soft)"/>')
    # 두 묶음의 빌딩 (AZ a / AZ c) — 구름 위 섬처럼
    def city(x0, x1, base, col):
        x = x0
        while x < x1:
            w = random.randint(26, 54); h = random.randint(70, 230)
            s.append(f'<rect x="{x}" y="{base-h}" width="{w}" height="{h+60}" fill="{col}"/>')
            s.append(f'<rect x="{x+w-6}" y="{base-h}" width="6" height="{h+60}" fill="#ffffff" opacity=".12"/>')
            for wy in range(base - h + 12, base, 16):
                for wx in range(x + 6, x + w - 8, 11):
                    if random.random() < .3:
                        s.append(f'<rect x="{wx}" y="{wy}" width="5" height="7" fill="#ffe7b0" opacity=".85"/>')
            x += w + random.randint(3, 9)
    city(760, 1040, 560, "#2b3d6f")
    city(1200, 1480, 590, "#34477c")
    # 뭉게구름: 원을 겹쳐 만든 덩어리
    def puff(cx, cy, scale, op=1):
        s.append(f'<g opacity="{op}">')
        s.append(f'<ellipse cx="{cx}" cy="{cy+30*scale:.0f}" rx="{260*scale:.0f}" ry="{40*scale:.0f}" fill="#9fb2cf" opacity=".5" filter="url(#cl-soft)"/>')
        for dx, dy, r in [(-170, 10, 70), (-90, -30, 95), (10, -55, 120), (120, -25, 95), (200, 12, 68), (40, 10, 110), (-60, 20, 90)]:
            s.append(f'<circle cx="{cx+dx*scale:.0f}" cy="{cy+dy*scale:.0f}" r="{r*scale:.0f}" fill="url(#cl-puff)"/>')
        s.append('</g>')
    puff(700, 690, 1.1); puff(1080, 640, 1.0); puff(1430, 660, 1.15); puff(250, 740, 1.2, .9); puff(1250, 760, 1.4)
    # 두 영역을 잇는 경로
    s.append('<path d="M900 330 C 1000 230, 1240 220, 1340 350" stroke="#5ff0c2" stroke-width="3" fill="none" stroke-dasharray="2 10" stroke-linecap="round"/>')
    for x, y in ((900, 330), (1340, 350)):
        s.append(f'<circle cx="{x}" cy="{y}" r="8" fill="#5ff0c2"/><circle cx="{x}" cy="{y}" r="20" fill="#5ff0c2" opacity=".25"/>')
    s.append('</symbol>')
    return ''.join(s)

# ---------- 장면 4: 빛 궤적 (블루그린 전환) ----------
def scene_trails():
    W, H = 1600, 800
    s = [f'<symbol id="sc-trails" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
         '<defs><linearGradient id="tr-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a0f2c"/><stop offset="1" stop-color="#1b2459"/></linearGradient>'
         '<linearGradient id="tr-b" x1="0" x2="1"><stop offset="0" stop-color="#4060e0" stop-opacity="0"/><stop offset=".6" stop-color="#5b7bff"/><stop offset="1" stop-color="#c9d4ff"/></linearGradient>'
         '<linearGradient id="tr-g" x1="0" x2="1"><stop offset="0" stop-color="#14916e" stop-opacity="0"/><stop offset=".6" stop-color="#2fd39f"/><stop offset="1" stop-color="#d6fff1"/></linearGradient>'
         '<filter id="tr-blur" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="3"/></filter></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#tr-bg)"/>']
    # 지평선의 도시 불빛
    for i in range(140):
        x = random.randint(500, 1600); y = random.randint(360, 395)
        s.append(f'<circle cx="{x}" cy="{y}" r="{random.choice([1,1.5,2])}" fill="#ffe2a8" opacity="{random.uniform(.3,.9):.2f}"/>')
    # 파란 궤적이 위로, 초록 궤적이 아래로 갈라지며 뻗는다
    for i in range(16):
        y0 = 720 + i * 7; ymid = 470 + i * 5
        blue = i < 7
        yend = (130 + i * 16) if blue else (420 + (i - 7) * 20)
        grad = "tr-b" if blue else "tr-g"
        w = random.uniform(1.5, 4.5)
        s.append(f'<path d="M-40 {y0} C 500 {ymid}, 900 {ymid-20}, 1660 {yend}" stroke="url(#{grad})" stroke-width="{w:.1f}" fill="none" filter="url(#tr-blur)" opacity=".9"/>')
        s.append(f'<path d="M-40 {y0} C 500 {ymid}, 900 {ymid-20}, 1660 {yend}" stroke="url(#{grad})" stroke-width="{w/3:.1f}" fill="none"/>')
    s.append('</symbol>')
    return ''.join(s)

# ---------- 장면 5: 정밀 가공 샤프트 (해든정밀) ----------
def scene_shafts():
    W, H = 1600, 800
    s = [f'<symbol id="sc-shafts" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
         '<defs><linearGradient id="sh-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#dfe4e9"/><stop offset="1" stop-color="#9aa6b2"/></linearGradient>'
         '<linearGradient id="sh-m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5d6873"/><stop offset=".25" stop-color="#f4f7fa"/><stop offset=".45" stop-color="#b9c3cc"/><stop offset=".8" stop-color="#6c7782"/><stop offset="1" stop-color="#3d464f"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#sh-bg)"/>']
    s.append('<g transform="rotate(-18 800 400)">')
    for k, y in enumerate(range(80, 900, 110)):
        L = random.randint(900, 1500); x = random.randint(-200, 300)
        r = 34
        s.append(f'<rect x="{x}" y="{y+16}" width="{L}" height="{2*r}" rx="6" fill="#2f3840" opacity=".25"/>')
        s.append(f'<rect x="{x}" y="{y}" width="{L}" height="{2*r}" rx="6" fill="url(#sh-m)"/>')
        # 단차 가공부
        st = x + L - 180
        s.append(f'<rect x="{st}" y="{y+10}" width="180" height="{2*r-20}" rx="4" fill="url(#sh-m)"/>')
        s.append(f'<rect x="{x+120}" y="{y}" width="6" height="{2*r}" fill="#47515b" opacity=".6"/>')
        if k == 3:
            s.append(f'<rect x="{x+300}" y="{y-6}" width="70" height="{2*r+12}" rx="3" fill="#f0b400"/>')
    s.append('</g></symbol>')
    return ''.join(s)

SYMBOLS = scene_tower() + scene_racks() + scene_cloud() + scene_trails() + scene_shafts()

html = open(__import__('os').path.join(__import__('os').path.dirname(__file__),'template.html'), encoding='utf-8').read()
html = html.replace('<!--SYMBOLS-->', SYMBOLS)
_fonts = __import__('os').path.join(__import__('os').path.dirname(__file__), 'fonts.css')
if __import__('os').path.exists(_fonts):
    html = html.replace('/*FONTS*/', open(_fonts, encoding='utf-8').read())
open(OUT, 'w', encoding='utf-8').write(html)
print(OUT, len(html) // 1024, 'KB')
