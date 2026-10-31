# FINN Architecture & Technical Specification

> **FINN** is a mobile-first, high-density AI investment assistant designed for active public-markets equity investors analyzing Indian equities (NSE & BSE).

---

## 1. System Architecture Overview

```
                               ┌────────────────────────────────────────┐
                               │   Mobile / Responsive Web Client       │
                               │   (HTML5 / Vanilla ES6+ / CSS3 SPA)    │
                               │   - Zero Build Step (Pure Browser)     │
                               │   - Interactive Canvas Charts (20d MA) │
                               │   - Web Speech Synthesis Audio Brief   │
                               └──────────────────┬─────────────────────┘
                                                  │ HTTP REST (JSON)
                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                Flask Application Gateway                               │
│                                                                                        │
│  ┌───────────────────────┐  ┌─────────────────────────┐  ┌──────────────────────────┐ │
│  │  Push Engine          │  │  Pull Engine (8 Pillars)│  │  Classification Engine   │ │
│  │  - /portfolio/quotes  │  │  - /research/<symbol>   │  │  - 17 Official Categories│ │
│  │  - /portfolio/filings │  │  - /research/historical │  │  - Priority Scoring      │ │
│  │  - /portfolio/alerts  │  │  - /research/screener   │  │  - Routine Paperwork Bury│ │
│  └───────────┬───────────┘  └────────────┬────────────┘  └────────────┬─────────────┘ │
└──────────────┼───────────────────────────┼────────────────────────────┼────────────────┘
               │                           │                            │
               ▼                           ▼                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           Concurrency & Ingestion Layer                                │
│                     ThreadPoolExecutor (8 Workers, Non-Blocking)                       │
│                     Persistent HTTP Connection & Session Pooling                       │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐              ┌──────────────────┐
│  Yahoo Finance   │             │  NSE India API   │              │   Screener.in    │
│  (yfinance)      │             │  Corporate Feed  │              │  Primary Source  │
│  - EOD Quotes    │             │  - Exchange Ann. │              │  - 10-Yr Balance │
│  - 20-Day MA     │             │  - Outcome Meets │              │  - Cash Flow     │
│  - OHLCV series  │             │  - Board Actions │              │  - Ratios        │
└────────┬─────────┘             └────────┬─────────┘              └────────┬─────────┘
         │                                │                                 │
         └────────────────────────────────┼─────────────────────────────────┘
                                          │
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               Cache & Persistence Layer                                │
│                         JSON Storage with Granular TTL Policies                        │
│           Quotes: 300s | Filings: 900s | Screener: 24h | Analysis: 4h                  │
│                        Graceful Stale-Cache Fallback Circuit                           │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Deterministic Financial Calculation Core                        │
│  - QoQ & YoY delta computation: Δ = (V_t - V_{t-1}) / |V_{t-1}|                        │
│  - Cash Conversion Ratio: Operating Cash Flow / Net Profit                             │
│  - Free Cash Flow: Operating Cash Flow - Capital Expenditure                           │
│  - Leverage & Solvency: Debt-to-Equity, Interest Coverage, Working Capital Buffer      │
│  - Promises vs. Delivered: 4-Quarter Guidance Alignment Audit                           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Modules & Responsibilities

### `backend/app.py`
- Serves the Single-Page Application (SPA) statically without proxy requirements.
- Exposes 10 REST endpoints with clean CORS headers and structured error responses.
- Enforces strict input validation and query normalization (handling both bare symbols like `TCS` and suffixed tickers like `TCS.NS`).

### `backend/portfolio.py`
- Houses the core institutional mock portfolio of 18 high-conviction companies spanning 9 distinct Indian economic sectors:
  - **IT Services**: TCS, Infosys, Wipro, HCL Tech
  - **Banking**: HDFC Bank, ICICI Bank, Kotak Mahindra Bank
  - **NBFC**: Bajaj Finance
  - **FMCG / Consumer Defensive**: Hindustan Unilever, Nestle India
  - **Energy & Petrochemicals**: Reliance Industries, ONGC
  - **Automotive**: Maruti Suzuki, Mahindra & Mahindra
  - **Healthcare & Pharma**: Sun Pharma, Dr. Reddy's Laboratories
  - **Conglomerate & Infrastructure**: Adani Enterprises
  - **Consumer Discretionary**: Titan Company
- Configures the official 17 ENAM Announcement Categories, their weights, and keyword classification rules.

### `backend/market_data.py`
- Integrates `yfinance` with parallelized thread-pool execution (`ThreadPoolExecutor(max_workers=8)`).
- Calculates 20-day moving averages and traded volume ratios:
  $$\text{Volume Ratio} = \frac{\text{Current Daily Volume}}{\mu_{20}(\text{Volume})}$$
- Detects market anomalies dynamically based on user-configurable sliders:
  - Price Move: $\pm X\%$ (Default $3\%$, range $1\%-10\%$)
  - Volume Spike: $> Y\times$ 20-day average (Default $2\times$, range $1.5\times-5\times$)
- Implements circuit-breaker fallback to last-known cached prices if Yahoo Finance throttles.

### `backend/filings.py`
- Connects to the National Stock Exchange of India (NSE) corporate announcements endpoint.
- Maintains a persistent session pool (`_get_nse_session()`) with session cookies, preventing connection handshake overhead across 18 concurrent requests.
- Classifies announcements into 4 priority bands (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW/ROUTINE`).
- Implements the two signature presentation formats requested by ENAM:
  1. **Enriched Quarterly Results**: Flash card featuring Revenue, EBITDA, PBT, and PAT with QoQ and YoY deltas and margin insights.
  2. **Enriched Management Transition**: Executive leadership card featuring incoming appointee biography, prior corporate pedigree, direct LinkedIn search link, and concall diligence questions.
