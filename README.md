# FINN — AI Investment Assistant

> **Mobile-first AI platform for public equity investors on Indian markets (NSE/BSE)**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-green)](https://flask.palletsprojects.com)
[![Data](https://img.shields.io/badge/Data-NSE%20%7C%20yfinance%20%7C%20Screener.in-orange)](https://www.nseindia.com)

---

## What is FINN?

FINN cuts through market noise for active equity investors. It provides two core workflows:

### 🔔 Push Intelligence (Portfolio → Dashboard, Digest, Alerts)
- **Portfolio Dashboard**: Real-time quotes for 18 NSE stocks across 9 sectors with anomaly alerts
- **Configurable Anomaly Engine**: Configurable price move ($\pm X\%$) and volume spike ($> Y\times$ 20-day average) thresholds
- **Windowed Filing Digest (1h–7d)**: Intelligently categorizes corporate disclosures into ENAM's official 17 categories
- **Enriched Earnings Cut**: Headline 4-metric flash (Revenue, EBITDA, PBT, PAT) with QoQ & YoY comparisons
- **Enriched Management Transition**: Executive leadership change card with former pedigree, LinkedIn search, and concall diligence questions
- **Collapsible Routine Paperwork**: ESOPs, duplicate share certificate filings, and routine compliance paperwork automatically buried to eliminate noise

### 🔬 Pull Research (8-Pillar Institutional Analysis)
- **Arbitrary NSE Symbol Research**: Deep-dive any listed company (generalizable, not hardcoded to demo stocks)
- **Pillar 1 — Business Snapshot**: Core business description, operating segments & percentage revenue mix
- **Pillar 2 — Financial Snapshot**: Headline valuation, ROCE, ROE, margins, and key financial ratios
- **Pillar 3 — Trajectory**: Multi-year direction, revenue CAGR, operating leverage, what's expanding vs compressing
- **Pillar 4 — Balance Sheet**: Debt-to-Equity (D/E), gross debt, working capital buffer, solvency rating
- **Pillar 5 — Cash Quality**: Cash conversion ratio (Operating Cash Flow / PAT), Free Cash Flow, capex intensity
- **Pillar 6 — Narrative vs. Numbers (Worked Example)**: 4-quarter accountability audit comparing management's past promises vs actual delivery with primary source citations
- **Pillar 7 — Forward Guidance**: Management's forward commitments on topline growth, margin band, and annual capex
- **Pillar 8 — Bull vs. Bear Thesis**: Tight, data-grounded bull and bear cases strictly tied to primary documents
- **Interactive Audio Dispatch**: 30-second spoken executive portfolio briefing powered by voice synthesis

---

## Quick Start

```bash
# 1. Clone / navigate to project
cd finn

# 2. Install dependencies
pip install flask flask-cors

# 3. (Optional) Configure Gemini API for enriched analysis
cp .env.example .env
# Edit .env and add GEMINI_API_KEY=...

# 4. Run
cd backend
python app.py

# 5. Open http://localhost:5000 on mobile or desktop
```

---

## Architecture

```
finn/
├── backend/
│   ├── app.py          # Flask REST API (10 endpoints)
│   ├── portfolio.py    # Portfolio config (18 stocks) + filing classification rules
│   ├── market_data.py  # yfinance integration: quotes, history, financials, anomaly detection
│   ├── filings.py      # NSE/BSE announcements fetch, classify, cache
│   ├── analysis.py     # Financial analysis engine: QoQ/YoY/cash quality/bull-bear
│   └── cache/          # JSON file cache (TTL-based)
├── frontend/
│   └── index.html      # Single-file mobile-first SPA (pure HTML/CSS/JS, no build step)
├── .env.example
└── README.md
```

### Data Flow

```
User → Frontend SPA → Flask API → [yfinance | NSE API | Screener.in]
                                 ↓
                             Cache Layer (JSON, TTL-based)
                                 ↓
                         Analysis Engine (deterministic)
                                 ↓
                         (Optional) Gemini Flash for enrichment
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check + config status |
| GET | `/api/portfolio/meta` | Portfolio composition |
| GET | `/api/portfolio/quotes` | Live quotes + anomaly detection |
| GET | `/api/portfolio/filings?window_hours=24` | Filing digest with classification |
| GET | `/api/portfolio/alerts` | Unified alert feed |
| GET | `/api/research/{symbol}` | Full research analysis |
| GET | `/api/research/{symbol}/historical` | Price history for charts |
| GET | `/api/research/{symbol}/filings` | Filing history |
| GET | `/api/research/{symbol}/screener` | Screener.in data |
| POST | `/api/classify` | Classify any filing subject |

---

## Data Sources

| Source | What | Access |
|--------|------|--------|
| **yfinance** | EOD prices, financials, fundamentals | Free, public |
| **NSE India API** | Corporate announcements | Public (rate-limited) |
| **Screener.in** | Ratios, pros/cons, quarterly tables | Public scrape |
| **Gemini API** | Executive enrichment (optional) | Free tier with API key |

> **Important**: FINN never uses third-party news, analyst reports, or unverified data sources. All financial claims are derived deterministically from the above primary sources.

---

## Filing Priority Classification

FINN classifies every NSE/BSE announcement into 4 tiers:

| Priority | Examples | Action |
|----------|----------|--------|
| 🔴 Critical | Quarterly results, M&A, CEO change, dividend, buyback | Immediate review |
| 🟠 High | Credit rating, capex announcement, analyst concall | Review today |
| 🟡 Medium | Shareholding pattern, AGM notice, trading window | Review this week |
| ⚫ Routine | Compliance filings, newspaper ads, address changes | Bulk bury |

---

## Trade-offs & Design Decisions

### What was built
- **Thin-but-working**: Two complete workflows (Push + Pull) tested end-to-end
- **No Node.js**: Pure Python backend + vanilla HTML/CSS/JS = zero build step, instant deploy
- **Deterministic financials**: All QoQ/YoY/cash quality computed with actual math, not LLM guesses
- **Graceful degradation**: NSE API has rate limits; FINN falls back to demo data with clear labeling
- **File-based cache**: Simple, robust, no Redis dependency; TTL-based, appropriate for EOD data

### What was deliberately omitted
- **WebSockets for real-time**: NSE doesn't offer free streaming; EOD data is the honest approach
- **Historical filing search**: Would require storing full NSE filing history (multi-GB)
- **Portfolio P&L tracking**: Requires user authentication + purchase price entry (future feature)
- **Multi-user auth**: Single-user MVP; adding auth is straightforward
- **PDF parsing**: pdfplumber available but NSE PDFs require OCR for scanned docs; skipped for reliability

### Future roadmap
1. Add portfolio P&L with purchase price tracking (SQLite via peewee)
2. WebSocket feed for intraday updates via NSE's unofficial websocket
3. Earnings calendar with pre-earnings research automation
4. Gemini Pro for full earnings call transcript analysis
5. Push notifications (PWA + Web Push API)
6. Multi-portfolio support with authentication

---

## AI Development Log

This project was built using Antigravity (Claude Sonnet 4.6 Thinking) with the following progression:

1. **Architecture design**: Chose Python Flask + vanilla SPA for zero-dependency deployment
2. **Data layer**: Built yfinance integration with TTL caching, NSE API with session handling
3. **Classification engine**: Rule-based priority scoring (deterministic, no LLM needed)
4. **Analysis engine**: Deterministic QoQ/YoY/cash quality calculations
5. **Frontend**: Mobile-first single-file SPA with canvas price charts
6. **Testing**: API health check, portfolio quotes, research flow, anomaly detection

---

## Covering Note

**Built**: FINN — a mobile-first AI investment assistant for NSE/BSE equity investors

**Key product decisions**:
- Chose NSE/yfinance/Screener.in over paid data providers to keep it deployable without credentials
- Classification is rule-based (keyword scoring) — more reliable and auditable than asking an LLM to prioritize filings
- Financial calculations (QoQ, YoY, cash quality) are all deterministic code, not LLM outputs
- LLM (Gemini) is used only for the optional executive enrichment feature where hallucination risk is lower and clearly labeled

**Key trade-offs**:
- NSE live API is rate-limited and requires session cookies; FINN gracefully falls back to demo data with clear labeling
- Chose simplicity (no DB, no auth, no build step) to ensure the app actually runs and is easy to evaluate

**What works end-to-end**:
- Portfolio dashboard with live NSE prices via yfinance
- Anomaly detection with configurable thresholds
- Filing digest with priority classification
- Full pull research for any NSE stock
- Price chart with 20-day MA overlay
- QoQ/YoY/cash quality analysis with sources

**Honest limitations**:
- NSE live announcement API may be unavailable (rate limits, CORS); demo data is shown with clear labeling
- yfinance data is EOD, not real-time
- Screener.in scraping may fail if they update their HTML structure
