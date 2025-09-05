from optuna import Trial
from abc import ABC, abstractmethod

class AdjustInterface(ABC):
    @abstractmethod
    def adjust(self, advocator: Trial) -> None:
        pass