- Automatically collapses routine filings (loss of share certificates, duplicate share issuances, routine ESOP compliance) into an expandable tray to preserve high signal density.

### `backend/analysis.py`
- Powers the Pull Research workflow for **any arbitrary NSE ticker**.
- Implements the 8 Pillars of Institutional Research:
  1. **Business Snapshot**: Operational description, segmental revenue breakdown, and growth trajectories.
  2. **Financial Snapshot**: Market capitalization, P/E, P/B, ROE, ROCE, and dividend yields.
  3. **Multi-Year Trajectory**: Trailing 4-year CAGRs, identifying expanding vs. compressing business lines.
  4. **Balance Sheet Health**: Debt-to-Equity (D/E), gross debt, working capital cycles, and solvency metrics.
  5. **Cash Quality Assessment**: Operating Cash Flow vs. PAT conversion analysis ($OCF / PAT > 0.9 = \text{High Quality}$).
  6. **Narrative vs. Numbers (ENAM Worked Example)**: 4-quarter audit comparing management's past forward commentary vs. audited reported numbers with primary source citations.
  7. **Forward Guidance**: Explicit management commitments on topline growth, operating margins, and capex intensity.
  8. **Bull vs. Bear Thesis**: Tight, data-grounded institutional arguments strictly anchored in audited primary reports.

---

## 3. The 17 Official ENAM Announcement Categories

FINN rigorously implements the official 17 categories provided in the ENAM companion specification:

| # | Category Key | Official Label | Priority | Keyword Rules |
|---|--------------|----------------|----------|---------------|
| 1 | `results` | Quarterly / Annual Results | CRITICAL | financial results, quarterly results, annual results, unaudited, audited |
| 2 | `M&A` | M&A / Demerger / JV | CRITICAL | acquisition, merger, amalgamation, demerger, joint venture, subsidiary stake |
| 3 | `fund_raise` | Fund Raise / Rights / Buyback | CRITICAL | fund raise, qip, rights issue, preferential allotment, buyback |
| 4 | `management_change` | Management Change | CRITICAL | change in management, resignation of, appointment of, cfo, ceo, md, kmp |
| 5 | `litigation` | Litigation / Regulatory Order | CRITICAL | litigation, lawsuit, nclt, insolvency, penalty, sebi order, tax demand |
| 6 | `dividend` | Dividend Declaration | CRITICAL | dividend, interim dividend, final dividend, record date |
| 7 | `bonus_split` | Bonus / Stock Split | HIGH | bonus issue, bonus shares, stock split, sub-division |
| 8 | `credit_rating` | Credit Rating Action | HIGH | credit rating, icra, crisil, care rating, rating reaffirm, downgrade |
| 9 | `capex` | Capex / Plant Expansion | HIGH | capex, capital expenditure, new plant, capacity expansion |
| 10 | `earnings_call` | Earnings Concall | HIGH | earnings call, concall, transcript, audio recording of call |
| 11 | `pledging` | Promoter Pledging | HIGH | promoter pledge, pledge of shares, release of pledge |
| 12 | `insider_trading` | Insider Trading / SAST | MEDIUM | insider trading, sast, pit regulation, acquisition of shares |
| 13 | `investor_meetings`| Investor Meetings | MEDIUM | analyst meet, investor meet, institutional investor, 1-on-1 |
| 14 | `press_release` | Press Release / Commercial | MEDIUM | press release, order win, contract award, commercial milestone |
| 15 | `postal_ballot` | Postal Ballot | LOW | postal ballot, voting results, scrutinizer report |
| 16 | `agm_egm` | AGM / EGM Notice | LOW | annual general meeting, extraordinary general meeting, agm, egm |
| 17 | `unclassified` | Routine Paperwork | LOW | routine compliance, loss of certificate, duplicate share, esop |

---

## 4. Mobile-First Interaction Design

The frontend is specifically crafted to serve as an indispensable daily mobile workflow tool:
- **Viewport Optimization**: Strict viewport lock, fluid CSS grid layouts, and thumb-friendly bottom navigation.
- **Micro-Interactions**: Filter chips with zero layout shift, skeleton loaders, and instant local tab switching.
- **Dynamic Visuals**: HTML5 Canvas rendering 6-month price trajectories with a 20-day Simple Moving Average overlay and peak/trough annotations.
- **Audio Dispatch (Executive Briefing)**: Uses the browser's native `window.speechSynthesis` API to generate a crisp 30-second spoken portfolio brief, reading current gainers, losers, and active anomaly alerts without consuming external audio API credits.
- **High Information Density**: Prioritizes numerical clarity, clean badge hierarchies, and collapsible routine paperwork to maximize investor focus.
