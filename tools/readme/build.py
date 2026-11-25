"""README 라이브 패널 생성기.

docs/images/live/progress.svg  · 파트별 이정표 진행률 (tools/progress/report.py와 같은 기준)
docs/images/live/schedule.svg  · 수행계획서 일정 + 오늘 선 + D-day
README.md <!-- smoke-activity --> 블록 · 최근 커밋, 열린 이슈·PR, 작업 브랜치

GitHub Actions(main push · 매일 00:05 KST)에서 실행한다. 로컬에서도 미리 볼 수 있다.
    python3 tools/readme/build.py            # gh CLI가 있으면 활동 블록까지 갱신
    python3 tools/readme/build.py --offline  # SVG만 갱신
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "docs/images/live"
KST = timezone(timedelta(hours=9))
REPO = os.environ.get("GITHUB_REPOSITORY", "CHANYOUNGKANG/Final_4gl_team_smoke")
FONT = "Noto Sans CJK KR,Noto Sans KR,Apple SD Gothic Neo,Malgun Gothic,Arial,sans-serif"

# role-*.svg 카드와 같은 색
PARTS = [
    ("network", "강민서", "네트워크·보안", "#91c4ff"),
    ("server", "이준호", "Linux 서버·메일", "#85e4cf"),
    ("aws", "이우빈", "AWS 클라우드", "#ffd0a2"),
    ("cicd", "강찬영", "CI/CD", "#d0b5ff"),
]
COLOR = {p[0]: p[3] for p in PARTS}

# docs/delivery/README.md 의 수행계획서 일정과 같게 유지한다.
SCHEDULE = [
    ("SRS·RFP 검토, 통합 아키텍처", "이준호 주관 · 전원", "server", "2026-11-21", "2026-11-26"),
    ("본사·지사 네트워크 · 보안 통제 검증", "강민서", "network", "2026-11-26", "2026-12-03"),
    ("Linux·메일 서버 정비 · 이관 원본 준비", "이준호", "server", "2026-11-26", "2026-12-03"),
    ("AWS·EKS · 데이터 이관 기반", "이우빈", "aws", "2026-11-26", "2026-12-05"),
    ("CI/CD · 후보 검증 · 트래픽 전환", "강찬영", "cicd", "2026-11-26", "2026-12-05"),
    ("통합 테스트 · 장애 조치 검증", "강찬영 주관 · 각 파트", "cicd", "2026-11-30", "2026-12-07"),
    ("최종 보고서 · 발표 자료", "이준호 주관 · 강찬영 협업", "server", "2026-12-07", "2026-12-09"),
]
SHORT = {"NET1": "VLAN·라우팅", "NET2": "방화벽 통제", "NET3": "본사·지사 VPN", "NET4": "IDS·로그 연동",
         "SRV1": "SSH·로그", "SRV2": "DB·파일 백업", "SRV3": "공지 앱 빌드", "SRV4": "운영 알림 메일",
         "AWS1": "2AZ EKS", "AWS2": "ALB HTTPS·전환", "AWS3": "RDS·S3 이관", "AWS4": "워커 교체·관찰",
         "CICD1": "Jenkins·WAR", "CICD2": "Docker·ECR", "CICD3": "Green 배포·검사", "CICD4": "전환·자동 롤백"}
START, END, FINAL = date(2026, 11, 21), date(2026, 12, 9), date(2026, 12, 9)
WEEKDAY = "월화수목금토일"


def load_report():
    spec = importlib.util.spec_from_file_location("report", ROOT / "tools/progress/report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def milestones(rep):
    tracked = rep.files_at(ROOT)
    corpus = rep.implementation(ROOT, tracked)
    evidence = rep.proof(ROOT, tracked)
    out = []
    for key, role, title, patterns in rep.MILESTONES:
        hit = all(any(re.search(p, s, re.I | re.M) for s in corpus[role].values()) for p in patterns)
        rec = evidence.get(key, {})
        impl = hit or "implementation" in rec
        out.append({"key": key, "role": role, "title": title, "impl": impl, "ver": impl and "verification" in rec})
    files = {}
    for role, *_ in PARTS:
        files[role] = sum(1 for p in tracked if p.parts[0] == role and p.name not in {".gitkeep", "README.md"})
    return out, files


def frame(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title><defs><linearGradient id="bg" x2="1" y2=".35"><stop stop-color="#101424"/>'
            f'<stop offset=".55" stop-color="#171b38"/><stop offset="1" stop-color="#221f4d"/></linearGradient>'
            f'<pattern id="grid" width="52" height="30" patternUnits="userSpaceOnUse"><path d="M0 0L52 30M52 0L0 30" stroke="#a8b5ff" opacity=".07" fill="none" stroke-width=".7"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/><rect width="{w}" height="{h}" rx="18" fill="url(#grid)"/>'
            f'<g font-family="{FONT}">{body}</g>'
            f'<rect x=".6" y=".6" width="{w-1.2}" height="{h-1.2}" rx="18" fill="none" stroke="#a5b6ff" opacity=".22"/></svg>\n')


def progress_svg(ms, files, now):
    total = sum(m["impl"] + m["ver"] for m in ms)
    pct = 100 * total / (2 * len(ms))
    W, H = 1200, 330
    b = []
    # 왼쪽 총계 + 링
    r, cx, cy = 70, 140, 165
    circ = 2 * 3.14159 * r
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#2a2f55" stroke-width="14"/>')
    if total:
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#80e4cb" stroke-width="14" stroke-linecap="round" '
                 f'stroke-dasharray="{circ*pct/100:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>')
    b.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="40" font-weight="bold" fill="#f4f5ff">{pct:.0f}%</text>')
    b.append(f'<text x="{cx}" y="{cy+30}" text-anchor="middle" font-size="15" fill="#a9b0d6">{total} / {2*len(ms)}점</text>')
    b.append(f'<text x="40" y="44" font-size="15" font-weight="bold" fill="#80e4cb">팀 구축 진행률</text>')
    b.append(f'<text x="40" y="298" font-size="13" fill="#7f87b3">{now:%m/%d %H:%M} KST 갱신</text>')
    b.append('<path d="M262 30V300" stroke="#a5b6ff" opacity=".18"/>')
    # 오른쪽 파트별 행
    x0, y0, rowh = 292, 42, 70
    b.append(f'<text x="{x0+206}" y="{y0-8}" font-size="12" fill="#7f87b3">각 칸 왼쪽 = 구현 근거 · 오른쪽 = 실행 결과</text>')
    for i, (role, name, label, col) in enumerate(PARTS):
        y = y0 + i * rowh
        mine = [m for m in ms if m["role"] == role]
        pts = sum(m["impl"] + m["ver"] for m in mine)
        b.append(f'<rect x="{x0}" y="{y+8}" width="5" height="44" rx="2.5" fill="{col}"/>')
        b.append(f'<text x="{x0+18}" y="{y+28}" font-size="19" font-weight="bold" fill="#f4f5ff">{name}</text>')
        b.append(f'<text x="{x0+18}" y="{y+49}" font-size="13" fill="{col}">{escape(label)} · 파일 {files.get(role, 0)}개</text>')
        cw, gap, cx0 = 150, 9, x0 + 206
        for j, m in enumerate(mine):
            x = cx0 + j * (cw + gap)
            b.append(f'<rect x="{x}" y="{y+6}" width="{cw}" height="48" rx="10" fill="#1b2142" stroke="{col}" stroke-opacity="{.75 if m["impl"] else .22}"/>')
            b.append(f'<text x="{x+12}" y="{y+25}" font-size="11.5" font-weight="bold" fill="{col}">{m["key"]}</text>')
            b.append(f'<text x="{x+12}" y="{y+43}" font-size="12.5" fill="#d9ddf5">{escape(SHORT.get(m["key"], m["title"]))}</text>')
            for k, on in enumerate((m["impl"], m["ver"])):
                b.append(f'<rect x="{x+cw-52+k*22}" y="{y+16}" width="18" height="6" rx="3" fill="{col if on else "#343a66"}"/>')
        b.append(f'<text x="{W-34}" y="{y+37}" text-anchor="end" font-size="22" font-weight="bold" fill="#f4f5ff">{pts}<tspan font-size="14" fill="#7f87b3">/8</tspan></text>')
    return frame(W, H, "".join(b), f"팀 구축 진행률 {pct:.1f}% ({total}/{2*len(ms)}점)")


def schedule_svg(today):
    W, rowh, top = 1200, 34, 108
    H = top + rowh * len(SCHEDULE) + 30
    lx, rx = 380, W - 40
    span = (END - START).days + 1
    X = lambda d: lx + (rx - lx) * ((d - START).days / span)
    dleft = (FINAL - today).days
    b = []
    head = f"최종 발표까지 D-{dleft}" if dleft > 0 else ("오늘 최종 발표" if dleft == 0 else "최종 발표 완료")
    b.append(f'<text x="40" y="44" font-size="15" font-weight="bold" fill="#80e4cb">일정 · 수행계획서</text>')
    b.append(f'<text x="40" y="78" font-size="28" font-weight="bold" fill="#f4f5ff">{head}</text>')
    b.append(f'<text x="{40+len(head)*21+16}" y="77" font-size="15" fill="#a9b0d6">12/9({WEEKDAY[FINAL.weekday()]}) · 오늘 {today.month}/{today.day}({WEEKDAY[today.weekday()]})</text>')
    for k in range(span):
        d = START + timedelta(days=k)
        x = X(d)
        if d.weekday() >= 5:
            b.append(f'<rect x="{x:.1f}" y="{top-6}" width="{(rx-lx)/span:.1f}" height="{rowh*len(SCHEDULE)+8}" fill="#a5b6ff" opacity=".05"/>')
        if k % 2 == 0 or d == FINAL:
            b.append(f'<text x="{x+(rx-lx)/span/2:.1f}" y="{top-14}" text-anchor="middle" font-size="11.5" fill="#7f87b3">{d.month}/{d.day}</text>')
    for i, (title, who, role, s, e) in enumerate(SCHEDULE):
        y = top + i * rowh
        s, e = date.fromisoformat(s), date.fromisoformat(e)
        col = COLOR[role]
        done = today > e
        active = s <= today <= e
        b.append(f'<path d="M40 {y+rowh}H{rx}" stroke="#a5b6ff" opacity=".08"/>')
        b.append(f'<text x="40" y="{y+15}" font-size="14" font-weight="bold" fill="{"#f4f5ff" if not done else "#7f87b3"}">{escape(title)}</text>')
        b.append(f'<text x="40" y="{y+29}" font-size="11.5" fill="{col}">{escape(who)} · {s.month}/{s.day}–{e.month}/{e.day}</text>')
        x1, x2 = X(s), X(e + timedelta(days=1))
        b.append(f'<rect x="{x1:.1f}" y="{y+8}" width="{x2-x1:.1f}" height="18" rx="9" fill="{col}" fill-opacity="{.9 if done else .22}" stroke="{col}" stroke-opacity="{1 if active else .55}"/>')
        if active and today <= e:
            frac = ((today - s).days + 1) / ((e - s).days + 1)
            b.append(f'<rect x="{x1:.1f}" y="{y+8}" width="{(x2-x1)*frac:.1f}" height="18" rx="9" fill="{col}" fill-opacity=".6"/>')
    if START <= today <= END:
        tx = X(today) + (rx - lx) / span / 2
        b.append(f'<path d="M{tx:.1f} {top-4}V{top+rowh*len(SCHEDULE)+4}" stroke="#ff7a7a" stroke-width="2.2"/>')
        b.append(f'<rect x="{tx-22:.1f}" y="{top+rowh*len(SCHEDULE)+6}" width="44" height="20" rx="10" fill="#ff7a7a"/>')
        b.append(f'<text x="{tx:.1f}" y="{top+rowh*len(SCHEDULE)+20}" text-anchor="middle" font-size="12" font-weight="bold" fill="#101424">오늘</text>')
    return frame(W, H, "".join(b), head)


def gh(path):
    try:
        return json.loads(subprocess.check_output(["gh", "api", path], text=True, stderr=subprocess.DEVNULL))
    except Exception:
        return None


def ago(ts, now):
    t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    s = (now - t).total_seconds()
    if s < 3600:
        return f"{max(1, int(s // 60))}분 전"
    if s < 86400:
        return f"{int(s // 3600)}시간 전"
    return f"{int(s // 86400)}일 전"


def cell(s):
    return str(s).replace("|", "／").replace("\n", " ").replace("<", "&lt;")


def activity_md(now):
    base = f"https://github.com/{REPO}"
    commits = gh(f"repos/{REPO}/commits?per_page=6") or []
    issues = gh(f"repos/{REPO}/issues?state=open&per_page=10") or []
    branches = gh(f"repos/{REPO}/branches?per_page=50") or []
    if not (commits or issues or branches):
        return None
    lines = ["| 최근 커밋 | 작성자 | 시각 |", "| --- | --- | ---: |"]
    for c in commits:
        m0 = c["commit"]["message"].split("\n")[0]
        msg = m0 if len(m0) <= 72 else m0[:70] + "…"
        who = (c.get("author") or {}).get("login") or c["commit"]["author"]["name"]
        if who.endswith("[bot]"):
            continue
        lines.append(f"| [`{c['sha'][:7]}`]({base}/commit/{c['sha']}) {cell(msg)} | {cell(who)} | {ago(c['commit']['author']['date'], now)} |")
    lines += ["", "**열린 이슈·PR**　"]
    if issues:
        lines[-1] += "　·　".join(f"[{'PR' if 'pull_request' in i else '#'}{'' if 'pull_request' not in i else ' #'}{i['number']} {cell(i['title'][:40])}]({i['html_url']})" for i in issues)
    else:
        lines[-1] += "없음"
    work = [b["name"] for b in branches if b["name"] != "main"]
    lines += ["", f"**작업 브랜치 {len(work)}개**　" + ("　".join(f"[`{cell(n)}`]({base}/tree/{n})" for n in work[:12]) if work else "아직 없음 · 아래 ‘작업 시작하기’ 참고")]
    return "\n".join(lines)


def replace_block(text, name, body):
    a, z = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if a not in text or z not in text:
        return text
    head, rest = text.split(a, 1)
    _, tail = rest.split(z, 1)
    return f"{head}{a}\n{body}\n{z}{tail}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="GitHub API를 부르지 않는다")
    args = ap.parse_args()
    now = datetime.now(KST)
    rep = load_report()
    ms, files = milestones(rep)
    LIVE.mkdir(parents=True, exist_ok=True)
    (LIVE / "progress.svg").write_text(progress_svg(ms, files, now))
    (LIVE / "schedule.svg").write_text(schedule_svg(now.date()))
    readme = ROOT / "README.md"
    text = readme.read_text()
    if not args.offline:
        act = activity_md(now)
        if act:
            text = replace_block(text, "smoke-activity", act)
    readme.write_text(text)


if __name__ == "__main__":
    main()
