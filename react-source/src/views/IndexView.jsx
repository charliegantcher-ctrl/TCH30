import { useMemo, useState } from "react";
import LineChart from "../components/LineChart";
import { DotKey, Dots, ScoreChip, Seg } from "../components/Bits";
import { PALETTE, RANGES, TIERS } from "../lib/constants";
import { money, num2, pct, tone, usd, wpct } from "../lib/format";
import { daySeries, fallbackSeries, liveSeries, withLive } from "../lib/useTchData";

function sliceRange(P, r) {
  const ix = P.index, end = ix[ix.length - 1][0];
  if (r === "1D") return P.intraday && P.intraday.points && P.intraday.points.length > 2 ? P.intraday.points : ix.slice(-2);
  const d = new Date(end + "T12:00:00Z");
  if (r === "1W") d.setUTCDate(d.getUTCDate() - 7);
  if (r === "1M") d.setUTCMonth(d.getUTCMonth() - 1);
  if (r === "1Y") d.setUTCFullYear(d.getUTCFullYear() - 1);
  if (r === "5Y") d.setUTCFullYear(d.getUTCFullYear() - 5);
  const from = d.toISOString().slice(0, 10);
  const s = ix.filter((p) => p[0] >= from);
  return s.length < 2 ? ix.slice(-2) : s;
}

// benchmark values on the same x points as s, rescaled to start at the same level as the index
function benchFor(P, s, r) {
  let raw;
  if (r === "1D") {
    if (!(P.intraday && P.intraday.bench && P.intraday.points === s)) return null;
    raw = P.intraday.bench.map((p) => p[1]);
  } else {
    if (!P.bench || !P.bench.length) return null;
    let last = null, j = 0;
    raw = s.map((p) => {
      while (j < P.bench.length && P.bench[j][0] <= p[0]) last = P.bench[j++][1];
      return last;
    });
  }
  const k = raw.findIndex((v) => v != null);
  if (k < 0) return null;
  const f = s[k][1] / raw[k];
  return raw.map((v) => (v == null ? null : v * f));
}

function Hero({ D, P }) {
  const [r, setR] = useState("1Y");
  const live = P && P.index && P.index.length > 1;

  const view = useMemo(() => {
    if (!live) return null;
    const ix = P.index, last = ix[ix.length - 1][1];
    const baseP = ix.find((p) => p[0] >= P.base_date) || ix[0];
    const s = sliceRange(P, r);
    const b = benchFor(P, s, r);
    const chg = (s[s.length - 1][1] / s[0][1] - 1) * 100;
    const bchg = b && b[b.length - 1] != null && b[0] != null ? (b[b.length - 1] / b[0] - 1) * 100 : null;
    const label = { "1D": P.intraday ? "on " + P.intraday.date : "last day", "1W": "past week", "1M": "past month", "1Y": "past year", "5Y": "past 5 years" }[r];
    const note = r === "5Y" && (new Date(ix[0][0]) - new Date(ix[ix.length - 1][0])) / 864e5 > -365 * 5 + 10 ? ` (back-test starts ${ix[0][0]})` : "";
    return { last, sinceBase: (last / baseP[1] - 1) * 100, s, b, chg, bchg, label: label + note };
  }, [P, r, live]);

  const top = useMemo(() => [...D.top].sort((a, b) => b.weight - a.weight), [D]);
  const big = top.slice(0, 8), rest = top.slice(8), restW = rest.reduce((s, c) => s + c.weight, 0);

  return (
    <div className="index-head panel">
      <div className="ih-left">
        <div className="eyebrow">TCH30 · half cap, half equal weighted</div>
        <div className="idx-val num">{num2(live ? view.last : D.index_value)}</div>
        {live ? (
          <>
            <div className="idx-chg">
              <span className={"pill " + tone(view.chg)}>{pct(view.chg)}</span>
              <span className="mut"> {view.label}</span>
              {view.bchg != null && (
                <span className="mut">
                  {" "}· {P.bench_name} {pct(view.bchg)} ·{" "}
                  <b className={tone(view.chg - view.bchg)}>
                    {view.chg >= view.bchg ? "beating" : "trailing"} by {Math.abs(view.chg - view.bchg).toFixed(1)} pts
                  </b>
                </span>
              )}
            </div>
            <Seg value={r} options={RANGES} onChange={setR} label="Chart range" />
            <LineChart
              s={view.s}
              bench={view.b}
              height={190}
              up={view.chg >= 0}
              baseDate={r === "1D" ? null : P.base_date}
              interactive
              axis
              benchName={P.bench_name}
              whenLabel={(p) => (r === "1D" ? (p[0] === "Prev close" ? "Previous close" : `${P.intraday.date} ${p[0]} ET`) : p[0])}
              ariaLabel={`TCH30 vs ${P.bench_name}, ${view.s[0][0]} to ${view.s[view.s.length - 1][0]}`}
              className="idxchart"
            />
            {view.b && (
              <div className="legend-line">
                <i className="lg-i" style={{ borderTopColor: view.chg >= 0 ? "var(--up)" : "var(--down)" }} /> TCH30
                <i className="lg-b" /> {P.bench_name} (scaled to the same start)
              </div>
            )}
            <p className="idx-sub">
              Since the {P.base_date} rebalance: <b className={tone(view.sinceBase)}>{pct(view.sinceBase)}</b>. Left of the dashed line is a
              back-test with current weights.
            </p>
          </>
        ) : (
          <>
            <div className="idx-chg">
              <span className={"pill " + tone(D.index_1m_pct)}>{pct(D.index_1m_pct)}</span>
              <span className="mut"> hypothetical prior month</span>
            </div>
            <p className="idx-sub">
              Base 1,000.00 set at {D.history[0]?.asof}. Valued at {D.asof} prices. Live price feed unavailable right now.
            </p>
          </>
        )}
      </div>
      <div className="ih-right">
        <div className="eyebrow">Constituent weights</div>
        <div className="strip">
          {big.map((c, i) => (
            <div key={c.ticker} style={{ width: wpct(c.weight), background: PALETTE[i] }} title={`${c.ticker} ${wpct(c.weight, 1)}`}>
              {c.weight > 0.045 ? c.ticker : ""}
            </div>
          ))}
          <div style={{ width: wpct(restW), background: PALETTE[8] }} title={`${rest.length} others ${wpct(restW, 1)}`}>
            {restW > 0.06 ? "+" + rest.length : ""}
          </div>
        </div>
        <div className="legend">
          {top.map((c) => (
            <span key={c.ticker}>
              <b>{c.ticker}</b>
              <span className="num">{wpct(c.weight)}</span>
            </span>
          ))}
        </div>
        <div className="mix">Weight = half the member's share of the 30 members' total market value, plus half an equal 1/30 share.</div>
      </div>
    </div>
  );
}

