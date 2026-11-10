#!/usr/bin/env python3
"""Download daily closing prices for the TCH30 members and compute the TCH30 index.

Runs in GitHub Actions every weekday (see .github/workflows/update-prices.yml).
Reads site_data.json (members + weights + base index value), writes prices.json.

Index math (like a real index between rebalances):
  value(t) = base_value * sum_i( weight_i * price_i(t) / price_i(base_date) )
Dates before the base date are a hypothetical back-test using today's weights, chained
day by day so members that IPO'd later simply join when they start trading (up to 5 years).
Also saves today's 5-minute index values for the 1-day chart.
"""
import json, datetime, math
import yfinance as yf  # unofficial Yahoo Finance library; personal/educational use

site = json.load(open("site_data.json"))
members = {c["ticker"]: c["weight"] for c in site["top"]}
base_value = site.get("index_value", 1000.0)
base_date = site.get("base_date")  # e.g. "2026-11-06"; set by the monthly refresh

# Yahoo symbols that differ from the exchange ticker can be mapped here.
YAHOO = {}
symbols = [YAHOO.get(t, t) for t in members]

raw = yf.download(symbols, period="5y", interval="1d", auto_adjust=True, progress=False, group_by="ticker")
full = {}
for t in members:
    s = YAHOO.get(t, t)
    try:
        closes = raw[s]["Close"].dropna()
    except KeyError:
        print(f"no data for {t}")
        continue
    full[t] = [[d.strftime("%Y-%m-%d"), round(float(v), 4)] for d, v in closes.items()]
# per-stock charts only need the last year
cut = (datetime.date.today() - datetime.timedelta(days=366)).isoformat()
series = {t: [p for p in s if p[0] >= cut] for t, s in full.items()}

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
dates = sorted({d for s in full.values() for d, _ in s})
lookup = {t: dict(s) for t, s in full.items()}
if not base_date or base_date not in dates:
    base_date = max(d for d in dates if d <= (base_date or dates[-1]))
base_px = {t: lookup[t].get(base_date) for t in members if t in lookup}

def official(px):
    """Index value from a {ticker: price} snapshot: fixed weights since the base date."""
    total = wsum = 0.0
    for t, w in members.items():
        if px.get(t) is not None and base_px.get(t):
            total += w * px[t] / base_px[t]
            wsum += w
    return base_value * total / wsum if wsum else None

# From the base date on: the real index.
value = {}
last = {}
for d in dates:
    for t in members:
        if t in lookup and lookup[t].get(d) is not None:
            last[t] = lookup[t][d]
    if d >= base_date:
        value[d] = official(last)
# Before the base date: back-test, chained backwards one day at a time.
before = [d for d in dates if d <= base_date]
for k in range(len(before) - 1, 0, -1):
    d0, d1 = before[k - 1], before[k]
    r = wsum = 0.0
    for t, w in members.items():
        a, b = lookup.get(t, {}).get(d0), lookup.get(t, {}).get(d1)
        if a and b:
            r += w * (b / a - 1)
            wsum += w
    if wsum < 0.5:  # too few members trading yet
        break
    value[d0] = value[d1] / (1 + r / wsum)
index = [[d, round(value[d], 2)] for d in dates if d in value and value[d] is not None]

# Today's (or the latest session's) 5-minute index values for the 1-day chart
intraday = None
try:
    ir = yf.download(symbols, period="1d", interval="5m", auto_adjust=True, progress=False, group_by="ticker", prepost=False)
    session = None
    px, pts = {}, []
    ticks = sorted({ts for t in members if YAHOO.get(t, t) in ir.columns.get_level_values(0)
                    for ts in ir[YAHOO.get(t, t)]["Close"].dropna().index})
    if ticks:
        session = ticks[-1].tz_convert("America/New_York").strftime("%Y-%m-%d")
        prev = max(d for d in dates if d < session)
        px = {t: lookup[t].get(prev) for t in members if t in lookup}
        pts.append(["Prev close", round(official(px), 2)])
        cols = {t: ir[YAHOO.get(t, t)]["Close"] for t in members if YAHOO.get(t, t) in ir.columns.get_level_values(0)}
        for ts in ticks:
            for t, c in cols.items():
                v = c.get(ts)
                if v is not None and not math.isnan(v):
                    px[t] = float(v)
            pts.append([ts.tz_convert("America/New_York").strftime("%H:%M"), round(official(px), 2)])
        intraday = {"date": session, "points": pts}
except Exception as e:
    print("intraday skipped:", e)

json.dump({"updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "base_date": base_date, "series": series, "latest": latest, "index": index, "intraday": intraday},
          open("prices.json", "w"))
print(f"prices.json: {len(series)} members, index {index[0]} .. {index[-1]}, intraday {len(intraday['points']) if intraday else 0} pts")
