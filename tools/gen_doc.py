#!/usr/bin/env python3
"""Write the "Top 100 tech stocks ranked" markdown doc from companies.json (with scores).

Usage: python3 gen_doc.py companies.json out.md "<Month D, YYYY>" [changelog.md]
changelog.md (optional): markdown bullet lines to put under "## Changelog", newest first.
"""
import json, sys

comp_path, out_path, date = sys.argv[1:4]
changelog = open(sys.argv[4]).read().strip() if len(sys.argv) > 4 else ""
C = json.load(open(comp_path))

def band(s):
    return ("Elite" if s >= 800 else "Strong" if s >= 650 else "Fair" if s >= 550
            else "Below average" if s >= 450 else "Weak" if s >= 300 else "Very weak")

top = sorted([c for c in C if c.get("tier")], key=lambda c: c["rank"])
ranked = sorted(C, key=lambda c: c.get("score_rank", 999))
L = []
A = L.append
A("# Top 100 tech stocks ranked\n")
A(f"*Updated {date}. Rankings use the TCH score (0–1,000). Latest-quarter data as reported by each company; quarters differ by company. Not financial advice.*\n")
A("## How the ranking works\n")
A("Every stock gets a TCH score out of 1,000. About 70% comes straight from reported data and the rest from fixed rubrics. TCH30, the index, holds the 30 highest scores, weighted half by market cap and half equally.\n")
A("| Part | Points | What it measures |\n|---|---|---|")
for r in [("Growth", "150", "Revenue and gross-profit growth, size-adjusted, discounted when acquired; smoothed with prior years when available"),
          ("Profitability", "150", "Operating margin level and trend; peak-cycle margins count less"),
          ("Cash & balance sheet", "125", "Free cash flow margin, net cash or years of runway"),
          ("Customers", "75", "Customer growth, spend per customer, net revenue retention, concentration"),
          ("Industry momentum", "100", "Peer growth on the watchlist and share of peers raising guidance"),
          ("Forward signals", "125", "Backlog and guidance (50), new contracts and investments (40), news and intel (35)"),
          ("Cross-industry use", "75", "How many industries rely on the company"),
          ("Durability & moat", "200", "How hard the company is to replace (fixed rubric)"),
          ("AI boom risk", "up to −80", "Deduction when results lean on a few AI buyers' spending in a contestable position")]:
    A(f"| {r[0]} | {r[1]} | {r[2]} |")
A("\nMissing metrics are left out and the rest is scaled up. Score bands: 800+ elite, 650–799 strong, 550–649 fair, 450–549 below average, 300–449 weak, under 300 very weak. Inputs and sources for every score are in the GitHub repo (charliegantcher-ctrl/TCH30, tools/score_data).\n")
A("## TCH30: the top 30 in five tiers\n")
for t in range(1, 6):
    lo = (t - 1) * 6 + 1
    A(f"### Tier {t}: Ranks {lo}–{lo + 5}\n")
    A("| # | Ticker | Rationale |\n|---|---|---|")
    for c in [x for x in top if x["tier"] == t]:
        A(f"| {c['rank']} | {c['ticker']} | {c['why'].replace('|', '—')} |")
    A("")
A("## All 100 scores\n")
A("| Rank | Ticker | Company | Score | Band | Boom-risk deduction |\n|---|---|---|---|---|---|")
for c in ranked:
    b = -c["score_parts"]["boom"]["pts"]
    A(f"| {c['score_rank']} | {c['ticker']} | {c['name']} | {c['score']} | {band(c['score'])} | {('−' + str(b)) if b else '—'} |")
A("\n## All 100 companies: latest-quarter data\n")
A("n/d = not disclosed; n/a = not applicable.\n")
secs = []
for c in C:
    if c["section"] not in secs:
        secs.append(c["section"])
for s in secs:
    A(f"### {s}\n")
    A("| Ticker | Company | Category | Period | Rev YoY | Organic | Cust growth | Rev/cust | GP growth | Op margin | FCF | NRR |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in [x for x in C if x["section"] == s]:
        A("| " + " | ".join(str(c[k]).replace("|", "/") for k in
                             ["ticker", "name", "category", "period", "rev", "organic", "cust", "revcust", "gp", "opm", "fcf", "nrr"]) + " |")
    A("")
A("## Caveats\n")
for x in ["Quarters differ by company; several report shortly after each update.",
          "Some companies lack 12-month revenue or cash-flow figures, so their scores lean on the latest quarter. Scores within about 30 points of each other can reshuffle.",
          "Durability, cross-industry use and boom risk are judgment calls on fixed rubrics; everything else is computed from reported figures.",
          "Figures come from company releases and data aggregators, which companies shape to look good. Several are computed. Valuation plays no part in the score.",
          "This is for learning and research, not financial advice."]:
    A(f"- {x}")
if changelog:
    A("\n## Changelog\n")
    A(changelog)
open(out_path, "w").write("\n".join(L) + "\n")
print("wrote", out_path)
