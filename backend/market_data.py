"""
FINN Market Data Module
Real-time and historical price/volume data via yfinance
"""

import yfinance as yf
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta
from portfolio import PORTFOLIO, PORTFOLIO_SYMBOLS

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

CACHE_TTL = 300  # 5 minutes for price data


def _cache_path(key: str) -> str:
    safe = key.replace(".", "_").replace("/", "_")
    return os.path.join(CACHE_DIR, f"{safe}.json")


def _read_cache(key: str, ttl: int = CACHE_TTL):
    path = _cache_path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if time.time() - data.get("_ts", 0) < ttl:
            return data.get("_data")
    except Exception:
        pass
    return None


def _write_cache(key: str, data):
    path = _cache_path(key)
    try:
        with open(path, "w") as f:
            json.dump({"_ts": time.time(), "_data": data}, f)
    except Exception:
        pass


def get_quote(symbol: str) -> dict:
    """Get current quote for a symbol. Returns dict with price, change, volume etc."""
    cache_key = f"quote_{symbol}"
    cached = _read_cache(cache_key, ttl=120)  # 2 min cache for quotes
    if cached:
        cached["_cached"] = True
        return cached

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        hist = ticker.history(period="2d", interval="1d")

        if hist.empty:
            return _empty_quote(symbol)

        last = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else hist.iloc[0]

        price = float(last["Close"])
        prev_close = float(prev["Close"])
        change = price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0
        volume = int(last["Volume"])

        # Get 20-day avg volume for anomaly detection
        hist_20d = ticker.history(period="1mo", interval="1d")
        avg_vol_20d = int(hist_20d["Volume"].mean()) if not hist_20d.empty else volume

        result = {
            "symbol": symbol,
            "price": round(price, 2),
            "prev_close": round(prev_close, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "avg_volume_20d": avg_vol_20d,
            "volume_ratio": round(volume / avg_vol_20d, 2) if avg_vol_20d else 1.0,
            "high": round(float(last["High"]), 2),
            "low": round(float(last["Low"]), 2),
            "open": round(float(last["Open"]), 2),
            "date": last.name.strftime("%Y-%m-%d"),
            "_cached": False,
            "_source": "yfinance"
        }
        _write_cache(cache_key, result)
        return result

    except Exception as e:
        return _empty_quote(symbol, str(e))


def _empty_quote(symbol: str, error: str = "") -> dict:
    return {
        "symbol": symbol,
        "price": None,
        "prev_close": None,
        "change": None,
        "change_pct": None,
        "volume": None,
        "avg_volume_20d": None,
        "volume_ratio": None,
        "high": None,
        "low": None,
        "open": None,
        "date": None,
        "_cached": False,
        "_source": "error",
        "_error": error
    }


def get_portfolio_quotes() -> list:
    """Get quotes for all portfolio stocks."""
    cache_key = "portfolio_quotes"
    cached = _read_cache(cache_key, ttl=120)
    if cached:
        for q in cached:
            q["_cached"] = True
        return cached

    quotes = []
    for stock in PORTFOLIO:
        q = get_quote(stock["symbol"])
        q["name"] = stock["name"]
        q["sector"] = stock["sector"]
        q["exchange"] = stock["exchange"]
        quotes.append(q)

    _write_cache(cache_key, quotes)
    return quotes


def get_historical(symbol: str, period: str = "6mo", interval: str = "1d") -> dict:
    """Get historical OHLCV data."""
    cache_key = f"hist_{symbol}_{period}_{interval}"
    cached = _read_cache(cache_key, ttl=3600)  # 1h cache for historical
    if cached:
        cached["_cached"] = True
        return cached

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            return {"symbol": symbol, "data": [], "_source": "error"}

        records = []
        for idx, row in hist.iterrows():
            records.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        # Calculate 20d MA
        closes = [r["close"] for r in records]
        for i, r in enumerate(records):
            window = closes[max(0, i-19):i+1]
            r["ma20"] = round(sum(window) / len(window), 2)

        result = {
            "symbol": symbol,
            "data": records,
            "_cached": False,
            "_source": "yfinance"
        }
        _write_cache(cache_key, result)
        return result

    except Exception as e:
        return {"symbol": symbol, "data": [], "_source": "error", "_error": str(e)}


def detect_anomalies(quotes: list, price_threshold: float = 3.0, volume_threshold: float = 2.0) -> list:
    """Detect price and volume anomalies in portfolio."""
    anomalies = []
    for q in quotes:
        if not q.get("change_pct"):
            continue

        alerts = []

        # Price anomaly
        if abs(q["change_pct"]) >= price_threshold:
            direction = "📈 Surge" if q["change_pct"] > 0 else "📉 Drop"
            alerts.append({
                "type": "PRICE",
                "severity": "CRITICAL" if abs(q["change_pct"]) >= 5 else "HIGH",
                "message": f"{direction} of {q['change_pct']:+.1f}% — significant price movement",
                "value": q["change_pct"]
            })

        # Volume anomaly
        vol_ratio = q.get("volume_ratio", 1.0)
        if vol_ratio and vol_ratio >= volume_threshold:
            alerts.append({
                "type": "VOLUME",
                "severity": "HIGH" if vol_ratio >= 3 else "MEDIUM",
                "message": f"Volume {vol_ratio:.1f}× avg — unusual trading activity",
                "value": vol_ratio
            })

        if alerts:
            anomalies.append({
                "symbol": q["symbol"],
                "name": q.get("name", q["symbol"]),
                "price": q["price"],
                "change_pct": q["change_pct"],
                "volume_ratio": q.get("volume_ratio"),
                "alerts": alerts
            })

    return sorted(anomalies, key=lambda x: max(a["value"] if a["type"] == "VOLUME" else abs(a["value"]) for a in x["alerts"]), reverse=True)


def get_stock_info(symbol: str) -> dict:
    """Get fundamental info for a stock (for Pull research)."""
    cache_key = f"info_{symbol}"
    cached = _read_cache(cache_key, ttl=86400)  # 24h cache for fundamentals
    if cached:
        cached["_cached"] = True
        return cached

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        result = {
            "symbol": symbol,
            "name": info.get("longName") or info.get("shortName", symbol),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "description": info.get("longBusinessSummary", ""),
            "website": info.get("website", ""),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "revenue": info.get("totalRevenue"),
            "ebitda": info.get("ebitda"),
            "net_income": info.get("netIncomeToCommon"),
            "debt_to_equity": info.get("debtToEquity"),
            "free_cashflow": info.get("freeCashflow"),
            "dividend_yield": info.get("dividendYield"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "employees": info.get("fullTimeEmployees"),
            "_cached": False,
            "_source": "yfinance"
        }
        _write_cache(cache_key, result)
        return result

    except Exception as e:
        return {
            "symbol": symbol,
            "name": symbol,
            "_cached": False,
            "_source": "error",
            "_error": str(e)
        }


def get_financials(symbol: str) -> dict:
    """Get quarterly and annual financials."""
    cache_key = f"financials_{symbol}"
    cached = _read_cache(cache_key, ttl=86400)
    if cached:
        cached["_cached"] = True
        return cached

    try:
        ticker = yf.Ticker(symbol)

        # Quarterly income statement
        q_income = ticker.quarterly_income_stmt
        quarterly = []
        if q_income is not None and not q_income.empty:
            for col in q_income.columns[:8]:  # last 8 quarters
                row = {}
                row["period"] = str(col.date()) if hasattr(col, 'date') else str(col)[:10]
                row["revenue"] = _safe_val(q_income, "Total Revenue", col)
                row["gross_profit"] = _safe_val(q_income, "Gross Profit", col)
                row["ebitda"] = _safe_val(q_income, "EBITDA", col)
                row["ebit"] = _safe_val(q_income, "EBIT", col)
                row["pbt"] = _safe_val(q_income, "Pretax Income", col)
                row["pat"] = _safe_val(q_income, "Net Income", col)
                quarterly.append(row)

        # Annual income statement
        a_income = ticker.income_stmt
        annual = []
        if a_income is not None and not a_income.empty:
            for col in a_income.columns[:4]:  # last 4 years
                row = {}
                row["period"] = str(col.date()) if hasattr(col, 'date') else str(col)[:10]
                row["revenue"] = _safe_val(a_income, "Total Revenue", col)
                row["gross_profit"] = _safe_val(a_income, "Gross Profit", col)
                row["ebitda"] = _safe_val(a_income, "EBITDA", col)
                row["pbt"] = _safe_val(a_income, "Pretax Income", col)
                row["pat"] = _safe_val(a_income, "Net Income", col)
                annual.append(row)

        # Cash flow
        q_cf = ticker.quarterly_cashflow
        cashflow = []
        if q_cf is not None and not q_cf.empty:
            for col in q_cf.columns[:8]:
                row = {
                    "period": str(col.date()) if hasattr(col, 'date') else str(col)[:10],
                    "operating_cf": _safe_val(q_cf, "Operating Cash Flow", col),
                    "investing_cf": _safe_val(q_cf, "Investing Cash Flow", col),
                    "financing_cf": _safe_val(q_cf, "Financing Cash Flow", col),
                    "free_cf": _safe_val(q_cf, "Free Cash Flow", col),
                    "capex": _safe_val(q_cf, "Capital Expenditure", col),
                }
                cashflow.append(row)

        # Balance sheet (Annual & Quarterly)
        bs_annual = ticker.balance_sheet
        balance_sheet = []
        if bs_annual is not None and not bs_annual.empty:
            for col in bs_annual.columns[:4]:
                row = {
                    "period": str(col.date()) if hasattr(col, 'date') else str(col)[:10],
                    "total_debt": _safe_val(bs_annual, "Total Debt", col),
                    "working_capital": _safe_val(bs_annual, "Working Capital", col),
                    "equity": _safe_val(bs_annual, "Common Stock Equity", col) or _safe_val(bs_annual, "Stockholders Equity", col),
                    "invested_capital": _safe_val(bs_annual, "Invested Capital", col),
                    "cash_equivalents": _safe_val(bs_annual, "Cash And Cash Equivalents", col),
                }
                balance_sheet.append(row)

        result = {
            "symbol": symbol,
            "quarterly": quarterly,
            "annual": annual,
            "cashflow": cashflow,
            "balance_sheet": balance_sheet,
            "_cached": False,
            "_source": "yfinance"
        }
        _write_cache(cache_key, result)
        return result

    except Exception as e:
        return {
            "symbol": symbol,
            "quarterly": [],
            "annual": [],
            "cashflow": [],
            "_source": "error",
            "_error": str(e)
        }


def _safe_val(df, row_name, col):
    """Safely extract a value from a dataframe."""
    try:
        matches = [r for r in df.index if row_name.lower() in str(r).lower()]
        if matches:
            v = df.loc[matches[0], col]
            if pd.notna(v):
                return round(float(v), 0)
    except Exception:
        pass
    return None
