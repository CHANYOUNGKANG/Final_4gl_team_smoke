"""Report implementation indicators and team-submitted evidence for Team Smoke."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

# One row = one equally weighted integration milestone. Each group must match.
MILESTONES = [
    ("NET1", "network", "VLAN 분리와 라우팅", [r"\bvlan(?:s)?\b", r"\b(?:ospf|bgp|hsrp|standby)\b"]),
    ("NET2", "network", "방화벽 접근 통제", [r"access-list|<filter>|\bfirewall\b", r"\b(?:deny|block|drop|reject)\b"]),
    ("NET3", "network", "본사·지사 VPN", [r"\b(?:ipsec|ikev2|isakmp)\b", r"tunnel-group|remote-gateway|remote_addrs|peer.address|crypto map"]),
    ("NET4", "network", "IDS 탐지 로그 연동", [r"\b(?:snort|alert_fast|alert_syslog)\b", r"syslog|alert_fast|rsyslog|swatchdog"]),
    ("SRV1", "server", "SSH와 로그 관리", [r"PubkeyAuthentication|PermitRootLogin|AllowUsers", r"rsyslog|imjournal|omfwd|imudp"]),
    ("SRV2", "server", "DB·파일 백업과 원본 목록", [r"mariadb-dump|mysqldump", r"sha256sum|hashlib\.sha256|Get-FileHash"]),
    ("SRV3", "server", "공지 앱 빌드·실행 정보", [r"<packaging>\s*war\s*</packaging>|\bid\s+['\x22]war['\x22]", r"@WebServlet|@GetMapping|@RequestMapping|<web-app|<%@\s*page"]),
    ("SRV4", "server", "운영 알림 메일", [r"postfix|mydestination\s*=", r"roundcube|smtp_server|smtp_host"]),
    ("AWS1", "aws", "두 AZ의 EKS 기반", [r"AWS::EKS::|aws_eks_cluster|eksctl|kind:\s*ClusterConfig", r"subnetIds|subnet_ids|subnets|availabilityZones"]),
    ("AWS2", "aws", "ALB HTTPS와 전환·복귀", [r"\bHTTPS\b|certificate_arn|certificateArn", r"modify-rule|modify-listener|forward_config|ForwardConfig|actions\..*forward"]),
    ("AWS3", "aws", "게시글·첨부 데이터 이관", [r"\b(?:mysql|mariadb|mysqldump|mariadb-dump)\b", r"aws\s+s3\s+(?:sync|cp)|upload_file\("]),
    ("AWS4", "aws", "워커 교체와 장애 관찰", [r"AutoScalingGroup|autoscaling|nodegroup|node_group", r"cloudwatch|describe-scaling-activities|AWS::CloudWatch"]),
    ("CICD1", "cicd", "Jenkins 테스트·WAR 빌드", [r"\bpipeline\s*\{|\bnode\s*\{", r"\bmvnw?\b[^\n]*(?:verify|package|install)"]),
    ("CICD2", "cicd", "Docker 이미지와 ECR 등록", [r"^\s*FROM\s+\S+", r"\b(?:docker|buildah|podman)\s+(?:image\s+)?push|buildx\s+build[^\n]*--push", r"get-login-password|\.dkr\.ecr\."]),
    ("CICD3", "cicd", "Ansible 후보 배포와 상태 검사", [r"^\s*-?\s*hosts\s*:", r"kind:\s*Deployment", r"kind:\s*Service\b", r"readinessProbe:"]),
    ("CICD4", "cicd", "검증 후 전환과 자동 롤백", [r"\bgreen\b", r"\bblue\b", r"rollback|roll_back|roll-back|복귀", r"modify-rule|modify-listener|switch.traffic|set.weight|전환"]),
]
OWNERS = {"network": "강민서 · 네트워크", "server": "이준호 · 서버", "aws": "이우빈 · AWS", "cicd": "강찬영 · CI/CD"}
CODE_EXT = set(".sh .bash .py .groovy .yaml .yml .tf .tfvars .json .xml .jsp .java .conf .cfg .config .ini .rules .gns3 .txt .ios .ps1 .sql .gradle .j2".split())
ROOT_NAMES = {"jenkinsfile", "dockerfile", "pom.xml", "build.gradle"}
VERIFICATIONS = Path("docs/progress/evidence.json")


def files_at(root):
    raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    return {Path(s.decode()) for s in raw.split(b"\0") if s}


def implementation(root, tracked):
    by_role = {role: {} for role in OWNERS}
    for path in sorted(tracked):
        first = path.parts[0]
        name = path.name.lower()
        if first in OWNERS:
            role = first
        elif first == "app" or name == "pom.xml":
            role = "server"
        elif len(path.parts) == 1 and (name in ROOT_NAMES or name.endswith(".groovy")):
            role = "cicd"
        else:
            continue
        f = root / path
        if not f.is_file() or f.is_symlink() or f.stat().st_size > 2_000_000:
            continue
        if path.suffix.lower() not in CODE_EXT | {".md"} and name not in ROOT_NAMES and not name.startswith(("jenkinsfile.", "dockerfile.")):
            continue
        data = f.read_text(errors="replace")
        if path.suffix.lower() == ".md":
            data = "\n".join(re.findall(r"^```[^\n]*\n(.*?)^```[ \t]*$", data, re.M | re.S))
        data = "\n".join(line for line in data.splitlines() if not line.lstrip().startswith(("#", "//", "!")))
        if data.strip():
            by_role[role][path] = data
    return by_role


def proof(root, tracked):
    evidence = json.loads((root / VERIFICATIONS).read_text())
    if not isinstance(evidence, dict):
        raise ValueError("evidence.json must be an object")
    valid_keys = {m[0] for m in MILESTONES}
    if evidence.keys() - valid_keys:
        raise ValueError("Unknown milestone in evidence.json")
    for key, record in evidence.items():
        if not isinstance(record, dict) or not record or record.keys() - {"implementation", "verification"}:
            raise ValueError(f"{key}: expected implementation or verification")
        for stage, entry in record.items():
            if not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ("file", "observed")):
                raise ValueError(f"{key}.{stage}: file and observed are required")
            p = Path(entry["file"])
            f = root / p
            if p not in tracked or p.parts[0] not in {*OWNERS, "app"} or p.name in {".gitkeep", "README.md"} or f.is_symlink() or not f.is_file() or not f.stat().st_size:
                raise ValueError(f"{key}.{stage}: evidence must refer to a tracked, nonempty project artifact")
        if len(record) == 2 and record["implementation"]["file"] == record["verification"]["file"] and record["implementation"]["observed"].strip() == record["verification"]["observed"].strip():
            raise ValueError(f"{key}: describe implementation and the observed test outcome separately")
    return evidence


def render(root, base_url):
    tracked = files_at(root)
    corpus = implementation(root, tracked)
    evidence = proof(root, tracked)
    scores = {role: [] for role in OWNERS}
    rows = []
    def link(p):
        return f"[{p.name.replace('|', ' ')}]({base_url}/{quote(p.as_posix())})"
    for key, role, title, patterns in MILESTONES:
        matches = []
        for pattern in patterns:
            match = next((p for p, s in corpus[role].items() if re.search(pattern, s, re.I | re.M)), None)
            if match is None:
                matches = []
                break
            matches.append(match)
        rec = evidence.get(key, {})
        impl = bool(matches or "implementation" in rec)
        verified = impl and "verification" in rec
        points = int(impl) + int(verified)
        scores[role].append(points)
        refs = [link(p) for p in dict.fromkeys(matches)]
        for stage, entry in rec.items():
            note = entry["observed"].replace("|", "／").replace("\n", " ")
            refs.append(f"{'구현' if stage == 'implementation' else '실측'} {link(Path(entry['file']))} · {note}")
        rows.append(f"| {key} | {title} | {points}/2 | {'<br>'.join(refs) or '근거 대기'} |")
    total = sum(sum(v) for v in scores.values())
    maximum = 2 * len(MILESTONES)
    summary = [f"**전체 구축 진행률 {100*total/maximum:.1f}%**　·　{total}/{maximum}점", "", "| 파트 | 점수 | 진행률 |", "| --- | ---: | ---: |"]
    for role, values in scores.items():
        summary.append(f"| {OWNERS[role]} | {sum(values)}/{2*len(values)} | {100*sum(values)/(2*len(values)):.1f}% |")
    return "\n".join(summary + ["", "구현 신호 또는 구성 증적 1점 + 팀이 등록한 실행 결과 1점. 설계 준비는 별도다.", "", "| ID | 측정 항목 | 점수 | 근거 |", "| --- | --- | ---: | --- |", *rows]) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()
    print(render(Path.cwd(), args.base_url), end="")
