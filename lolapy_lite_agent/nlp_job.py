from typing import Any
from lolapy_lite_agent.chat_lead import ChatLead

DEFAULT_PROMPT = "Hello {{state.name}} this is a default prompt"


class AgentJob:
    def __init__(self, job_id: str, lead: ChatLead, message: Any, prompt: str = None, init_state: dict = None):
        self.job_id = job_id  # UUID
        self.lead = lead
        self.message = message
        self.prompt = prompt or DEFAULT_PROMPT
        self.init_state = init_state 