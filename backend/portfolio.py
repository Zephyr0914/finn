"""
FINN Portfolio Configuration
Mock portfolio of 18 NSE/BSE stocks across sectors
"""

PORTFOLIO = [
    # Large Cap IT
    {"symbol": "TCS.NS",    "name": "Tata Consultancy Services", "sector": "IT",           "exchange": "NSE", "isin": "INE467B01029"},
    {"symbol": "INFY.NS",   "name": "Infosys",                   "sector": "IT",           "exchange": "NSE", "isin": "INE009A01021"},
    {"symbol": "WIPRO.NS",  "name": "Wipro",                     "sector": "IT",           "exchange": "NSE", "isin": "INE075A01022"},
    # Banking & Finance
    {"symbol": "HDFCBANK.NS","name": "HDFC Bank",                "sector": "Banking",      "exchange": "NSE", "isin": "INE040A01034"},
    {"symbol": "ICICIBANK.NS","name": "ICICI Bank",              "sector": "Banking",      "exchange": "NSE", "isin": "INE090A01021"},
    {"symbol": "KOTAKBANK.NS","name": "Kotak Mahindra Bank",     "sector": "Banking",      "exchange": "NSE", "isin": "INE237A01028"},
    {"symbol": "BAJFINANCE.NS","name": "Bajaj Finance",          "sector": "NBFC",         "exchange": "NSE", "isin": "INE296A01024"},
    # Consumer / FMCG
    {"symbol": "HINDUNILVR.NS","name": "Hindustan Unilever",     "sector": "FMCG",         "exchange": "NSE", "isin": "INE030A01027"},
    {"symbol": "NESTLEIND.NS","name": "Nestle India",            "sector": "FMCG",         "exchange": "NSE", "isin": "INE239A01016"},
    # Energy & Resources
    {"symbol": "RELIANCE.NS","name": "Reliance Industries",      "sector": "Energy",       "exchange": "NSE", "isin": "INE002A01018"},
    {"symbol": "ONGC.NS",   "name": "ONGC",                     "sector": "Energy",       "exchange": "NSE", "isin": "INE213A01029"},
    # Auto
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki",             "sector": "Auto",         "exchange": "NSE", "isin": "INE585B01010"},
    {"symbol": "M&M.NS",       "name": "Mahindra & Mahindra",    "sector": "Auto",         "exchange": "NSE", "isin": "INE101A01026"},
    # Healthcare
    {"symbol": "SUNPHARMA.NS","name": "Sun Pharmaceutical",      "sector": "Pharma",       "exchange": "NSE", "isin": "INE044A01036"},
    {"symbol": "DRREDDY.NS","name": "Dr Reddy's Laboratories",   "sector": "Pharma",       "exchange": "NSE", "isin": "INE089A01023"},
    # Industrials / Conglomerate
    {"symbol": "ADANIENT.NS","name": "Adani Enterprises",        "sector": "Conglomerate", "exchange": "NSE", "isin": "INE423A01024"},
    {"symbol": "HCLTECH.NS","name": "HCL Technologies",         "sector": "IT",           "exchange": "NSE", "isin": "INE860A01027"},
    {"symbol": "TITAN.NS",  "name": "Titan Company",             "sector": "Consumer",     "exchange": "NSE", "isin": "INE280A01028"},
]

PORTFOLIO_SYMBOLS = [s["symbol"] for s in PORTFOLIO]

# Official 17 Announcement Categories from ENAM Reference Document
OFFICIAL_CATEGORIES = {
    "results": {"priority": "CRITICAL", "label": "Quarterly / Annual Results", "score": 100},
    "M&A": {"priority": "CRITICAL", "label": "M&A / Demerger / JV", "score": 95},
    "fund_raise": {"priority": "CRITICAL", "label": "Fund Raise / Rights / Buyback", "score": 90},
    "management_change": {"priority": "CRITICAL", "label": "Management Change", "score": 95},
    "litigation": {"priority": "CRITICAL", "label": "Litigation / Regulatory Order", "score": 90},
    "dividend": {"priority": "CRITICAL", "label": "Dividend / Record Date", "score": 85},
    "bonus_split": {"priority": "HIGH", "label": "Bonus / Stock Split", "score": 80},
    "credit_rating": {"priority": "HIGH", "label": "Credit Rating Action", "score": 75},
    "capex": {"priority": "HIGH", "label": "Capex / Plant Expansion", "score": 75},
    "earnings_call": {"priority": "HIGH", "label": "Earnings Call / Transcript", "score": 70},
    "pledging": {"priority": "HIGH", "label": "Promoter Pledging", "score": 70},
    "insider_trading": {"priority": "MEDIUM", "label": "Insider Trading / SAST", "score": 50},
    "investor_meetings": {"priority": "MEDIUM", "label": "Investor Meetings / 1-on-1", "score": 45},
    "press_release": {"priority": "MEDIUM", "label": "Press Release / Order Win", "score": 45},
    "postal_ballot": {"priority": "LOW", "label": "Postal Ballot", "score": 20},
    "agm_egm": {"priority": "LOW", "label": "AGM / EGM Notice", "score": 20},
    "unclassified": {"priority": "LOW", "label": "Routine Compliance Paperwork", "score": 10}
}

# Filing priority classification based on ENAM reference guide
FILING_PRIORITY = {
    "CRITICAL": {
        "keywords": [
            "quarterly results", "q1 results", "q2 results", "q3 results", "q4 results",
            "annual results", "financial results", "earnings",
            "board meeting outcome", "board meeting intimation",
            "acquisition", "merger", "amalgamation", "demerger", "restructuring",
            "change in management", "resignation", "appointment", "ceo", "cfo", "md",
            "managing director", "whole time director",
            "open offer", "buyback", "delisting", "rights issue", "ipo",
            "insolvency", "nclt", "default", "npa",
            "fii", "dii", "promoter pledge", "promoter selling",
            "regulatory action", "sebi", "enforcement", "penalty",
            "dividend", "bonus", "stock split",
        ],
        "color": "#ef4444",
        "label": "Critical",
        "score": 100
    },
    "HIGH": {
        "keywords": [
            "credit rating", "downgrade", "upgrade",
            "capex", "expansion", "new plant", "new product",
            "mou", "agreement", "contract", "order win",
            "jv", "joint venture", "partnership",
            "guidance", "outlook", "concall", "analyst meet",
            "auditor", "statutory audit", "qualified opinion",
            "related party", "loan", "debt",
        ],
        "color": "#f97316",
        "label": "High",
        "score": 70
    },
    "MEDIUM": {
        "keywords": [
            "investor presentation", "press release",
            "change in shareholding", "shareholding pattern",
            "trading window", "insider trading",
            "agm", "egm", "postal ballot",
            "record date", "book closure",
        ],
        "color": "#eab308",
        "label": "Medium",
        "score": 40
    },
    "LOW": {
        "keywords": [
            "compliance", "newspaper advertisement", "newspaper publication",
            "loss of share certificate", "duplicate share",
            "change of address", "change of rta",
            "secretarial compliance", "esop allotment"
        ],
        "color": "#6b7280",
        "label": "Routine",
        "score": 10
    }
}

# NSE/BSE screener.in base URL
SCREENER_BASE = "https://www.screener.in/company"

# Sectors for color coding
SECTOR_COLORS = {
    "IT": "#6366f1",
    "Banking": "#0ea5e9",
    "NBFC": "#38bdf8",
    "FMCG": "#22c55e",
    "Energy": "#f97316",
    "Auto": "#a855f7",
    "Pharma": "#ec4899",
    "Conglomerate": "#f59e0b",
    "Consumer": "#14b8a6",
}
