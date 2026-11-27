<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    String pageTitle = "보안 인프라 · 클라우드 전문기업";
    String navActive = "home";

    // ---- 최신 공지 5건 (DB) ----
    List<Map<String, Object>> latest = new ArrayList<Map<String, Object>>();
    String dbError = null;
    Connection conn = null; PreparedStatement ps = null; ResultSet rs = null;
    try {
        conn = getConn();
        ps = conn.prepareStatement(
            "SELECT b.id, b.title, b.writer, b.reg_date, b.category, b.is_pinned," +
            " (SELECT COUNT(*) FROM board_file f WHERE f.board_id = b.id) AS fcnt" +
            " FROM board b WHERE b.is_check = 0 ORDER BY b.is_pinned DESC, b.id DESC LIMIT 5");
        rs = ps.executeQuery();
        while (rs.next()) {
            Map<String, Object> m = new HashMap<String, Object>();
            m.put("id", rs.getInt("id"));
            m.put("title", rs.getString("title"));
            m.put("writer", rs.getString("writer"));
            m.put("reg", rs.getTimestamp("reg_date"));
            m.put("cat", rs.getString("category"));
            m.put("pin", rs.getInt("is_pinned") == 1);
            m.put("fcnt", rs.getInt("fcnt"));
            latest.add(m);
        }
    } catch (Exception e) {
        dbError = e.getMessage();
    } finally { closeQuietly(rs, ps, conn); }

    String sent = request.getParameter("sent");
%>
<%@ include file="/WEB-INF/jspf/header.jspf" %>
<% if (!latest.isEmpty()) { Map<String, Object> t = latest.get(0); %>
<div class="ribbon"><b>새 소식</b><%= esc(t.get("title")) %><a class="more" href="<%= ctx %>/view.jsp?id=<%= t.get("id") %>">자세히 보기</a></div>
<% } %>

<!-- ============ HERO ============ -->
<section class="hero" id="top">
  <div class="wrap">
    <p class="hero-kicker rv"><%= esc(COMPANY_KO) %></p>
    <h1 class="hero-title rv">멈추지 않는<br><span class="grad">인프라.</span></h1>
    <p class="hero-sub rv">망 분리 보안부터 AWS 이전, 무중단 배포까지. <br class="pc">비즈니스가 한순간도 멈추지 않도록 설계합니다.</p>
    <div class="hero-cta rv"><a class="pill" href="#contact">상담 신청하기</a><a class="more" href="#business">더 알아보기</a></div>
  </div>
  <div class="hero-stage">
    <div class="stage-frame">
      <img src="<%= ctx %>/assets/img/hero.svg" alt="밤의 도시 위로 데이터 연결선이 이어진 일러스트">
      <div class="stage-cap">
        <div><b>본사 전산실에서 AWS 서울 리전까지.</b><span>Seoul HQ · Branch · ap-northeast-2</span></div>
        <span class="stage-live"><i></i>서비스 정상 운영 중</span>
      </div>
    </div>
  </div>
</section>

<!-- ============ STATEMENT (스크롤하면 단어가 밝아짐) ============ -->
<section class="statement" aria-label="회사 소개 문장">
  <div class="statement-in"><div class="wrap">
    <p>우리는 보이지 않는 곳에서 가장 중요한 일을 합니다. 망을 나누어 지키고, 서비스를 클라우드로 옮기고, <span class="hl">단 1초도 멈추지 않고</span> 배포합니다.</p>
  </div></div>
</section>

<!-- ============ NUMBERS ============ -->
<section class="numbers">
  <div class="wrap center">
    <p class="sec-eyebrow rv">숫자로 보는 약속</p>
    <h2 class="h2 rv">작은 팀도 감당할 수 있는,<br>큰 회사 수준의 안정성.</h2>
    <div class="num-grid">
      <div class="num rv"><b data-count="99.9" data-dec="1">99.9<em>%</em></b><span>서비스 가용성 목표</span></div>
      <div class="num rv"><b data-count="0">0<em>초</em></b><span>배포 중 서비스 중단</span></div>
      <div class="num rv"><b data-count="2">2<em>AZ</em></b><span>다중 가용영역 이중화</span></div>
      <div class="num rv"><b data-count="24">24<em>/7</em></b><span>운영 알림 · 장애 대응</span></div>
    </div>
  </div>
</section>

