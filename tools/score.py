#!/usr/bin/env python3
"""TCH score: 0-1000 for every stock on the watchlist.

Usage: python3 score.py score_data/ companies.json scores.json [news.json]

Eight parts (max points):
  growth 150 | profitability 150 | cash 125 | customers 75 | industry momentum 100
  forward signals 125 (pipeline 50, contracts & investments 40, news & intel 35)
  cross-industry utility 75 | durability & moat 200
Each sub-part produces a fraction 0..1, or None when the data is not reported.
Missing sub-parts are left out and the rest is scaled up, so companies are not
penalised for metrics they don't disclose. Durability is a fixed rubric (DURABILITY).
"""
import json, glob, sys, statistics, os

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def lin(x, x0, x1):
    """0 at x0, 1 at x1, clamped."""
    return clamp((x - x0) / (x1 - x0))

# Durability & moat rubric: 1.0 bottleneck/monopoly, 0.85 entrenched leader,
# 0.7 strong competitor, 0.55 promising but contested, 0.4 early/unproven,
# 0.2-0.35 pre-revenue or speculative bet.
DURABILITY = {
    **dict.fromkeys("NVDA TSM ASML MSFT GOOGL AMZN KLAC SNPS CDNS ISRG AVGO".split(), 1.0),
    **dict.fromkeys("AAPL META ORCL AMAT LRCX ANET GEV CEG CRWD NOW PLTR MU SKHY ARM SPCX VRT ETN CCJ BWXT EQIX PANW APP".split(), 0.85),
    **dict.fromkeys("AMD MRVL MPWR TER IBM DELL CIEN COHR LITE ALAB CRDO NET ZS DDOG SNOW MDB CRM FSLR VST ALB MP KTOS AVAV RKLB TSLA ON SNDK P CLS".split(), 0.7),
    **dict.fromkeys("INTC ASTS SMCI OKTA S RBRK IOT FIG GTLB TEM NBIS CRWV BE FLNC LEU PL SYM MBLY CBRS".split(), 0.55),
    **dict.fromkeys("IREN APLD EOSE RDW LUNR FLY IONQ".split(), 0.42),
    **dict.fromkeys("OKLO SMR STDN FRVO RGTI QBTS JOBY".split(), 0.32),
    **dict.fromkeys("QUBT NNE QS SERV ACHR".split(), 0.22),
}

# Boom risk: how much a company's current results depend on the AI build-out spending of a
# few hyperscale customers, in a position competitors can enter (judgment, fixed rubric).
# 1.0 = commodity-like supplier to a handful of AI buyers; 0.5 = AI-exposed but diversified
# or hard to replace; 0.3 = some exposure. Deduction = exposure x how far growth exceeds 30%
# (full at 90%+) x 80 points. Applied after scaling.
BOOM = {
    **dict.fromkeys("LITE COHR CRDO ALAB CLS DELL SMCI CIEN BE CRWV NBIS IREN APLD SNDK SKHY MU CBRS".split(), 1.0),
    **dict.fromkeys("NVDA AVGO AMD MRVL ANET VRT MPWR TER LRCX AMAT KLAC ASML ORCL".split(), 0.5),
    **dict.fromkeys("TSM GEV ETN CEG VST EQIX".split(), 0.3),
}
BOOM_MAX = 80

WEIGHTS = {
    "growth": [("rev", 110), ("gp", 40)],
    "profit": [("level", 100), ("trend", 50)],
    "cash": [("fcf", 75), ("balance", 50)],
    "customers": [("expansion", 45), ("concentration", 30)],
    "momentum": [("peer_growth", 75), ("peer_guidance", 25)],
    "forward": [("pipeline", 50), ("contracts", 40), ("news", 35)],
    "utility": [("industries", 75)],
    "durability": [("moat", 200)],
}
PART_MAX = {p: sum(w for _, w in subs) for p, subs in WEIGHTS.items()}
assert sum(PART_MAX.values()) == 1000

def num(v):
    return v if isinstance(v, (int, float)) else None

import math
def full_growth(rev):
    """Growth rate that earns full points, scaled by size: ~60% for a $1B company,
    ~48% at $10B, ~36% at $100B, 28% for $400B+. Growing fast is harder when big."""
    if not rev or rev <= 0:
        return 60.0
    return max(25.0, min(60.0, 60 - 12 * math.log10(max(rev, 1))))

def hist_mean(d, key):
    h = [x for x in (d.get(key) or []) if isinstance(x, (int, float))]
    return sum(h) / len(h) if h else None

