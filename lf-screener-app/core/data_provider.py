"""Data provider for screener PoC.
Attempts to use tradingview-screener if available; falls back to a small static list and mock data.
"""
import random
from typing import List, Dict
import os
import time
import traceback
from dotenv import load_dotenv

# Load .env if present to support TV creds
load_dotenv()

# Detect tradingview-screener package and available APIs (Screener class vs Query API)
try:
    import tradingview_screener as tv
    _HAS_TV_PACKAGE = True
    _HAS_TV_SCREENER_CLASS = hasattr(tv, 'Screener')
    try:
        from tradingview_screener.query import Query
        _HAS_TV_QUERY = True
    except Exception:
        _HAS_TV_QUERY = False
    tv_import_error = None
except Exception as e:
    _HAS_TV_PACKAGE = False
    _HAS_TV_SCREENER_CLASS = False
    _HAS_TV_QUERY = False
    tv_import_error = e

try:
    # yfinance is optional but preferred for live data
    import yfinance as yf
    _HAS_YFINANCE = True
except Exception:
    _HAS_YFINANCE = False

# Optional scraping libraries
try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    _HAS_BS4 = True
except Exception:
    _HAS_BS4 = False

import re

class DataProvider:
    def __init__(self, config: Dict = None):
        self.config = config or {}

    def _discover_tickers_tradingview(self, index: str) -> List[str]:
        """Try multiple TradingView query patterns and optionally attempt with credentials if provided.

        Supports both the legacy `Screener` class and the `Query` API from the installed package.
        """
        verbose = bool(self.config.get("discovery_verbose", False))
        tv_user = os.getenv("TV_USERNAME")
        tv_pass = os.getenv("TV_PASSWORD")

        # Masked logging for credential presence (do not print raw secrets)
        if verbose:
            def _mask(s: str):
                if s is None:
                    return "<none>"
                s = str(s)
                if len(s) <= 4:
                    return "***"
                return f"{s[:2]}...{s[-2:]}"
            print(f"DataProvider: TV_USERNAME present={bool(tv_user)}, TV_PASSWORD present={bool(tv_pass)}")
            print(f"DataProvider: TV_USERNAME_masked={_mask(tv_user)}, TV_PASSWORD_masked={_mask(tv_pass)}")

        # If the package failed import earlier, log it
        if not _HAS_TV_PACKAGE:
            if verbose:
                print(f"DataProvider: tradingview_screener package import failed earlier: {tv_import_error}")
            return []

        # 1) If the legacy Screener class is available, attempt it
        if _HAS_TV_SCREENER_CLASS:
            try:
                def try_screener_call(**kw):
                    try:
                        from tradingview_screener import Screener
                        scr = Screener(**kw)
                        res = [s.get("symbol") for s in scr.get_all()]
                        return res, None
                    except Exception as e:
                        if verbose:
                            print(f"DataProvider: Screener call failed for args={kw}: {e}")
                            traceback.print_exc()
                        return [], e

                attempts = []
                if tv_user and tv_pass:
                    attempts.append({"username": tv_user, "password": tv_pass, "screener_type": "stocks", "exchange": index})
                    attempts.append({"username": tv_user, "password": tv_pass, "screener_type": "stocks"})
                attempts.extend([
                    {"exchange": index, "screener_type": "stocks"},
                    {"country": "turkey", "exchange": "BIST", "screener_type": "stocks"},
                    {"screener_type": "stocks"},
                ])

                for args in attempts:
                    res, err = try_screener_call(**args)
                    if res:
                        print(f"DataProvider: fetched {len(res)} symbols from tradingview-screener using args={args}")
                        return res
            except Exception as e:
                if verbose:
                    print("DataProvider: unexpected error in Screener-based discovery:", e)
                    traceback.print_exc()

        # 2) Fallback to Query API if available
        if _HAS_TV_QUERY:
            try:
                from tradingview_screener.query import Query
                q = Query()
                is_turkey = any(x in index for x in ("BIST", "TURKEY", "IST"))
                is_us = any(x in index for x in ("NASDAQ", "NYSE", "AMEX", "SPX", "DOWJONES", "AMERICA", "USA"))
                if is_turkey:
                    q = q.set_markets('turkey')
                    count, df = q.get_scanner_data()
                    symbol_col = 'ticker'
                elif is_us:
                    q = q.set_markets('america')
                    count, df = q.select('symbol', 'name', 'close').get_scanner_data()
                    symbol_col = 'symbol'
                else:
                    # fallback: try global
                    count, df = q.select('symbol', 'name', 'close').get_scanner_data()
                    symbol_col = 'symbol'

                if count and not df.empty and symbol_col in df.columns:
                    pref = f"{index}:"
                    items = [t for t in df[symbol_col].astype(str).tolist() if t.upper().startswith(pref)]
                    if items:
                        print(f"DataProvider: fetched {len(items)} symbols from tradingview Query API filtered by prefix={pref}")
                        return items
                    # If no strict prefix match, try contains index
                    items = [t for t in df[symbol_col].astype(str).tolist() if index in t.upper()]
                    if items:
                        print(f"DataProvider: fetched {len(items)} symbols from tradingview Query API by contains '{index}'")
                        return items
            except Exception as e:
                if verbose:
                    print("DataProvider: Query-based discovery failed:", e)
                    traceback.print_exc()

        # Nothing worked
        if verbose:
            print("DataProvider: tradingview discovery returned no symbols (no Screener/Query results)")
        return []

    def debug_discovery(self, index: str) -> Dict:
        """Run all discovery methods and return a diagnostic report with counts and errors."""
        report = {}
        verbose = bool(self.config.get("discovery_verbose", False))

        # Log masked TV env var presence so user can confirm .env loading
        tv_user = os.getenv("TV_USERNAME")
        tv_pass = os.getenv("TV_PASSWORD")
        if verbose:
            def _mask(s: str):
                if s is None:
                    return "<none>"
                s = str(s)
                if len(s) <= 4:
                    return "***"
                return f"{s[:2]}...{s[-2:]}"
            print(f"DataProvider: DEBUG env TV_USERNAME present={bool(tv_user)}, TV_PASSWORD present={bool(tv_pass)}")
            print(f"DataProvider: DEBUG TV_USERNAME_masked={_mask(tv_user)}, TV_PASSWORD_masked={_mask(tv_pass)}")

        try:
            try:
                tv = self._discover_tickers_tradingview(index)
                report["tradingview"] = {"count": len(tv), "sample": tv[:20]}
            except Exception as e:
                report["tradingview"] = {"count": 0, "error": str(e)}
                if verbose:
                    report["tradingview"]["trace"] = traceback.format_exc()
        except Exception:
            report["tradingview"] = {"count": 0, "error": "unexpected"}

        try:
            try:
                ex = self._discover_tickers_exchange(index)
                report["exchange"] = {"count": len(ex), "sample": ex[:20]}
            except Exception as e:
                report["exchange"] = {"count": 0, "error": str(e)}
                if verbose:
                    report["exchange"]["trace"] = traceback.format_exc()
        except Exception:
            report["exchange"] = {"count": 0, "error": "unexpected"}

        try:
            try:
                lo = self._load_local_tickers(index)
                report["local"] = {"count": len(lo), "sample": lo[:20]}
            except Exception as e:
                report["local"] = {"count": 0, "error": str(e)}
                if verbose:
                    report["local"]["trace"] = traceback.format_exc()
        except Exception:
            report["local"] = {"count": 0, "error": "unexpected"}

        return report

    def _discover_tickers_exchange(self, index: str) -> List[str]:
        """Attempt to discover tickers from exchange websites for known exchanges (e.g., BIST).
        This is best-effort and may fail depending on site structure.
        """
        if not (_HAS_REQUESTS and _HAS_BS4):
            return []
        index = index.upper()
        results = set()

        try:
            if "BIST" in index or "IST" in index or "TURKEY" in index:
                # Borsa Istanbul symbols listing (best-effort)
                urls = [
                    "https://www.borsaistanbul.com/en/symbols",
                    "https://www.borsaistanbul.com/en/lists/companies"
                ]
                for url in urls:
                    try:
                        r = requests.get(url, timeout=8)
                        if r.status_code != 200:
                            continue
                        soup = BeautifulSoup(r.text, "html.parser")
                        # Attempt to find ticker-like patterns in the page
                        text = soup.get_text(separator=" ")
                        candidates = re.findall(r"\b[A-Z0-9\.]{2,10}\b", text)
                        for c in candidates:
                            # heuristics: exclude clearly non-symbol words and short ones
                            if len(c) >= 2 and not c.isdigit() and not c.lower().startswith("bursa"):
                                results.add(f"BIST:{c}")
                        if results:
                            lst = sorted(results)
                            print(f"DataProvider: discovered {len(lst)} symbols from BIST exchange pages")
                            return lst
                    except Exception:
                        continue

            # Other exchanges could be implemented similarly
        except Exception:
            pass
        return []

    def _load_local_tickers(self, index: str) -> List[str]:
        tickers_file = f"data/tickers/{index}.txt"
        try:
            with open(tickers_file, "r") as f:
                raw = f.readlines()
                items = []
                for l in raw:
                    s = l.strip()
                    # Ignore empty lines and comments starting with '#'
                    if not s or s.startswith("#"):
                        continue
                    items.append(s)
                if items:
                    print(f"DataProvider: loaded {len(items)} symbols from local file {tickers_file}")
                    return items
        except Exception:
            pass
        return []

    def get_index_tickers(self, index: str) -> List[str]:
        """Discover tickers for an index.

        Priority behavior:
        1) Always try TradingView discovery first and log any exceptions or empty results.
        2) If TradingView fails or returns no symbols, fall back to the local tickers file (if allowed).
        3) If local fallback is disabled or no local tickers found, return an empty list to avoid silent fallbacks.
        """
        index = index.upper()
        verbose = bool(self.config.get("discovery_verbose", False))
        allow_local = bool(self.config.get("allow_local_ticker_fallback", True))

        # 1) Try TradingView discovery and capture any errors
        try:
            items = self._discover_tickers_tradingview(index)
            if items:
                return items
            if verbose:
                print(f"DataProvider: TradingView discovery returned 0 symbols for {index}")
        except Exception as e:
            # Log the full exception when verbose, otherwise a short message
            print(f"DataProvider: TradingView discovery failed for {index}: {e}")
            if verbose:
                traceback.print_exc()

        # 2) Fallback to local file if allowed
        if allow_local:
            items = self._load_local_tickers(index)
            if items:
                print(f"DataProvider: using local ticker fallback for {index} (count={len(items)})")
                return items
            if verbose:
                print(f"DataProvider: local fallback enabled but no tickers found for {index}")

        # 3) When discovery fails and local fallback is disabled or empty, return empty list
        print("DataProvider: discovery failed and no local tickers available; returning empty list.")
        return []

    def _convert_for_yahoo(self, ticker: str) -> str:
        """Convert a tradingview-like ticker to a Yahoo Finance compatible symbol where possible."""
        if ":" in ticker:
            exch, sym = ticker.split(":", 1)
            exch = exch.upper()
            sym = sym.replace(" ", "")
            if exch == "BIST":
                return f"{sym}.IS"
            if exch in ("NASDAQ", "NYSE"):
                # Handle cases like BRK.B -> BRK-B for Yahoo
                return sym.replace(".", "-")
            return sym
        # If no exchange prefix, return as-is
        return ticker

    def _fetch_data_yfinance(self, ticker: str) -> Dict:
        """Fetch OHLCV and basic fundamentals using yfinance. Returns None on failure."""
        if not _HAS_YFINANCE:
            return None
        cfg = self.config.get("yfinance", {})
        max_retries = int(cfg.get("max_retries", 3))
        period = cfg.get("history_period", "1y")
        interval = cfg.get("history_interval", "1d")

        yf_sym = self._convert_for_yahoo(ticker)
        attempt = 0
        while attempt < max_retries:
            try:
                t = yf.Ticker(yf_sym)
                hist = t.history(period=period, interval=interval)
                if hist is None or hist.empty:
                    attempt += 1
                    time.sleep(0.5 * attempt)
                    continue

                close = hist["Close"]
                high = hist["High"]
                low = hist["Low"]
                volume = hist.get("Volume") if "Volume" in hist.columns else None

                price = float(close.iloc[-1])
                ma150 = float(close.rolling(window=150).mean().iloc[-1]) if len(close) >= 150 else None
                ma200 = float(close.rolling(window=200).mean().iloc[-1]) if len(close) >= 200 else None

                # ATR approximation (14 and 20 periods)
                prev_close = close.shift(1)
                tr = (high - low).abs()
                tr = tr.fillna(0)
                tr = tr.combine((high - prev_close).abs(), max)
                tr = tr.combine((low - prev_close).abs(), max)
                atr_current = float(tr.rolling(window=14).mean().iloc[-1]) if len(tr) >= 14 else None
                atr_20 = float(tr.rolling(window=20).mean().iloc[-1]) if len(tr) >= 20 else None

                vol_now = float(volume.iloc[-1]) if volume is not None and len(volume) else None
                vol_20 = float(volume.rolling(window=20).mean().iloc[-1]) if volume is not None and len(volume) >= 20 else None

                info = {}
                try:
                    info = t.info or {}
                except Exception:
                    info = {}

                roe = info.get("returnOnEquity") or info.get("returnOnEquityTrailing") or None
                debt_equity = info.get("debtToEquity") or None
                # Ensure numeric conversion where possible
                try:
                    roe = float(roe) if roe is not None else None
                except Exception:
                    roe = None
                try:
                    debt_equity = float(debt_equity) if debt_equity is not None else None
                except Exception:
                    debt_equity = None

                return {
                    "ticker": ticker,
                    "price": price,
                    "ma150": ma150,
                    "ma200": ma200,
                    "atr_current": atr_current,
                    "atr_20": atr_20,
                    "volume": vol_now,
                    "vol_20": vol_20,
                    "roe": roe,
                    "debt_equity": debt_equity,
                }
            except Exception:
                attempt += 1
                time.sleep(0.5 * attempt)
                continue
        # If we get here, yfinance attempts failed
        return None

    def fetch_data(self, ticker: str) -> Dict:
        """
        Try live providers in order:
        1. yfinance (for price/volume/MA/ATR, some fundamentals)
        2. Deterministic mock fallback for PoC
        """
        provider = self.config.get("preferred_provider", "")

        # 1. Try yfinance for price/volume/MA/ATR
        data = None
        if provider == "tradingview_yfinance" and _HAS_YFINANCE:
            data = self._fetch_data_yfinance(ticker)
            if data:
                print(f"DataProvider: fetched live data for {ticker} via yfinance")

        # If nothing from yfinance, use deterministic mock fallback
        merged = data.copy() if data else {"ticker": ticker}
        if not merged or len(merged) <= 1:
            seed = abs(hash(ticker)) % (2**32)
            rnd = random.Random(seed)
            price = rnd.uniform(10, 200)
            ma150 = price * rnd.uniform(0.85, 1.02)
            ma200 = ma150 * rnd.uniform(0.95, 1.05)
            atr_current = rnd.uniform(0.1, 5.0)
            atr_20 = atr_current * rnd.uniform(0.9, 1.5)
            volume = rnd.uniform(10000, 1_000_000)
            vol_20 = volume * rnd.uniform(0.8, 1.2)
            roe = rnd.uniform(-5, 30)
            debt_equity = rnd.uniform(0.0, 2.0)
            merged = {
                "ticker": ticker,
                "price": price,
                "ma150": ma150,
                "ma200": ma200,
                "atr_current": atr_current,
                "atr_20": atr_20,
                "volume": volume,
                "vol_20": vol_20,
                "roe": roe,
                "debt_equity": debt_equity,
            }
        return merged