<!-- ============ BUSINESS (bento) ============ -->
<section class="biz" id="business">
  <div class="wrap">
    <p class="sec-eyebrow rv">사업분야</p>
    <h2 class="h2 rv">하나의 팀.<br>네 가지 전문성.</h2>
    <div class="bento">
      <article class="tile dark span-4 rv scale">
        <div class="tile-copy"><small>Network Security</small><h3>보안 네트워크 구축</h3><p>본사·지사 망 분리와 OSPF·BGP·HSRP 이중화, ASA·pfSense 방화벽과 IPsec VPN으로 내부 자산을 지킵니다.</p>
          <ul class="tile-tags"><li>VLAN 분리</li><li>ASA Failover</li><li>IPsec VPN</li><li>Snort IDS</li></ul></div>
        <div class="tile-img"><img src="<%= ctx %>/assets/img/biz-security.svg" alt="" loading="lazy"></div>
      </article>
      <article class="tile span-2 rv scale">
        <div class="tile-copy"><small>Cloud</small><h3>클라우드 마이그레이션</h3><p>VPC 설계부터 EKS·RDS·S3까지, 서울 리전으로 안전하게.</p></div>
        <div class="tile-img"><img src="<%= ctx %>/assets/img/biz-cloud.svg" alt="" loading="lazy"></div>
      </article>
      <article class="tile span-3 rv scale">
        <div class="tile-copy"><small>CI/CD</small><h3>무중단 배포</h3><p>Jenkins·Docker·ECR·Ansible 파이프라인과 블루그린 전환으로 다운타임 없이 릴리스합니다.</p>
          <ul class="tile-tags"><li>Jenkins</li><li>Docker · ECR</li><li>Blue / Green</li></ul></div>
        <div class="tile-img"><img src="<%= ctx %>/assets/img/biz-deploy.svg" alt="" loading="lazy"></div>
      </article>
      <article class="tile dark span-3 rv scale">
        <div class="tile-copy"><small>Operations</small><h3>운영 모니터링 · 알림</h3><p>보안 탐지, 백업 결과, CloudWatch 장애 알람을 사내 메일 한 곳으로 모아 즉시 대응합니다.</p>
          <ul class="tile-tags"><li>Postfix · Dovecot</li><li>CloudWatch</li><li>Grafana</li></ul></div>
        <div class="tile-img"><img src="<%= ctx %>/assets/img/biz-monitor.svg" alt="" loading="lazy"></div>
      </article>
    </div>
  </div>
</section>

<!-- ============ PROCESS (세로 스크롤 → 가로 이동) ============ -->
<section class="process" id="process">
  <div class="process-pin">
    <div class="wrap process-head">
      <div><p class="sec-eyebrow">작동 방식</p><h2 class="h2">서비스가 클라우드로<br>가는 길.</h2></div>
      <div class="process-bar" aria-hidden="true"><i></i></div>
    </div>
    <div class="track">
      <article class="step"><img src="<%= ctx %>/assets/img/biz-security.svg" alt="" loading="lazy"><div class="step-copy"><small>Step 1</small><h3>진단하고, 나눕니다.</h3><p>비정상 접근 흔적을 점검하고 업무·관리·서비스·데이터망을 VLAN으로 분리합니다.</p></div></article>
      <article class="step"><img src="<%= ctx %>/assets/img/biz-cloud.svg" alt="" loading="lazy"><div class="step-copy"><small>Step 2</small><h3>하나도 잃지 않고 옮깁니다.</h3><p>DB 덤프와 첨부파일을 RDS·S3로 이관하고, 건수와 SHA-256 해시로 검증합니다.</p></div></article>
      <article class="step"><img src="<%= ctx %>/assets/img/biz-deploy.svg" alt="" loading="lazy"><div class="step-copy"><small>Step 3</small><h3>멈추지 않고 배포합니다.</h3><p>Green 버전이 헬스체크를 통과해야만 트래픽을 넘기고, 실패하면 자동으로 되돌립니다.</p></div></article>
      <article class="step"><img src="<%= ctx %>/assets/img/biz-monitor.svg" alt="" loading="lazy"><div class="step-copy"><small>Step 4</small><h3>메일 한 통으로 알아챕니다.</h3><p>장애·탐지·백업 알림이 운영 메일함으로 모여, 소규모 팀도 바로 대응합니다.</p></div></article>
    </div>
  </div>
</section>

