from abc import ABC, abstractmethod
from typing import Dict

class BaseAlgorithm(ABC):
    @abstractmethod
    def run(self, ticker: str, data_provider) -> Dict:
        """Run the algorithm for a ticker and return a result dict."""
        raise NotImplementedError
