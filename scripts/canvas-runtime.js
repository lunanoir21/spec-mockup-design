/* canvas-runtime: turns any page whose boards carry [data-board] into a pan/zoom infinite canvas.
 * Injected inline by new-canvas.py / canvasify.py. No dependencies. Never needed by Claude's own Design canvas.
 * Gestures: drag background = pan, wheel = pan (or zoom, toggle), ctrl/cmd+wheel or pinch = zoom,
 * double-click background = fit all, F / expand button = focus a board, Esc = back, arrows = next/prev board in focus,
 * 0 = fit all, 1 = 100%, + / - = zoom, download button = board as standalone HTML.
 * URL: ?only=<id> single board (used by shoot.sh) · ?flat=1 classic scroll page · #<id> opens focused on a board.
 */
(function () {
  if (window.__canvasRuntime) return;
  window.__canvasRuntime = true;
  var doc = document, root = doc.documentElement, body = doc.body;
  var q = new URLSearchParams(location.search);
  var all = [].slice.call(doc.querySelectorAll('[data-board]')).filter(function (b) { return !b.parentElement.closest('[data-board]'); });
  if (!all.length) return;
  var SKIP = /^(SCRIPT|STYLE|LINK|META|TITLE|TEMPLATE)$/;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- ?only=<id>: show one board, nothing else (screenshots) ---------- */
  var only = q.get('only');
  if (only) {
    var target = all.filter(function (b) { return b.dataset.board === only; })[0];
    if (target) {
      all.forEach(function (b) { if (b !== target) b.style.display = 'none'; });
      for (var n = target; n && n !== body; n = n.parentElement) {
        [].forEach.call(n.parentElement.children, function (s) { if (s !== n && !SKIP.test(s.tagName)) s.style.display = 'none'; });
      }
      root.dataset.cv = 'only';
    }
    return;
  }
  if (q.get('flat')) { root.dataset.cv = 'flat'; return; }

  /* ---------- structure: world = lowest common ancestor of the boards ---------- */
  function lca(els) {
    var a = els[0].parentElement;
    while (a && !els.every(function (e) { return a.contains(e); })) a = a.parentElement;
    return a;
  }
  var A = lca(all);
  if (!A || A === body || A === root) {
    A = doc.createElement('div');
    all[0].parentElement.insertBefore(A, all[0]);
    all.forEach(function (b) { A.appendChild(b); });
  }
  var cs0 = getComputedStyle(body), pageBg = cs0.backgroundColor, pageFg = cs0.color;
  var pageBgOrig = pageBg;
  if (/rgba\(0, 0, 0, 0\)|transparent/.test(pageBgOrig)) pageBgOrig = getComputedStyle(root).backgroundColor;
  if (/rgba\(0, 0, 0, 0\)|transparent/.test(pageBgOrig)) pageBgOrig = '#ffffff';
  pageBg = '#0f1211'; pageFg = 'rgb(214, 220, 217)';

  var chain = [];
  for (var c = A; c && c !== body; c = c.parentElement) chain.push(c);
  var chrome = [];
  chain.forEach(function (nd) {
    [].forEach.call(nd.parentElement.children, function (s) {
      if (s !== nd && chain.indexOf(s) < 0 && !SKIP.test(s.tagName) && chrome.indexOf(s) < 0) chrome.push(s);
    });
  });

  /* ---------- CSS ---------- */
  var css = [
    'html.cv,html.cv body{margin:0!important;padding:0!important;height:100%!important;overflow:hidden!important;overscroll-behavior:none;background:' + pageBg + '!important;touch-action:none}',
    '.cv-anc{position:fixed!important;inset:0!important;width:auto!important;height:auto!important;max-width:none!important;max-height:none!important;margin:0!important;padding:0!important;overflow:hidden!important;border:0!important;background:transparent!important;transform:none!important;display:block!important}',
    '.cv-world{position:absolute!important;left:0!important;top:0!important;margin:0!important;padding:48px!important;max-width:none!important;transform-origin:0 0;will-change:transform;box-sizing:content-box!important}',
    '.cv-world.cv-anim{transition:transform .26s cubic-bezier(.2,.8,.2,1)}',
    '.cv-world>*{max-width:none}',
    '.cv-board-head{display:flex;align-items:center;gap:8px}',
    '.cv-tools{margin-left:auto;display:inline-flex;gap:4px}',
    '.cv-btn{all:unset;box-sizing:border-box;display:inline-grid;place-items:center;width:28px;height:28px;border-radius:7px;cursor:pointer;opacity:.7;color:inherit}',
    '.cv-btn:hover,.cv-btn:focus-visible{opacity:1;background:rgba(127,127,127,.22)}',
    '.cv-btn svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}',
    '.cv-meta,.cv-meta *{color:#aab3af!important}.cv-meta b,.cv-meta strong,.cv-board-head b{color:#e6ebe8!important}.cv-meta code{background:rgba(255,255,255,.08)!important}',
    '.cv-art{transform:translateZ(0);box-shadow:0 8px 40px rgba(0,0,0,.45)!important;border-color:rgba(255,255,255,.08)!important}',
    'body.cv-focus [data-board]:not(.cv-on){opacity:.18;transition:opacity .2s}',
    '[data-board]{transition:opacity .2s}',
    '#cv-hud{position:fixed;left:12px;top:12px;z-index:30;max-width:min(420px,calc(100vw - 24px));max-height:calc(100vh - 90px);overflow:auto;box-sizing:border-box;padding:12px 14px;border-radius:12px;border:1px solid rgba(127,127,127,.35);background:' + pageBg + ';color:' + pageFg + ';font:13px/1.5 system-ui,sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.25)}',
    '#cv-hud.cv-min{padding:6px 10px;cursor:pointer}#cv-hud.cv-min>*:not(.cv-hud-t){display:none!important}',
    '#cv-hud,#cv-hud *{color:#d6dcd9!important}#cv-hud a{text-decoration:none}#cv-hud button{border-color:#3a4240!important}#cv-hud h1{font-size:16px!important;margin:0 0 4px!important}#cv-hud .cv-hud-t{display:flex;align-items:center;gap:8px;margin:0 0 6px;font-weight:600;font-size:12px;opacity:.8}#cv-hud.cv-min .cv-hud-t{margin:0}',
    '#cv-hud>*{margin-inline:0!important;max-width:none!important}',
    '#cv-bar{position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:31;display:flex;align-items:center;gap:2px;padding:4px;border-radius:12px;background:rgba(18,20,19,.94);color:#e6e9e7;border:1px solid #2d3331;font:12px system-ui,sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.35)}',
    '#cv-bar .cv-btn{width:32px;height:32px;opacity:.9}#cv-bar .cv-zoom{min-width:48px;text-align:center;font-variant-numeric:tabular-nums;opacity:.85}',
    '#cv-bar .cv-txt{all:unset;box-sizing:border-box;padding:0 10px;height:32px;line-height:32px;border-radius:7px;cursor:pointer;opacity:.9;font:12px/32px system-ui,sans-serif}#cv-bar .cv-txt:hover,#cv-bar .cv-txt:focus-visible{background:rgba(255,255,255,.12)}',
    '#cv-bar .cv-sep{width:1px;height:18px;background:#2d3331;margin:0 4px}',
    '#cv-list{position:fixed;left:50%;bottom:62px;transform:translateX(-50%);z-index:32;max-height:50vh;width:min(360px,calc(100vw - 24px));overflow:auto;padding:6px;border-radius:12px;background:rgba(18,20,19,.97);color:#e6e9e7;border:1px solid #2d3331;font:13px system-ui,sans-serif;box-shadow:0 10px 30px rgba(0,0,0,.4)}',
    '#cv-list button{all:unset;box-sizing:border-box;display:flex;width:100%;gap:10px;padding:7px 10px;border-radius:7px;cursor:pointer}#cv-list button:hover,#cv-list button:focus-visible{background:rgba(255,255,255,.12)}#cv-list small{margin-left:auto;opacity:.55;font-variant-numeric:tabular-nums}',
    '#cv-hint{position:fixed;right:12px;bottom:14px;z-index:30;font:11px system-ui,sans-serif;color:' + pageFg + ';opacity:.5;max-width:40vw;text-align:right}',
    '@media (max-width:640px){#cv-hint{display:none}}',
    'html.cv-bare #cv-hud,html.cv-bare #cv-bar,html.cv-bare #cv-hint{display:none!important}'
  ].join('\n');
  var st = doc.createElement('style'); st.id = 'cv-runtime-style'; st.textContent = css; doc.head.appendChild(st);

  root.classList.add('cv'); if (q.get('bare')) root.classList.add('cv-bare');
  chain.forEach(function (nd, i) { nd.classList.add(i === 0 ? 'cv-world' : 'cv-anc'); });
  if (!all.length) return;
  if (getComputedStyle(A).display === 'block') { A.style.display = 'flex'; A.style.flexWrap = 'wrap'; A.style.alignItems = 'flex-start'; A.style.gap = '56px 40px'; }
  var area = 0;
  all.forEach(function (b) { var r = b.getBoundingClientRect(); area += (r.width + 40) * (r.height + 80); });
  var W = Math.max(1400, Math.round(Math.sqrt(area * (innerWidth / Math.max(400, innerHeight))) * 1.08));
  A.style.width = W + 'px';

  /* ---------- HUD (page chrome moved here), toolbar ---------- */
  var hud = doc.createElement('div'); hud.id = 'cv-hud';
  var hudT = doc.createElement('div'); hudT.className = 'cv-hud-t'; hudT.innerHTML = '<span>Canvas · ' + all.length + ' tahta</span><span style="margin-left:auto;opacity:.6">▾</span>';
  hud.appendChild(hudT); chrome.forEach(function (s) { hud.appendChild(s); });
  hudT.addEventListener('click', function () { hud.classList.toggle('cv-min'); });
  body.appendChild(hud);
  hud.classList.add('cv-min');

  var ICON = {
    expand: '<svg viewBox="0 0 16 16"><path d="M9.5 2.5h4v4M6.5 13.5h-4v-4M13.5 2.5 9 7M2.5 13.5 7 9"/></svg>',
    dl: '<svg viewBox="0 0 16 16"><path d="M8 2.5v7.5M4.8 7 8 10.2 11.2 7M3 13.5h10"/></svg>',
    minus: '<svg viewBox="0 0 16 16"><path d="M3.5 8h9"/></svg>',
    plus: '<svg viewBox="0 0 16 16"><path d="M3.5 8h9M8 3.5v9"/></svg>',
    fit: '<svg viewBox="0 0 16 16"><path d="M2.5 6V2.5H6M10 2.5h3.5V6M13.5 10v3.5H10M6 13.5H2.5V10"/></svg>'
  };
  var bar = doc.createElement('div'); bar.id = 'cv-bar'; bar.setAttribute('role', 'toolbar'); bar.setAttribute('aria-label', 'Canvas');
  bar.innerHTML = '<button class="cv-btn" data-a="out" title="Uzaklaştır (-)">' + ICON.minus + '</button><span class="cv-zoom" id="cv-z">100%</span><button class="cv-btn" data-a="in" title="Yakınlaştır (+)">' + ICON.plus + '</button><span class="cv-sep"></span><button class="cv-btn" data-a="fit" title="Hepsini sığdır (0)">' + ICON.fit + '</button><button class="cv-txt" data-a="one" title="%100 (1)">1:1</button><span class="cv-sep"></span><button class="cv-txt" data-a="list" title="Tahtalar">Tahtalar</button><button class="cv-txt" data-a="wheel" title="Tekerlek davranışı">Tekerlek: kaydır</button>';
  body.appendChild(bar);
  var hint = doc.createElement('div'); hint.id = 'cv-hint'; hint.textContent = 'Sürükle: gez · Ctrl+tekerlek / sıkıştır: yakınlaştır · çift tık: hepsi · F: odakla';
  body.appendChild(hint);
  var list = null;

  /* ---------- boards: header + tools ---------- */
  all.forEach(function (b) {
    var big = null, ba = 0;
    [].forEach.call(b.children, function (c) { var r = c.getBoundingClientRect(), a = r.width * r.height; if (a > ba) { ba = a; big = c; } });
    [].forEach.call(b.children, function (c) { c.classList.add(c === big ? 'cv-art' : 'cv-meta'); });
  });
  function titleOf(b) {
    if (b.dataset.title) return b.dataset.title;
    var h = b.querySelector(':scope > header b, :scope > header, :scope > h2, :scope > h3');
    return (h && h.textContent.trim().split('\n')[0].slice(0, 60)) || b.dataset.board;
  }
  all.forEach(function (b) {
    var h = b.querySelector(':scope > header');
    if (!h) { h = doc.createElement('header'); h.textContent = titleOf(b); h.style.cssText = 'font:600 13px system-ui,sans-serif;margin-bottom:8px'; b.insertBefore(h, b.firstChild); }
    h.classList.add('cv-board-head');
    var t = doc.createElement('span'); t.className = 'cv-tools';
    t.innerHTML = '<button class="cv-btn" data-a="focus" title="Genişlet (F)" aria-label="Genişlet">' + ICON.expand + '</button><button class="cv-btn" data-a="dl" title="Tahtayı HTML olarak indir" aria-label="İndir">' + ICON.dl + '</button>';
    h.appendChild(t);
    h.addEventListener('dblclick', function (e) { if (!e.target.closest('.cv-btn')) focusBoard(b); });
  });

  /* ---------- view math ---------- */
  var v = { x: 0, y: 0, k: 1 }, rects = [], vw = root.clientWidth || innerWidth, vh = root.clientHeight || innerHeight, focused = null, wheelZoom = false;
  var LS = 'cv:' + location.pathname;
  function unscroll() { chain.concat([root, body]).forEach(function (n) { if (n.scrollLeft || n.scrollTop) { n.scrollLeft = 0; n.scrollTop = 0; } }); }
  doc.addEventListener('scroll', unscroll, true); window.addEventListener('hashchange', function () { unscroll(); var id = location.hash.slice(1), b = all.filter(function (x) { return x.dataset.board === id; })[0]; if (b) focusBoard(b); });
  function apply(anim) {
    unscroll();
    if (anim && !reduce) A.classList.add('cv-anim'); else A.classList.remove('cv-anim');
    A.style.transform = 'translate(' + v.x + 'px,' + v.y + 'px) scale(' + v.k + ')';
    root.style.backgroundImage = 'radial-gradient(circle, ' + dot() + ' 1px, transparent 1.4px)';
    var s = Math.max(8, 28 * v.k); root.style.backgroundSize = s + 'px ' + s + 'px'; root.style.backgroundPosition = v.x + 'px ' + v.y + 'px';
    var z = doc.getElementById('cv-z'); if (z) z.textContent = Math.round(v.k * 100) + '%';
  }
  var dotC = null;
  function dot() { if (!dotC) { var m = /\d+/g, n = (pageFg.match(m) || [200, 200, 200]); dotC = 'rgba(' + n[0] + ',' + n[1] + ',' + n[2] + ',.13)'; } return dotC; }
  function measure() {
    var keep = A.style.transform, kc = A.className; A.classList.remove('cv-anim'); A.style.transform = 'none';
    var o = A.getBoundingClientRect(); rects = all.map(function (b) { var r = b.getBoundingClientRect(); return { el: b, x: r.left - o.left, y: r.top - o.top, w: r.width, h: r.height }; });
    A.style.transform = keep; A.className = kc;
  }
  function bbox() {
    var x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    rects.forEach(function (r) { x0 = Math.min(x0, r.x); y0 = Math.min(y0, r.y); x1 = Math.max(x1, r.x + r.w); y1 = Math.max(y1, r.y + r.h); });
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  }
  function fitRect(r, pad, max) {
    pad = pad == null ? 56 : pad; var k = Math.min((vw - pad * 2) / r.w, (vh - pad * 2) / r.h, max || 1);
    k = Math.max(0.04, k); v.k = k; v.x = (vw - r.w * k) / 2 - r.x * k; v.y = (vh - r.h * k) / 2 - r.y * k;
  }
  function fitAll(anim) { exitFocus(true); fitRect(bbox(), 72, 1); apply(anim); save(); }
  function rectOf(b) { return rects.filter(function (r) { return r.el === b; })[0]; }
  function focusBoard(b, noDim, instant) {
    var r = rectOf(b); if (!r) return;
    focused = b; all.forEach(function (x) { x.classList.toggle('cv-on', x === b); });
    body.classList.toggle('cv-focus', !noDim);
    var head = 40, rr = { x: r.x, y: r.y - 0, w: r.w, h: r.h + head };
    fitRect(rr, 64, 2); apply(!instant); save();
    try { history.replaceState(null, '', '#' + b.dataset.board); } catch (e) {}
  }
  function exitFocus(silent) {
    if (!focused) return; focused = null; body.classList.remove('cv-focus'); all.forEach(function (x) { x.classList.remove('cv-on'); });
    try { history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
    if (!silent) fitAll(true);
  }
  function zoomAt(cx, cy, f, anim) {
    var nk = Math.min(4, Math.max(0.04, v.k * f)), r = nk / v.k;
    v.x = cx - (cx - v.x) * r; v.y = cy - (cy - v.y) * r; v.k = nk; apply(anim); save();
  }
  function save() { try { localStorage.setItem(LS, JSON.stringify(v)); } catch (e) {} }
  function step(dir) {
    if (!focused) return; var i = all.indexOf(focused), j = Math.min(all.length - 1, Math.max(0, i + dir)); if (j !== i) focusBoard(all[j]);
  }

  /* ---------- download one board ---------- */
  function download(b) {
    var clone = b.cloneNode(true);
    [].forEach.call(clone.querySelectorAll('.cv-tools'), function (n) { n.remove(); });
    clone.classList.remove('cv-on'); clone.style.opacity = '';
    var styles = [].map.call(doc.querySelectorAll('style,link[rel=stylesheet]'), function (n) { return n.id === 'cv-runtime-style' ? '' : n.outerHTML; }).join('\n');
    var theme = root.getAttribute('data-theme') ? ' data-theme="' + root.getAttribute('data-theme') + '"' : '';
    var html = '<!doctype html><html lang="' + (root.lang || 'tr') + '"' + theme + '><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + titleOf(b).replace(/</g, '&lt;') + '</title>' + styles + '<style>html,body{margin:0;padding:24px;background:' + pageBgOrig + '!important;height:auto!important;overflow:auto!important}</style></head><body>' + clone.outerHTML + '</body></html>';
    var a = doc.createElement('a'); a.href = URL.createObjectURL(new Blob([html], { type: 'text/html' }));
    a.download = (b.dataset.board || 'board') + '.html'; doc.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  /* ---------- list popover ---------- */
  function toggleList() {
    if (list) { list.remove(); list = null; return; }
    list = doc.createElement('div'); list.id = 'cv-list';
    list.innerHTML = all.map(function (b, i) { return '<button data-i="' + i + '"><span>' + titleOf(b).replace(/</g, '&lt;') + '</span><small>' + Math.round(rectOf(b).w) + '×' + Math.round(rectOf(b).h) + '</small></button>'; }).join('');
    list.addEventListener('click', function (e) { var bt = e.target.closest('button'); if (!bt) return; focusBoard(all[+bt.dataset.i], true); list.remove(); list = null; });
    body.appendChild(list);
  }

  /* ---------- events ---------- */
  doc.addEventListener('click', function (e) {
    var bt = e.target.closest('.cv-btn,.cv-txt'); if (!bt) { if (list && !e.target.closest('#cv-list')) { list.remove(); list = null; } return; }
    var a = bt.dataset.a, b = bt.closest('[data-board]');
    if (a === 'focus') { if (focused === b) fitAll(true); else focusBoard(b); }
    else if (a === 'dl') download(b);
    else if (a === 'in') zoomAt(vw / 2, vh / 2, 1.25, true);
    else if (a === 'out') zoomAt(vw / 2, vh / 2, 0.8, true);
    else if (a === 'fit') fitAll(true);
    else if (a === 'one') { exitFocus(true); zoomAt(vw / 2, vh / 2, 1 / v.k, true); }
    else if (a === 'list') toggleList();
    else if (a === 'wheel') { wheelZoom = !wheelZoom; bt.textContent = 'Tekerlek: ' + (wheelZoom ? 'yakınlaştır' : 'kaydır'); }
  });
  doc.addEventListener('wheel', function (e) {
    if (e.target.closest('#cv-hud,#cv-list')) return;
    var inScroll = false; for (var n = e.target; n && n !== body; n = n.parentElement) { if (n.scrollHeight > n.clientHeight + 2 && /(auto|scroll)/.test(getComputedStyle(n).overflowY) && !n.classList.contains('cv-anc')) { inScroll = true; break; } }
    if (inScroll && !e.ctrlKey) return;
    e.preventDefault();
    var dy = e.deltaMode === 1 ? e.deltaY * 33 : e.deltaY, dx = e.deltaMode === 1 ? e.deltaX * 33 : e.deltaX;
    if (e.ctrlKey || e.metaKey || wheelZoom) zoomAt(e.clientX, e.clientY, Math.exp(-dy * (e.ctrlKey ? 0.01 : 0.0016)));
    else { if (e.shiftKey && !dx) { dx = dy; dy = 0; } v.x -= dx; v.y -= dy; apply(); save(); }
    exitFocusDim();
  }, { passive: false });
  function exitFocusDim() { if (focused) { focused = null; body.classList.remove('cv-focus'); all.forEach(function (x) { x.classList.remove('cv-on'); }); } }

  var ptrs = {}, drag = null, pinch = null, space = false;
  function noPan(t) { return t.closest('#cv-hud,#cv-bar,#cv-list,.cv-btn,a,button,input,select,textarea,summary,label,[contenteditable]'); }
  doc.addEventListener('pointerdown', function (e) {
    if (noPan(e.target)) return;
    var inBoard = e.target.closest('.artboard');
    if (inBoard && !(space || e.button === 1 || e.altKey) && e.pointerType === 'mouse') return;
    if (e.button > 1) return;
    ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
    var ids = Object.keys(ptrs);
    if (ids.length === 2) { var p = ids.map(function (i) { return ptrs[i]; }); pinch = { d: Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y), cx: (p[0].x + p[1].x) / 2, cy: (p[0].y + p[1].y) / 2 }; drag = null; }
    else { drag = { x: e.clientX, y: e.clientY, vx: v.x, vy: v.y, moved: false }; }
    doc.body.style.cursor = 'grabbing'; e.preventDefault();
  });
  window.addEventListener('pointermove', function (e) {
    if (!ptrs[e.pointerId]) return; ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
    var ids = Object.keys(ptrs);
    if (ids.length >= 2 && pinch) {
      var p = ids.slice(0, 2).map(function (i) { return ptrs[i]; }), d = Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y), cx = (p[0].x + p[1].x) / 2, cy = (p[0].y + p[1].y) / 2;
      v.x += cx - pinch.cx; v.y += cy - pinch.cy; zoomAt(cx, cy, d / pinch.d); pinch.d = d; pinch.cx = cx; pinch.cy = cy; exitFocusDim();
    } else if (drag) {
      var dx = e.clientX - drag.x, dy = e.clientY - drag.y; if (!drag.moved && Math.hypot(dx, dy) < 3) return; drag.moved = true;
      v.x = drag.vx + dx; v.y = drag.vy + dy; apply(); exitFocusDim();
    }
  });
  function up(e) { delete ptrs[e.pointerId]; if (Object.keys(ptrs).length < 2) pinch = null; if (!Object.keys(ptrs).length) { drag && save(); drag = null; doc.body.style.cursor = ''; } }
  window.addEventListener('pointerup', up); window.addEventListener('pointercancel', up);
  doc.addEventListener('dblclick', function (e) { if (!noPan(e.target) && !e.target.closest('.artboard') && !e.target.closest('[data-board]')) fitAll(true); });
  doc.addEventListener('keydown', function (e) {
    if (/INPUT|TEXTAREA|SELECT/.test(e.target.tagName) || e.target.isContentEditable || e.ctrlKey || e.metaKey) return;
    var k = e.key;
    if (k === ' ') { space = true; e.preventDefault(); }
    else if (k === '0') fitAll(true);
    else if (k === '1') { exitFocus(true); zoomAt(vw / 2, vh / 2, 1 / v.k, true); }
    else if (k === '+' || k === '=') zoomAt(vw / 2, vh / 2, 1.25, true);
    else if (k === '-' || k === '_') zoomAt(vw / 2, vh / 2, 0.8, true);
    else if (k === 'Escape') { if (list) { list.remove(); list = null; } else if (focused) fitAll(true); }
    else if (k === 'f' || k === 'F') { var cur = focused || nearestBoard(); if (focused) fitAll(true); else focusBoard(cur); }
    else if (k === 'ArrowRight' || k === 'ArrowDown' || k === 'PageDown') { if (focused) { step(1); e.preventDefault(); } else { v.x -= (k === 'ArrowRight' ? 80 : 0); v.y -= (k === 'ArrowDown' ? 80 : 0); apply(); } }
    else if (k === 'ArrowLeft' || k === 'ArrowUp' || k === 'PageUp') { if (focused) { step(-1); e.preventDefault(); } else { v.x += (k === 'ArrowLeft' ? 80 : 0); v.y += (k === 'ArrowUp' ? 80 : 0); apply(); } }
  });
  doc.addEventListener('keyup', function (e) { if (e.key === ' ') space = false; });
  function nearestBoard() {
    var cx = (vw / 2 - v.x) / v.k, cy = (vh / 2 - v.y) / v.k, best = all[0], bd = 1e18;
    rects.forEach(function (r) { var d = Math.hypot(r.x + r.w / 2 - cx, r.y + r.h / 2 - cy); if (d < bd) { bd = d; best = r.el; } });
    return best;
  }
  var rz = null;
  window.addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(function () { vw = root.clientWidth || innerWidth; vh = root.clientHeight || innerHeight; if (focused) focusBoard(focused, false, true); }, 80); });

  /* ---------- boot ---------- */
  function boot() {
    measure(); vw = root.clientWidth || innerWidth; vh = root.clientHeight || innerHeight;
    var id = (location.hash || '').slice(1), hit = all.filter(function (b) { return b.dataset.board === id; })[0], saved = null;
    try { saved = JSON.parse(localStorage.getItem(LS) || 'null'); } catch (e) {}
    var qv = (q.get('view') || '').split(',').map(Number);
    if (qv.length === 3 && qv.every(isFinite) && qv[2] > 0) { v = { x: qv[0], y: qv[1], k: qv[2] }; apply(false); }
    else if (hit) focusBoard(hit, false, true);
    else if (saved && isFinite(saved.k) && !q.get('cvtest')) { v = saved; apply(); }
    else fitAll(false);
    root.dataset.cv = 'ready'; root.dataset.cvBoards = String(all.length);
    (function () { var hr = hit ? rectOf(hit) : rects[0]; root.dataset.cvDbg = JSON.stringify({ rect: hr && [hr.x, hr.y, hr.w, hr.h].map(Math.round), v: [v.x, v.y, v.k].map(function (n) { return +n.toFixed(2); }), vw: vw, vh: vh, actual: hit ? (function () { var a = hit.getBoundingClientRect(); return [a.left, a.top, a.width, a.height].map(Math.round); })() : null, cw: root.clientWidth, iw: innerWidth, W: W, aw: A.offsetWidth, dispA: getComputedStyle(A).display, wrap: getComputedStyle(A).flexWrap, meas: rects.slice(0, 5).map(function (r) { return Math.round(r.x); }), now: all.slice(0, 5).map(function (b) { return Math.round((b.getBoundingClientRect().left - v.x) / v.k); }) }); })();
    window.__canvas = { view: function () { return v; }, fit: fitAll, focus: function (id2) { var b = all.filter(function (x) { return x.dataset.board === id2; })[0]; if (b) focusBoard(b); }, zoomAt: zoomAt, boards: all, rects: function () { return rects; } };
    if (q.get('cvtest') || q.get('cvrects')) root.dataset.cvRects = JSON.stringify(rects.map(function (r) { return [r.el.dataset.board, Math.round(r.x), Math.round(r.y), Math.round(r.w), Math.round(r.h)]; }));
    if (q.get('cvtest')) {
      fitAll(false); var k0 = v.k; zoomAt(300, 200, 2); var k1 = v.k; fitAll(false); focusBoard(all[0], false, true); var f = v.k; fitAll(false);
      var hr = hit ? rectOf(hit) : rects[0]; root.dataset.cvDbg = JSON.stringify({ rect: hr && [hr.x, hr.y, hr.w, hr.h].map(Math.round), v: [v.x, v.y, v.k].map(function (n) { return +n.toFixed(2); }), vw: vw, vh: vh });
      var esc = 0; all.forEach(function (b) { var br = b.getBoundingClientRect(); [].forEach.call(b.querySelectorAll('*'), function (el) { if (getComputedStyle(el).position === 'fixed') { var r = el.getBoundingClientRect(); if (r.right < br.left - 2 || r.left > br.right + 2 || r.bottom < br.top - 2 || r.top > br.bottom + 2) esc++; } }); });
      root.dataset.cvTest = JSON.stringify({ fixedEscaped: esc, k0: +k0.toFixed(3), zoomed: +(k1 / k0).toFixed(3), focusK: +f.toFixed(3), boards: all.length, world: Math.round(W), hud: chrome.length });
    }
  }
  var go = function () { setTimeout(boot, 20); };
  function start() { if (doc.fonts && doc.fonts.ready) { var done = false, once = function () { if (!done) { done = true; go(); } }; doc.fonts.ready.then(once); setTimeout(once, 700); } else go(); }
  if (doc.readyState === 'complete') start(); else window.addEventListener('load', start);
})();
