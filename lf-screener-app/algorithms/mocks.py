from .base import BaseAlgorithm
import random

class RandomScoreAlgorithm(BaseAlgorithm):
    def run(self, ticker: str, data_provider) -> dict:
        rnd = random.Random(abs(hash(ticker)))
        score = rnd.uniform(0, 100)
        return {"ticker": ticker, "score": round(score, 2), "category": None}

class AlwaysPassAlgorithm(BaseAlgorithm):
    def run(self, ticker: str, data_provider) -> dict:
        return {"ticker": ticker, "score": 100.0, "category": "Mükemmel Setup"}
