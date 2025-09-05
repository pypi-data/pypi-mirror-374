from abc import ABC, abstractmethod
from optuna import Trial

class ExperimentInterface(ABC):
    """
    returns score
    either in int or float.
    """
    @abstractmethod
    def experiment(self, advocator: Trial) -> float|int:
        pass
