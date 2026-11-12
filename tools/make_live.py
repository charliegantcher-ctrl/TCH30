#!/usr/bin/env python3
"""Make live/index.html from template.html: same page, but it loads site_data.json and
prices.json at runtime and draws real 1-year price charts and the TCH30 index line."""
src = open("template.html").read()

def sub(old, new):
    global src
    assert old in src, f"pattern not found: {old[:60]}"
    src = src.replace(old, new)

sub("const D = /*__DATA__*/null;", "let D, P = null;")

# Real price series when prices.json is available
sub("function spark(m, w=260, h=54){\n  const now = m.price, pts = [];",
"""function liveSeries(t){ return P && P.series && P.series[t] && P.series[t].length > 5 ? P.series[t] : null; }
function lineChart(s, w, h, up, baseDate){
  const ys = s.map(p => p[1]), lo = Math.min(...ys), hi = Math.max(...ys), pad = 6, n = s.length;
  const X = i => pad + i/(n-1)*(w-2*pad), Y = y => pad + (hi-y)/((hi-lo)||1)*(h-2*pad-10);
  const col = up ? "var(--up)" : "var(--down)";
  const line = s.map((p,i) => X(i).toFixed(1) + "," + Y(p[1]).toFixed(1)).join(" ");
  const bi = baseDate ? s.findIndex(p => p[0] >= baseDate) : -1;
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-label="daily closes ${s[0][0]} to ${s[n-1][0]}">
    <line x1="${pad}" x2="${w-pad}" y1="${h-10}" y2="${h-10}" stroke="var(--rule)"/>
    ${bi > 0 ? `<line x1="${X(bi)}" x2="${X(bi)}" y1="${pad}" y2="${h-10}" stroke="var(--muted)" stroke-dasharray="2 3"/>` : ""}
    <polygon points="${X(0)},${h-10} ${line} ${X(n-1)},${h-10}" fill="${col}" opacity=".12"/>
    <polyline points="${line}" fill="none" stroke="${col}" stroke-width="1.6" vector-effect="non-scaling-stroke"/>
    <circle cx="${X(n-1)}" cy="${Y(s[n-1][1])}" r="3" fill="${col}"/>
    <text x="${pad}" y="${h-1}" font-size="9" fill="var(--muted)" font-family="IBM Plex Mono, monospace">${s[0][0]}</text>
    <text x="${w-pad}" y="${h-1}" font-size="9" fill="var(--muted)" text-anchor="end" font-family="IBM Plex Mono, monospace">${s[n-1][0]}</text></svg>`;
}
function spark(m, w=260, h=54, t=null){
  const s = t && liveSeries(t);
  if (s) return lineChart(s, w, h, (m.chg_1m_pct ?? 0) >= 0);
  const now = m.price, pts = [];""")

# Prefer live quotes over the monthly snapshot
sub("function card(c){\n  const m = c.mkt;",
"""function withLive(c){
  const L = P && P.latest && P.latest[c.ticker];
  return L ? {...c.mkt, price: L.price, chg_1m_pct: L.chg_1m_pct, chg_1y_pct: L.chg_1y_pct, chg_1d_pct: L.chg_1d_pct} : c.mkt;
}
function card(c){
  const m = withLive(c);""")
sub("    ${spark(m)}\n    ${dots(c)}", "    ${spark(m, 260, 54, c.ticker)}\n    ${dots(c)}")
sub('<span class="pill ${tone(m.chg_1m_pct)}">${pct(m.chg_1m_pct)} 1m</span></div></div>\n    ${spark(m, 260, 54, c.ticker)}',
    '${m.chg_1d_pct != null ? `<span class="pill ${tone(m.chg_1d_pct)}">${pct(m.chg_1d_pct)} today</span><div class="m1">${pct(m.chg_1m_pct)} 1m</div>` : `<span class="pill ${tone(m.chg_1m_pct)}">${pct(m.chg_1m_pct)} 1m</span>`}</div></div>\n    ${spark(m, 260, 54, c.ticker)}')
