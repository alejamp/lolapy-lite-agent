from typing import Any
from lolapy.assistant.chat_lead import ChatLead

DEFAULT_PROMPT = "Create an assistant funny and sarcastic, dark humor chatbot."


class AgentJob:
    def __init__(self, job_id: str, lead: ChatLead, message: Any, prompt: str = None, init_state: dict = None, new_state: dict = None):
        self.job_id = job_id  # UUID
        self.lead = lead
        self.message = message
        self.prompt = prompt or DEFAULT_PROMPT
        self.init_state = init_state
        self.new_state = new_state