import { useCallback, useEffect, useRef, useState } from "react";

// Where the live JSON feeds live. Override with VITE_DATA_BASE in .env.local
// (e.g. "./" once this build is deployed next to the JSON files).
export const DATA_BASE = (import.meta.env.VITE_DATA_BASE || "https://charliegantcher-ctrl.github.io/TCH30/").replace(
  /\/?$/,
  "/"
);

const get = async (file, required) => {
  try {
    const r = await fetch(`${DATA_BASE}${file}?t=${Date.now()}`, { cache: "no-store" });
    if (!r.ok) throw new Error(`${file}: HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    if (required) throw e;
    return null;
  }
};

/**
 * Loads site_data.json, prices.json and news.json, then re-polls on an interval
 * and whenever the tab becomes visible again.
 */
export function useTchData(everyMs = 5 * 60 * 1000) {
  const [state, setState] = useState({ status: "loading", D: null, P: null, N: null, error: null, fetchedAt: null, refreshing: false });
  const inFlight = useRef(false);

  const load = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    setState((s) => ({ ...s, refreshing: true }));
    try {
      const [D, P, N] = await Promise.all([get("site_data.json", true), get("prices.json"), get("news.json")]);
      setState({ status: "ready", D, P, N: N || D.news || null, error: null, fetchedAt: new Date(), refreshing: false });
    } catch (e) {
      setState((s) => ({ ...s, status: s.D ? "ready" : "error", error: String(e.message || e), refreshing: false }));
    } finally {
      inFlight.current = false;
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, everyMs);
    const onVis = () => document.visibilityState === "visible" && load();
    document.addEventListener("visibilitychange", onVis);
    return () => {
      clearInterval(id);
      document.removeEventListener("visibilitychange", onVis);
    };
  }, [load, everyMs]);

  return { ...state, reload: load, everyMs };
}

export const liveSeries = (P, t) => (P && P.series && P.series[t] && P.series[t].length > 5 ? P.series[t] : null);

export const withLive = (c, P) => {
  const L = P && P.latest && P.latest[c.ticker];
  return L ? { ...c.mkt, price: L.price, chg_1m_pct: L.chg_1m_pct, chg_1y_pct: L.chg_1y_pct, chg_1d_pct: L.chg_1d_pct, date: L.date } : c.mkt;
};

/** Fallback 3-point "sparkline" when no daily series is published for a ticker. */
export const fallbackSeries = (m) => {
  const now = m.price, pts = [];
  if (m.chg_1y_pct != null) pts.push(["1y ago", now / (1 + m.chg_1y_pct / 100)]);
  else if (m.chg_since_ipo_pct != null) pts.push(["IPO", now / (1 + m.chg_since_ipo_pct / 100)]);
  if (m.chg_1m_pct != null) pts.push(["1m ago", now / (1 + m.chg_1m_pct / 100)]);
  pts.push(["now", now]);
  return pts.length > 1 ? pts : [["", now], ["now", now]];
};