sub('<div class="fact"><small>1-month change</small>',
    '${m.chg_1d_pct != null ? `<div class="fact"><small>1-day change</small><b class="${tone(m.chg_1d_pct)}">${pct(m.chg_1d_pct)}</b></div>` : ""}<div class="fact"><small>1-month change</small>')
sub("const c = D.top.find(x => x.ticker === t), m = c.mkt;", "const c = D.top.find(x => x.ticker === t), m = withLive(c);")
sub("${spark(m, 520, 80)}", "${spark(m, 520, 80, c.ticker)}")
sub('<div class="fact"><small>Price (${esc(D.asof)})</small>', '<div class="fact"><small>Price (${esc(P && P.latest[c.ticker] ? P.latest[c.ticker].date : D.asof)})</small>')

# Index header from the live index series
sub("""  const h0 = D.history[0];""",
"""  if (P && P.index && P.index.length > 1) {
    const ix = P.index, last = ix[ix.length-1][1], base = ix.find(p => p[0] >= P.base_date) || ix[0];
    const ch = (last / base[1] - 1) * 100;
    $("#asof").textContent = "Prices updated " + P.updated;
    $("#idxval").textContent = last.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});
    $("#idxsub").innerHTML = `<div class="rng" role="tablist">${["1D","1W","1M","1Y","5Y"].map(r =>
        `<button type="button" data-r="${r}">${r}</button>`).join("")}</div><div id="idxchart"></div>
      <span>Since the ${esc(P.base_date)} rebalance: <b class="${tone(ch)}">${pct(ch)}</b>. Left of the dashed line is a back-test with current weights.</span>`;
    $("#idxsub").querySelectorAll(".rng button").forEach(b => b.onclick = () => idxRange(b.dataset.r));
    idxRange(window.__rng || "1Y");
    return renderBoard();
  }
  const h0 = D.history[0];""")
sub("""Live tracking is not available on this page.`;
  const top""", """Live tracking is not available on this page.`;
  renderBoard();
}
function renderBoard(){
  const top""")

# "What moved the index today" panel
sub('  $("#dotkey").innerHTML = dotKey();', '  $("#dotkey").innerHTML = dotKey();\n  renderMovers();')
sub("function spark(m, w=260, h=54, t=null){", """function renderMovers(){
  const box = $("#movers");
  if (!(P && P.latest)) { box.innerHTML = ""; return; }
  const rows = D.top.map(c => { const L = P.latest[c.ticker]; return L && L.chg_1d_pct != null ? {t: c.ticker, d: L.chg_1d_pct, pts: c.weight * L.chg_1d_pct, date: L.date} : null; }).filter(Boolean);
  if (!rows.length) { box.innerHTML = ""; return; }
  rows.sort((a, b) => b.pts - a.pts);
  const tot = rows.reduce((s, r) => s + r.pts, 0), mx = Math.max(...rows.map(r => Math.abs(r.pts))) || 1;
  const up = rows.filter(r => r.d > 0).length, dn = rows.filter(r => r.d < 0).length;
  const bar = r => `<div class="mv-row" title="${r.t}: ${pct(r.d)} today, ${r.pts >= 0 ? "adds" : "takes"} ${Math.abs(r.pts).toFixed(2)} pts of % to the index">
      <span class="mv-t">${r.t}</span><span class="mv-d ${tone(r.d)}">${pct(r.d)}</span>
      <span class="mv-bar"><i style="${r.pts >= 0 ? "left:50%" : "right:50%"};width:${(Math.abs(r.pts) / mx * 50).toFixed(1)}%;background:${r.pts >= 0 ? "var(--up)" : "var(--down)"}"></i></span>
      <span class="mv-c ${tone(r.pts)}">${r.pts >= 0 ? "+" : "−"}${Math.abs(r.pts).toFixed(2)}</span></div>`;
  box.innerHTML = `<details class="movers" open><summary><b>What moved the index on ${esc(rows[0].date)}</b>
      <span>${up} up · ${dn} down · total <b class="${tone(tot)}">${pct(tot)}</b></span></summary>
    <p class="mv-note">Each stock's daily change, and how much it added to or took from TCH30 (its weight × its move, in % points). Biggest boosts at the top, biggest drags at the bottom.</p>
    <div class="mv-grid">${rows.map(bar).join("")}</div></details>`;
}
function spark(m, w=260, h=54, t=null){""")

