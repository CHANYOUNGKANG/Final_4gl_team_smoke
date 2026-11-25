// 시스템 아키텍처 구성도 · IP 문서 생성기
//   입력: docs/architecture/topology.json (주소·포트의 단일 기준)
//   출력: docs/images/architecture.svg, docs/architecture/ip-plan.md 의 자동 표 블록
// 구성도 배치는 팀 아키텍처 대시보드(2페이지 전체 아키텍처, IP 표시)의 그리기 코드를 옮긴 것이다.
// main 병합 시 Actions(Team progress)가 자동 실행한다. 로컬 미리보기: node tools/readme/architecture.js
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "../..");
const OUT = path.join(ROOT, "docs/images/architecture.svg");
const PLAN = path.join(ROOT, "docs/architecture/ip-plan.md");
const TOPO = JSON.parse(fs.readFileSync(path.join(ROOT, "docs/architecture/topology.json"), "utf8"));
/* 대역 검증: 형식 오류·사설 대역 겹침이면 실패 (본사·지사·AWS가 겹치면 VPN·이관 라우팅이 깨진다) */
const cidr = (c) => {
  const m = /^(\d+)\.(\d+)\.(\d+)\.(\d+)\/(\d+)$/.exec(c);
  if (!m || m.slice(1, 5).some((o) => +o > 255) || +m[5] > 32) throw new Error(`잘못된 CIDR: ${c}`);
  const ip = m.slice(1, 5).reduce((a, o) => a * 256 + +o, 0), size = 2 ** (32 - +m[5]);
  if (ip % size) throw new Error(`네트워크 주소가 아님: ${c}`);
  return [ip, ip + size - 1];
};
const R = TOPO.ranges.map(([n, c]) => [n, c, cidr(c)]);
for (let i = 0; i < R.length; i++) for (let j = i + 1; j < R.length; j++)
  if (R[i][2][0] <= R[j][2][1] && R[j][2][0] <= R[i][2][1]) throw new Error(`대역 겹침: ${R[i][0]} ${R[i][1]} ↔ ${R[j][0]} ${R[j][1]}`);
for (const [sub, a, c] of TOPO.aws) for (const x of [a, c]) { const [lo, hi] = cidr(x), v = R.find((r) => r[0] === "AWS VPC")[2]; if (lo < v[0] || hi > v[1]) throw new Error(`VPC 밖 서브넷: ${sub} ${x}`); }
for (const [, c] of TOPO.gns3) if (/^\d/.test(c)) cidr(c);
const D = new Proxy(TOPO.diagram, { get: (o, k) => { if (!(k in o)) throw new Error(`topology.json diagram.${String(k)} 없음`); return o[k]; } });

