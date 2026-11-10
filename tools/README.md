# Build tools (used by Claude's scheduled tasks)

- `template.html`: the TCH30 page template (Claude version; `make_live.py` turns it into the GitHub `index.html`)
- `prepare.py`: turns the monthly ranking doc into `companies.json`
- `build.py`: computes market-cap weights and the carried-forward index value; writes `site_data.json` and `index_state.json`
- `render.py`: re-renders the Claude page from `site_data_claude.json` + `../news.json` (weekly news refresh)
- `index_state.json`: index value, weights and prices at the last monthly rebalance
- `site_data_claude.json`: the data embedded in the Claude page (includes the monthly price snapshot)

The live site reads `../site_data.json`, `../prices.json` (daily, from GitHub Actions) and `../news.json` (weekly, from Claude).

## TCH score (added Nov 9, 2026)
- `score_data/*.json`: per-company inputs (see `score_data/SPEC.md` for fields)
- `score.py`: computes the 0-1000 score: `python3 score.py score_data companies.json scores.json ../news.json`
- `apply_scores.py`: attaches scores; monthly mode sets the top 30 and tiers by score; `--keep-members` (weekly) only updates scores
- `refresh_scores.py`: copies updated scores into `site_data_claude.json` and `../site_data.json` without changing members or the index
- `companies.json`: the 100 companies with the 8 data points, signs, scores, tiers
- `market_batch*.json`: market data used for the current TCH30 weights (Nov 6, 2026 close)

## Membership rules (decided Nov 10, 2026)
- Research and scoring: every month, plus extra stocks Charlie asks for mid-month.
- TCH30 membership: 15-point buffer (apply_scores.py). An outsider only replaces the weakest member
  if it scores at least 15 points higher. Seats freed by companies removed from the list are refilled
  with the best outsiders.
- For now membership can change every month. Planned later, once the dataset is larger (Charlie will
  say when): membership changes only on June 1 and December 1, and weights reset every 3 months
  (Mar 1, Jun 1, Sep 1, Dec 1).
