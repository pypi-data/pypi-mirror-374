from abc import ABC, abstractmethod

class BaseModel(ABC):
    def __init__(self, model_name, client):
        self.model_name = model_name
        self.client = client

    @abstractmethod
    def completions(self, **kwargs):
        pass

    @abstractmethod
    def create(self, **kwargs):
        pass