def rev_growth(d):
    """Current growth (TTM blended with latest quarter), smoothed with up to 3 prior fiscal
    years' growth when available (rev_growth_hist_pct) so one boom year can't carry a company."""
    t, q = num(d.get("rev_growth_ttm_pct")), num(d.get("rev_growth_q_pct"))
    if t is not None and q is not None:
        cur = 0.6 * t + 0.4 * q
    else:
        cur = t if t is not None else q
    h = hist_mean(d, "rev_growth_hist_pct")
    if cur is not None and h is not None:
        return 0.5 * cur + 0.5 * h
    return cur

def subparts(d, peers, news_extra, fcf_sign=0):
    f = {}
    pre = bool(d.get("pre_revenue"))
    rev = num(d.get("rev_ttm_b"))
    size = rev if rev is not None else num(d.get("rev_size_est_b"))
    g = rev_growth(d)
    org = num(d.get("organic_share"))
    org = 0.85 if org is None else org

    # Growth
    if pre or g is None:
        f["rev"] = 0.0 if pre else None
    else:
        base = lin(g, 0, full_growth(size)) * (0.4 + 0.6 * org)
        if rev is not None and rev < 0.1:      # tiny bases inflate % growth
            base *= 0.5
        f["rev"] = base
    gm, gm0, q = num(d.get("gross_margin_pct")), num(d.get("gross_margin_prior_pct")), num(d.get("rev_growth_q_pct"))
    if not pre and gm is not None and gm0 not in (None, 0) and q is not None and gm > 0 and gm0 > 0:
        gpg = (gm / gm0) * (1 + q / 100) * 100 - 100
        f["gp"] = lin(gpg, 0, full_growth(size)) * (0.4 + 0.6 * org)
    else:
        f["gp"] = 0.0 if pre else None

    # Profitability
    om, om0 = num(d.get("op_margin_adj_pct")) or num(d.get("op_margin_pct")), num(d.get("op_margin_prior_pct"))
    if pre:
        f["level"], f["trend"] = 0.0, None
    else:
        h = hist_mean(d, "op_margin_hist_pct")       # smoothing: blend with prior fiscal years
        if om is not None and h is not None:
            om = 0.6 * om + 0.4 * h
        if om is None:
            f["level"] = None
        elif om < 0:
            f["level"] = 0.2 * lin(om, -40, 0)
        else:
            f["level"] = 0.2 + 0.8 * lin(om, 0, 45)
        if om is not None and om0 is not None:
            delta = (om - om0) + (0.5 * (gm - gm0) if gm is not None and gm0 is not None else 0)
            f["trend"] = clamp(0.5 + delta / 20)
        else:
            f["trend"] = None
    if d.get("peak_cycle"):
        for k in ("level", "trend", "rev", "gp"):
            if f.get(k) is not None:
                f[k] *= 0.65

    # Cash & balance sheet
    fcf, cash, debt = num(d.get("fcf_ttm_b")), num(d.get("cash_b")), num(d.get("debt_b"))
    if fcf is not None and rev and rev > 0 and not pre:
        m = fcf / rev * 100
        f["fcf"] = 0.33 * lin(m, -50, 0) if m < 0 else 0.33 + 0.67 * lin(m, 0, 30)
        if m < 0 and om is not None and om >= 10:   # profitable company spending on capacity
            f["fcf"] = max(f["fcf"], 0.5)
    elif pre:
        f["fcf"] = 0.0
    elif fcf_sign:                     # no TTM figure: fall back to the latest quarter's direction
        f["fcf"] = 0.6 if fcf_sign > 0 else (0.5 if (om or 0) >= 10 else 0.15)
    else:
        f["fcf"] = None
    if fcf is not None and fcf < 0 and cash is not None:
        f["balance"] = lin(cash / -fcf, 0, 4)                 # years of runway
    elif cash is not None and debt is not None:
        net_debt = debt - cash
        f["balance"] = 1.0 if net_debt <= 0 else clamp(1 - 0.5 * net_debt / max(rev or 1, 0.1), 0.2, 1)
    else:
        f["balance"] = None

    # Customers
    parts = []
    if num(d.get("customer_growth_pct")) is not None:
        parts.append(lin(d["customer_growth_pct"], 0, 30))
    if num(d.get("rev_per_customer_growth_pct")) is not None:
        parts.append(lin(d["rev_per_customer_growth_pct"], -5, 20))
    if num(d.get("nrr_pct")) is not None:
        n = d["nrr_pct"]
        parts.append(0.4 * lin(n, 85, 100) if n < 100 else 0.4 + 0.6 * lin(n, 100, 130))
    f["expansion"] = sum(parts) / len(parts) if parts else None
    t1, t3 = num(d.get("top_customer_pct")), num(d.get("top3_customers_pct"))
    if t1 is not None:
        f["concentration"] = 1 - lin(t1, 10, 50)
    elif t3 is not None:
        f["concentration"] = 1 - lin(t3, 25, 80)
    else:
        f["concentration"] = 0.85   # >10% customers must be disclosed, so silence usually means low concentration

    # Industry momentum (peers = same category in the watchlist)
    f["peer_growth"] = 0.3 + 0.7 * lin(peers["median_growth"], 0, 60) if peers["median_growth"] is not None else None
    f["peer_guidance"] = peers["raised_share"]

    # Forward signals
    bg = num(d.get("backlog_growth_pct"))
    gd = {"raised": 1.0, "maintained": 0.6, "none": 0.5, "cut": 0.0}.get((d.get("guidance") or "none").lower(), 0.5)
    f["pipeline"] = 0.6 * lin(bg, -10, 50) + 0.4 * gd if bg is not None else gd
    cs = d.get("contracts_90d") or []
    vals = sum(num(c.get("value_b")) or 0 for c in cs)
    ratio = vals / rev if rev else (1.0 if vals else 0)
    f["contracts"] = clamp(0.15 + 0.2 * len(cs) + ratio)
    tone = 0.5
    for item in (d.get("news_90d") or []) + news_extra:
        tone += {"good": 0.12, "bad": -0.2, "mixed": -0.03}.get(item.get("tone") or item.get("impact"), 0)
    f["news"] = clamp(tone)

    # Utility and durability
    inds = d.get("industries_served") or []
    f["industries"] = clamp(len(inds) / 5) if inds else None
    f["moat"] = DURABILITY.get(d["ticker"], 0.5)
    return f

