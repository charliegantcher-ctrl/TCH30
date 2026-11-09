# TCH30 live site: setup guide

This folder is a complete website. Once it's on GitHub, it updates itself with real stock prices every weekday after the market closes. It costs nothing and you don't write any code. You just need a free GitHub account and about 20 minutes.

## What's in the folder

| File | What it does |
|---|---|
| `index.html` | The website: TCH30 index, tiers, click-through fundamentals, the other 70 |
| `site_data.json` | Rankings, the 8 data points, and TCH30 weights (changes monthly) |
| `fetch_prices.py` | Downloads 1 year of daily prices for the 30 members and computes the TCH30 index line |
| `.github/workflows/update-prices.yml` | Tells GitHub to run `fetch_prices.py` every weekday at 4:30pm New York time and save `prices.json` |

`prices.json` doesn't exist yet. It's created the first time the update runs.

## One-time setup

1. **Create a GitHub account** at github.com (free).
2. **Create a repository.** Click **New repository**, name it `tch30`, choose **Public** (free GitHub Pages needs public repos), and click **Create repository**.
3. **Upload the files.** On the new repo page, click **uploading an existing file**. Drag in everything from this folder, including the `.github` folder. Your computer may hide folders starting with a dot: on Mac press `Cmd+Shift+.` in Finder to show them; on Windows turn on **View → Hidden items**. Click **Commit changes**.
   If the `.github` folder won't upload, create the file by hand: click **Add file → Create new file**, type `.github/workflows/update-prices.yml` as the name, paste the contents of that file, and commit.
4. **Let the update job save files.** Go to **Settings → Actions → General → Workflow permissions**, choose **Read and write permissions**, and click **Save**.
5. **Fetch prices for the first time.** Go to the **Actions** tab. If it asks, click **I understand my workflows, go ahead and enable them**. Click **Update TCH30 prices → Run workflow**. After a minute or two it should show a green check, and `prices.json` will appear in your repo.
6. **Turn on the website.** Go to **Settings → Pages**. Under **Source** pick **Deploy from a branch**, branch `main`, folder `/ (root)`, and click **Save**. After a minute your site is live at `https://YOUR-USERNAME.github.io/tch30/`.

After that, prices refresh every weekday by themselves.

## Monthly update (new rankings)

Each month, the Claude refresh writes a new `site_data.json` (members, tiers, weights, and the index value carried forward). To update your site:

1. Open your repo, click `site_data.json`, then the pencil icon (or **Add file → Upload files** and drop in the new one).
2. Commit. The site uses it immediately, and the next daily run charts the new members.

To skip this step, you could connect GitHub to Claude later and have the monthly task commit the file for you.

## How the pieces fit

```
Claude (monthly)                    GitHub Actions (every weekday)
 research → rankings → weights       yfinance → daily prices → TCH30 index
          │                                      │
          ▼                                      ▼
   site_data.json  ──────────►  your repo  ◄──── prices.json
                                   │
                              GitHub Pages
                                   │
                          index.html in your browser
```

- **Prices** come from `yfinance`, a free, unofficial Python library that reads Yahoo Finance. It isn't made by Yahoo, is meant for personal and educational use, and sometimes breaks briefly when Yahoo changes something; it's usually fixed within days. If it breaks for longer, a free API key from a provider like Twelve Data or Finnhub can replace it.
- **The TCH30 index** keeps each member's weight fixed between monthly rebalances: `value = base × Σ weight × price today ÷ price at rebalance`. Values before the first rebalance date are a back-test using the current weights.
- **Fundamentals** (the 8 data points) only change monthly, when Claude refreshes the rankings.

## Things to know

- **This is a learning tool, not financial advice.** The site separates business quality (the colored data points) from stock price so you can form your own view on valuation.
- **Public repo:** anyone with the link can see the site. Free GitHub Pages requires public repos.
- **Want to change something?** Every part is plain text. Ask Claude to modify `index.html` or `fetch_prices.py` and upload the new version the same way.
