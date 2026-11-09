# Scoring data spec (TCH score research)

Today is November 9, 2026. For each assigned ticker, collect the fields below from the latest reported quarter / trailing twelve months, using company earnings releases, SEC filings and major outlets (Reuters, Bloomberg, WSJ, FT, CNBC, AP). Never invent numbers: use null when not found. Be efficient: about 2-3 searches per company.

Background notes for many companies already exist in /home/claude/research_notes/Top 100 tech stocks ranked/ (files 00-09). Read the file for your companies first and reuse what is there; only search for what is missing.

Write a JSON array to the output path you were given. One object per ticker with exactly these keys:

```json
{
  "ticker": "NVDA",
  "period": "Q3 FY27 (Oct-26) or TTM to Sep-26",
  "rev_ttm_b": 303.0,                 // trailing 12-month revenue, USD billions
  "rev_growth_ttm_pct": 85.0,         // TTM revenue vs prior TTM, %
  "rev_growth_q_pct": 106.0,          // latest quarter YoY, %
  "organic_share": 1.0,               // fraction of growth that is organic: 1.0 none acquired, 0.5 half, 0.0 all acquired; null if unknown
  "gross_margin_pct": 75.0,           // latest quarter
  "gross_margin_prior_pct": 72.4,     // same quarter a year earlier
  "op_margin_pct": 66.2,              // GAAP operating margin, latest quarter
  "op_margin_prior_pct": 62.0,        // same quarter a year earlier
  "fcf_ttm_b": 80.0,                  // TTM free cash flow, USD billions (negative if burning)
  "cash_b": 60.0,                     // cash + short-term investments
  "debt_b": 8.5,                      // total debt (exclude operating leases)
  "pre_revenue": false,
  "peak_cycle": false,                // true if margins are far above the company's historical range because of a commodity/pricing cycle (e.g. memory)
  "customer_growth_pct": null,        // only if disclosed
  "rev_per_customer_growth_pct": null,// only if disclosed or cleanly computable
  "nrr_pct": null,                    // only if disclosed
  "top_customer_pct": null,           // largest single customer as % of revenue, if disclosed
  "top3_customers_pct": null,
  "backlog_b": null,                  // backlog / RPO / contracted revenue, USD billions
  "backlog_growth_pct": null,         // YoY
  "guidance": "raised",               // "raised" | "maintained" | "cut" | "none" (latest guidance vs prior)
  "contracts_90d": [                  // major new contracts/partnerships in the last ~90 days (max 3)
    {"what": "10 GW supply deal with OpenAI", "value_b": null, "date": "2026-10-05", "source": "Reuters", "url": "https://..."}
  ],
  "investments": "1-2 lines: big capex/R&D/capacity plans, R&D % of revenue, and notable outside investors or stake changes",
  "news_90d": [                       // up to 3 most material news items, positive or negative
    {"what": "Board opens investigation into CEO", "tone": "bad", "date": "2026-11-08", "source": "TechCrunch", "url": "https://..."}
  ],
  "industries_served": ["AI data centers", "gaming", "automotive", "robotics", "scientific computing"],
  "bottleneck_note": "1 line: how hard this company is to replace (monopoly/duopoly position, switching costs, scale), and main competitors",
  "sources": ["https://...", "https://..."]
}
```

Rules:
- Paraphrase; no quotes.
- Treat company releases as promotional; prefer GAAP figures.
- Mark computed values in your reply summary (not in the JSON).
- Reply with a 3-5 line summary of gaps only.
