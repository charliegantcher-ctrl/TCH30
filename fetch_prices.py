#!/usr/bin/env python3
"""Download daily closing prices for the TCH30 members and compute the TCH30 index.

Runs in GitHub Actions every weekday (see .github/workflows/update-prices.yml).
Reads site_data.json (members + weights + base index value), writes prices.json.

Index math (like a real index between rebalances):
  value(t) = base_value * sum_i( weight_i * price_i(t) / price_i(base_date) )
Dates before the base date are a hypothetical back-test using today's weights.
"""
import json, datetime
import yfinance as yf  # unofficial Yahoo Finance library; personal/educational use

site = json.load(open("site_data.json"))
members = {c["ticker"]: c["weight"] for c in site["top"]}
base_value = site.get("index_value", 1000.0)
base_date = site.get("base_date")  # e.g. "2026-11-06"; set by the monthly refresh

# Yahoo symbols that differ from the exchange ticker can be mapped here.
YAHOO = {}
symbols = [YAHOO.get(t, t) for t in members]

raw = yf.download(symbols, period="1y", interval="1d", auto_adjust=True, progress=False, group_by="ticker")
series = {}
for t in members:
    s = YAHOO.get(t, t)
    try:
        closes = raw[s]["Close"].dropna()
    except KeyError:
        print(f"no data for {t}")
        continue
    series[t] = [[d.strftime("%Y-%m-%d"), round(float(v), 4)] for d, v in closes.items()]

latest = {}
for t, s in series.items():
    if len(s) < 2:
        continue
    px = s[-1][1]
    month_ago = s[-22][1] if len(s) > 22 else s[0][1]
    latest[t] = {"price": px, "date": s[-1][0],
                 "chg_1d_pct": (px / s[-2][1] - 1) * 100,
                 "chg_1m_pct": (px / month_ago - 1) * 100,
                 "chg_1y_pct": (px / s[0][1] - 1) * 100}

# TCH30 index series
dates = sorted({d for s in series.values() for d, _ in s})
lookup = {t: dict(s) for t, s in series.items()}
if not base_date or base_date not in dates:
    base_date = max(d for d in dates if d <= (base_date or dates[-1]))
base_px = {t: lookup[t].get(base_date) for t in members if t in lookup}
index = []
last = {t: None for t in members}
for d in dates:
    total, wsum = 0.0, 0.0
    for t, w in members.items():
        if t in lookup and lookup[t].get(d) is not None:
            last[t] = lookup[t][d]
        if last[t] is not None and base_px.get(t):
            total += w * last[t] / base_px[t]
            wsum += w
    if wsum > 0.9:  # skip early dates before most members traded (e.g. pre-IPO)
        index.append([d, round(base_value * total / wsum, 2)])

json.dump({"updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
           "base_date": base_date, "series": series, "latest": latest, "index": index},
          open("prices.json", "w"))
print(f"prices.json: {len(series)} members, index {index[-1] if index else 'n/a'}")
