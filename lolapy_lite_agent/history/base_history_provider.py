from abc import ABC, abstractmethod


class BaseHistoryProvider(ABC):
    @abstractmethod
    def append_to_history(self, lead, entry, metadata=None, ttl=None):
        pass

    @abstractmethod
    def get_history(self, lead):
        pass

    @abstractmethod
    def clear_history(self, lead, keep_last_messages=None):
        pass

    @abstractmethod
    def get_history_slice(self, lead, start, end):
        pass

    @abstractmethod
    def get_last_messages(self, lead, count):
        pass

    @abstractmethod
    def close_conversation(self, lead):
        pass

