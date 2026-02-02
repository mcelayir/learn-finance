from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from algorithms.mcsa import MCSAAlgorithm
from algorithms.mocks import RandomScoreAlgorithm
from core.data_provider import DataProvider

class Engine:
    def __init__(self, config: dict):
        self.config = config
        self.dp = DataProvider(config)
        self.max_workers = config.get("max_workers", 5)

    def _run_for_ticker(self, ticker: str):
        algo = MCSAAlgorithm()
        return algo.run(ticker, self.dp)

    def run(self, market: str = None) -> List[dict]:
        market = market or self.config.get("market", "BIST")
        tickers = self.dp.get_index_tickers(market)

        # Abort early if discovery returned no tickers to avoid empty reports
        if not tickers:
            raise RuntimeError(f"No tickers discovered for market '{market}'. Aborting.")

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(self._run_for_ticker, t): t for t in tickers}
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    results.append(res)
                except Exception as e:
                    # Fail gracefully for PoC
                    results.append({"ticker": futures[fut], "score": 0.0, "category": "Zayıf Setup", "error": str(e)})
        return results
