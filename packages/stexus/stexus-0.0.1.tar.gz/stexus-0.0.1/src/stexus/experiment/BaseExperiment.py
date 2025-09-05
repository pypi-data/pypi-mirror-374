from abc import abstractmethod
from optuna import Trial
from .ExperimentInterface import ExperimentInterface
from .ExperimentException import ExperimentException
from ..config.Config import ConfigModel
from ..adjust.AdjustInterface import AdjustInterface

class BaseExperiment(ExperimentInterface):
    _config: ConfigModel
    _adjust: AdjustInterface

    def __init__(self,
                 config: ConfigModel|None = None,
                 adjust: AdjustInterface|None = None
    ) -> None:
        super().__init__()
        if config is None:
            raise ExperimentException("config cannot be empty.")
        if adjust is None:
            raise ExperimentException("adjust cannot be empty.")

        self._config = config
        self._adjust = adjust

    """
    returns score
    either in int or float.
    """
    @abstractmethod
    def experiment(self, advocator: Trial) -> float|int:
        pass
