from abc import ABC, abstractmethod
from lolapy.assistant.agents.lola import LolaAgent
from lolapy.assistant.chat_lead import ChatLead


class Gateway(ABC):
    
    @abstractmethod
    def get_agent(self) -> LolaAgent:
        raise NotImplementedError()
    
    @abstractmethod
    def get_lead(self) -> ChatLead:
        raise NotImplementedError()
    
    @abstractmethod
    def add_outgoing_message(self, message: str, appendToHistory=False, isPrivate=False, blend=False):
        raise NotImplementedError()
    
    # @abstractmethod
    # def get_state(self, lead: ChatLead):
    #     raise NotImplementedError()
    
    # @abstractmethod
    # def set_state(self, lead: ChatLead):
    #     raise NotImplementedError()
    
    # @abstractmethod
    # def clear_state(self, lead: ChatLead):
    #     raise NotImplementedError()