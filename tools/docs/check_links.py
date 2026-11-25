"""저장소 Markdown의 상대 링크·앵커 검사 (네트워크 없이).

    python3 tools/docs/check_links.py          # 깨진 링크가 있으면 종료 코드 1

GitHub 앵커 규칙: 소문자, 공백→-, 영문·숫자·한글·-·_ 외 문자는 제거.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
SKIP = {"docs/originals", "node_modules", ".git"}
LINK = re.compile(r"(?<!!)\[(?:[^\]]|\][^(])*?\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)|<img[^>]+src=\"([^\"]+)\"")
REPO_URL = re.compile(r"^https://github\.com/CHANYOUNGKANG/Final_4gl_team_smoke/(?:blob|tree)/main/(.+)$", re.I)


def slug(h):
    h = re.sub(r"<[^>]+>", "", h).strip().lower()
    h = re.sub(r"[^\w\- 가-힣ㄱ-ㅎㅏ-ㅣ]", "", h)
    return h.replace(" ", "-")


def anchors(md):
    text = md.read_text(errors="replace")
    text = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    seen, out = {}, set()
    for m in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        s = slug(m.group(1))
        n = seen.get(s, 0)
        out.add(s if n == 0 else f"{s}-{n}")
        seen[s] = n + 1
    out |= set(re.findall(r'id="([^"]+)"', text))
    return out


def main():
    bad = []
    files = [p for p in ROOT.rglob("*.md") if not any(str(p.relative_to(ROOT)).startswith(s) for s in SKIP)]
    cache = {}
    for md in files:
        text = re.sub(r"^```.*?^```", "", md.read_text(errors="replace"), flags=re.S | re.M)
        text = re.sub(r"`[^`\n]*`", "", text)
        for m in LINK.finditer(text):
            url = next(g for g in m.groups() if g)
            r = REPO_URL.match(url)
            if r:
                target, frag = (r.group(1).split("#", 1) + [""])[:2]
                path = ROOT / unquote(target)
            elif re.match(r"^[a-z]+:", url, re.I):
                continue
            else:
                target, frag = (url.split("#", 1) + [""])[:2]
                path = (md.parent / unquote(target)).resolve() if target else md
            rel = md.relative_to(ROOT)
            if not path.exists():
                bad.append(f"{rel}: 파일 없음 → {url}")
                continue
            if frag and path.suffix == ".md":
                if path not in cache:
                    cache[path] = anchors(path)
                if unquote(frag).lower() not in cache[path]:
                    bad.append(f"{rel}: 앵커 없음 → {url}")
    for b in bad:
        print(b)
    print(f"검사한 문서 {len(files)}개 · 문제 {len(bad)}건")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
