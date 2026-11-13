import { useCallback, useEffect, useMemo, useState } from "react";
import { useTchData } from "./lib/useTchData";
import { timeAgo } from "./lib/format";
import IndexView from "./views/IndexView";
import SectorsView from "./views/SectorsView";
import NewsView from "./views/NewsView";
import WatchlistView from "./views/WatchlistView";
import MethodView from "./views/MethodView";
import Drawer from "./components/Drawer";

const VIEWS = [
  ["tch30", "TCH30 index"],
  ["sectors", "Sectors"],
  ["news", "News"],
  ["watchlist", "The other 70"],
  ["method", "How it works"],
];

const readHash = () => {
  const v = (location.hash || "#tch30").slice(1);
  return VIEWS.some((x) => x[0] === v) ? v : "tch30";
};

function useHashRoute() {
  const [v, setV] = useState(readHash);
  useEffect(() => {
    const f = () => {
      setV(readHash());
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", f);
    return () => window.removeEventListener("hashchange", f);
  }, []);
  return v;
}

function useTheme() {
  const [t, setT] = useState(() => {
    try { return localStorage.getItem("tch30-theme") || "auto"; } catch { return "auto"; }
  });
  useEffect(() => {
    if (t === "auto") delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = t;
    try { localStorage.setItem("tch30-theme", t); } catch { /* storage unavailable */ }
  }, [t]);
  const next = { auto: "dark", dark: "light", light: "auto" };
  return [t, () => setT(next[t])];
}

function useNow(ms = 1000) {
  const [n, setN] = useState(Date.now());
  useEffect(() => {
    const id = setInterval(() => setN(Date.now()), ms);
    return () => clearInterval(id);
  }, [ms]);
  return n;
}

function LiveStatus({ data }) {
  const now = useNow();
  const { P, D, fetchedAt, refreshing, reload, error, everyMs } = data;
  const nextIn = fetchedAt ? Math.max(0, Math.round((fetchedAt.getTime() + everyMs - now) / 1000)) : null;
  return (
    <div className="live">
      <span className={"live-dot" + (error ? " err" : "")} />
      <span className="live-txt">
        {P ? <>Prices updated <b>{P.updated}</b></> : D ? <>Prices: {D.asof}</> : "Connecting…"}
        {fetchedAt && (
          <span className="live-sub">
            {" "}· checked {timeAgo(fetchedAt, now)}
            {nextIn != null && ` · next ${Math.floor(nextIn / 60)}:${String(nextIn % 60).padStart(2, "0")}`}
          </span>
        )}
      </span>
      <button className={"icon-btn" + (refreshing ? " spin" : "")} onClick={reload} title="Refresh data now" aria-label="Refresh data now">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 12a9 9 0 1 1-2.64-6.36" />
          <path d="M21 3v6h-6" />
        </svg>
      </button>
    </div>
  );
}

export default function App() {
  const data = useTchData();
  const view = useHashRoute();
  const [theme, cycleTheme] = useTheme();
  const [open, setOpen] = useState(null);
  const onOpen = useCallback((t) => setOpen(t), []);
  const onClose = useCallback(() => setOpen(null), []);
  const { D, P, N, status, error, reload } = data;
  const members = useMemo(() => new Set(D ? D.top.map((c) => c.ticker) : []), [D]);

  return (
    <>
      <header className="top">
        <div className="wrap">
          <a className="brand" href="#tch30">
            <span className="logo" aria-hidden>
              <svg viewBox="0 0 32 32" width="26" height="26"><rect width="32" height="32" rx="8" fill="var(--accent)" /><path d="M6 22 L12 15 L17 18 L26 8" stroke="#fff" strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </span>
            <span className="brand-txt">TCH<span>30</span></span>
          </a>
          <nav>
            {VIEWS.map(([k, l]) => (
              <a key={k} href={"#" + k} aria-current={view === k ? "page" : undefined}>
                {l}
              </a>
            ))}
          </nav>
          <div className="top-right">
            <LiveStatus data={data} />
            <button className="icon-btn" onClick={cycleTheme} title={`Theme: ${theme}`} aria-label={`Theme: ${theme}. Click to change`}>
              {theme === "dark" ? "☾" : theme === "light" ? "☀" : "◐"}
            </button>
          </div>
        </div>
      </header>

      <main className="wrap view" key={view}>
        {status === "loading" && <Skeleton />}
        {status === "error" && (
          <div className="panel error">
            <h2>Couldn't load the TCH30 data feed</h2>
            <p className="mut">{error}</p>
            <button className="btn" onClick={reload}>Try again</button>
          </div>
        )}
        {D && (
          <>
            {error && <div className="banner">Last refresh failed ({error}). Showing the previous data.</div>}
            {view === "tch30" && <IndexView D={D} P={P} onOpen={onOpen} />}
            {view === "sectors" && <SectorsView D={D} />}
            {view === "news" && <NewsView N={N} onOpen={onOpen} members={members} />}
            {view === "watchlist" && <WatchlistView D={D} />}
            {view === "method" && <MethodView D={D} />}
          </>
        )}
      </main>

      <footer className="foot">
        <div className="wrap">
          TCH30 is for learning and research, not financial advice. Data refreshes automatically every 5 minutes from the published feed.
        </div>
      </footer>

      {D && <Drawer D={D} P={P} ticker={open} onClose={onClose} />}
    </>
  );
}

function Skeleton() {
  return (
    <div aria-busy="true" aria-label="Loading">
      <div className="panel sk" style={{ height: 330 }} />
      <div className="panel sk" style={{ height: 160, marginTop: 18 }} />
      <div className="grid" style={{ marginTop: 34 }}>
        {Array.from({ length: 6 }, (_, i) => <div key={i} className="panel sk" style={{ height: 200 }} />)}
      </div>
    </div>
  );
}
