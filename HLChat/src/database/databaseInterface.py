from abc import ABC, abstractmethod

class DatabaseInterface(ABC):

    @abstractmethod
    def get_client(self):
        pass