#!/usr/bin/env python3
"""Build the TCH30 site (index.html) from companies.json + market_batch*.json.

Usage: python3 build.py [asof_label]
- companies.json : all 100 companies with the 8 metrics + signs (+1 green, -1 red, 0 gray), tier/rank/why for the top 30
- market_batch*.json : market cap, price, 1m/1y change, TTM revenue, net income, book value, dividends for the top 30
Weights: half market-cap share, half equal weight (1/30). The fundamental share
(equal blend of sales, earnings>=0, book value, dividends) is still computed and shown for reference.
"""
import json, glob, sys, html, datetime

ASOF = sys.argv[1] if len(sys.argv) > 1 else "Nov 6, 2026 close"
companies = json.load(open("companies.json"))
market = []
for f in sorted(glob.glob("market_batch*.json")):
    market += json.load(open(f))
mk = {r["ticker"]: r for r in market}

top = [c for c in companies if c.get("tier")]
top.sort(key=lambda c: c["rank"])
missing = [c["ticker"] for c in top if c["ticker"] not in mk]
if missing:
    sys.exit(f"missing market data for {missing}")

def shares(key):
    vals = {t: max((mk[t].get(key) or 0), 0) for t in (c["ticker"] for c in top)}
    s = sum(vals.values()) or 1
    return {k: v / s for k, v in vals.items()}

mc, sa, ea, bk, dv = (shares(k) for k in ("mcap_b", "rev_ttm_b", "ni_ttm_b", "book_b", "div_ttm_b"))
for c in top:
    t = c["ticker"]
    fund = (sa[t] + ea[t] + bk[t] + dv[t]) / 4
    c["w_mcap"], c["w_fund"] = mc[t], fund
    c["weight"] = 0.5 * mc[t] + 0.5 / len(top)  # half market cap, half equal (fundamental share kept for reference only)
    m = mk[t]
    c["mkt"] = {k: m.get(k) for k in ("price", "mcap_b", "chg_1m_pct", "chg_1y_pct", "chg_since_ipo_pct",
                                      "rev_ttm_b", "ni_ttm_b", "book_b", "div_ttm_b", "price_date")}
    c["w_parts"] = {"sales": sa[t], "earnings": ea[t], "book": bk[t], "dividends": dv[t]}

idx_1m = sum(c["weight"] * (c["mkt"]["chg_1m_pct"] or 0) for c in top)

# Sector mix of this month's 30 (kept in the history so the Sectors page can show how it shifts)
sectors = {}
for c in top:
    s_ = sectors.setdefault(c["section"], {"count": 0, "weight": 0.0})
    s_["count"] += 1
    s_["weight"] = round(s_["weight"] + c["weight"], 6)

# Index level: carry forward from index_state.json (previous refresh) if present.
# New value = old value x (1 + sum over OLD members of old weight x price return since last refresh).
# Old members that have left the list need a current price in prices_extra.json {"TICKER": price}.
import os
state = json.load(open("index_state.json")) if os.path.exists("index_state.json") else None
extra = json.load(open("prices_extra.json")) if os.path.exists("prices_extra.json") else {}
cur_prices = {t: mk[t]["price"] for t in mk}
cur_prices.update(extra)
if state:
    ret = 0.0
    for t, w in state["weights"].items():
        if t not in cur_prices:
            sys.exit(f"need current price for former member {t} in prices_extra.json")
        ret += w * (cur_prices[t] / state["prices"][t] - 1)
    value, period_ret, since = state["value"] * (1 + ret), ret * 100, state["asof"]
    history = state.get("history", []) + [{"asof": ASOF, "value": round(value, 2), "sectors": sectors}]
else:
    value, period_ret, since = 1000.0, None, None
    history = [{"asof": ASOF, "value": 1000.0, "sectors": sectors}]
json.dump({"value": value, "asof": ASOF, "history": history,
           "weights": {c["ticker"]: c["weight"] for c in top},
           "prices": {c["ticker"]: mk[c["ticker"]]["price"] for c in top}},
          open("index_state.json", "w"), indent=1)

news = json.load(open("news.json")) if os.path.exists("news.json") else None
payload = {
    "news": news,
    "index_value": value, "period_ret_pct": period_ret, "since": since, "history": history,
    "asof": ASOF,
    "built": datetime.date.today().isoformat(),
    "index_1m_pct": idx_1m,
    "top": top,
    "others": [c for c in companies if not c.get("tier")],
}
open("site_data.json", "w").write(json.dumps(payload, indent=1))
data_js = json.dumps(payload).replace("</", "<\\/")
page = open("template.html").read().replace("/*__DATA__*/null", data_js)
open("index.html", "w").write(page)
print(f"built index.html: {len(top)} constituents, {len(payload['others'])} watchlist, index 1m {idx_1m:.1f}%")
