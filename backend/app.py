"""
FINN API Server
Flask-based REST API for the FINN investment assistant
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from portfolio import PORTFOLIO, PORTFOLIO_SYMBOLS, SECTOR_COLORS, FILING_PRIORITY
from market_data import (
    get_portfolio_quotes, get_quote, get_historical,
    get_stock_info, get_financials, detect_anomalies
)
from filings import get_portfolio_filings, fetch_nse_announcements, classify_filing, get_company_filings_from_screener
from analysis import analyze_stock, enrich_management_change

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend"),
    static_url_path=""
)
CORS(app)

# ── Health & Meta ──────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "FINN API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "gemini_configured": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    })


@app.route("/api/portfolio/meta")
def portfolio_meta():
    """Return portfolio composition metadata."""
    return jsonify({
        "stocks": PORTFOLIO,
        "symbols": PORTFOLIO_SYMBOLS,
        "sector_colors": SECTOR_COLORS,
        "count": len(PORTFOLIO)
    })


# ── Push Mode: Portfolio Dashboard ────────────────────────────────────────────

@app.route("/api/portfolio/quotes")
def portfolio_quotes():
    """Get current quotes for all portfolio stocks with anomaly detection."""
    try:
        price_threshold = float(request.args.get("price_threshold", 3.0))
        volume_threshold = float(request.args.get("volume_threshold", 2.0))

        quotes = get_portfolio_quotes()
        anomalies = detect_anomalies(quotes, price_threshold, volume_threshold)

        # Compute portfolio summary
        valid_quotes = [q for q in quotes if q.get("price")]
        gainers = sorted([q for q in valid_quotes if (q.get("change_pct") or 0) > 0],
                         key=lambda x: x["change_pct"], reverse=True)
        losers = sorted([q for q in valid_quotes if (q.get("change_pct") or 0) < 0],
                        key=lambda x: x["change_pct"])

        return jsonify({
            "quotes": quotes,
            "anomalies": anomalies,
            "summary": {
                "total_stocks": len(PORTFOLIO),
                "data_available": len(valid_quotes),
                "gainers": len(gainers),
                "losers": len(losers),
                "unchanged": len(valid_quotes) - len(gainers) - len(losers),
                "top_gainer": gainers[0] if gainers else None,
                "top_loser": losers[0] if losers else None,
                "anomaly_count": len(anomalies)
            },
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/portfolio/filings")
def portfolio_filings():
    """
    Get filtered & classified filings for all portfolio stocks.
    Supports windowed digest with configurable time window.
    """
    try:
        window_hours = int(request.args.get("window_hours", 24))
        priority_filter = request.args.get("priority", "ALL").upper()
        symbol_filter = request.args.get("symbol", "ALL").upper()

        # Clamp window
        window_hours = max(1, min(window_hours, 168))  # 1h to 7d

        data = get_portfolio_filings(window_hours)

        filings = data["all_filings"]

        # Apply filters
        if priority_filter != "ALL":
            filings = [f for f in filings if f["classification"]["priority"] == priority_filter]
        if symbol_filter != "ALL":
            filings = [f for f in filings if f["symbol"].upper().startswith(symbol_filter.replace(".NS", "").replace(".BO", ""))]

        return jsonify({
            "filings": filings,
            "by_priority": data["by_priority"] if priority_filter == "ALL" else {},
            "stats": data["stats"],
            "filters_applied": {
                "window_hours": window_hours,
                "priority": priority_filter,
                "symbol": symbol_filter
            },
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/portfolio/alerts")
def portfolio_alerts():
    """Get triggered alerts: high-priority filings + price/volume anomalies."""
    try:
        price_threshold = float(request.args.get("price_threshold", 3.0))
        volume_threshold = float(request.args.get("volume_threshold", 2.0))
        window_hours = int(request.args.get("window_hours", 24))

        # Get quotes and anomalies
        quotes = get_portfolio_quotes()
        anomalies = detect_anomalies(quotes, price_threshold, volume_threshold)

        # Get critical and high filings
        filings_data = get_portfolio_filings(window_hours)
        critical_filings = filings_data["by_priority"].get("CRITICAL", [])
        high_filings = filings_data["by_priority"].get("HIGH", [])
        alert_filings = (critical_filings + high_filings)[:20]

        # Build unified alert feed
        alerts = []

        for anomaly in anomalies:
            for a in anomaly["alerts"]:
                alerts.append({
                    "type": a["type"],
                    "severity": a["severity"],
                    "symbol": anomaly["symbol"],
                    "name": anomaly["name"],
                    "title": a["message"],
                    "detail": f"Price: ₹{anomaly['price']:,.0f} ({anomaly['change_pct']:+.1f}%)" if anomaly.get("price") else "",
                    "category": "MARKET",
                    "timestamp": datetime.now().isoformat()
                })

        for filing in alert_filings:
            alerts.append({
                "type": "FILING",
                "severity": filing["classification"]["priority"],
                "symbol": filing["symbol"],
                "name": next((s["name"] for s in PORTFOLIO if s["symbol"] == filing["symbol"]), filing["symbol"]),
                "title": filing["subject"],
                "detail": filing["body"][:150] if filing.get("body") else "",
                "category": "FILING",
                "timestamp": filing["date"],
                "url": filing.get("url", ""),
                "keywords": filing["classification"].get("keywords", [])
            })

        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 4))

        return jsonify({
            "alerts": alerts,
            "counts": {
                "total": len(alerts),
                "critical": len([a for a in alerts if a["severity"] == "CRITICAL"]),
                "high": len([a for a in alerts if a["severity"] == "HIGH"]),
                "market_anomalies": len(anomalies),
                "filing_alerts": len(alert_filings)
            },
            "thresholds": {
                "price_pct": price_threshold,
                "volume_ratio": volume_threshold
            },
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Pull Mode: On-Demand Research ─────────────────────────────────────────────

@app.route("/api/research/<symbol>")
def research_stock(symbol: str):
    """
    Full research analysis for any NSE stock.
    Strictly grounded in primary sources.
    """
    try:
        # Normalize symbol
        sym = symbol.upper()
        if not sym.endswith(".NS") and not sym.endswith(".BO"):
            sym = sym + ".NS"

        analysis = analyze_stock(sym)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e), "symbol": symbol}), 500


@app.route("/api/research/<symbol>/historical")
def research_historical(symbol: str):
    """Get historical price data for charts."""
    try:
        sym = symbol.upper()
        if not sym.endswith(".NS") and not sym.endswith(".BO"):
            sym = sym + ".NS"
        period = request.args.get("period", "6mo")
        valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
        if period not in valid_periods:
            period = "6mo"
        data = get_historical(sym, period=period)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/research/<symbol>/filings")
def research_filings(symbol: str):
    """Get recent filings for a specific stock."""
    try:
        sym = symbol.upper()
        if not sym.endswith(".NS") and not sym.endswith(".BO"):
            sym = sym + ".NS"
        days = int(request.args.get("days", 90))
        filings = fetch_nse_announcements(sym, from_days=days)
        return jsonify({
            "symbol": sym,
            "filings": filings,
            "count": len(filings)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/research/<symbol>/screener")
def research_screener(symbol: str):
    """Get screener.in data for a stock."""
    try:
        sym = symbol.upper()
        if not sym.endswith(".NS") and not sym.endswith(".BO"):
            sym = sym + ".NS"
        data = get_company_filings_from_screener(sym)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/research/<symbol>/quote")
def research_quote(symbol: str):
    """Get current quote for any stock."""
    try:
        sym = symbol.upper()
        if not sym.endswith(".NS") and not sym.endswith(".BO"):
            sym = sym + ".NS"
        q = get_quote(sym)
        info = get_stock_info(sym)
        q["name"] = info.get("name", sym)
        q["sector"] = info.get("sector", "N/A")
        return jsonify(q)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Classify Filing (utility) ──────────────────────────────────────────────────

@app.route("/api/classify", methods=["POST"])
def classify():
    """Classify a filing subject/body."""
    try:
        data = request.get_json()
        subject = data.get("subject", "")
        body = data.get("body", "")
        result = classify_filing(subject, body)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Frontend Serving ───────────────────────────────────────────────────────────

@app.route("/")
@app.route("/<path:path>")
def serve_frontend(path=""):
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    if path and os.path.exists(os.path.join(frontend_dir, path)):
        return send_from_directory(frontend_dir, path)
    return send_from_directory(frontend_dir, "index.html")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"[FINN] API starting on http://localhost:{port}")
    print(f"[FINN] Gemini AI: {'configured' if os.environ.get('GEMINI_API_KEY') else 'not configured (set GEMINI_API_KEY for AI features)'}")
    app.run(host="0.0.0.0", port=port, debug=debug, threaded=True)
