from abc import abstractmethod
from .StudyInterface import StudyInterface
from .StudyException import StudyException
from ..config.Config import ConfigModel
from ..experiment.ExperimentInterface import ExperimentInterface

class BaseStudy(StudyInterface):
    _config: ConfigModel
    _experiment: ExperimentInterface

    def __init__(self,
                 config: ConfigModel|None = None,
                 experiment: ExperimentInterface|None = None
    ) -> None:
        super().__init__()
        if config is None:
            raise StudyException("config cannot be empty.")
        if experiment is None:
            raise StudyException("experiment cannot be empty.")

        self._config = config
        self._experiment = experiment

    @abstractmethod
    def study(self):
        pass
