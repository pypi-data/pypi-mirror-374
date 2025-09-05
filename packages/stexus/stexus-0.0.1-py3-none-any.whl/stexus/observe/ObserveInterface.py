from abc import ABC, abstractmethod

class ObserveInterface(ABC):
    @abstractmethod
    def observe(self, ignore_config_enabled: bool=False) -> None:
        pass