# Range buttons for the index chart
sub("function spark(m, w=260, h=54, t=null){", """function idxRange(r){
  window.__rng = r;
  const ix = P.index, end = ix[ix.length-1][0];
  let s;
  if (r === "1D") {
    s = P.intraday && P.intraday.points && P.intraday.points.length > 2 ? P.intraday.points : ix.slice(-2);
  } else {
    const d = new Date(end + "T12:00:00Z");
    if (r === "1W") d.setUTCDate(d.getUTCDate() - 7);
    if (r === "1M") d.setUTCMonth(d.getUTCMonth() - 1);
    if (r === "1Y") d.setUTCFullYear(d.getUTCFullYear() - 1);
    if (r === "5Y") d.setUTCFullYear(d.getUTCFullYear() - 5);
    const from = d.toISOString().slice(0, 10);
    s = ix.filter(p => p[0] >= from);
    if (s.length < 2) s = ix.slice(-2);
  }
  const chg = (s[s.length-1][1] / s[0][1] - 1) * 100;
  const b = benchFor(s, r);
  const bchg = b && b[b.length-1] != null && b[0] != null ? (b[b.length-1] / b[0] - 1) * 100 : null;
  const label = {"1D": P.intraday ? "on " + P.intraday.date : "last day", "1W": "past week", "1M": "past month", "1Y": "past year", "5Y": "past 5 years"}[r];
  const note = r === "5Y" && (new Date(ix[0][0]) - new Date(end)) / 864e5 > -365 * 5 + 10 ? ` (back-test starts ${ix[0][0]})` : "";
  const vs = bchg != null ? ` <span style="color:var(--muted);font-size:13px">· ${esc(P.bench_name)} ${pct(bchg)} · <b class="${tone(chg - bchg)}">${chg >= bchg ? "beating" : "trailing"} by ${Math.abs(chg - bchg).toFixed(1)} pts</b></span>` : "";
  $("#idxchg").innerHTML = `<span class="pill ${tone(chg)}">${pct(chg)}</span> <span style="color:var(--muted);font-size:13px">${label}${note}</span>${vs}`;
  const ch = idxChart(s, b, 420, 90, chg >= 0, r === "1D" ? null : P.base_date);
  $("#idxchart").innerHTML = ch.svg +
    `<div class="xh-line" hidden></div><div class="xh-dot" hidden></div><div class="xh-tip" hidden></div>` +
    (b ? `<span class="bxlg"><i class="lg-i" style="border-top-color:${chg >= 0 ? "var(--up)" : "var(--down)"}"></i> TCH30 <i class="lg-b"></i> ${esc(P.bench_name)} (scaled to the same start)</span>` : "");
  idxHover(s, r, b, ch.lo, ch.hi);
  document.querySelectorAll(".rng button").forEach(b => b.setAttribute("aria-selected", b.dataset.r === r));
}
function benchFor(s, r){
  // QQQ values on the same x points as s, rescaled to start at the same level as the index
  let raw;
  if (r === "1D") {
    if (!(P.intraday && P.intraday.bench && P.intraday.points === s)) return null;
    raw = P.intraday.bench.map(p => p[1]);
  } else {
    if (!P.bench || !P.bench.length) return null;
    const bd = new Map(P.bench); let last = null, j = 0;
    raw = s.map(p => { while (j < P.bench.length && P.bench[j][0] <= p[0]) last = P.bench[j++][1]; return last; });
  }
  const k = raw.findIndex(v => v != null);
  if (k < 0) return null;
  const f = s[k][1] / raw[k];
  return raw.map(v => v == null ? null : v * f);
}
function idxChart(s, b, w, h, up, baseDate){
  const ys = s.map(p => p[1]).concat(b ? b.filter(v => v != null) : []);
  const lo = Math.min(...ys), hi = Math.max(...ys), pad = 6, n = s.length;
  const X = i => pad + i/(n-1)*(w-2*pad), Y = y => pad + (hi-y)/((hi-lo)||1)*(h-2*pad-10);
  const col = up ? "var(--up)" : "var(--down)";
  const line = s.map((p,i) => X(i).toFixed(1) + "," + Y(p[1]).toFixed(1)).join(" ");
  const bl = b ? b.map((v,i) => v == null ? null : X(i).toFixed(1) + "," + Y(v).toFixed(1)).filter(Boolean).join(" ") : "";
  const bi = baseDate ? s.findIndex(p => p[0] >= baseDate) : -1;
  return {lo, hi, svg: `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-label="TCH30${b ? " vs " + P.bench_name : ""}, ${s[0][0]} to ${s[n-1][0]}">
    <line x1="${pad}" x2="${w-pad}" y1="${h-10}" y2="${h-10}" stroke="var(--rule)"/>
    ${bi > 0 ? `<line x1="${X(bi)}" x2="${X(bi)}" y1="${pad}" y2="${h-10}" stroke="var(--muted)" stroke-dasharray="2 3"/>` : ""}
    <polygon points="${X(0)},${h-10} ${line} ${X(n-1)},${h-10}" fill="${col}" opacity=".12"/>
    ${bl ? `<polyline points="${bl}" fill="none" stroke="var(--bench)" stroke-width="1.4" stroke-dasharray="4 3" vector-effect="non-scaling-stroke"/>` : ""}
    <polyline points="${line}" fill="none" stroke="${col}" stroke-width="1.8" vector-effect="non-scaling-stroke"/>
    <circle cx="${X(n-1)}" cy="${Y(s[n-1][1])}" r="3" fill="${col}"/>
    <text x="${pad}" y="${h-1}" font-size="9" fill="var(--muted)" font-family="IBM Plex Mono, monospace">${s[0][0]}</text>
    <text x="${w-pad}" y="${h-1}" font-size="9" fill="var(--muted)" text-anchor="end" font-family="IBM Plex Mono, monospace">${s[n-1][0]}</text></svg>`};
}
function idxHover(s, r, b, lo, hi){
  const box = $("#idxchart"), svg = box.querySelector("svg"), line = box.querySelector(".xh-line"),
        dot = box.querySelector(".xh-dot"), tip = box.querySelector(".xh-tip");
  const w = 420, h = 90, pad = 6, n = s.length;
  const hide = () => { line.hidden = dot.hidden = tip.hidden = true; };
  const show = e => {
    const rc = svg.getBoundingClientRect(), fx = (e.clientX - rc.left) / rc.width;
    const i = Math.max(0, Math.min(n - 1, Math.round((fx * w - pad) / (w - 2 * pad) * (n - 1))));
    const px = (pad + i / (n - 1) * (w - 2 * pad)) / w * rc.width;
    const py = (pad + (hi - s[i][1]) / ((hi - lo) || 1) * (h - 2 * pad - 10)) / h * rc.height;
    const v = s[i][1], c = (v / s[0][1] - 1) * 100;
    const when = r === "1D" ? (s[i][0] === "Prev close" ? "Previous close" : P.intraday.date + " " + s[i][0] + " ET") : s[i][0];
    line.style.left = px + "px"; line.style.height = rc.height - 10 / h * rc.height + "px";
    dot.style.left = px + "px"; dot.style.top = py + "px";
    const bc = b && b[i] != null && b[0] != null ? (b[i] / b[0] - 1) * 100 : null;
    tip.innerHTML = `<b>${v.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2})}</b> <span class="${tone(c)}">${pct(c)}</span>` +
      (bc != null ? ` <span>· ${esc(P.bench_name)}</span> <span class="${tone(bc)}">${pct(bc)}</span>` : "") + `<br><span>${esc(when)}</span>`;
    line.hidden = dot.hidden = tip.hidden = false;
    tip.style.left = Math.max(0, Math.min(rc.width - tip.offsetWidth, px - tip.offsetWidth / 2)) + "px";
  };
  svg.addEventListener("pointermove", show);
  svg.addEventListener("pointerdown", show);
  svg.addEventListener("pointerleave", hide);
  svg.style.touchAction = "pan-y";
}
function spark(m, w=260, h=54, t=null){""")

