(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };

  /* 모바일 메뉴 */
  var burger = document.getElementById('burger');
  var menu = document.getElementById('menu');
  if (burger && menu) {
    var close = function () { menu.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); document.body.style.overflow = ''; };
    burger.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });
    menu.addEventListener('click', function (e) { if (e.target.tagName === 'A') close(); });
  }

  /* 화면에 들어오면 부드럽게 등장 (.rv) · 구성도 노드 순차 등장 (.diagram) */
  var revealables = document.querySelectorAll('.rv, .diagram');
  if (!('IntersectionObserver' in window) || reduce) {
    revealables.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        if (el.classList.contains('diagram')) {
          el.querySelectorAll('.nd').forEach(function (n, i) { n.style.transitionDelay = (i * 60) + 'ms'; });
        } else {
          var sibs = Array.prototype.filter.call(el.parentNode.children, function (c) { return c.classList.contains('rv'); });
          el.style.transitionDelay = Math.min(sibs.indexOf(el), 4) * 110 + 'ms';
        }
        el.classList.add('in');
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* 숫자 카운트업 */
  var nums = document.querySelectorAll('[data-count]');
  function countUp(el) {
    var to = parseFloat(el.getAttribute('data-count'));
    var dec = parseInt(el.getAttribute('data-dec') || '0', 10);
    var unit = el.querySelector('em');
    var unitHtml = unit ? unit.outerHTML : '';
    if (reduce || to === 0) return;
    var t0 = null, dur = 1800;
    function step(t) {
      if (!t0) t0 = t;
      var p = Math.min(1, (t - t0) / dur);
      var e = 1 - Math.pow(1 - p, 4);
      el.innerHTML = (to * e).toFixed(dec) + unitHtml;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { countUp(en.target); cio.unobserve(en.target); } });
    }, { threshold: 0.5 });
    nums.forEach(function (el) { cio.observe(el); });
  }

  /* 문장 단어 단위로 쪼개기 (스크롤하면 한 단어씩 밝아짐) */
  var statement = document.querySelector('.statement p');
  var words = [];
  if (statement) {
    var html = '';
    statement.childNodes.forEach(function (node) {
      var hl = node.nodeType === 1 && node.classList.contains('hl');
      var text = node.textContent;
      text.split(/(\s+)/).forEach(function (w) {
        if (!w) return;
        if (/^\s+$/.test(w)) { html += ' '; return; }
        html += '<span class="w' + (hl ? ' hl' : '') + '">' + w.replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }) + '</span>';
      });
    });
    statement.innerHTML = html;
    words = statement.querySelectorAll('.w');
  }

  /* ----------------------------------------------------------------
     스크롤 연동 애니메이션 (requestAnimationFrame 한 번에 처리)
     ---------------------------------------------------------------- */
  var frame = document.querySelector('.stage-frame');
  var frameImg = frame && frame.querySelector('img');
  var statementSec = document.querySelector('.statement');
  var process = document.querySelector('.process');
  var track = document.querySelector('.track');
  var bar = document.querySelector('.process-bar i');
  var aboutImg = document.querySelector('.about-img img');

  function progress(el) {           // 섹션이 화면을 지나가는 정도 0 → 1
    var r = el.getBoundingClientRect();
    var total = r.height - window.innerHeight;
    return total <= 0 ? 0 : clamp(-r.top / total, 0, 1);
  }

  var gnb = document.getElementById('gnb');
  var darkSecs = document.querySelectorAll('.statement, .infra');
  var ticking = false;
  function update() {
    ticking = false;
    var vh = window.innerHeight;

    // 0) 어두운 섹션 위에서는 내비게이션도 어둡게
    if (gnb) {
      var y = gnb.offsetHeight / 2, dark = false;
      for (var d = 0; d < darkSecs.length; d++) {
        var dr = darkSecs[d].getBoundingClientRect();
        if (dr.height && dr.top <= y && dr.bottom >= y) { dark = true; break; }
      }
      gnb.classList.toggle('dark', dark);
    }

    // 1) 히어로 이미지: 둥근 카드 → 화면 가득
    if (frame) {
      var fr = frame.parentNode.getBoundingClientRect();
      var p = clamp((vh - fr.top) / (vh * 1.1), 0, 1);
      var vw = document.documentElement.clientWidth;
      var ins0 = Math.max(22, vw * .06);
      var ins = ins0 * (1 - p), rad = (vw < 640 ? 22 : 34) * (1 - p);
      frame.style.setProperty('--ins', ins.toFixed(1) + 'px');
      frame.style.setProperty('--rad', rad.toFixed(1) + 'px');
      if (frameImg) frameImg.style.transform = 'scale(' + (1.12 - .12 * p).toFixed(4) + ')';
    }

    // 2) 문장: 스크롤한 만큼 단어가 밝아짐
    if (statementSec && words.length) {
      var sp = progress(statementSec);
      var lit = Math.round(clamp(sp * 1.25, 0, 1) * words.length);
      for (var i = 0; i < words.length; i++) words[i].classList.toggle('lit', i < lit);
    }

    // 3) 작동 방식: 세로 스크롤 → 가로로 카드 이동
    if (process && track && window.innerWidth > 833) {
      var pp = progress(process);
      var dist = track.scrollWidth - document.documentElement.clientWidth;
      track.style.transform = 'translate3d(' + (-Math.max(0, dist) * pp).toFixed(1) + 'px,0,0)';
      if (bar) bar.style.width = (pp * 100).toFixed(1) + '%';
    }

    // 4) 회사소개 이미지 패럴랙스
    if (aboutImg) {
      var ar = aboutImg.parentNode.getBoundingClientRect();
      var ap = clamp((vh - ar.top) / (vh + ar.height), 0, 1);
      aboutImg.style.transform = 'translate3d(0,' + (-13 * ap).toFixed(2) + '%,0)';
    }
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }

  if (!reduce) {
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    update();
  } else {
    words.forEach && words.forEach(function (w) { w.classList.add('lit'); });
  }
  window.__siteUpdate = update;

  /* 첨부파일 선택 목록 */
  var input = document.getElementById('fileInput');
  var drop = document.getElementById('drop');
  var list = document.getElementById('dropList');
  if (input && list) {
    var size = function (n) { return n < 1048576 ? (n / 1024).toFixed(1) + ' KB' : (n / 1048576).toFixed(1) + ' MB'; };
    input.addEventListener('change', function () {
      list.innerHTML = '';
      Array.prototype.forEach.call(input.files, function (f) {
        var li = document.createElement('li');
        var name = document.createElement('b'); name.textContent = f.name; name.style.fontWeight = '500';
        var s = document.createElement('span'); s.textContent = size(f.size);
        if (f.size > 20 * 1048576) { s.textContent += ' · 20MB 초과'; s.style.color = '#d70015'; }
        li.appendChild(name); li.appendChild(s); list.appendChild(li);
      });
      if (input.files.length > 5) {
        var w = document.createElement('li'); w.textContent = '파일은 최대 5개까지 올릴 수 있어요.'; w.style.color = '#d70015'; list.appendChild(w);
      }
    });
    ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function () { drop.classList.add('over'); }); });
    ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function () { drop.classList.remove('over'); }); });
  }
})();
