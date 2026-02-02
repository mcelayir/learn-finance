from abc import ABC, abstractmethod
from typing import List, Dict

class BaseReporter(ABC):
    @abstractmethod
    def report(self, results: List[Dict]):
        raise NotImplementedError
