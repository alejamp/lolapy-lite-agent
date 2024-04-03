from abc import ABC, abstractmethod

from lolapy_lite_agent.chat_lead import ChatLead

class BaseChatStateProvider(ABC):
    @abstractmethod
    def get_key(self, lead: ChatLead):
        pass

    @abstractmethod
    def set_key_value(self, lead: ChatLead, key, value, ttl_in_seconds=None):
        pass

    @abstractmethod
    def get_key_value(self, lead: ChatLead, key):
        pass

    @abstractmethod
    def clear_store(self, lead: ChatLead):
        pass

    @abstractmethod
    def clear_all_stores(self, tenant_id, assistant_id):
        pass

    @abstractmethod
    def get_store(self, lead: ChatLead):
        pass

    @abstractmethod
    def set_store(self, lead: ChatLead, store, ttl=None):
        pass