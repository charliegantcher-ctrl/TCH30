import { METRICS, PARTS, band } from "../lib/constants";
import { cls } from "../lib/format";

export function ScoreChip({ s }) {
  if (s == null) return null;
  const b = band(s);
  return (
    <span className="score" style={{ background: b[1], color: b[2] }} title={`TCH score: ${b[3]}`}>
      {s}
      <small>/1000</small>
    </span>
  );
}

export function Dots({ c }) {
  return (
    <div className="dots">
      {METRICS.map(([k, l]) => (
        <span key={k} className={"dot " + cls(c.signs[k])} title={l} />
      ))}
    </div>
  );
}

export function DotKey() {
  return (
    <div className="dotkey">
      {METRICS.map(([k, l], i) => (
        <span key={k}>
          <b>{i + 1}</b> {l}
        </span>
      ))}
      <span><span className="dot g inl" /> positive</span>
      <span><span className="dot r inl" /> negative</span>
      <span><span className="dot x inl" /> not disclosed / n/a</span>
    </div>
  );
}

export function ScoreBars({ c }) {
  if (!c.score_parts) return null;
  const boom = c.score_parts.boom;
  return (
    <div className="sbars">
      {PARTS.map(([k, l]) => {
        const p = c.score_parts[k];
        if (!p || p.missing || !p.max)
          return (
            <div className="sbar" key={k}>
              <span>{l}</span>
              <div className="trk" />
              <span className="v">not reported</span>
            </div>
          );
        const f = Math.max(0, Math.min(1, p.pts / p.max)), b = band(f * 1000);
        return (
          <div className="sbar" key={k}>
            <span>{l}</span>
            <div className="trk">
              <div className="fill" style={{ width: `${(f * 100).toFixed(0)}%`, background: b[1] }} />
            </div>
            <span className="v">
              {p.pts} / {p.max}
            </span>
          </div>
        );
      })}
      {boom && boom.pts ? (
        <div className="sbar">
          <span>AI boom risk</span>
          <div className="trk">
            <div className="fill" style={{ width: `${((-boom.pts / 80) * 100).toFixed(0)}%`, background: "#791F1F" }} />
          </div>
          <span className="v">{boom.pts}</span>
        </div>
      ) : null}
    </div>
  );
}

export function Seg({ value, options, onChange, label }) {
  return (
    <div className="seg" role="tablist" aria-label={label}>
      {options.map((o) => {
        const [v, t] = Array.isArray(o) ? o : [o, o];
        return (
          <button key={v} type="button" role="tab" aria-selected={value === v} onClick={() => onChange(v)}>
            {t}
          </button>
        );
      })}
    </div>
  );
}
