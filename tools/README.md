# Build tools (used by Claude's scheduled tasks)

- `template.html`: the TCH30 page template (Claude version; `make_live.py` turns it into the GitHub `index.html`)
- `prepare.py`: turns the monthly ranking doc into `companies.json`
- `build.py`: computes market-cap weights and the carried-forward index value; writes `site_data.json` and `index_state.json`
- `render.py`: re-renders the Claude page from `site_data_claude.json` + `../news.json` (weekly news refresh)
- `index_state.json`: index value, weights and prices at the last monthly rebalance
- `site_data_claude.json`: the data embedded in the Claude page (includes the monthly price snapshot)

The live site reads `../site_data.json`, `../prices.json` (daily, from GitHub Actions) and `../news.json` (weekly, from Claude).
