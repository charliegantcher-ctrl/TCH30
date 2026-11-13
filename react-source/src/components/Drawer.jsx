import React, { useEffect, useRef, useState } from "react";
import LineChart from "./LineChart";
import { ScoreBars, ScoreChip, Seg } from "./Bits";
import { METRICS } from "../lib/constants";
import { cls, linkify, money, pct, tone, usd, wpct } from "../lib/format";
import { fallbackSeries, liveSeries, withLive } from "../lib/useTchData";

function cut(s, r) {
  if (!s || r === "1Y") return s;
  const end = new Date(s[s.length - 1][0] + "T12:00:00Z");
  if (r === "1M") end.setUTCMonth(end.getUTCMonth() - 1);
  if (r === "3M") end.setUTCMonth(end.getUTCMonth() - 3);
  const from = end.toISOString().slice(0, 10);
  const out = s.filter((p) => p[0] >= from);
  return out.length > 1 ? out : s;
}

export default function Drawer({ D, P, ticker, onClose }) {
  const c = ticker ? D.top.find((x) => x.ticker === ticker) : null;
  const closeRef = useRef(null);
  const [r, setR] = useState("1Y");

  useEffect(() => {
    if (!c) return;
    setR("1Y");
    closeRef.current?.focus();
    const onKey = (e) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [c, onClose]);

  const open = !!c;
  let body = null;
  if (c) {
    const m = withLive(c, P);
    const live = liveSeries(P, c.ticker);
    const s = live ? cut(live, r) : fallbackSeries(m);
    const chg = (s[s.length - 1][1] / s[0][1] - 1) * 100;
    const [headline, detail] = (c.why || "").split(" | ");
    const ratio = c.w_fund ? c.weight / c.w_fund : null;
    body = (
      <>
        <div className="dr-head">
          <div>
            <span className="rank">
              Tier {c.tier} · #{c.rank}
            </span>
            <h2 id="dr-title">
              {c.ticker} <span className="dr-name">{c.name}</span>
            </h2>
            <div className="mut sm">
              {c.category} · latest quarter {c.period}
            </div>
          </div>
          <button className="close" ref={closeRef} onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="dr-price">
          <span className="num big">{usd(m.price)}</span>
          {m.chg_1d_pct != null && <span className={"pill " + tone(m.chg_1d_pct)}>{pct(m.chg_1d_pct)} today</span>}
          {live && <Seg value={r} options={["1M", "3M", "1Y"]} onChange={setR} label="Price range" />}
        </div>
        <LineChart s={s} height={150} up={chg >= 0} interactive axis valueFmt={usd} ariaLabel={`${c.ticker} price`} />

        <h3 className="dr-h">
          TCH score <ScoreChip s={c.score} />
        </h3>
        <ScoreBars c={c} />

        <h3 className="dr-h">The eight data points</h3>
        <div className="mgrid">
          {METRICS.map(([k, l, why]) => (
            <div key={k} className={"metric " + cls(c.signs[k])}>
              <span className="lbl">{l}</span>
              <span className="val">{c[k]}</span>
              <span className="why">{why}</span>
            </div>
          ))}
        </div>

        <div className="note">
          <b>Why it ranks here.</b> {linkify(headline || "", React)}
          {detail && <p>{linkify(detail, React)}</p>}
        </div>

        <h3 className="dr-h">Market vs. business</h3>
        <div className="facts">
          <div className="fact"><small>Price ({m.date || D.asof})</small><b>{usd(m.price)}</b></div>
          {m.chg_1d_pct != null && <div className="fact"><small>1-day change</small><b className={tone(m.chg_1d_pct)}>{pct(m.chg_1d_pct)}</b></div>}
          <div className="fact"><small>1-month change</small><b className={tone(m.chg_1m_pct)}>{pct(m.chg_1m_pct)}</b></div>
          <div className="fact">
            <small>{m.chg_1y_pct == null ? "Since IPO" : "1-year change"}</small>
            <b className={tone(m.chg_1y_pct ?? m.chg_since_ipo_pct)}>{pct(m.chg_1y_pct ?? m.chg_since_ipo_pct)}</b>
          </div>
          <div className="fact"><small>Market cap</small><b>{money(m.mcap_b)}</b></div>
          <div className="fact"><small>Sales (TTM)</small><b>{money(m.rev_ttm_b)}</b></div>
          <div className="fact"><small>Net income (TTM)</small><b className={tone(m.ni_ttm_b)}>{money(m.ni_ttm_b)}</b></div>
          <div className="fact"><small>Book value</small><b>{money(m.book_b)}</b></div>
          <div className="fact"><small>Price / sales</small><b>{m.rev_ttm_b ? (m.mcap_b / m.rev_ttm_b).toFixed(1) + "×" : "n/d"}</b></div>
          <div className="fact"><small>Price / earnings</small><b>{m.ni_ttm_b > 0 ? (m.mcap_b / m.ni_ttm_b).toFixed(1) + "×" : "n/m"}</b></div>
          <div className="fact"><small>TCH30 weight</small><b>{wpct(c.weight)}</b></div>
          <div className="fact"><small>Business weight (reference)</small><b>{wpct(c.w_fund)}</b></div>
        </div>
        {ratio != null && (
          <p className="mut sm" style={{ marginTop: 10 }}>
            Market weight is <b className="ink">{ratio.toFixed(2)}×</b> its business weight —{" "}
            {ratio > 1.15 ? "the market is pricing in a lot of future growth." : ratio < 0.85 ? "the market is paying less for today's business." : "roughly in line with today's business."}
          </p>
        )}
        <p className="mut xs" style={{ marginTop: 14 }}>
          Figures from company releases and data aggregators; quarters differ by company. Not financial advice.
        </p>
      </>
    );
  }

  return (
    <>
      <div className={"scrim" + (open ? " on" : "")} onClick={onClose} />
      <aside className={"drawer" + (open ? " on" : "")} aria-hidden={!open} role="dialog" aria-modal="true" aria-labelledby="dr-title">
        {body}
      </aside>
    </>
  );
}
