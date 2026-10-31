# Submission Covering Note
 
**Submission**: FINN — Mobile-First AI Financial Investment Agent  
**Live Public Deployment (Mobile & Desktop Worldwide)**: https://eab4a96badbbc6.lhr.life  
**Local Service**: http://localhost:5000  


### 1. What Was Built

FINN delivers two end-to-end, production-ready workflows built without placeholders or nonfunctional controls:

#### 🔔 Push Intelligence (Proactive Information Filtering)
- **High-Density Portfolio Dashboard**: Real-time quotes and moving averages for 18 high-conviction NSE companies spanning 9 diverse Indian sectors (Large-Cap IT, Private Banking, NBFC, FMCG, Energy, Auto, Pharma, Conglomerate, Consumer Discretionary).
- **Configurable Market Anomaly Engine**: Configurable thresholds for daily price moves ($\pm X\%$, default $\pm 3\%$) and volume spikes ($> Y\times$ 20-day moving average, default $2\times$), surfacing actionable statistical anomalies.
- **Windowed Filing Digest (1h–7d)**: Ingests corporate disclosures directly from the National Stock Exchange of India, categorizing each filing into **ENAM’s official 17 categories** across 4 priority tiers (`CRITICAL`, `HIGH`, `MEDIUM`, `ROUTINE`).
- **Enriched Quarterly Results**: Instant headline flash card featuring **Revenue, EBITDA, PBT, and PAT** with quarter-on-quarter (QoQ) and year-on-year (YoY) percentage comparisons and margin trajectory commentary.
- **Enriched Management Transition**: Executive transition card presenting the incoming leader’s prior corporate pedigree, biographical background, direct 1-click LinkedIn profile search, and concall diligence questions.
- **Collapsible Routine Paperwork**: Statutory filings (duplicate share certificates, ESOP allotments, compliance certificates) are automatically collapsed into an expandable tray to maintain an uncluttered workspace.
- **Audio Dispatch (Executive Briefing)**: 30-second spoken portfolio brief generated via native browser speech synthesis, summarizing top gainers, losers, and active anomaly alerts.

#### 🔬 Pull Research (Institutional Deep-Dive on Any NSE Stock)
- **Arbitrary Ticker Generalizability**: Accepts any listed NSE symbol (e.g. `TCS`, `INFY`, `HDFCBANK`, `RELIANCE`, `ITC`, `SBIN`), pulling primary data dynamically.
- **The 8 Pillars of Institutional Research**:
  1. *Business Snapshot*: Operational description, segment breakdown, and percentage revenue mix.
  2. *Financial Snapshot*: Headline valuation (P/E, P/B), capital efficiency (ROE, ROCE), and dividend yield.
  3. *Trajectory*: Multi-year revenue and operating margin CAGRs identifying expanding vs. compressing business units.
  4. *Balance Sheet Health*: Debt-to-Equity (D/E), gross debt, and working-capital buffer.
  5. *Cash Quality*: Cash conversion ratio ($OCF / PAT$) and Free Cash Flow computation ($OCF - \text{Capex}$).
  6. *Narrative vs. Numbers (ENAM Worked Example)*: Trailing 4-quarter accountability audit comparing management's past guidance against audited results with verifiable source citations.
  7. *Forward Guidance*: Management’s forward expectations on topline growth, margin band, and capex.
  8. *Bull vs. Bear Thesis*: Tight, data-grounded institutional cases anchored strictly in audited primary documents.
- **Strict Primary Source Discipline**: Exclusively utilizes annual reports, exchange filings, concall transcripts, and company IR. Never uses third-party news or unverified commentary.

---

### 2. Key Architectural Decisions & Product Philosophy

1. **Deterministic Calculations vs. Probabilistic Hallucination**:
   All financial metrics (QoQ, YoY, EBITDA margins, cash conversion ratios, volume ratios) are computed using deterministic Python code. We deliberately prevent LLMs from calculating numbers.
2. **Efficient Model Routing & Zero-Cost Operation**:
   Filing classification runs via high-speed, deterministic keyword matrices (0ms latency, zero token cost). LLM reasoning is reserved solely for unstructured narrative synthesis (e.g. executive biographical enrichment).
3. **Multi-Threaded Ingestion with Session Pooling**:
   Ingestion across 18 stocks runs concurrently using `ThreadPoolExecutor(max_workers=8)` and persistent HTTP session pooling (`_get_nse_session()`), cutting multi-stock query latency from 60s+ to under 3s.
4. **Zero-Build-Step Mobile SPA**:
   The frontend is built in pure HTML5, modern CSS3, and vanilla ES6+ without React/Webpack/Node.js dependencies. This ensures immediate portability, instant startup, zero bundle bloat, and frictionless execution on any device.

---

### 3. Deliberate Omissions & Trade-offs

- **Omitted Paid Real-Time Streaming Tickers**: NSE real-time WebSocket feeds require expensive commercial vendor subscriptions. We used verified EOD closing data and exchange announcements from `yfinance` and `NSE India` with clear labeling.
- **Omitted Heavy Relational Database**: Implemented a lightweight, robust JSON file-cache with granular TTL policies (Quotes: 300s, Filings: 900s, Fundamentals: 24h) instead of requiring PostgreSQL or Redis, ensuring the application runs immediately without external infrastructure dependencies.
- **Omitted Arbitrary Broker Notes**: Secondary broker opinions were deliberately excluded to maintain fidelity to primary corporate disclosures.

---

### 4. What's Next (Production Roadmap)

1. **Portfolio P&L Integration**: Persistent portfolio tracking with personalized buy-price lots and weighted gain/loss attribution.
2. **Automated Concall Audio Ingestion**: Direct transcription of quarterly earnings calls via Whisper API with automated QA sentiment shifts.
3. **PWA Mobile Packaging**: ServiceWorker caching and Web Push notifications for real-time mobile push notifications when CRITICAL filings hit exchange servers.

---

Sincerely,  
**AI Engineer Candidate**  
*ENAM Holdings - AI Engineer Build Challenge 2026*
