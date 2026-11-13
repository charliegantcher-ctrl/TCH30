import { ScoreChip } from "../components/Bits";

const SCORE_ROWS = [
  ["Growth", "150", "Revenue and gross-profit growth, size-adjusted (big companies earn full marks at lower rates) and discounted when growth is bought through acquisitions"],
  ["Profitability", "150", "Operating margin and whether margins are widening; peak-cycle margins count less"],
  ["Cash & balance sheet", "125", "Free cash flow as a share of revenue, plus net cash or years of cash runway"],
  ["Customers", "75", "Customer growth, spend per customer, net revenue retention, and dependence on a few customers"],
  ["Industry momentum", "100", "Growth of the company's peers on the watchlist and how many raised guidance"],
  ["Forward signals", "125", "Backlog and guidance (50), big new contracts and investments (40), and news and intel from the weekly briefings (35)"],
  ["Cross-industry use", "75", "How many different industries rely on the company"],
  ["Durability & moat", "200", "How hard the company is to replace, from bottleneck owner down to pre-revenue bet"],
  ["AI boom risk", "up to −80", "Deducted when results lean on the AI build-out of a few big buyers in a position rivals can enter"],
];

export default function MethodView({ D }) {
  return (
    <div className="prose method">
      <h1 className="page-h">How TCH30 works</h1>
      <h2>Membership</h2>
      <p>
        TCH30 holds the 30 highest-ranked companies from a 100-stock tech watchlist (semiconductors, AI infrastructure, power and nuclear, space, quantum,
        robotics, software). Rankings score each company on durability of its 10–15 year role (~30%), growth quality with organic preferred over acquired
        (~25%), margins and their trend (~20%), free cash flow and balance sheet (~15%), and customer concentration and execution risk (~10%). Share price and
        valuation play no part in the ranking.
      </p>
      <p>
        The list is reviewed on the 1st of each month: 10 new companies are researched, the 10 weakest leave the watchlist, and the top 30 is re-ranked. A
        company enters TCH30 when it ranks in the top 30 and leaves when it falls out.
      </p>
      <h2>TCH score</h2>
      <p>Every stock gets a score out of 1,000. About 70% comes straight from the data and the rest from fixed rubrics. Membership is simply the 30 highest scores.</p>
      <div className="tblwrap">
        <table className="otbl">
          <thead><tr><th>Part</th><th>Points</th><th>What it measures</th></tr></thead>
          <tbody>
            {SCORE_ROWS.map(([a, b, c]) => (
              <tr key={a}><td><b>{a}</b></td><td className="num nowrap">{b}</td><td>{c}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <p>
        Metrics a company doesn't report are left out and the rest is scaled up, so no one loses points for silence. Colors: <ScoreChip s={800} /> elite,{" "}
        <ScoreChip s={650} /> strong, <ScoreChip s={550} /> fair, <ScoreChip s={450} /> below average, <ScoreChip s={300} /> weak, <ScoreChip s={0} /> very weak.
      </p>
      <h2>Weighting</h2>
      <p>
        Each member's weight is half its share of the 30 members' total market capitalisation plus half an equal share (1/30). Bigger companies still count for
        more, but no stock is too small to matter: the largest sits around 11% and the smallest around 1.7%.
      </p>
      <p>
        Each company page also shows a "business weight" for comparison: its share of the group's trailing-12-month sales, net income (losses count as zero),
        book value and dividends, equally blended. When a company's market weight is far above its business weight, the market is pricing in a lot of future
        growth; when it is below, the market is paying less for today's business.
      </p>
      <p>
        The index started at 1,000.00 on {D.asof}. The prior-month figure shown on the index page is hypothetical: today's weights applied to each member's
        price change over the month before launch.
      </p>
      <h2>When members change</h2>
      <p>
        Every company is re-researched and re-scored each month. A stock outside the TCH30 only replaces the weakest member if it scores at least{" "}
        <b>15 points higher</b>. This buffer stops near-ties from swapping in and out every month. Companies removed from the watchlist are replaced by the
        best-scoring outsiders.
      </p>
      <h2>Where the data comes from</h2>
      <ul>
        <li><b>Business figures</b> (revenue growth, margins, free cash flow, customers, retention, backlog): each company's own quarterly earnings release and SEC filings (8-K, 10-Q), or the investor-relations page for foreign companies such as TSMC, ASML and SK Hynix.</li>
        <li><b>Stock prices and the index chart:</b> Yahoo Finance daily closes (5 years) and 5-minute prices for the 1-day view, downloaded every weekday after the market closes.</li>
        <li><b>Market cap, 12-month sales, net income and book value:</b> financial data sites, refreshed in each monthly update.</li>
        <li><b>News and the news part of the score:</b> large, established outlets such as Reuters, Bloomberg, CNBC, The Wall Street Journal and the Financial Times, refreshed weekly.</li>
      </ul>
      <p>
        Keep in mind: earnings releases are written by the companies themselves. They choose which numbers to highlight and often lead with "adjusted" figures
        that leave out costs such as stock-based pay, so this site uses the official GAAP figures where possible. A few figures (for example SpaceX) come from
        secondary sources, and the figures for the 11 largest companies were gathered without saved source links, so they are worth checking against each
        company's own release.
      </p>
      <h2>Colors</h2>
      <p>
        Green means the figure is positive (growth up, margin above zero, cash flow positive, NRR at or above 100%). Red means negative. Grey means the company
        does not disclose it or it does not apply, such as NRR for a chipmaker. Operating margin uses the GAAP figure.
      </p>
      <h2>Limits</h2>
      <p>
        Prices and fundamentals are a snapshot, not live. Quarters differ by company. Figures come from company releases and data aggregators, which companies
        shape to show themselves well; several figures are computed. This page is for learning and research, not financial advice.
      </p>
    </div>
  );
}