<!-- ============ INFRA (dark) ============ -->
<section class="infra" id="infra">
  <div class="wrap">
    <p class="sec-eyebrow rv">인프라</p>
    <h2 class="h2 rv">온프레미스와 클라우드.<br>하나의 흐름으로.</h2>
    <p class="sec-desc rv">사내 업무는 망 분리된 본사 전산실에서, 대외 공지·자료 서비스는 AWS에서. 두 환경은 검증된 이관 경로와 운영 알림으로 이어집니다.</p>
    <div class="diagram" role="img" aria-label="온프레미스 본사·지사 네트워크와 AWS 클라우드 구성도">
      <svg viewBox="0 0 1200 610" class="arch">
        <!-- panels -->
        <rect class="pnl" x="20" y="30" width="500" height="460" rx="18"/>
        <text class="pnl-k" x="44" y="62">ON-PREMISE</text><text class="pnl-t" x="44" y="84">본사 · 지사 전산망</text>
        <rect class="pnl aws" x="680" y="30" width="500" height="460" rx="18"/>
        <text class="pnl-k" x="704" y="62">AWS · ap-northeast-2</text><text class="pnl-t" x="704" y="84">대외 공지 · 자료 서비스</text>

        <!-- links -->
        <g class="lk">
          <path d="M194 131 H330" class="flow"/>
          <path d="M405 158 V196"/><path d="M405 250 V288"/>
          <path d="M405 342 V372 M114 372 H418 M114 372 V400 M266 372 V400 M418 372 V400"/>
          <path d="M330 315 H260 Q240 315 240 295 V250" class="dash"/>
          <path d="M480 131 H566" class="flow"/><path d="M634 131 H704" class="flow"/>
          <path d="M774 158 V196" class="flow"/><path d="M774 250 V288" class="flow"/>
          <path d="M774 342 V400"/><path d="M860 342 V371 H930 V400"/>
          <path d="M1086 158 V196"/>
          <path d="M1016 315 H884" class="dash"/>
          <path d="M844 131 H1016" class="dash"/>
        </g>
        <g class="lk mig"><path d="M418 454 V548 H774 V454" class="flow"/></g>
        <g class="lk alert"><path d="M1086 454 V584 H266 V454" class="flow"/></g>
        <g class="lbl">
          <rect x="452" y="536" width="290" height="24" rx="12"/><text x="597" y="552">DB 덤프 · 첨부파일 이관 · SHA-256 검증</text>
          <rect x="544" y="572" width="226" height="24" rx="12" class="al"/><text x="657" y="588">CloudWatch → SNS → 운영 알림 메일</text>
          <text x="262" y="122" class="sm">IPsec VPN</text>
        </g>

        <!-- internet -->
        <g class="inet"><circle cx="600" cy="131" r="34"/><text x="600" y="127">INTERNET</text><text x="600" y="143" class="s">고객 · 외부 사용자</text></g>

        <!-- on-prem nodes -->
        <g class="nd" transform="translate(44 104)"><rect width="150" height="54" rx="10"/><text x="14" y="23" class="t">지사 pfSense</text><text x="14" y="41" class="s">방화벽 · VPN 출발지</text></g>
        <g class="nd" transform="translate(330 104)"><rect width="150" height="54" rx="10"/><text x="14" y="23" class="t">Edge R1 · R2</text><text x="14" y="41" class="s">BGP · HSRP 이중화</text></g>
        <g class="nd" transform="translate(330 196)"><rect width="150" height="54" rx="10"/><text x="14" y="23" class="t">ASA 방화벽</text><text x="14" y="41" class="s">Active / Standby</text></g>
        <g class="nd" transform="translate(166 196)"><rect width="150" height="54" rx="10"/><text x="14" y="23" class="t">Snort IDS</text><text x="14" y="41" class="s">SPAN 미러링 탐지</text></g>
        <g class="nd" transform="translate(330 288)"><rect width="150" height="54" rx="10"/><text x="14" y="23" class="t">Core SW ×2</text><text x="14" y="41" class="s">VLAN 10·20·30·40</text></g>
        <g class="nd" transform="translate(44 400)"><rect width="140" height="54" rx="10"/><text x="12" y="23" class="t">관리 VLAN 20</text><text x="12" y="41" class="s">Bastion · 백업 · 로그</text></g>
        <g class="nd hl" transform="translate(196 400)"><rect width="140" height="54" rx="10"/><text x="12" y="23" class="t">서비스 VLAN 30</text><text x="12" y="41" class="s">Tomcat · Mail</text></g>
        <g class="nd" transform="translate(348 400)"><rect width="140" height="54" rx="10"/><text x="12" y="23" class="t">데이터 VLAN 40</text><text x="12" y="41" class="s">MariaDB · NFS</text></g>

        <!-- aws nodes -->
        <g class="nd" transform="translate(704 104)"><rect width="140" height="54" rx="10"/><text x="14" y="23" class="t">Route 53</text><text x="14" y="41" class="s">notice · files 도메인</text></g>
        <g class="nd" transform="translate(1016 104)"><rect width="140" height="54" rx="10"/><text x="14" y="23" class="t">CloudFront</text><text x="14" y="41" class="s">첨부파일 캐시</text></g>
        <g class="nd" transform="translate(704 196)"><rect width="140" height="54" rx="10"/><text x="14" y="23" class="t">ALB</text><text x="14" y="41" class="s">HTTPS · 헬스체크</text></g>
        <g class="nd" transform="translate(1016 196)"><rect width="140" height="54" rx="10"/><text x="14" y="23" class="t">S3</text><text x="14" y="41" class="s">첨부파일 원본</text></g>
        <g class="nd hl" transform="translate(704 288)"><rect width="180" height="54" rx="10"/><text x="14" y="23" class="t">EKS 클러스터</text><text x="14" y="41" class="s">Blue v1 ⇄ Green v2</text></g>
        <g class="nd" transform="translate(1016 288)"><rect width="140" height="54" rx="10"/><text x="14" y="23" class="t">Jenkins → ECR</text><text x="14" y="41" class="s">빌드 · 이미지 배포</text></g>
        <g class="nd" transform="translate(704 400)"><rect width="140" height="54" rx="10"/><text x="14" y="23" class="t">RDS MariaDB</text><text x="14" y="41" class="s">게시판 데이터</text></g>
        <g class="nd" transform="translate(860 400)"><rect width="140" height="54" rx="10"/><text x="14" y="23" class="t">ElastiCache</text><text x="14" y="41" class="s">세션 · 캐시</text></g>
        <g class="nd" transform="translate(1016 400)"><rect width="140" height="54" rx="10"/><text x="14" y="23" class="t">CloudWatch</text><text x="14" y="41" class="s">장애 알람</text></g>
      </svg>
    </div>
    <div class="infra-pts">
      <div class="rv"><b>망 분리</b><p>업무·관리·서비스·데이터를 VLAN으로 나누고 필요한 포트만 엽니다.</p></div>
      <div class="rv"><b>무중단 전환</b><p>ALB 헬스체크를 통과한 버전으로만 트래픽을 넘깁니다.</p></div>
      <div class="rv"><b>무결성 이관</b><p>게시글 건수와 해시를 이관 전후로 비교합니다.</p></div>
      <div class="rv"><b>하나의 알림 창구</b><p>탐지·백업·장애 알림이 사내 메일로 모입니다.</p></div>
    </div>
  </div>
