import { useMemo, useState } from "react";
import { SECTORS, secInfo } from "../lib/constants";

function Donut({ parts, center, sub }) {
  const [act, setAct] = useState(null);
  const R = 84, r = 54, cx = 100, cy = 100;
  let a = -Math.PI / 2;
  const P = (rad, t) => `${(cx + rad * Math.cos(t)).toFixed(2)},${(cy + rad * Math.sin(t)).toFixed(2)}`;
  const a_ = act != null ? parts[act] : null;
  return (
    <svg viewBox="0 0 200 200" role="img" aria-label={`${center} ${sub}`} onPointerLeave={() => setAct(null)}>
      {parts.map((p, i) => {
        const a0 = a, a1 = a + p.value * 2 * Math.PI;
        a = a1;
        const dim = act != null && act !== i ? 0.35 : 1;
        if (p.value >= 0.9999)
          return (
            <circle key={i} cx={cx} cy={cy} r={(R + r) / 2} fill="none" stroke={p.color} strokeWidth={R - r} opacity={dim} onPointerEnter={() => setAct(i)}>
              <title>{`${p.label}: ${p.text}`}</title>
            </circle>
          );
        const big = a1 - a0 > Math.PI ? 1 : 0;
        const mid = (a0 + a1) / 2, pop = act === i ? 4 : 0;
        return (
          <path
            key={i}
            d={`M${P(R, a0)} A${R},${R} 0 ${big} 1 ${P(R, a1)} L${P(r, a1)} A${r},${r} 0 ${big} 0 ${P(r, a0)} Z`}
            fill={p.color}
            stroke="var(--card)"
            strokeWidth="1.5"
            opacity={dim}
            style={{ transform: `translate(${pop * Math.cos(mid)}px,${pop * Math.sin(mid)}px)`, transition: "transform .15s, opacity .15s" }}
            onPointerEnter={() => setAct(i)}
          >
            <title>{`${p.label}: ${p.text}`}</title>
          </path>
        );
      })}
      <text x="100" y={a_ ? 94 : 97} textAnchor="middle" fontSize={a_ ? 13 : 22} fontWeight="700" fill="var(--ink)">
        {a_ ? a_.short : center}
      </text>
      <text x="100" y={a_ ? 112 : 116} textAnchor="middle" fontSize="10.5" fill="var(--muted)">
        {a_ ? a_.text : sub}
      </text>
    </svg>
  );
}

export default function SectorsView({ D }) {
  const { rows, n, hist, keys } = useMemo(() => {
    const m = {};
    D.top.forEach((c) => {
      const x = (m[c.section] = m[c.section] || { count: 0, weight: 0, tickers: [] });
      x.count++;
      x.weight += c.weight;
      x.tickers.push(c);
    });
    const rows = Object.entries(m)
      .map(([k, v]) => ({ key: k, ...secInfo(k), ...v }))
      .sort((a, b) => b.weight - a.weight);
    const hist = (D.history || []).filter((h) => h.sectors);
    const keys = SECTORS.map((x) => x[0]).filter((k) => hist.some((h) => h.sectors[k]));
    return { rows, n: D.top.length, hist, keys };
  }, [D]);

  const byCount = rows.slice().sort((a, b) => b.count - a.count || a.i - b.i);
  const short = (l) => (l.length > 18 ? l.slice(0, 17) + "…" : l);

  return (
    <>
      <h1 className="page-h">Sectors</h1>
      <p className="prose mut">
        Which corners of tech the TCH30 is made of. The left chart counts stocks; the right one shows how much of the index each sector actually is. A sector
        with a few giant companies can hold far more weight than its number of stocks suggests.
      </p>
      <div className="pies">
        <figure className="pie panel">
          <figcaption>By number of stocks</figcaption>
          <Donut parts={byCount.map((r) => ({ label: r.label, short: short(r.label), color: r.color, value: r.count / n, text: `${r.count} of ${n} stocks` }))} center={String(n)} sub="stocks" />
        </figure>
        <figure className="pie panel">
          <figcaption>By index weight</figcaption>
          <Donut parts={rows.map((r) => ({ label: r.label, short: short(r.label), color: r.color, value: r.weight, text: (r.weight * 100).toFixed(1) + "% of the index" }))} center="100%" sub="of the index" />
        </figure>
      </div>
      <div className="tblwrap">
        <table className="otbl">
          <thead>
            <tr>
              <th>Sector</th>
              <th className="r">Stocks</th>
              <th className="r">Share of stocks</th>
              <th className="r">Index weight</th>
              <th>Members</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.key}>
                <td><span className="swatch" style={{ background: r.color }} />{r.label}</td>
                <td className="r num">{r.count}</td>
                <td className="r num">{((r.count / n) * 100).toFixed(0)}%</td>
                <td className="r num">
                  <div className="wcell"><span className="wbar" style={{ width: `${(r.weight * 100).toFixed(1)}%`, background: r.color }} /><b>{(r.weight * 100).toFixed(1)}%</b></div>
                </td>
                <td className="num xs">{[...r.tickers].sort((a, b) => b.weight - a.weight).map((c) => c.ticker).join(", ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h2 className="sub-h">How the mix changes</h2>
      <p className="prose mut">
        {hist.length < 2
          ? `The mix is recorded at every monthly rebalance. This is the first snapshot (${hist.length ? hist[0].asof : "today"}); from the next rebalance on, this section shows how each sector's share of the index grows or shrinks over time.`
          : "Each bar is one monthly rebalance; segment size is the sector's share of the index weight."}
      </p>
      <div className="trend">
        {hist.map((h) => (
          <div className="trow" key={h.asof}>
            <span className="tdate num">{h.asof.replace(" close", "")}</span>
            <div className="tbar">
              {keys
                .filter((k) => h.sectors[k])
                .map((k) => {
                  const s = secInfo(k), w = h.sectors[k].weight;
                  return <span key={k} style={{ width: `${(w * 100).toFixed(2)}%`, background: s.color }} title={`${s.label}: ${(w * 100).toFixed(1)}% (${h.sectors[k].count} stocks)`} />;
                })}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