function Movers({ D, P }) {
  if (!(P && P.latest)) return null;
  const rows = D.top
    .map((c) => {
      const L = P.latest[c.ticker];
      return L && L.chg_1d_pct != null ? { t: c.ticker, d: L.chg_1d_pct, pts: c.weight * L.chg_1d_pct, date: L.date } : null;
    })
    .filter(Boolean)
    .sort((a, b) => b.pts - a.pts);
  if (!rows.length) return null;
  const tot = rows.reduce((s, r) => s + r.pts, 0), mx = Math.max(...rows.map((r) => Math.abs(r.pts))) || 1;
  const up = rows.filter((r) => r.d > 0).length, dn = rows.filter((r) => r.d < 0).length;
  return (
    <details className="movers panel" open>
      <summary>
        <b>What moved the index on {rows[0].date}</b>
        <span>
          {up} up · {dn} down · total <b className={tone(tot)}>{pct(tot)}</b>
        </span>
      </summary>
      <p className="mv-note">
        Each stock's daily change, and how much it added to or took from TCH30 (its weight × its move, in % points). Biggest boosts at the top, biggest
        drags at the bottom.
      </p>
      <div className="mv-grid">
        {rows.map((r) => (
          <div className="mv-row" key={r.t} title={`${r.t}: ${pct(r.d)} today, ${r.pts >= 0 ? "adds" : "takes"} ${Math.abs(r.pts).toFixed(2)} pts of % to the index`}>
            <span className="mv-t">{r.t}</span>
            <span className={"mv-d " + tone(r.d)}>{pct(r.d)}</span>
            <span className="mv-bar">
              <i
                style={{
                  [r.pts >= 0 ? "left" : "right"]: "50%",
                  width: `${((Math.abs(r.pts) / mx) * 50).toFixed(1)}%`,
                  background: r.pts >= 0 ? "var(--up)" : "var(--down)",
                }}
              />
            </span>
            <span className={"mv-c " + tone(r.pts)}>
              {r.pts >= 0 ? "+" : "−"}
              {Math.abs(r.pts).toFixed(2)}
            </span>
          </div>
        ))}
      </div>
    </details>
  );
}