</section>

<!-- ============ ABOUT ============ -->
<section class="about" id="about">
  <div class="wrap about-grid">
    <figure class="about-img rv"><img src="<%= ctx %>/assets/img/about.svg" alt="유리 외벽의 고층 사옥 일러스트" loading="lazy"></figure>
    <div>
      <p class="sec-eyebrow rv">회사소개</p>
      <h2 class="h2 rv">기술은 복잡하게.<br>경험은 단순하게.</h2>
      <p class="sec-desc rv">한 대의 서버에 몰려 있던 업무와 대외 서비스, 배포할 때마다 멈추던 홈페이지. <%= esc(COMPANY_KO) %>는 이런 문제를 지키고, 옮기고, 끊김 없이 배포하는 구조로 바꿉니다.</p>
      <ul class="values">
        <li class="rv"><b>Security First</b><p>다층 방어를 처음부터 기본값으로 설계합니다.</p></li>
        <li class="rv"><b>Zero Downtime</b><p>새 버전을 올리는 순간에도 고객은 그대로 이용합니다.</p></li>
        <li class="rv"><b>Data Integrity</b><p>단 하나의 공지, 단 하나의 첨부파일도 잃지 않습니다.</p></li>
      </ul>
    </div>
  </div>
</section>

<!-- ============ NEWS (DB) ============ -->
<section class="news" id="news">
  <div class="wrap">
    <div class="news-head">
      <div><p class="sec-eyebrow rv">공지 · 자료실</p><h2 class="h2 rv">최신 소식.</h2></div>
      <a class="more rv" href="<%= ctx %>/notice.jsp">전체 보기</a>
    </div>
    <div class="news-list rv" id="newsList">
      <% if (dbError != null) { %>
        <div class="db-alert"><b>데이터베이스에 연결할 수 없습니다.</b><span>DB_URL 설정과 MariaDB 상태를 확인해 주세요.</span><code><%= esc(dbError) %></code></div>
      <% } else if (latest.isEmpty()) { %>
        <div class="empty-box">아직 등록된 공지가 없습니다.<a href="<%= ctx %>/write.jsp">첫 공지 작성하기</a></div>
      <% } else { for (Map<String, Object> m : latest) { String cat = (String) m.get("cat"); %>
        <a class="news-item" href="<%= ctx %>/view.jsp?id=<%= m.get("id") %>">
          <span class="badge <%= catClass(cat) %>"><%= esc(cat) %></span>
          <span class="news-title"><% if ((Boolean) m.get("pin")) { %><i class="pin">중요</i><% } %><%= esc(m.get("title")) %><% if ((Integer) m.get("fcnt") > 0) { %><svg class="clip" viewBox="0 0 24 24" aria-label="첨부파일"><path d="M21 11.5l-8.6 8.6a5.5 5.5 0 01-7.8-7.8l9.2-9.2a3.7 3.7 0 015.2 5.2l-9.2 9.2a1.8 1.8 0 01-2.6-2.6l8.5-8.5"/></svg><% } %><% if (isNew((Timestamp) m.get("reg"))) { %><i class="new">N</i><% } %></span>
          <span class="news-date"><%= fmt((Timestamp) m.get("reg"), "yyyy.MM.dd") %></span>
          <span class="news-arrow" aria-hidden="true">›</span>
        </a>
      <% } } %>
    </div>
  </div>
