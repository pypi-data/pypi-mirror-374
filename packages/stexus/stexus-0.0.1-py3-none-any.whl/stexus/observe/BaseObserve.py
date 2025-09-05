from abc import abstractmethod
from .ObserveInterface import ObserveInterface
from .ObserveException import ObserveException
from ..config.Config import ConfigModel

class BaseObserve(ObserveInterface):
    _config: ConfigModel

    def __init__(self,
                 config: ConfigModel|None = None,
    ) -> None:
        super().__init__()
        if config is None:
            raise ObserveException("config cannot be empty.")

        self._config = config

    @abstractmethod
    def observe(self, ignore_config_enabled: bool=False) -> None:
        pass
