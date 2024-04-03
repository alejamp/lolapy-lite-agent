from abc import ABC, abstractmethod
import json

class ChatLead(ABC):

    def __init__(self, id, channel_source, tenant_id, assistant_id, metadata=None, signature=None):
        self.id = id
        self.channel_source = channel_source
        self.tenant_id = tenant_id
        self.assistant_id = assistant_id
        self.metadata = metadata
        self.signature = signature        

    def get_token(self):
        return self.id

    def serialize(input):
        return json.dumps(input)
        

        
