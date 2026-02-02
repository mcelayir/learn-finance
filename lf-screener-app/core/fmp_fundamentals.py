# FinancialModelingPrep (FMP) fundamentals fetcher for BIST stocks
# Usage: from fmp_fundamentals import fetch_fmp_fundamentals
import os
import requests

def fetch_fmp_fundamentals(ticker: str, exchange: str = "BIST") -> dict:
    """
    Fetches key fundamentals (PE, PB, ROE, etc.) for a given ticker from FMP API.
    Ticker should be in TradingView format (e.g., BIST:THYAO).
    Returns a dict with keys: pe, pb, roe, market_cap, etc. or None on failure.
    """
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        raise RuntimeError("FMP_API_KEY not set in environment")
    # FMP uses e.g. THYAO.IS for BIST stocks
    if ticker.upper().startswith("BIST:"):
        symbol = ticker.split(":", 1)[1] + ".IS"
    else:
        symbol = ticker
    base_url = "https://financialmodelingprep.com/api/v3"
    # Profile endpoint for market cap, ratios endpoint for PE, PB, ROE, etc.
    try:
        ratios_url = f"{base_url}/ratios/{symbol}?apikey={api_key}"
        profile_url = f"{base_url}/profile/{symbol}?apikey={api_key}"
        ratios = requests.get(ratios_url, timeout=8).json()
        profile = requests.get(profile_url, timeout=8).json()
        if not isinstance(ratios, list) or not ratios:
            return None
        if not isinstance(profile, list) or not profile:
            return None
        r = ratios[0]
        p = profile[0]
        return {
            "pe": r.get("priceEarningsRatio"),
            "pb": r.get("priceToBookRatio"),
            "roe": r.get("returnOnEquity"),
            "market_cap": p.get("mktCap"),
            "sector": p.get("sector"),
            "industry": p.get("industry"),
            "company_name": p.get("companyName"),
        }
    except Exception as e:
        print(f"FMP fundamentals fetch failed for {ticker}: {e}")
        return None