def score(d, peers, news_extra, fcf_sign=0):
    f = subparts(d, peers, news_extra, fcf_sign)
    got, avail, parts = 0.0, 0.0, {}
    for p, subs in WEIGHTS.items():
        pg, pa = 0.0, 0.0
        for k, w in subs:
            if f.get(k) is not None:
                pg += w * f[k]; pa += w
        parts[p] = {"pts": pg, "avail": pa, "max": PART_MAX[p]}
        got += pg; avail += pa
    total = round(1000 * got / avail) if avail else 0
    k = 1000 / avail if avail else 0
    g = rev_growth(d) or 0
    boom = round(BOOM.get(d["ticker"], 0) * lin(g, 30, 90) * BOOM_MAX)
    total -= boom
    for p in parts:          # show each part on the same rescaled basis so the bars add up to the total
        parts[p] = {"pts": round(parts[p]["pts"] * k), "max": round(parts[p]["avail"] * k) if parts[p]["avail"] else 0,
                    "of": PART_MAX[p], "missing": parts[p]["avail"] == 0}
    parts["boom"] = {"pts": -boom, "max": 0, "of": BOOM_MAX, "missing": False}
    return total, parts, f

def main():
    data_dir, comp_path, out_path = sys.argv[1:4]
    news_path = sys.argv[4] if len(sys.argv) > 4 else None
    data = {}
    for fn in sorted(glob.glob(os.path.join(data_dir, "*.json"))):
        for d in json.load(open(fn)):
            data[d["ticker"]] = d
    companies = json.load(open(comp_path))
    weekly = json.load(open(news_path))["items"] if news_path and os.path.exists(news_path) else []
    missing = [c["ticker"] for c in companies if c["ticker"] not in data]
    if missing:
        print("WARNING no scoring data for:", missing)
    by_sec = {}
    for c in companies:
        by_sec.setdefault(c["section"], []).append(c["ticker"])
    peer_stats = {}
    for sec, ts in by_sec.items():
        gs = [rev_growth(data[t]) for t in ts if t in data and rev_growth(data[t]) is not None and not data[t].get("pre_revenue")]
        gds = [(data[t].get("guidance") or "none").lower() for t in ts if t in data]
        peer_stats[sec] = {"median_growth": statistics.median(gs) if gs else None,
                           "raised_share": (sum(g == "raised" for g in gds) / len(gds)) if gds else None}
    out = {}
    for c in companies:
        t = c["ticker"]
        if t not in data:
            continue
        extra = [i for i in weekly if t in (i.get("tickers") or [])]
        total, parts, f = score(data[t], peer_stats[c["section"]], extra, c.get("signs", {}).get("fcf", 0))
        out[t] = {"score": total, "parts": parts}
    json.dump(out, open(out_path, "w"), indent=1)
    ranked = sorted(out.items(), key=lambda kv: -kv[1]["score"])
    for i, (t, v) in enumerate(ranked, 1):
        print(f"{i:3d} {t:5s} {v['score']:4d}  " + " ".join(f"{p[:4]}:{v['parts'][p]['pts']:>3}" for p in list(WEIGHTS) + ["boom"]))

if __name__ == "__main__":
    main()
