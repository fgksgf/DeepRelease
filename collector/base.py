from abc import ABC, abstractmethod


class Collector(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def get_all_since_last_release(self, owner, name):
        pass
