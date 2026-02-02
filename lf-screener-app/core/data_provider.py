"""Data provider for screener PoC.
Attempts to use tradingview-screener if available; falls back to a small static list and mock data.
"""
import random
from typing import List, Dict

try:
    # best-effort import; not required for PoC
    from tradingview_screener import Screener
    _HAS_TV_SCREENER = True
except Exception:
    _HAS_TV_SCREENER = False

class DataProvider:
    def __init__(self, config: Dict = None):
        self.config = config or {}

    def get_index_tickers(self, index: str) -> List[str]:
        """Return a list of tickers for a given index. If tradingview-screener is available, try to use it.
        For PoC, support 'BIST' returning a few examples."""
        index = index.upper()
        if _HAS_TV_SCREENER:
            try:
                # NOTE: tradingview-screener API may differ; this is a best-effort attempt
                scr = Screener(country="turkey", exchange="BIST", screener_type="stocks")
                items = [s.get("symbol") for s in scr.get_all()[:50]]
                return items
            except Exception:
                pass
        # Fallback static sample tickers (BIST examples)
        if "BIST" in index:
            return ["BIST:AKBNK", "BIST:THYAO", "BIST:EREGL", "BIST:GARAN", "BIST:SISE"]
        if "SP500" in index or "SPX" in index or "SP500" in index.upper():
            return ["NYSE:BRK.B", "NASDAQ:MSFT", "NASDAQ:AAPL", "NYSE:AMZN", "NASDAQ:GOOGL"]
        # Generic fallback
        return ["AAPL", "MSFT", "GOOGL"]

    def fetch_data(self, ticker: str) -> Dict:
        """For the PoC, return a mock data structure that algorithms can use.
        In production this should fetch historical OHLCV and financials.
        """
        # Create reproducible but varied mock values
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

        return {
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
