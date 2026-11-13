export const METRICS = [
  ["rev", "Revenue growth (YoY)", "How quickly the company is growing"],
  ["organic", "Organic revenue growth", "How much growth comes from the existing business rather than acquisitions"],
  ["cust", "Customer growth", "Whether the company is attracting more customers"],
  ["revcust", "Revenue per customer", "Whether existing customers are spending more"],
  ["gp", "Gross profit growth", "Whether the company is generating more profit from its products"],
  ["opm", "Operating margin", "Whether the business is becoming more efficient"],
  ["fcf", "Free cash flow", "Whether growth is translating into actual cash"],
  ["nrr", "Net revenue retention (NRR)", "Whether existing customers are expanding their spending"],
];

export const TIERS = {
  1: ["Tier 1", "Ranks 1–6 by TCH score"],
  2: ["Tier 2", "Ranks 7–12"],
  3: ["Tier 3", "Ranks 13–18"],
  4: ["Tier 4", "Ranks 19–24"],
  5: ["Tier 5", "Ranks 25–30"],
};

export const BANDS = [
  [800, "#3B6D11", "#fff", "Elite"],
  [650, "#97C459", "#173404", "Strong"],
  [550, "#EF9F27", "#412402", "Fair"],
  [450, "#D85A30", "#fff", "Below avg"],
  [300, "#E24B4A", "#fff", "Weak"],
  [0, "#791F1F", "#fff", "Very weak"],
];
export const band = (s) => BANDS.find((b) => s >= b[0]) || BANDS[BANDS.length - 1];

export const PARTS = [
  ["growth", "Growth"],
  ["profit", "Profitability"],
  ["cash", "Cash & balance sheet"],
  ["customers", "Customers"],
  ["momentum", "Industry momentum"],
  ["forward", "Forward signals"],
  ["utility", "Cross-industry use"],
  ["durability", "Durability & moat"],
];

export const PALETTE = ["#2347c5", "#3a63d8", "#5580e0", "#7099e6", "#8aafe9", "#a3c2ec", "#5b6878", "#7f8b99", "#a2acb8"];

// fixed order + colors so a sector keeps its color month to month
export const SECTORS = [
  ["Semiconductors: compute, IP and power chips", "Chips: compute, IP & power", "#2347c5"],
  ["Semiconductor equipment and EDA", "Chip equipment & design software", "#5b8def"],
  ["Memory and storage", "Memory & storage", "#9db8f5"],
  ["AI networking, optics and servers", "AI networking, optics & servers", "#7b4fd6"],
  ["Neoclouds and data centers", "Neoclouds & data centers", "#b494ef"],
  ["Megacap platforms and enterprise cloud", "Megacap platforms & cloud", "#4a5568"],
  ["Data, AI and application software", "Data, AI & app software", "#13804a"],
  ["Security software", "Security software", "#5fbf8c"],
  ["Data-center power, cooling and grid equipment", "Data-center power & grid", "#d9822b"],
  ["Power generation and nuclear", "Power generation & nuclear", "#f2b766"],
  ["Batteries, solar and critical materials", "Batteries, solar & materials", "#a8761f"],
  ["Space", "Space", "#c2332b"],
  ["Quantum computing", "Quantum computing", "#e8776f"],
  ["Defense tech, robotics and future mobility", "Defense, robotics & mobility", "#8a96a3"],
];
export const secInfo = (name) => {
  const i = SECTORS.findIndex((x) => x[0] === name);
  return i < 0 ? { i: 99, label: name, color: "#9aa5b1" } : { i, label: SECTORS[i][1], color: SECTORS[i][2] };
};

export const RANGES = ["1D", "1W", "1M", "1Y", "5Y"];
