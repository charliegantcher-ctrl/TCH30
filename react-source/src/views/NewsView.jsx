import { useState } from "react";
import { Seg } from "../components/Bits";

const LABEL = { good: "Good", bad: "Bad", mixed: "Mixed" };

export default function NewsView({ N, onOpen, members }) {
  const [f, setF] = useState("all");
  const items = (N && N.items) || [];
  const norm = items.map((s) => ({ ...s, imp: ["good", "bad", "mixed"].includes(s.impact) ? s.impact : "mixed" }));
  const count = (k) => norm.filter((s) => s.imp === k).length;
  const shown = f === "all" ? norm : norm.filter((s) => s.imp === f);

  return (
    <>
      <div className="news-head">
        <h1 className="page-h">This week in the TCH30</h1>
        {items.length > 0 && <p className="mut">Week of {N.week_of} · {items.length} stories</p>}
      </div>
      <p className="prose mut">
        The biggest stories for the 30 members from major, credible outlets, refreshed every Sunday night. Green is good for the business, red is bad, amber is mixed.
      </p>
      {!items.length ? (
        <p className="empty">No news briefing yet. The first one arrives Sunday night.</p>
      ) : (
        <>
          <Seg
            value={f}
            onChange={setF}
            label="Filter by impact"
            options={[["all", `All ${items.length}`], ["good", `Good ${count("good")}`], ["bad", `Bad ${count("bad")}`], ["mixed", `Mixed ${count("mixed")}`]]}
          />
          <div className="news-list">
            {shown.map((s, i) => {
              const url = /^https?:\/\//.test(s.url || "") ? s.url : "";
              return (
                <article className={"story " + s.imp} key={s.title + i}>
                  <div className="story-top">
                    {(s.tickers || [s.ticker]).filter(Boolean).map((t) =>
                      members.has(t) ? (
                        <button key={t} className="tkchip" onClick={() => onOpen(t)} title={`Open ${t}`}>{t}</button>
                      ) : (
                        <span key={t} className="tkchip">{t}</span>
                      )
                    )}
                    <span className={"impact " + s.imp}>{LABEL[s.imp]}</span>
                    <span className="src">{s.date || ""}</span>
                  </div>
                  <h3>{url ? <a href={url} target="_blank" rel="noopener noreferrer">{s.title}</a> : s.title}</h3>
                  <p>{s.summary}</p>
                  <div className="src">
                    {s.source || ""}
                    {url && <> · <a href={url} target="_blank" rel="noopener noreferrer">{new URL(url).hostname.replace(/^www\./, "")} ↗</a></>}
                  </div>
                </article>
              );
            })}
          </div>
        </>
      )}
    </>
  );
}
