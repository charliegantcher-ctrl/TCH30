#!/usr/bin/env python3
"""Attach TCH scores to companies.json and set the top 30 / tiers from the score order.

Usage: python3 apply_scores.py companies.json scores.json
- every company gets "score" and "score_parts"
- top 30 by score become TCH30 members, 6 per tier in score order
- "why" keeps the earlier written rationale when there is one and adds a score summary
"""
import json, sys

LABEL = {"growth": "growth", "profit": "profitability", "cash": "cash & balance sheet", "customers": "customers",
         "momentum": "industry momentum", "forward": "forward signals", "utility": "cross-industry use",
         "durability": "durability & moat"}

comp_path, score_path = sys.argv[1:3]
keep = "--keep-members" in sys.argv     # weekly refresh: update scores but leave TCH30 membership and tiers alone
companies = json.load(open(comp_path))
scores = json.load(open(score_path))

def summary(t, s):
    parts = {k: v for k, v in s["parts"].items() if k != "boom" and not v["missing"] and v["max"]}
    ratio = {k: v["pts"] / v["max"] for k, v in parts.items()}
    best = sorted(ratio, key=lambda k: -ratio[k])[:2]
    worst = min(ratio, key=lambda k: ratio[k])
    txt = f"Score {s['score']}/1000. Strongest in {LABEL[best[0]]} and {LABEL[best[1]]}; weakest in {LABEL[worst]}."
    boom = -s["parts"]["boom"]["pts"]
    if boom:
        txt += f" Loses {boom} points for AI boom risk."
    return txt

ranked = sorted((c for c in companies if c["ticker"] in scores), key=lambda c: -scores[c["ticker"]]["score"])
if not keep:
    for c in companies:
        for k in ("tier", "rank"):
            c.pop(k, None)
for i, c in enumerate(ranked, 1):
    s = scores[c["ticker"]]
    c["score"], c["score_parts"], c["score_rank"] = s["score"], s["parts"], i
    old_why = c.get("why", "")
    if old_why.startswith("Score "):           # drop a previous auto-summary
        old_why = old_why.split(" | ", 1)[1] if " | " in old_why else ""
    c["why"] = summary(c["ticker"], s) + (f" | {old_why}" if old_why else "")
    if i <= 30 and not keep:
        c["tier"], c["rank"] = (i - 1) // 6 + 1, i
json.dump(companies, open(comp_path, "w"), indent=1)
print("top 30:", " ".join(c["ticker"] for c in ranked[:30]))
