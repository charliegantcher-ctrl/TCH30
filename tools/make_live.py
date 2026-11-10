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
    $("#idxchg").innerHTML = `<span class="pill ${tone(ch)}">${pct(ch)}</span> <span style="color:var(--muted);font-size:13px">since ${esc(P.base_date)} rebalance</span>`;
    $("#idxsub").innerHTML = lineChart(ix, 420, 90, ch >= 0, P.base_date) +
      `<span>Daily closes. Left of the dashed line is a back-test with current weights.</span>`;
    return renderBoard();
  }
  const h0 = D.history[0];""")
sub("""Live tracking is not available on this page.`;
  const top""", """Live tracking is not available on this page.`;
  renderBoard();
}
function renderBoard(){
  const top""")

# Load data at runtime
sub("renderIndex(); renderOthers(); renderNews(); route();",
"""Promise.all([
  fetch("site_data.json", {cache: "no-cache"}).then(r => r.json()),
  fetch("prices.json", {cache: "no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null),
  fetch("news.json", {cache: "no-cache"}).then(r => r.ok ? r.json() : null).catch(() => null)
]).then(([d, p, n]) => { D = d; P = p; if (n) D.news = n; renderIndex(); renderOthers(); renderNews(); route(); })
  .catch(e => { document.querySelector("main").innerHTML = "<p style='padding:40px 0'>Could not load site_data.json. Open this page from a web server (GitHub Pages), not as a local file.</p>"; });""")
sub('.idx-sub{color:var(--muted);font-size:13px;max-width:44ch}', '.idx-sub{color:var(--muted);font-size:13px;max-width:52ch}\n.idx-sub .spark{height:90px;margin:6px 0}')

import os
os.makedirs("live", exist_ok=True)
open("live/index.html", "w").write(src)
print("wrote live/index.html")