export function StockCard({ c, P, onOpen, i = 0 }) {
  const m = withLive(c, P);
  // default view: the latest trading day, same day as "What moved the index"
  const day = daySeries(P, c.ticker, m);
  const s = day || liveSeries(P, c.ticker) || fallbackSeries(m);
  const up = day ? s[s.length - 1][1] >= s[0][1] : (m.chg_1m_pct ?? 0) >= 0;
  const labelled = day ? s.map((p, i) => (i === s.length - 1 ? [p[0] === "Close" ? "Close" : p[0] + " ET", p[1]] : p)) : s;
  return (
    <button className="card" onClick={() => onOpen(c.ticker)} aria-label={`Open ${c.name} fundamentals`} style={{ animationDelay: `${Math.min(i, 12) * 25}ms` }}>
      <div className="card-top">
        <div>
          <div className="tkline">
            <span className="rank">#{c.rank}</span>
            <span className="tk">{c.ticker}</span>
            <ScoreChip s={c.score} />
          </div>
          <div className="nm">{c.name}</div>
        </div>
        <div className="px">
          <div className="p">{usd(m.price)}</div>
          {m.chg_1d_pct != null ? (
            <>
              <span className={"pill " + tone(m.chg_1d_pct)}>{pct(m.chg_1d_pct)} today</span>
              <div className="m1">{pct(m.chg_1m_pct)} 1m</div>
            </>
          ) : (
            <span className={"pill " + tone(m.chg_1m_pct)}>{pct(m.chg_1m_pct)} 1m</span>
          )}
        </div>
      </div>
      <LineChart
        s={labelled}
        height={58}
        up={up}
        refLine={day ? s[0][1] : null}
        ariaLabel={day ? `${c.ticker} price on ${m.date || "the latest session"}, from previous close` : `${c.ticker} price`}
      />
      <Dots c={c} />
      <div className="card-foot">
        <span>
          Weight <b className="num ink">{wpct(c.weight)}</b>
        </span>
        <span>
          Mkt cap <span className="num">{money(m.mcap_b)}</span>
        </span>
      </div>
    </button>
  );
}

const SORTS = [
  ["tier", "Tiers"],
  ["weight", "Weight"],
  ["today", "Today"],
  ["m1", "1 month"],
  ["small", "Smallest first"],
];

const SORT_NOTES = {
  small:
    "Smallest companies by market value first. A smaller company has more room to double than a giant, but it can also fall harder. This is size, not a forecast.",
};

function Board({ D, P, onOpen }) {
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("tier");
  const needle = q.trim().toLowerCase();
  const list = D.top.filter(
    (c) => !needle || c.ticker.toLowerCase().includes(needle) || c.name.toLowerCase().includes(needle) || (c.category || "").toLowerCase().includes(needle)
  );
  const key = {
    weight: (c) => c.weight,
    today: (c) => withLive(c, P).chg_1d_pct ?? -1e9,
    m1: (c) => withLive(c, P).chg_1m_pct ?? -1e9,
    small: (c) => -(withLive(c, P).mcap_b ?? 1e9),
  }[sort];

  return (
    <>
      <div className="toolbar">
        <input className="search" type="search" placeholder="Filter by ticker, name or category…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Filter constituents" />
        <Seg value={sort} options={SORTS} onChange={setSort} label="Sort constituents" />
      </div>
      <DotKey />
      {sort === "tier" && !needle ? (
        [1, 2, 3, 4, 5].map((t) => {
          const cs = list.filter((c) => c.tier === t).sort((a, b) => a.rank - b.rank);
          return (
            <section className="tier" key={t}>
              <div className="tier-h">
                <h2>{TIERS[t][0]}</h2>
                <p>{TIERS[t][1]}</p>
              </div>
              <div className="grid">
                {cs.map((c, i) => (
                  <StockCard key={c.ticker} c={c} P={P} onOpen={onOpen} i={i} />
                ))}
              </div>
            </section>
          );
        })
      ) : (
        <section className="tier">
          <div className="tier-h">
            <h2>{needle ? `${list.length} match${list.length === 1 ? "" : "es"}` : "All 30"}</h2>
            <p>{sort === "small" ? "Smallest market value first" : `Sorted by ${SORTS.find((x) => x[0] === sort)[1].toLowerCase()}`}</p>
          </div>
          {SORT_NOTES[sort] && !needle && <p className="sort-note">{SORT_NOTES[sort]}</p>}
          {list.length ? (
            <div className="grid">
              {[...list].sort(key ? (a, b) => key(b) - key(a) : (a, b) => a.rank - b.rank).map((c, i) => (
                <StockCard key={c.ticker} c={c} P={P} onOpen={onOpen} i={i} />
              ))}
            </div>
          ) : (
            <p className="empty">No constituents match “{q}”.</p>
          )}
        </section>
      )}
    </>
  );
}

export default function IndexView({ D, P, onOpen }) {
  return (
    <>
      <Hero D={D} P={P} />
      <Movers D={D} P={P} />
      <Board D={D} P={P} onOpen={onOpen} />
    </>
  );
}
