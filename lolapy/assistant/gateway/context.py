
from lolapy.assistant.gateway.gateway import Gateway
from loguru import logger as log

class LolaContext:

    def __init__(self, gateway): # type: ignore
        self.gateway = gateway
        self.state = LolaCtxStateManager(gateway)
        self.messanger = LolaCtxMessageSender(gateway)



class LolaCtxMessageSender:

    def __init__(self, gateway: Gateway):
        self.gateway = gateway

    async def send_text_message(self, text, appendToHistory=False, isPrivate=False, blend=False):
        """Send a text message to the user"""
        # execute async method to send a message to the user
        await self.gateway.add_outgoing_message(text, appendToHistory, isPrivate, blend)
    
    async def send_image_message(self, img_url, text=None, appendToHistory=False, isPrivate=False):
        """Send an image message to the user"""
        log.critical("Not implemented yet")
    
    async def send_typing_action(self):
        """Send a typing action to the user"""
        log.critical("Not implemented yet")

    async def send_action_card(self, title, actions):
        """Send an action card to the user"""
        log.critical("Not implemented yet")

class LolaCtxStateManager:

    def __init__(self, gateway: Gateway):
        self.gateway = gateway

    def get(self) -> dict:
        return self.gateway.get_agent().get_state(self.gateway.get_lead())
    
    def set(self, state: dict):
        self.gateway.get_agent().set_state(self.gateway.get_lead(), state)
    
    def reset(self):
        self.gateway.get_agent().clear_state(self.gateway.get_lead())





