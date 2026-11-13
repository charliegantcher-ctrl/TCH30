import { useId, useLayoutEffect, useRef, useState } from "react";
import { num2, pct, tone } from "../lib/format";

function useWidth() {
  const ref = useRef(null);
  const [w, setW] = useState(0);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    setW(el.clientWidth);
    const ro = new ResizeObserver(() => setW(el.clientWidth));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, w];
}

/**
 * Responsive SVG line chart.
 * s: [[label, value], ...]; bench: values aligned with s (or null)
 */
export default function LineChart({
  s,
  bench = null,
  height = 160,
  up = true,
  baseDate = null,
  interactive = false,
  axis = false,
  whenLabel = (p) => p[0],
  benchName = "",
  valueFmt = num2,
  refLine = null,
  className = "",
  ariaLabel,
}) {
  const [ref, w0] = useWidth();
  const gid = "g" + useId().replace(/[^a-zA-Z0-9]/g, "");
  const [hov, setHov] = useState(null);
  const n = s ? s.length : 0;
  const w = Math.max(w0, 60);

  if (n < 2) return <div ref={ref} className={"chart " + className} style={{ height }} />;

  const padL = 4, padR = axis ? 52 : 4, padT = 10, padB = axis ? 22 : 14;
  const ys = s.map((p) => p[1]).concat(bench ? bench.filter((v) => v != null) : [], refLine != null ? [refLine] : []);
  let lo = Math.min(...ys), hi = Math.max(...ys);
  const span = hi - lo || Math.abs(hi) * 0.02 || 1;
  lo -= span * 0.06;
  hi += span * 0.06;
  const X = (i) => padL + (i / (n - 1)) * (w - padL - padR);
  const Y = (v) => padT + ((hi - v) / (hi - lo)) * (height - padT - padB);
  const base = height - padB;
  const col = up ? "var(--up)" : "var(--down)";

  const line = s.map((p, i) => `${i ? "L" : "M"}${X(i).toFixed(1)},${Y(p[1]).toFixed(1)}`).join("");
  const area = `${line}L${X(n - 1).toFixed(1)},${base}L${X(0).toFixed(1)},${base}Z`;
  let bpath = "";
  if (bench) {
    let pen = false;
    bench.forEach((v, i) => {
      if (v == null) { pen = false; return; }
      bpath += `${pen ? "L" : "M"}${X(i).toFixed(1)},${Y(v).toFixed(1)}`;
      pen = true;
    });
  }
  const bi = baseDate ? s.findIndex((p) => p[0] >= baseDate) : -1;
  const ticks = axis ? [0, 1, 2, 3].map((k) => lo + ((hi - lo) * (k + 0.5)) / 4) : [];

  const onMove = (e) => {
    if (!interactive) return;
    const r = e.currentTarget.getBoundingClientRect();
    const fx = e.clientX - r.left;
    const i = Math.round(((fx - padL) / (w - padL - padR)) * (n - 1));
    setHov(Math.max(0, Math.min(n - 1, i)));
  };

  const h = hov != null ? s[hov] : null;
  const hc = h ? (h[1] / s[0][1] - 1) * 100 : null;
  const bc = h && bench && bench[hov] != null && bench[0] != null ? (bench[hov] / bench[0] - 1) * 100 : null;

  return (
    <div ref={ref} className={"chart " + className} style={{ height }}>
      <svg
        width={w}
        height={height}
        viewBox={`0 0 ${w} ${height}`}
        role="img"
        aria-label={ariaLabel || `${s[0][0]} to ${s[n - 1][0]}`}
        onPointerMove={onMove}
        onPointerDown={onMove}
        onPointerLeave={() => setHov(null)}
        style={{ touchAction: interactive ? "pan-y" : "auto", cursor: interactive ? "crosshair" : "inherit" }}
      >
        <defs>
          <linearGradient id={gid} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={col} stopOpacity=".28" />
            <stop offset="100%" stopColor={col} stopOpacity="0" />
          </linearGradient>
        </defs>
        {ticks.map((t) => (
          <g key={t}>
            <line x1={padL} x2={w - padR} y1={Y(t)} y2={Y(t)} stroke="var(--grid)" />
            <text x={w - padR + 6} y={Y(t) + 3.5} className="ax">{t >= 1000 ? Math.round(t).toLocaleString("en-US") : t.toFixed(t < 10 ? 2 : 1)}</text>
          </g>
        ))}
        <line x1={padL} x2={w - padR} y1={base} y2={base} stroke="var(--rule)" />
        {refLine != null && <line x1={padL} x2={w - padR} y1={Y(refLine)} y2={Y(refLine)} stroke="var(--muted)" strokeDasharray="2 3" opacity=".6" />}
        {bi > 0 && <line x1={X(bi)} x2={X(bi)} y1={padT} y2={base} stroke="var(--muted)" strokeDasharray="3 4" opacity=".7" />}
        <path d={area} fill={`url(#${gid})`} />
        {bpath && <path d={bpath} fill="none" stroke="var(--bench)" strokeWidth="1.4" strokeDasharray="4 3" />}
        <path d={line} fill="none" stroke={col} strokeWidth={axis ? 2 : 1.7} strokeLinejoin="round" strokeLinecap="round" />
        <circle cx={X(n - 1)} cy={Y(s[n - 1][1])} r="3.2" fill={col} />
        <circle cx={X(n - 1)} cy={Y(s[n - 1][1])} r="3.2" fill={col} className="pulse" />
        <text x={padL} y={height - 2} className="ax">{s[0][0]}</text>
        <text x={w - padR} y={height - 2} className="ax" textAnchor="end">{s[n - 1][0]}</text>
        {h && (
          <g pointerEvents="none">
            <line x1={X(hov)} x2={X(hov)} y1={padT} y2={base} stroke="var(--muted)" strokeDasharray="2 3" />
            {bench && bench[hov] != null && <circle cx={X(hov)} cy={Y(bench[hov])} r="3.5" fill="var(--bench)" />}
            <circle cx={X(hov)} cy={Y(h[1])} r="4.5" fill="var(--card)" stroke={col} strokeWidth="2" />
          </g>
        )}
      </svg>
      {h && (
        <div className="tip" style={{ left: Math.max(70, Math.min(w - 70, X(hov))) }}>
          <b>{valueFmt(h[1])}</b> <span className={tone(hc)}>{pct(hc)}</span>
          {bc != null && (
            <>
              {" "}<span className="mut">· {benchName}</span> <span className={tone(bc)}>{pct(bc)}</span>
            </>
          )}
          <div className="mut">{whenLabel(h)}</div>
        </div>
      )}
    </div>
  );
}
