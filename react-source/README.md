# TCH30 — React

A React + Vite rebuild of https://charliegantcher-ctrl.github.io/TCH30/.

## Run

Requires Node.js 18+ (https://nodejs.org).

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # static site in dist/
```

## Live data

The app fetches `site_data.json`, `prices.json` and `news.json` from the published
GitHub Pages site, re-polls every 5 minutes and whenever the tab regains focus, and
has a manual refresh button in the header. To point it elsewhere (e.g. when deploying
`dist/` next to the JSON files), create `.env.local`:

```
VITE_DATA_BASE=./
```

## Publishing a change

`npm run build` creates one self-contained `index.html` (copied to
`../upload-to-github/index.html`). Upload that file to the root of the TCH30 repo
in place of the old one. It reads the JSON data files sitting next to it.

Never upload an `index.html` made by `tools/build.py`, `make_live.py` or
`render.py`: those use the old page design and would replace this site.

## Layout

- `src/lib/useTchData.js` – data fetching, polling, live-price helpers
- `src/components/LineChart.jsx` – responsive SVG chart with hover tooltip
- `src/views/` – Index, Sectors, News, The other 70, How it works
- `src/components/Drawer.jsx` – company detail panel
