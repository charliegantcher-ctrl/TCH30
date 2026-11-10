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
  const label = {"1D": P.intraday ? "on " + P.intraday.date : "last day", "1W": "past week", "1M": "past month", "1Y": "past year", "5Y": "past 5 years"}[r];
  const note = r === "5Y" && ix[0][0] > new Date(new Date(end).setFullYear(new Date(end).getFullYear()-5)).toISOString().slice(0,10) ? ` (back-test starts ${ix[0][0]})` : "";
  $("#idxchg").innerHTML = `<span class="pill ${tone(chg)}">${pct(chg)}</span> <span style="color:var(--muted);font-size:13px">${label}${note}</span>`;
  $("#idxchart").innerHTML = lineChart(s, 420, 90, chg >= 0, r === "1D" ? null : P.base_date);
  document.querySelectorAll(".rng button").forEach(b => b.setAttribute("aria-selected", b.dataset.r === r));
}
function spark(m, w=260, h=54, t=null){""")

# Load data at runtime
sub("renderIndex(); renderOthers(); renderNews(); route();",
"""Promise.all([
  fetch("site_data.json", {cache: "no-cache"}).then(r => r.json()),
  fetch("prices.json", {cache: "no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null),
  fetch("news.json", {cache: "no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null)
]).then(([d, p, n]) => { D = d; P = p; if (n) D.news = n; renderIndex(); renderOthers(); renderNews(); route(); })
  .catch(e => { document.querySelector("main").innerHTML = "<p style='padding:40px 0'>Could not load site_data.json. Open this page from a web server (GitHub Pages), not as a local file.</p>"; });""")
sub('.idx-sub{color:var(--muted);font-size:13px;max-width:44ch}', '.idx-sub{color:var(--muted);font-size:13px;max-width:52ch}\n.idx-sub .spark{height:90px;margin:6px 0}\n.rng{display:flex;gap:4px;margin:2px 0 4px}\n.rng button{font:600 12px IBM Plex Mono,monospace;padding:4px 10px;border:1px solid var(--rule);background:transparent;color:var(--muted);border-radius:999px;cursor:pointer}\n.rng button[aria-selected=true]{background:var(--ink);color:var(--paper);border-color:var(--ink)}')

import os
os.makedirs("live", exist_ok=True)
open("live/index.html", "w").write(src)
print("wrote live/index.html")
