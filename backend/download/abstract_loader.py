from abc import ABC, abstractmethod


class BaseAPILoader(ABC):
    @abstractmethod
    def fetch_data(self):
        pass