</section>

<!-- ============ CONTACT (DB) ============ -->
<section class="contact" id="contact">
  <div class="wrap contact-grid">
    <div>
      <p class="sec-eyebrow rv">문의하기</p>
      <h2 class="h2 rv">이야기를<br>시작해 볼까요.</h2>
      <p class="sec-desc rv">인프라 진단, 보안 점검, 클라우드 이전 상담까지. 남겨 주신 문의는 담당자가 확인 후 회신드립니다.</p>
      <dl class="info-list rv">
        <div><dt>주소</dt><dd><%= esc(COMPANY_ADDR) %></dd></div>
        <div><dt>전화</dt><dd><%= esc(COMPANY_TEL) %></dd></div>
        <div><dt>이메일</dt><dd><%= esc(COMPANY_MAIL) %></dd></div>
        <div><dt>운영 시간</dt><dd>평일 09:00 – 18:00 · 장애 대응 24/7</dd></div>
      </dl>
    </div>
    <form class="contact-form rv" id="contactForm" action="<%= ctx %>/contact_process.jsp" method="post">
      <% if ("1".equals(sent)) { %><div class="form-ok" role="status">문의가 접수되었습니다. 빠르게 회신드리겠습니다.</div><% } %>
      <% if ("0".equals(sent)) { %><div class="form-err" role="alert">접수 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.</div><% } %>
      <div class="f-row two">
        <label><span>회사명</span><input id="c-company" type="text" name="company" maxlength="100" placeholder="회사명"></label>
        <label><span>담당자 <i>*</i></span><input id="c-name" type="text" name="name" maxlength="50" required placeholder="이름"></label>
      </div>
      <div class="f-row two">
        <label><span>이메일 <i>*</i></span><input id="c-email" type="email" name="email" maxlength="120" required placeholder="name@company.com"></label>
        <label><span>연락처</span><input id="c-phone" type="tel" name="phone" maxlength="40" placeholder="010-0000-0000"></label>
      </div>
      <div class="f-row">
        <span class="f-lbl">문의 분야</span>
        <div class="chips">
          <label><input type="radio" name="topic" value="보안 네트워크" checked><span>보안 네트워크</span></label>
          <label><input type="radio" name="topic" value="클라우드 이전"><span>클라우드 이전</span></label>
          <label><input type="radio" name="topic" value="CI/CD"><span>CI/CD</span></label>
          <label><input type="radio" name="topic" value="운영 · 기타"><span>운영 · 기타</span></label>
        </div>
      </div>
      <div class="f-row"><label><span>문의 내용 <i>*</i></span><textarea id="c-msg" name="message" rows="5" maxlength="4000" required placeholder="현재 환경과 고민을 편하게 적어 주세요."></textarea></label></div>
      <button type="submit" class="pill full">문의 보내기</button>
    </form>
  </div>
</section>

<%@ include file="/WEB-INF/jspf/footer.jspf" %>
