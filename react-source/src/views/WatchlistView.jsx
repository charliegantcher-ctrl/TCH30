import { useMemo, useState } from "react";
import { DotKey, ScoreChip } from "../components/Bits";
import { METRICS, secInfo } from "../lib/constants";
import { cls } from "../lib/format";

export default function WatchlistView({ D }) {
  const [q, setQ] = useState("");
  const needle = q.trim().toLowerCase();
  const bySec = useMemo(() => {
    const m = {};
    D.others
      .filter((c) => !needle || c.ticker.toLowerCase().includes(needle) || c.name.toLowerCase().includes(needle) || (c.category || "").toLowerCase().includes(needle))
      .forEach((c) => (m[c.section] ||= []).push(c));
    return Object.entries(m);
  }, [D, needle]);

  return (
    <>
      <h1 className="page-h">The other 70</h1>
      <p className="prose mut">
        The rest of the 100-stock watchlist. Each square is one of the eight fundamentals from the latest reported quarter: green is positive, red is negative,
        grey is not disclosed or not applicable. Full figures open only for TCH30 members.
      </p>
      <div className="toolbar">
        <input className="search" type="search" placeholder="Filter the watchlist…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Filter watchlist" />
      </div>
      <DotKey />
      {!bySec.length && <p className="empty">No watchlist companies match “{q}”.</p>}
      {bySec.map(([s, cs]) => (
        <div className="cat" key={s}>
          <h3><span className="swatch" style={{ background: secInfo(s).color }} />{s}</h3>
          <div className="tblwrap">
            <table className="otbl">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Company</th>
                  <th>Score</th>
                  {METRICS.map((m, i) => (
                    <th className="c" key={m[0]} title={m[1]}>{i + 1}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[...cs].sort((a, b) => (b.score || 0) - (a.score || 0)).map((c) => (
                  <tr key={c.ticker} title={c.why || ""}>
                    <td><b>{c.ticker}</b></td>
                    <td>{c.name}<div className="mut xs">{c.category}</div></td>
                    <td className="nowrap"><ScoreChip s={c.score} /> <span className="rank">#{c.score_rank || "–"}</span></td>
                    {METRICS.map(([k, l]) => (
                      <td className="c" key={k}>
                        <span className={"dot inl " + cls(c.signs[k])} title={`${l}: ${c[k] ?? "n/d"}`} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </>
  );
}