const OWN = {
  net: { c: "#2b4fbf", n: "강민서", r: "네트워크·보안" },
  srv: { c: "#0f7a5a", n: "이준호", r: "Linux 서버·메일" },
  aws: { c: "#c45a1c", n: "이우빈", r: "AWS 클라우드" },
  cicd: { c: "#7b4a9e", n: "강찬영", r: "CI/CD" },
  user: { c: "#3a3a3a", n: "", r: "" },
};
const FLOW = {
  A: { n: 1, c: "#1f1f1f" }, B: { n: 2, c: "#b83268" }, C: { n: 3, c: "#6a4fc8" },
  D: { n: 4, c: "#2b4fbf" }, E: { n: 5, c: "#0f7a6c" }, F: { n: 6, c: "#a16207" },
};
const G = {
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
  pc: '<rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M8 20h8M12 16v4"/>',
  fw: '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 10h18M3 15h18M9 5v5M15 10v5M9 15v4"/>',
  router: '<circle cx="12" cy="12" r="9"/><path d="M12 6v12M6 12h12M9 9l3-3 3 3M9 15l3 3 3-3"/>',
  switch: '<rect x="3" y="8" width="18" height="8" rx="1.5"/><path d="M7 5h10l-2-2M17 19H7l2 2"/>',
  server: '<rect x="4" y="3" width="16" height="7" rx="1"/><rect x="4" y="14" width="16" height="7" rx="1"/><path d="M8 6.5h.01M8 17.5h.01"/>',
  db: '<ellipse cx="12" cy="5" rx="7" ry="2.6"/><path d="M5 5v14c0 1.5 3.1 2.6 7 2.6s7-1.1 7-2.6V5M5 12c0 1.5 3.1 2.6 7 2.6s7-1.1 7-2.6"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><ellipse cx="12" cy="12" rx="4" ry="9"/>',
  bolt: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
  bucket: '<ellipse cx="12" cy="6" rx="8" ry="2.5"/><path d="M4 6l2 14c.3 1.2 2.8 2 6 2s5.7-.8 6-2l2-14"/>',
  box: '<path d="M12 2l9 5v10l-9 5-9-5V7z"/><path d="M3 7l9 5 9-5M12 12v10"/>',
  chart: '<path d="M4 4v16h16"/><path d="M8 15l4-5 3 3 5-6"/>',
  lock: '<rect x="5" y="11" width="14" height="10" rx="1.5"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
  gear: '<circle cx="12" cy="12" r="3.2"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/>',
  git: '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="8" r="2"/><path d="M6 7v10M18 10c0 4-6 3-11 7"/>',
  check: '<path d="M4 12.5l5 5L20 6"/>',
  layers: '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
  play: '<path d="M7 4l13 8-13 8z"/>',
  pods: '<rect x="3" y="3" width="7.5" height="7.5" rx="1"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="1"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="1"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1"/>',
  swap: '<path d="M4 8h15l-4-4M20 16H5l4 4"/>',
  disk: '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="16.5" cy="12" r="1.5"/><path d="M6 12h6"/>',
  file: '<path d="M6 2h8l5 5v15H6z"/><path d="M14 2v5h5M9 13h7M9 17h7"/>',
  bug: '<ellipse cx="12" cy="13" rx="5" ry="7"/><path d="M12 6V3M7 9 4 8M17 9l3-1M7 14H3M17 14h4M7 18l-3 2M17 18l3 2"/>',
  folder: '<path d="M3 6h6l2 2h10v11H3z"/>',
  term: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M12 15h5"/>',
  log: '<path d="M4 6h16M4 12h16M4 18h10"/>',
  web: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M7 6.5h.01M10 6.5h.01"/>',
  cloud: '<path d="M7 18h10a4 4 0 0 0 0-8 6 6 0 0 0-11.3-1.5A4.5 4.5 0 0 0 7 18z"/>',
  shield: '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
};
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
const tw = (s, z) => [...s].reduce((a, ch) => a + (ch.charCodeAt(0) > 0x1100 ? z : z * 0.6), 0);
const tint = (h, a) => { const n = parseInt(h.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; };
const TXT = "#141414", SUB = "#7a766e", MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace";
let S = "";
const mk = (id, c) => `<marker id="${id}" viewBox="0 0 10 10" refX="6.5" refY="5" markerWidth="3.6" markerHeight="3.6" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="${c}"/></marker>`;
S += "<defs>" + Object.entries(FLOW).map(([k, f]) => mk("m" + k, f.c)).join("") + mk("mX", "#c0392b") + "</defs>";
S += `<rect x="0" y="0" width="1710" height="1444" fill="#ffffff"/>`;

const icon = (g, x, y, s, c) => `<rect x="${x}" y="${y}" width="${s}" height="${s}" rx="${s * 0.26}" fill="${tint(c, 0.1)}"/><g transform="translate(${x + s * 0.2} ${y + s * 0.2}) scale(${s * 0.6 / 24})" fill="none" stroke="${c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${G[g]}</g>`;
const ZE = { "GNS3 네트워크": "🌐", "Linux 서버 VM": "🐧", "AWS 클라우드": "☁️", "CI/CD 파이프라인": "🚀" };
function zone(o, x, y, w, h, title, sub) {
  const c = OWN[o].c, emo = ZE[title] || "", tx = x + 72;
  S += `<g><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="18" fill="#fbfaf8" stroke="#e6e3dc" stroke-width="1"/>` +
    `<rect x="${x + 18}" y="${y + 8}" width="42" height="42" rx="12" fill="#fff" stroke="${tint(c, 0.35)}" stroke-width="1.2"/><text x="${x + 39}" y="${y + 38}" font-size="24" text-anchor="middle">${emo}</text>` +
    `<text x="${tx}" y="${y + 38}" font-size="22" font-weight="700" fill="${TXT}" letter-spacing="-0.6">${esc(title)}</text>` +
    (sub ? `<text x="${tx + 12 + tw(title, 22)}" y="${y + 37}" font-size="14" font-weight="500" fill="#9a958b">${esc(sub)}</text>` : "") +
    `<line x1="${x + 24}" y1="${y + 60}" x2="${x + w - 24}" y2="${y + 60}" stroke="#e6e3dc"/>`;
  if (OWN[o].n) S += `<text x="${x + w - 26}" y="${y + 37}" font-size="14" text-anchor="end"><tspan font-weight="700" fill="${c}">${esc(OWN[o].n)}</tspan><tspan font-weight="500" fill="#9a958b">  ${esc(OWN[o].r)}</tspan></text>`;
  S += "</g>";
}
function block(x, y, w, h, label) {
  S += `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14" fill="none" stroke="#e6e3dc" stroke-width="1" stroke-dasharray="3 4"/>`;
  if (label) S += `<text x="${x + 16}" y="${y + 26}" font-size="14" font-weight="600" fill="#9a958b">${esc(label)}</text>`;
}
function node(n) {
  const o = OWN[n.o], h = n.h || 72, is = n.is || 42;
  S += `<g><rect x="${n.x}" y="${n.y}" width="${n.w}" height="${h}" rx="12" fill="#fff" stroke="#e3e0d9" stroke-width="1"/>` + icon(n.g, n.x + 13, n.y + (h - is) / 2, is, o.c);
  const tx = n.x + is + 24;
  S += `<text x="${tx}" y="${n.y + (n.s || n.ip ? h / 2 - 3 : h / 2 + 6)}" font-size="${n.fs || 17.5}" font-weight="700" fill="${TXT}" letter-spacing="-0.4">${esc(n.t)}</text>`;
  if (n.ip) S += `<text x="${tx}" y="${n.y + h / 2 + 17}" font-size="12.5" font-weight="700" fill="${o.c}" font-family="${MONO}" letter-spacing="-0.3">${esc(n.ip)}</text>`;
  else if (n.s) S += `<text x="${tx}" y="${n.y + h / 2 + 17}" font-size="13.5" fill="${SUB}">${esc(n.s)}</text>`;
  S += "</g>";
}
function tile(n) {
  const o = OWN[n.o], w = n.w, h = n.h || 112;
  S += `<g><rect x="${n.x}" y="${n.y}" width="${w}" height="${h}" rx="12" fill="#fff" stroke="#e3e0d9" stroke-width="1"/>` + icon(n.g, n.x + w / 2 - 22, n.y + 14, 44, o.c);
  S += `<text x="${n.x + w / 2}" y="${n.y + h - 33}" font-size="17" font-weight="700" fill="${TXT}" text-anchor="middle" letter-spacing="-0.4">${esc(n.t)}</text>`;
  S += `<text x="${n.x + w / 2}" y="${n.y + h - 12}" font-size="13.5" fill="${n.sc || SUB}" font-weight="${n.sc ? 700 : 400}" text-anchor="middle">${esc(n.s)}</text>`;
  if (n.num) S += `<text x="${n.x + 14}" y="${n.y + 25}" font-size="12.5" font-weight="500" fill="#b5b1a8">0${n.num}</text>`;
  S += "</g>";
}
function flow(f, pts, opt = {}) {
  const c = opt.deny ? "#c0392b" : FLOW[f].c, m = opt.deny ? "mX" : "m" + f;
  S += `<g><path class="fl" d="M${pts.map((p) => p.join(" ")).join(" L")}" stroke="${c}" marker-end="url(#${m})"/>`;
  if (opt.l) { const w = tw(opt.l, 13.5) + 26; S += `<rect x="${opt.lx - w / 2}" y="${opt.ly - 14}" width="${w}" height="28" rx="14" fill="#fff" stroke="${c}" stroke-width="1.2"/><text x="${opt.lx}" y="${opt.ly + 5}" font-size="13.5" font-weight="700" fill="${c}" text-anchor="middle">${esc(opt.l)}</text>`; }
  S += "</g>";
}
function badge(f, x, y) { const c = FLOW[f].c; S += `<circle cx="${x}" cy="${y}" r="15" fill="${c}" stroke="#fff" stroke-width="3"/><text x="${x}" y="${y + 5.3}" font-size="15" font-weight="700" fill="#fff" text-anchor="middle">${FLOW[f].n}</text>`; }
function tip_(x, y, s, c, anc, z) { S += `<text x="${x}" y="${y}" font-size="${z || 12}" font-weight="700" fill="${c}" font-family="${MONO}" ${anc ? `text-anchor="${anc}"` : ""}>${esc(s)}</text>`; }
function t(x, y, s, c, z, w, anc) { S += `<text x="${x}" y="${y}" font-size="${z || 14}" font-weight="${w || 500}" fill="${c || SUB}" ${anc ? `text-anchor="${anc}"` : ""}>${esc(s)}</text>`; }
const role = (x, y, l, c) => { const w = tw(l, 11.5) + 20; S += `<rect x="${x - w}" y="${y}" width="${w}" height="21" rx="10.5" fill="${c}" stroke="#fff" stroke-width="2"/><text x="${x - w / 2}" y="${y + 14.6}" font-size="11.5" font-weight="800" fill="#fff" text-anchor="middle">${l}</text>`; };

/* ============ 인터넷 · ISP ============ */
S += `<rect x="24" y="24" width="1652" height="140" rx="18" fill="#f7f6f3" stroke="#e6e3dc" stroke-dasharray="3 4"/><text x="44" y="50" font-size="14" font-weight="700" fill="#7a766e">🌍 인터넷 · ISP 구간 <tspan font-weight="500" font-size="12.5">GNS3 안의 가상 통신사 → GNS3 NAT 노드 → 실제 인터넷</tspan></text>`;
node({ ip: D.kali, x: 44, y: 66, w: 212, h: 70, is: 40, g: "bug", t: "Kali 공격자", s: "Kali Linux VM", fs: 16.5, o: "net" });
node({ ip: D.isp, x: 380, y: 66, w: 220, h: 70, is: 40, g: "router", t: "ISP 라우터", s: "AS 65100 · 가상 통신사", fs: 16.5, o: "net" });
node({ ip: D.gns3_nat, x: 660, y: 66, w: 220, h: 70, is: 40, g: "cloud", t: "GNS3 NAT 노드", s: "실제 인터넷 출구", fs: 16.5, o: "net" });
S += `<rect x="560" y="52" width="64" height="24" rx="12" fill="#141414" stroke="#fff" stroke-width="2"/><text x="592" y="68.5" font-size="12" font-weight="800" fill="#fff" text-anchor="middle">NAT ①</text>`;
S += `<path d="M600 101H656" stroke="#a8a399" stroke-width="2.5"/><path d="M880 101H1300V180" fill="none" stroke="#c45a1c" stroke-width="2.5" stroke-dasharray="7 6"/>`;
S += `<rect x="960" y="88" width="260" height="26" rx="13" fill="#fff" stroke="#c45a1c"/><text x="1090" y="105.5" font-size="13" font-weight="700" fill="#c45a1c" text-anchor="middle">인터넷 · HTTPS 443 → AWS</text>`;
t(1320, 108, "이관 데이터 · 알림(SQS) · 외부 사용자 접속", "#9a958b", 13, 500);

/* ============ GNS3 (강민서) ============ */
zone("net", 24, 184, 776, 500, "GNS3 네트워크", "");
tip_(112, 273, D.branch_range, "#2b4fbf", "", 12); tip_(346, 273, D.hq_range, "#2b4fbf", "", 12);
block(44, 250, 210, 414, "🏬  지사");
node({ ip: D.pfsense, x: 56, y: 290, w: 186, g: "fw", t: "pfSense", s: "지사 방화벽", o: "net" });
node({ ip: D.branch_pc, x: 56, y: 392, w: 186, g: "pc", t: "지사 PC", s: "VLAN 10 업무", o: "net" });
t(149, 520, "공지 허용", OWN.net.c, 13.5, 600, "middle"); t(149, 542, "관리망·서버팜 차단", "#c0392b", 13.5, 600, "middle");
block(274, 250, 506, 414, "🏢  본사");
node({ ip: D.r1, x: 288, y: 284, w: 226, h: 64, is: 38, g: "router", t: "Edge R1", s: "eBGP · HSRP Active", fs: 16, o: "net" });
node({ ip: D.r2, x: 540, y: 284, w: 226, h: 64, is: 38, g: "router", t: "Edge R2", s: "eBGP · HSRP Standby", fs: 16, o: "net" });
S += `<rect x="380" y="356" width="294" height="22" rx="11" fill="#eef2fb"/>`; tip_(527, 371.5, D.hsrp, "#2b4fbf", "middle");
node({ ip: D.asa1, x: 288, y: 386, w: 226, h: 64, is: 38, g: "fw", t: "ASA-1", s: "Active · ACL · VPN 종단", fs: 16, o: "net" });
node({ ip: D.asa2, x: 540, y: 386, w: 226, h: 64, is: 38, g: "fw", t: "ASA-2", s: "Standby", fs: 16, o: "net" });
S += `<rect x="700" y="376" width="64" height="24" rx="12" fill="#2b4fbf" stroke="#fff" stroke-width="2"/><text x="732" y="392.5" font-size="12" font-weight="800" fill="#fff" text-anchor="middle">NAT ②</text>`;
node({ ip: D.sw1, x: 288, y: 482, w: 226, h: 64, is: 38, g: "switch", t: "Core SW-1", s: "VLAN SVI · RSTP", fs: 16, o: "net" });
node({ ip: D.sw2, x: 540, y: 482, w: 226, h: 64, is: 38, g: "switch", t: "Core SW-2", s: "SPAN → Snort", fs: 16, o: "net" });
node({ ip: D.cloud, x: 288, y: 578, w: 226, h: 64, is: 38, g: "cloud", t: "Cloud 노드 ×3", s: "VLAN 20·30·40 ↔ VMnet", fs: 16, o: "net" });
node({ ip: D.snort, x: 540, y: 578, w: 226, h: 64, is: 38, g: "shield", t: "Snort IDS", s: "Ubuntu VM", fs: 16, o: "net" });
S += `<g stroke="#b5b1a8" stroke-width="2" fill="none"><path d="M149 290V176H330V140"/><path d="M450 284V140"/><path d="M560 284V140"/><path d="M514 316H540"/><path d="M401 348V386"/><path d="M653 348V386"/><path d="M514 418H540" stroke-dasharray="5 4"/><path d="M401 450V482"/><path d="M653 450V482"/><path d="M514 508H540M514 520H540" stroke="#2b4fbf" stroke-width="3.5"/><path d="M401 546V578"/><path d="M149 354V392"/></g>`;
tip_(158, 190, D.link_branch_wan, "#6b675f"); tip_(462, 200, D.link_r1, "#2b4fbf", "", 11); tip_(572, 200, D.link_r2, "#2b4fbf", "", 11);
tip_(527, 470, D.link_failover, "#2b4fbf", "middle", 11.5); tip_(296, 470, D.link_asa_sw, "#2b4fbf", "", 11.5); t(527, 566, "↔ LACP", "#2b4fbf", 11.5, 700, "middle");
S += `<text x="440" y="662" font-size="12" font-weight="600"><tspan fill="#c0392b" font-weight="800">공격</tspan><tspan fill="#6b675f"> Kali → ISP → R1 → ASA → 공지 웹</tspan><tspan fill="#c9c5bc">  │  </tspan><tspan fill="#1f8a4c" font-weight="800">방어</tspan><tspan fill="#6b675f"> ASA 차단 · Snort 탐지</tspan></text>`;
const colsX = [162, 418, 674];
[["VMnet2 ↔ VLAN 20"], ["VMnet3 ↔ VLAN 30"], ["VMnet4 ↔ VLAN 40"]].forEach(([l], i) => {
  const x = colsX[i], sl = l.replace(/(VMnet\d) ↔ (VLAN \d+)/, "$2 ↔ $1");
  S += `<rect x="${x + 14}" y="694" width="${tw(sl, 13) + 20}" height="26" rx="13" fill="#fff" stroke="#e6e3dc"/><text x="${x + 24}" y="711.5" font-size="13" font-weight="600" fill="#6b675f">${sl}</text>`;
});

S += `<g transform="translate(0,280)">`;
/* ============ VMware Linux (이준호) ============ */
zone("srv", 24, 452, 776, 360, "Linux 서버 VM", "");
tip_(248, 490, D.vlan_summary, "#0f7a5a", "", 13.5);
[[44, "관리망 · VLAN 20", D.vm_mgmt, "① 관리 서버"], [300, "서비스망 · VLAN 30", D.vm_svc, "② 서비스 서버"], [556, "서버팜 · VLAN 40", D.vm_data, "③ 데이터 서버"]].forEach(([x, l, ip, vm]) => {
  S += `<line x1="${x}" y1="544" x2="${x + 236}" y2="544" stroke="${OWN.srv.c}" stroke-opacity=".35"/><text x="${x}" y="535" font-size="14" font-weight="700" fill="${OWN.srv.c}">${l}</text>` +
    `<rect x="${x}" y="782" width="112" height="22" rx="11" fill="${tint(OWN.srv.c, 0.1)}"/><text x="${x + 56}" y="797.5" font-size="12.5" font-weight="700" fill="${OWN.srv.c}" text-anchor="middle">${vm.slice(0, 1)} <tspan font-family="${MONO}">${esc(ip)}</tspan></text>`;
});
[
  [44, 556, "term", "SSH Bastion", `${D.vm_mgmt} ${D.svc_ssh}`], [44, 632, "disk", "Ansible·백업", `${D.vm_mgmt}${D.svc_backup}`], [44, 708, "log", "로그 수집", `${D.vm_mgmt} ${D.svc_log}`],
  [300, 556, "web", "Tomcat 웹", `${D.vm_svc} ${D.svc_tomcat}`], [300, 632, "swap", "Nginx", `${D.vm_svc} ${D.svc_nginx}`], [300, 708, "mail", "메일 서버", `${D.vm_svc} ${D.svc_mail}`],
  [556, 556, "folder", "첨부파일", `${D.vm_data} ${D.svc_nfs}`], [556, 632, "db", "MariaDB", `${D.vm_data} ${D.svc_db}`], [556, 708, "file", "원본 검증", `${D.vm_data}${D.svc_hash}`],
].forEach(([x, y, g, tt, ip]) => node({ x, y, w: 236, h: 66, is: 42, g, t: tt, s: "", o: "srv", ip }));
role(530, 546, "🎯 공격 대상", "#c0392b");
flow("E", [[280, 665], [290, 665], [290, 741], [296, 741]]);
{
  const EC = FLOW.E.c;
  S += `<rect x="24" y="830" width="776" height="122" rx="18" fill="#f6fbf9" stroke="${tint(EC, 0.35)}"/><text x="44" y="857" font-size="16" font-weight="700" fill="${TXT}">📬 운영 알림 메일함 <tspan font-weight="500" fill="#7a766e" font-size="13.5">ops@ · 어디서 어떤 알림이 오나요</tspan></text>`;
  [["[Snort]", "공격 탐지", "Snort IDS → swatchdog", "GNS3 · 강민서", OWN.net.c], ["[백업]", "백업 성공·실패", "cron · Ansible 백업 스크립트", "Linux · 이준호", OWN.srv.c],
   ["[배포]", "배포 결과·롤백", "Jenkins → SNS → SQS", "CI/CD · 강찬영", OWN.cicd.c], ["[장애]", "서버 장애 알람", "CloudWatch → SNS → SQS", "AWS · 이우빈", OWN.aws.c]].forEach(([tag, tt, src, who, c], i) => {
    const x = 40 + i * 190, y = 868, w = 178;
    S += `<rect x="${x}" y="${y}" width="${w}" height="72" rx="11" fill="#fff" stroke="#e3e0d9"/><rect x="${x + 10}" y="${y + 10}" width="${tw(tag, 11.5) + 14}" height="20" rx="10" fill="${c}"/><text x="${x + 17}" y="${y + 24.2}" font-size="11.5" font-weight="800" fill="#fff">${tag}</text>` +
      `<text x="${x + 18 + tw(tag, 11.5) + 10}" y="${y + 25}" font-size="14" font-weight="700" fill="${TXT}">${tt}</text><text x="${x + 12}" y="${y + 48}" font-size="12" font-weight="500" fill="#4b5058">${src}</text><text x="${x + 12}" y="${y + 64}" font-size="11.5" font-weight="500" fill="#9a958b">${who}</text>`;
  });
}
flow("E", [[418, 830], [418, 778]], { l: "수신", lx: 448, ly: 806 });
S += `</g>`;

S += `<g transform="translate(0,160)">`;
/* ============ AWS (이우빈) ============ */
zone("aws", 840, 24, 836, 904, "AWS 클라우드", "서울 리전"); tip_(1150, 62, D.vpc, "#c45a1c", "", 13.5);
node({ x: 860, y: 104, w: 180, g: "user", t: "외부 사용자", s: "조회 · 다운로드", o: "user" });
node({ ip: D.route53, x: 1062, y: 104, w: 180, g: "globe", t: "Route 53", s: "", o: "aws" });
node({ ip: D.cloudfront, x: 1264, y: 104, w: 180, g: "bolt", t: "CloudFront", s: "", o: "aws", fs: 17 });
node({ ip: D.s3, x: 1478, y: 104, w: 178, g: "bucket", t: "S3", s: "", o: "aws" });
node({ ip: D.alb, x: 900, y: 206, w: 460, g: "swap", t: "ALB 로드밸런서", s: "", o: "aws" });
node({ x: 1478, y: 206, w: 178, g: "lock", t: "IAM · SG", s: "최소 권한", o: "aws" });
S += `<rect x="860" y="304" width="586" height="252" rx="16" fill="none" stroke="#d9d5cc" stroke-width="1" stroke-dasharray="3 4"/>`;
S += icon("box", 876, 316, 28, OWN.aws.c) + `<text x="914" y="336" font-size="17" font-weight="700" fill="${TXT}">Amazon EKS  ☸️</text>`;
t(1054, 543, "장애 시에도 유지 · ASG 교체", "#9a958b", 13, 500, "middle");
[["wA", 876, "워커 A · AZ-a", D.worker_a], ["wC", 1160, "워커 C · AZ-c", D.worker_c]].forEach(([id, x, l, ip]) => {
  S += `<rect x="${x}" y="352" width="270" height="164" rx="12" fill="#fff" stroke="#e3e0d9" stroke-width="1"/>${icon("server", x + 12, 362, 32, OWN.aws.c)}<text x="${x + 54}" y="384" font-size="16.5" font-weight="700" fill="${TXT}">${l}</text><text x="${x + 258}" y="384" font-size="12.5" font-weight="700" fill="${OWN.aws.c}" text-anchor="end" font-family="${MONO}">${ip}</text>`;
  [["Blue v1 · 운영", "#2b4fbf", "#f4f6fc"], ["Green v2 · 검증", "#1f8a4c", "#f3faf6"]].forEach(([p, s, f], i) => { const y = 404 + i * 50; S += `<rect x="${x + 12}" y="${y}" width="246" height="42" rx="11" fill="${f}"/>${icon("pods", x + 20, y + 8, 26, s)}<text x="${x + 56}" y="${y + 27}" font-size="15" font-weight="600" fill="${s}">공지 서비스 ${p}</text>`; });
});
node({ ip: D.rds, x: 860, y: 596, w: 186, g: "db", t: "RDS", s: "", o: "aws" });
node({ ip: D.redis, x: 1062, y: 596, w: 186, g: "bolt", t: "Redis", s: "", o: "aws" });
node({ ip: D.efs, x: 1264, y: 596, w: 186, g: "folder", t: "EFS", s: "", o: "aws" });
node({ x: 1478, y: 596, w: 178, g: "chart", t: "CloudWatch", s: "장애 측정 · 알람", o: "aws", fs: 16.5 });
node({ ip: D.bastion, x: 860, y: 690, w: 186, h: 70, g: "term", t: "Bastion EC2", s: "", o: "aws", fs: 17 });
S += `<rect x="1062" y="690" width="390" height="70" rx="12" fill="#fff" stroke="${tint(FLOW.B.c, 0.45)}"/><text x="1080" y="717" font-size="15" font-weight="700" fill="${FLOW.B.c}">MariaDB → RDS 이관 · 백업</text><text x="1080" y="743" font-size="13" font-weight="500" fill="#6b675f">① mysqldump ② SSH 전송 ③ mysql 복원 ④ 건수 대조</text>`;
t(862, 792, "RDS Multi-AZ는 고객 요구에 따라 선택 · 단일 AZ면 스냅샷 복원 시간 측정", "#9a958b", 13, 500);
flow("A", [[1040, 140], [1058, 140]]); flow("A", [[1242, 140], [1260, 140]]); flow("A", [[1444, 140], [1474, 140]]);
flow("A", [[1152, 176], [1152, 202]]); flow("A", [[1090, 278], [1090, 348]]); flow("A", [[1295, 278], [1295, 348]]);
flow("A", [[953, 516], [953, 592]]); flow("A", [[1155, 516], [1155, 592]]);
badge("A", 1110, 190);
flow("B", [[953, 690], [953, 672]]);
S += `</g>`;

S += `<g transform="translate(0,280)">`;
/* ============ CI/CD (강찬영) ============ */
zone("cicd", 24, 968, 1652, 180, "CI/CD 파이프라인", "무중단 블루그린 배포");
[["git", "GitHub", "코드 push"], ["gear", "Jenkins", D.jenkins_trigger], ["box", "Docker", "이미지 빌드"], ["layers", "ECR", "커밋 태그 저장"], ["play", "Ansible", "Green 배포"], ["check", "Green 검증", "글 작성·조회"], ["swap", "ALB 전환", "실패 시 롤백"]]
  .forEach(([g, tt, s], i) => tile({ x: 44 + i * 232, y: 1022, w: 200, h: 112, g, t: tt, s, o: "cicd", num: i + 1, sc: i === 6 ? "#c0392b" : null }));
for (let i = 0; i < 6; i++) flow("C", [[44 + i * 232 + 200, 1078], [44 + (i + 1) * 232 - 6, 1078]]);
S += `</g>`;

/* ============ 구역을 넘나드는 흐름 ============ */
flow("D", [[149, 392], [149, 358]]);
flow("D", [[242, 322], [264, 322], [264, 418], [284, 418]], { l: "VPN", lx: 264, ly: 372 });
flow("D", [[420, 450], [420, 478]]); flow("D", [[420, 546], [420, 574]]); flow("D", [[420, 642], [420, 728]]);
flow("D", [[420, 674], [162, 674], [162, 728]], { deny: true });
flow("D", [[420, 674], [674, 674], [674, 728]], { deny: true });
S += `<circle cx="136" cy="707" r="15" fill="#c0392b" stroke="#fff" stroke-width="3"/><path d="M130 701l12 12M142 701l-12 12" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>`;
S += `<circle cx="394" cy="707" r="15" fill="#1f8a4c" stroke="#fff" stroke-width="3"/><path d="M386.5 707l5 5 9-10" stroke="#fff" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
S += `<circle cx="648" cy="707" r="15" fill="#c0392b" stroke="#fff" stroke-width="3"/><path d="M642 701l12 12M654 701l-12 12" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>`;
badge("D", 44, 250);
flow("F", [[256, 101], [376, 101]]); flow("F", [[653, 546], [653, 574]]); flow("F", [[440, 138], [440, 280]]);
flow("F", [[380, 350], [380, 382]]); flow("F", [[380, 452], [380, 478]]); flow("F", [[380, 548], [380, 574]]); flow("F", [[380, 644], [380, 728]]);
S += `<rect x="662" y="550" width="52" height="20" rx="10" fill="#fff" stroke="#a16207"/><text x="688" y="564" font-size="12" font-weight="700" fill="#a16207" text-anchor="middle">SPAN</text>`;
badge("F", 44, 66);
role(256, 56, "⚔ 공격", "#c0392b"); role(514, 376, "🛡 방어 · 차단", "#1f8a4c"); role(766, 568, "🛡 탐지", "#1f8a4c"); role(242, 280, "🛡 차단", "#1f8a4c");
flow("B", [[792, 869], [820, 869], [820, 250], [1567, 250], [1567, 260]], { l: "첨부파일 → S3 · aws s3 sync (HTTPS)", lx: 1180, ly: 250 });
flow("B", [[792, 945], [830, 945], [830, 885], [856, 885]], { l: "덤프 SSH 전송", lx: 830, ly: 915 });
badge("B", 820, 600);
S += `<rect x="796" y="686" width="48" height="52" rx="10" fill="#fff" stroke="${FLOW.B.c}" stroke-width="1.2"/><text x="820" y="707" font-size="12" font-weight="700" fill="${FLOW.B.c}" text-anchor="middle">인터넷</text><text x="820" y="725" font-size="12" font-weight="700" fill="${FLOW.B.c}" text-anchor="middle">NAT</text>`;
flow("C", [[1636, 1358], [1686, 1358], [1686, 590], [1450, 590]], { l: "EKS 반영", lx: 1640, ly: 660 });
badge("C", 1686, 1276);
flow("E", [[1567, 828], [1567, 1180], [804, 1180]], { l: "CloudWatch 알람 → SNS → SQS ← 메일 서버가 가져감", lx: 1190, ly: 1180 });
flow("E", [[456, 1302], [456, 1224]]);
badge("E", 804, 1138);

const FONT = "Inter,Noto Sans KR,Noto Sans CJK KR,Apple SD Gothic Neo,Malgun Gothic,system-ui,sans-serif,Apple Color Emoji,Segoe UI Emoji,Noto Color Emoji";
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1710" height="1444" viewBox="0 0 1710 1444" role="img" aria-label="㈜스모크 전체 아키텍처: GNS3 본사·지사, Linux 서버 VM, AWS, CI/CD와 흐름 6개 (IP 표시)">` +
  `<title>㈜스모크 전체 아키텍처 (IP 표시)</title>` +
  `<style>.fl{fill:none;stroke-width:2.8;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:9 7;animation:run 1.1s linear infinite}@keyframes run{to{stroke-dashoffset:-32}}@media (prefers-reduced-motion:reduce){.fl{animation:none}}</style>` +
  `<g font-family="${FONT}">${S}</g></svg>\n`;
fs.writeFileSync(OUT, svg);

/* ============ ip-plan.md 자동 표 ============ */
const cell = (v) => {
  const s = String(v).replace(/\|/g, "／");
  return /^\d[\d./]*$/.test(s) ? "`" + s + "`" : s;
};
const table = (head, rows) => ["| " + head.join(" | ") + " |", "| " + head.map(() => "---").join(" | ") + " |", ...rows.map((r) => "| " + r.map(cell).join(" | ") + " |")].join("\n");
const blocks = {
  "topology-status": `> **상태: ${TOPO.status} (${TOPO.updated}).** 값을 바꿀 때는 [topology.json](topology.json)만 고쳐 PR을 올린다. 이 문서의 자동 표와 [구성도](../images/architecture.svg)는 main 병합 때 Actions가 다시 만든다.`,
  "topology-ranges": table(["구역", "대역", "용도"], TOPO.ranges),
  "topology-gns3": table(["구간", "대역", "장비 · 주소", "메모"], TOPO.gns3),
  "topology-vms": table(["VM", "주소", "서비스"], TOPO.vms),
  "topology-aws": table(["서브넷", "AZ a", "AZ c", "들어가는 것", "라우팅"], TOPO.aws),
  "topology-allow": TOPO.allow.map(([g, rows]) => `### ${g}\n\n` + table(["출발", "도착", "포트", "용도", "어디서 열기"], rows)).join("\n\n"),
};
let plan = fs.readFileSync(PLAN, "utf8");
for (const [k, body] of Object.entries(blocks)) {
  const a = `<!-- ${k}:start -->`, z = `<!-- ${k}:end -->`;
  const i = plan.indexOf(a), j = plan.indexOf(z);
  if (i < 0 || j < 0) throw new Error(`ip-plan.md에 ${k} 표시가 없음`);
  plan = plan.slice(0, i + a.length) + "\n" + body + "\n" + plan.slice(j);
}
fs.writeFileSync(PLAN, plan);
console.log("architecture.svg · ip-plan.md 갱신");
