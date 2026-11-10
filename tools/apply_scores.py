#!/usr/bin/env python3
"""Attach TCH scores to companies.json and set the top 30 / tiers from the score order.

Usage: python3 apply_scores.py companies.json scores.json
- every company gets "score" and "score_parts"
- TCH30 membership uses a 15-point buffer: a current member is only replaced when an outsider
  scores at least BUFFER points higher than the weakest member (stops near-ties from flipping back
  and forth). Members dropped from the list are refilled with the best outsiders. Pass
  --no-buffer to pick the plain top 30 by score instead.
- members are ranked by score into 5 tiers of 6
- "why" keeps the earlier written rationale when there is one and adds a score summary
"""
import json, sys

LABEL = {"growth": "growth", "profit": "profitability", "cash": "cash & balance sheet", "customers": "customers",
         "momentum": "industry momentum", "forward": "forward signals", "utility": "cross-industry use",
         "durability": "durability & moat"}

comp_path, score_path = sys.argv[1:3]
keep = "--keep-members" in sys.argv     # weekly refresh: update scores but leave TCH30 membership and tiers alone
BUFFER = 0 if "--no-buffer" in sys.argv else 15
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
sc = lambda c: scores[c["ticker"]]["score"]

# Decide membership (before clearing old tiers)
members = [c for c in ranked if c.get("tier")] if BUFFER else []
outside = [c for c in ranked if c not in members]
while len(members) < 30 and outside:          # refill seats left by removed companies (or first run)
    members.append(outside.pop(0))
swaps = []
while outside and members:
    weakest = min(members, key=sc)
    if sc(outside[0]) < sc(weakest) + BUFFER:
        break
    challenger = outside.pop(0)
    members.remove(weakest); members.append(challenger); outside.append(weakest)
    outside.sort(key=lambda c: -sc(c))
    swaps.append((challenger["ticker"], sc(challenger), weakest["ticker"], sc(weakest)))
members.sort(key=lambda c: -sc(c))
member_rank = {c["ticker"]: i for i, c in enumerate(members, 1)}

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
    if c["ticker"] in member_rank and not keep:
        r = member_rank[c["ticker"]]
        c["tier"], c["rank"] = (r - 1) // 6 + 1, r
json.dump(companies, open(comp_path, "w"), indent=1)
if keep:
    print("membership unchanged (--keep-members)")
else:
    print("TCH30:", " ".join(c["ticker"] for c in members))
    for a, sa, b, sb in swaps:
        print(f"  {a} ({sa}) replaces {b} ({sb})")
    if BUFFER and outside:
        weakest = min(members, key=sc)
        near = [c for c in outside if sc(c) > sc(weakest)]
        if near:
            print(f"  held by the {BUFFER}-point buffer: " + ", ".join(f"{c['ticker']} {sc(c)}" for c in near)
                  + f" (weakest member {weakest['ticker']} {sc(weakest)})")
