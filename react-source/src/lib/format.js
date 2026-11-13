export const usd = (v) =>
  v == null ? "n/d" : "$" + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export const num2 = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export const pct = (v, d = 1) =>
  v == null ? "n/d" : (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toFixed(d) + "%";

export const tone = (v) => (v == null ? "na" : v > 0 ? "up" : v < 0 ? "down" : "na");

export const cls = (s) => (s > 0 ? "g" : s < 0 ? "r" : "x");

export const money = (b) =>
  b == null
    ? "n/d"
    : (b < 0 ? "−" : "") +
      "$" +
      (Math.abs(b) >= 1000
        ? (Math.abs(b) / 1000).toFixed(2) + "T"
        : Math.abs(b) >= 1
        ? Math.abs(b).toFixed(1) + "B"
        : (Math.abs(b) * 1000).toFixed(0) + "M");

export const wpct = (w, d = 2) => (w * 100).toFixed(d) + "%";

/** Turn [label](https://...) markdown links into React nodes. */
export function linkify(text, React) {
  const out = [];
  const re = /\[([^\]]+)\]\((https:[^)\s]+)\)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    out.push(text.slice(last, m.index));
    out.push(
      React.createElement("a", { key: m.index, href: m[2], target: "_blank", rel: "noopener noreferrer" }, m[1])
    );
    last = re.lastIndex;
  }
  out.push(text.slice(last));
  return out;
}

export function timeAgo(date, now = Date.now()) {
  const s = Math.max(0, Math.round((now - date) / 1000));
  if (s < 10) return "just now";
  if (s < 60) return s + "s ago";
  const m = Math.round(s / 60);
  if (m < 60) return m + "m ago";
  return Math.round(m / 60) + "h ago";
}
