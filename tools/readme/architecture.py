"""시스템 아키텍처 구성도 생성기 → docs/images/architecture.svg

값의 기준은 docs/architecture/ip-plan.md 이다. 주소·서브넷이 바뀌면 아래 표를 고친 뒤
    python3 tools/readme/architecture.py
를 실행하고 SVG와 함께 커밋한다. (실제 공인 IP·계정 ID는 넣지 않는다)
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs/images/architecture.svg"
W, H = 1440, 1040
FONT = "Noto Sans CJK KR,Noto Sans KR,Apple SD Gothic Neo,Malgun Gothic,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
NET, SRV, AWS, CICD = "#91c4ff", "#85e4cf", "#ffd0a2", "#d0b5ff"
INK, SUB, DIM, CARD = "#f4f5ff", "#a9b0d6", "#7f87b3", "#1b2142"
FLOW = {  # 번호, 색, 이름
    1: ("#f4f5ff", "사용자 요청"), 2: ("#ff8fb3", "데이터 이관"), 3: ("#d0b5ff", "무중단 배포"),
    4: ("#91c4ff", "지사 접근 통제"), 5: ("#80e4cb", "운영 알림"), 6: ("#ffcc66", "모의해킹 점검"),
}
DENY = "#ff7a7a"
S = []


def t(x, y, s, c=INK, z=14, w=400, anc="start", mono=False):
    fam = f' font-family="{MONO}"' if mono else ""
    S.append(f'<text x="{x}" y="{y}" font-size="{z}" font-weight="{w}" fill="{c}" text-anchor="{anc}"{fam}>{escape(s)}</text>')


def zone(x, y, w, h, title, sub, c, who=""):
    S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#151a33" stroke="{c}" stroke-opacity=".35"/>')
    S.append(f'<rect x="{x}" y="{y+14}" width="4" height="26" rx="2" fill="{c}"/>')
    t(x + 18, y + 33, title, INK, 19, 700)
    if sub:
        tw = sum(19 if ord(ch) > 0x1100 else 11 for ch in title)
        t(x + 30 + tw, y + 32, sub, c, 13, 600, mono=True)
    if who:
        t(x + w - 16, y + 32, who, c, 13, 600, "end")


def area(x, y, w, h, label, c, ip=""):
    S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{c}" stroke-opacity=".28" stroke-dasharray="4 4"/>')
    t(x + 12, y + 18, label, c, 12, 700)
    if ip:  # 라벨 바로 뒤에 붙여 오른쪽을 선이 지나갈 수 있게 비운다
        lw = sum(12.5 if ord(ch) > 0x1100 else 7 for ch in label)
        t(x + 22 + lw, y + 18, ip, c, 11.5, 600, mono=True)


def box(x, y, w, h, title, lines, c, tag=None):
    S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{CARD}" stroke="{c}" stroke-opacity=".55"/>')
    t(x + 12, y + 21, title, INK, 14.5, 700)
    for i, (s, mono) in enumerate(lines):
        t(x + 12, y + 39 + i * 16, s, c if mono else SUB, 12 if mono else 12, 600 if mono else 400, mono=mono)
    if tag:
        tw = len(tag[0]) * 7.2 + 14
        S.append(f'<rect x="{x+w-tw-8}" y="{y+8}" width="{tw}" height="18" rx="9" fill="{tag[1]}"/>')
        t(x + w - tw / 2 - 8, y + 21, tag[0], "#101424", 11, 800, "middle")


def line(pts, c, dash="", w=2, arrow=True, both=False):
    d = "M" + " L".join(f"{a} {b}" for a, b in pts)
    m = f' marker-end="url(#a{c[1:]})"' if arrow else ""
    ms = f' marker-start="url(#a{c[1:]})"' if both else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    S.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}"{da}{m}{ms} stroke-linecap="round" stroke-linejoin="round"/>')


def pill(x, y, s, c, fill="#101424"):
    w = sum(13 if ord(ch) > 0x1100 else 7 for ch in s) + 18
    S.append(f'<rect x="{x-w/2}" y="{y-11}" width="{w}" height="22" rx="11" fill="{fill}" stroke="{c}"/>')
    t(x, y + 4.5, s, c, 12, 700, "middle")


def badge(x, y, n):
    c = FLOW[n][0]
    S.append(f'<circle cx="{x}" cy="{y}" r="12" fill="{c}" stroke="#101424" stroke-width="3"/>')
    t(x, y + 4.5, str(n), "#101424", 13, 800, "middle")


def build():
    colors = {c for c, _ in FLOW.values()} | {DENY, NET, SRV, AWS, CICD, "#a9b0d6"}
    defs = "".join(f'<marker id="a{c[1:]}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="{c}"/></marker>' for c in colors)
    S.append(f'<defs><linearGradient id="bg" x2="1" y2=".35"><stop stop-color="#101424"/><stop offset=".55" stop-color="#171b38"/><stop offset="1" stop-color="#221f4d"/></linearGradient>{defs}</defs>')
    S.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>')
    t(30, 42, "㈜스모크 시스템 아키텍처", INK, 24, 800)
    t(320, 41, "온프레미스(GNS3·VMware) · AWS 서울 리전 · CI/CD  —  주소는 docs/architecture/ip-plan.md 제안 값", DIM, 13)

    # ── 인터넷 · ISP
    area(20, 60, 1400, 92, "인터넷 · ISP 구간 (GNS3 안의 가상 통신사)", "#a9b0d6")
    box(36, 86, 200, 56, "Kali 공격자", [("203.0.113.50/24", True)], FLOW[6][0])
    box(300, 86, 250, 56, "ISP 라우터 · AS 65100", [(".1 R1 · .5 R2 · .9 지사", True)], NET, ("NAT ①", "#f4f5ff"))
    box(610, 86, 230, 56, "GNS3 NAT 노드", [("192.168.122.0/24 → 인터넷", True)], NET)
    box(1180, 86, 224, 56, "외부 사용자", [("notice.<도메인> HTTPS", False)], "#f4f5ff")
    line([(236, 114), (296, 114)], FLOW[6][0])
    line([(550, 114), (606, 114)], "#a9b0d6", arrow=False)
    line([(840, 114), (930, 114), (930, 170)], AWS, "6 5")
    pill(1000, 114, "인터넷 HTTPS 443 → AWS", AWS)

    # ── GNS3 네트워크 (강민서)
    zone(20, 170, 680, 330, "GNS3 네트워크", "", NET, "강민서")
    area(34, 220, 176, 268, "지사 10.1.0.0/16", NET)
    box(44, 248, 156, 70, "pfSense", [("WAN 198.51.100.10", True), ("LAN 10.1.10.1", True)], NET)
    box(44, 352, 156, 56, "지사 PC", [("10.1.10.100", True)], NET)
    t(122, 436, "공지·웹메일만 허용", FLOW[4][0], 12, 700, "middle")
    t(122, 454, "관리망·서버팜 차단", DENY, 12, 700, "middle")
    line([(122, 352), (122, 322)], FLOW[4][0])
    area(222, 220, 466, 268, "본사 10.0.0.0/16", NET)
    box(234, 246, 216, 52, "Edge R1 · HSRP Active", [("198.51.100.2 · .130", True)], NET)
    box(462, 246, 214, 52, "Edge R2 · Standby", [("198.51.100.6 · .131", True)], NET)
    pill(455, 310, "공인 .128/28 · HSRP VIP .129 · iBGP", NET)
    box(234, 322, 216, 66, "ASA-1 Active", [("out .132 · in 10.0.0.1", True), ("NAT ② .140 → 10.0.30.10", True)], NET, ("80·443", "#80e4cb"))
    box(462, 322, 214, 66, "ASA-2 Standby", [("out .133 · FO 10.0.255.0/30", True)], NET)
    box(234, 404, 216, 52, "Core SW-1 · RSTP", [("10.0.0.2 · SVI .2 · GW .1", True)], NET)
    box(462, 404, 214, 52, "Core SW-2 · LACP · SPAN", [("10.0.0.3 · SVI .3", True)], NET)
    box(462, 460, 214, 34, "Snort IDS · 관리 10.0.20.20", [], FLOW[6][0])
    line([(569, 456), (569, 460)], FLOW[6][0], arrow=False)
    # 위·아래 연결
    line([(360, 142), (360, 242)], NET)
    line([(500, 142), (500, 152), (600, 152), (600, 242)], NET)
    line([(330, 142), (330, 160), (185, 160), (185, 244)], NET)
    line([(200, 282), (216, 282), (216, 356), (230, 356)], FLOW[4][0], "5 4")
    pill(216, 324, "IPsec", FLOW[4][0])
    line([(342, 298), (342, 318)], NET)
    line([(342, 388), (342, 400)], NET)
    badge(612, 190, 4)

    # ── Linux 서버 VM (이준호)
    zone(20, 518, 680, 210, "Linux 서버 VM", "", SRV, "이준호")
    vms = [
        (34, "① 관리 · VLAN 20 · VMnet2", "10.0.20.10", ["SSH Bastion :22", "Ansible · 백업 /backup", "rsyslog :514"]),
        (256, "② 서비스 · VLAN 30 · VMnet3", "10.0.30.10", ["Tomcat :8080 · Nginx :80·443", "메일 :25·143 (ops@)", "DVWA :8081 (점검용)"]),
        (478, "③ 데이터 · VLAN 40 · VMnet4", "10.0.40.10", ["MariaDB :3306", "NFS 첨부 :2049", "건수·sha256 원본 목록"]),
    ]
    for x, ttl, ip, items in vms:
        box(x, 564, 210, 150, ttl, [(ip, True)] + [(s, False) for s in items], SRV)
    line([(342, 456), (342, 506), (220, 506), (220, 560)], NET)
    line([(342, 506), (440, 506), (440, 560)], NET)
    line([(440, 506), (600, 506), (600, 560)], NET)
    for cx, ok in [(220, False), (440, True), (600, False)]:
        S.append(f'<circle cx="{cx}" cy="535" r="9" fill="{"#80e4cb" if ok else DENY}"/>')
        t(cx, 539.5, "✓" if ok else "✕", "#101424", 12, 800, "middle")
    t(512, 545, "지사 PC 기준", FLOW[4][0], 11, 700, "middle")
    badge(268, 114, 6)

    # ── 운영 알림 메일함
    S.append(f'<rect x="20" y="740" width="680" height="62" rx="14" fill="#122a2c" stroke="#80e4cb" stroke-opacity=".5"/>')
    t(36, 764, "운영 알림 메일함 ops@ (Roundcube)", INK, 14.5, 700)
    tags = [("[Snort] 탐지", NET), ("[백업] 결과", SRV), ("[장애] CloudWatch", AWS), ("[배포] Jenkins", CICD)]
    for i, (s, c) in enumerate(tags):
        x = 36 + i * 164
        S.append(f'<rect x="{x}" y="774" width="152" height="20" rx="10" fill="{c}" fill-opacity=".18" stroke="{c}" stroke-opacity=".6"/>')
        t(x + 76, 788, s, c, 11.5, 700, "middle")
    line([(440, 714), (440, 736)], FLOW[5][0], "", 2, both=True)
    badge(690, 754, 5)

    # ── AWS (이우빈)
    zone(720, 170, 700, 632, "AWS 클라우드", "VPC 10.100.0.0/16 · 서울", AWS, "이우빈")
    box(734, 214, 172, 52, "CloudWatch → SNS", [("→ SQS smoke-ops-mail", True)], AWS)
    box(916, 214, 150, 52, "S3 첨부 원본", [("비공개 · VPC 밖", False)], AWS)
    box(1076, 214, 150, 52, "CloudFront", [("files.<도메인>", True)], AWS)
    box(1236, 214, 170, 52, "Route 53 · ACM", [("notice.<도메인>", True)], AWS)
    line([(1320, 142), (1320, 210)], "#f4f5ff")
    badge(1320, 176, 1)
    line([(1076, 240), (1066, 240)], "#a9b0d6")
    area(734, 280, 672, 106, "퍼블릭 서브넷", AWS, "a 10.100.1.0/24 · c 10.100.2.0/24")
    box(746, 306, 128, 70, "Bastion", [("22 ← 실습 PC/32", True), ("덤프 → RDS 3306", True)], AWS)
    box(884, 306, 122, 70, "Jenkins", [("8080 ← 실습 PC", True), ("Poll SCM", False)], CICD)
    box(1016, 306, 120, 70, "NAT GW", [("프라이빗 출구", False)], AWS)
    box(1146, 306, 250, 70, "ALB · HTTPS 443", [("대상 그룹 Blue / Green", False), ("→ Pod :8080", True)], AWS)
    line([(1320, 266), (1320, 302)], "#f4f5ff")
    area(734, 396, 672, 216, "프라이빗 앱 · EKS", AWS, "a 10.100.11.0/24 · c 10.100.12.0/24")
    for i, (x, nm) in enumerate([(746, "워커 A · AZ a"), (986, "워커 C · AZ c")]):
        S.append(f'<rect x="{x}" y="422" width="230" height="140" rx="10" fill="{CARD}" stroke="{AWS}" stroke-opacity=".55"/>')
        t(x + 12, 443, nm, INK, 14.5, 700)
        t(x + 218, 443, "ASG", DIM, 11.5, 700, "end")
        for j, (lab, c) in enumerate([("Blue v1 · 운영", "#7fb2ff"), ("Green v2 · 검증", "#7fe0a6")]):
            y = 456 + j * 50
            S.append(f'<rect x="{x+12}" y="{y}" width="206" height="40" rx="9" fill="{c}" fill-opacity=".14" stroke="{c}" stroke-opacity=".6"/>')
            t(x + 24, y + 25, "공지 서비스 " + lab, c, 13, 700)
    box(1226, 422, 170, 70, "Ansible EC2", [("DEPLOY_HOST", True), ("→ EKS API 443", True)], CICD)
    box(1226, 502, 170, 60, "IAM 역할", [("ECR · EKS Access Entry", False)], AWS)
    t(1396, 594, "Pod도 서브넷 IP (VPC CNI) · 태그 role/elb · role/internal-elb", DIM, 11.5, 600, "end")
    line([(1180, 376), (1180, 391), (861, 391), (861, 418)], "#f4f5ff")
    line([(1180, 391), (1150, 391), (1150, 418)], "#f4f5ff")

    area(734, 622, 672, 168, "프라이빗 데이터 · 인터넷 경로 없음", AWS, "a 10.100.21.0/24 · c 10.100.22.0/24")
    box(746, 650, 200, 62, "RDS MariaDB", [("db.smoke.internal :3306", True)], AWS)
    box(956, 650, 200, 62, "ElastiCache Redis", [("cache.smoke.internal :6379", True)], AWS)
    box(1166, 650, 230, 62, "EFS 탑재 대상 a·c", [(":2049 · Pod 공유", True)], AWS)
    t(1070, 742, "SG 참조: ALB SG → 노드 SG 8080 · 노드 SG → RDS·Redis·EFS · Bastion SG → RDS 3306", DIM, 11.5, 600, "middle")
    t(1070, 762, "RDS Multi-AZ는 선택 · 단일 AZ면 스냅샷 복원 시간 측정", DIM, 11.5, 600, "middle")
    line([(746, 520), (739, 520), (739, 681), (742, 681)], "#f4f5ff")

    # ── 이관 경로 (2)
    line([(600, 714), (600, 726), (708, 726), (708, 162), (990, 162), (990, 210)], FLOW[2][0], "6 5")
    line([(708, 342), (742, 342)], FLOW[2][0], "6 5")
    pill(708, 470, "이관", FLOW[2][0])
    badge(708, 162, 2)
    # ── 알림 경로 (5)
    line([(734, 240), (727, 240), (727, 818), (440, 818), (440, 806)], FLOW[5][0], "6 5")
    t(560, 834, "CloudWatch·Jenkins → SNS → SQS ← 메일 서버가 HTTPS 443으로 가져감 (들어오는 포트 없음)", FLOW[5][0], 12, 700, "middle")
    # ── CI/CD (강찬영)
    zone(20, 846, 1400, 146, "CI/CD 파이프라인", "커밋 SHA = 이미지 태그", CICD, "강찬영")
    steps = [("GitHub", "PR · main 병합"), ("Jenkins", "Poll SCM · mvn package"), ("Docker", "WAR → 이미지"),
             ("ECR", "커밋 태그 push"), ("Ansible", "EKS Green 배포"), ("Green 검증", "글 작성 · 조회"), ("ALB 전환", "실패 시 Blue 롤백")]
    for i, (a, b) in enumerate(steps):
        x = 36 + i * 196
        S.append(f'<rect x="{x}" y="892" width="176" height="82" rx="10" fill="{CARD}" stroke="{CICD}" stroke-opacity=".55"/>')
        t(x + 12, 912, f"0{i+1}", DIM, 11.5, 700)
        t(x + 88, 938, a, INK, 15.5, 700, "middle")
        t(x + 88, 960, b, DENY if i == 6 else SUB, 12, 600 if i == 6 else 400, "middle")
        if i < 6:
            line([(x + 176, 933), (x + 194, 933)], CICD)
    line([(1388, 933), (1428, 933), (1428, 457), (1400, 457)], CICD, "6 5")
    badge(1428, 700, 3)


def legend_row():
    x = 30
    t(x, 1022, "흐름", DIM, 11.5, 700)
    x += 34
    for n, (c, name) in FLOW.items():
        S.append(f'<circle cx="{x}" cy="1018" r="7" fill="{c}"/>')
        t(x, 1022, str(n), "#101424", 10, 800, "middle")
        t(x + 11, 1022, name, SUB, 11.5, 600)
        x += 24 + len(name) * 12.5


def main():
    build()
    legend_row()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="㈜스모크 시스템 아키텍처: GNS3 본사·지사 네트워크, Linux 서버 VM 3대, AWS VPC 서브넷 3계층, CI/CD 블루그린 파이프라인">'
           f'<title>㈜스모크 시스템 아키텍처</title><g font-family="{FONT}">' + "".join(s for s in S if s) + "</g></svg>\n")
    OUT.write_text(svg)


if __name__ == "__main__":
    main()