# Load data at runtime
sub("renderIndex(); renderOthers(); renderNews(); renderSectors(); route();",
"""Promise.all([
  fetch("site_data.json", {cache: "no-cache"}).then(r => r.json()),
  fetch("prices.json", {cache: "no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null),
  fetch("news.json", {cache: "no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null)
]).then(([d, p, n]) => { D = d; P = p; if (n) D.news = n; renderIndex(); renderOthers(); renderNews(); renderSectors(); route(); })
  .catch(e => { document.querySelector("main").innerHTML = "<p style='padding:40px 0'>Could not load site_data.json. Open this page from a web server (GitHub Pages), not as a local file.</p>"; });""")
sub('.idx-sub{color:var(--muted);font-size:13px;max-width:44ch}', '.idx-sub{color:var(--muted);font-size:13px;max-width:52ch}\n.idx-sub .spark{height:90px;margin:6px 0}\n.m1{font-size:11px;color:var(--muted);text-align:right;margin-top:3px;font-family:IBM Plex Mono,monospace}\n.movers{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:12px 16px;margin:18px 0}\n.movers summary{cursor:pointer;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:15px}\n.movers summary span{color:var(--muted);font-size:13px}\n.mv-note{color:var(--muted);font-size:12.5px;margin:8px 0 10px}\n.mv-grid{columns:3 280px;column-gap:28px}\n.mv-row{display:grid;grid-template-columns:48px 62px 1fr 48px;gap:8px;align-items:center;break-inside:avoid;margin-bottom:4px;font:12.5px IBM Plex Mono,monospace}\n.mv-t{font-weight:600}\n.mv-d,.mv-c{text-align:right}\n.mv-bar{position:relative;height:10px;background:var(--na-soft);border-radius:3px}\n.mv-bar i{position:absolute;top:0;bottom:0;border-radius:3px}\n.mv-bar::after{content:'';position:absolute;left:50%;top:-2px;bottom:-2px;border-left:1px solid var(--muted)}\n.rng{display:flex;gap:4px;margin:2px 0 4px}\n.rng button{font:600 12px IBM Plex Mono,monospace;padding:4px 10px;border:1px solid var(--rule);background:transparent;color:var(--muted);border-radius:999px;cursor:pointer}\n.rng button[aria-selected=true]{background:var(--ink);color:var(--paper);border-color:var(--ink)}\n#idxchart{position:relative;padding-top:34px}\n#idxchart svg{cursor:crosshair;display:block}\n.xh-line{position:absolute;top:34px;width:0;border-left:1px dashed var(--muted);pointer-events:none}\n.xh-dot{position:absolute;width:8px;height:8px;margin:30px 0 0 -4px;border-radius:50%;background:var(--ink);pointer-events:none}\n.xh-tip{position:absolute;top:0;white-space:nowrap;font:12px/1.3 IBM Plex Mono,monospace;color:var(--ink);background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:2px 7px;pointer-events:none}\n.bxlg{display:block;font-size:11px;color:var(--muted);margin-top:2px;white-space:nowrap}\n.lg-i,.lg-b{display:inline-block;width:16px;height:0;vertical-align:middle;border-top:2px solid var(--up)}\n.lg-b{border-top:2px dashed var(--bench);margin-left:10px}\n:root{--bench:#6b5bd6}\n.xh-tip span{color:var(--muted)} .xh-tip .up{color:var(--up)} .xh-tip .down{color:var(--down)}')

import os
os.makedirs("live", exist_ok=True)
open("live/index.html", "w").write(src)
print("wrote live/index.html")
