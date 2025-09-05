from abc import ABC, abstractmethod

class StudyInterface(ABC):
    @abstractmethod
    def study(self):
        pass
