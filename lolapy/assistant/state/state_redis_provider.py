import json
from redis import Redis
from lolapy.assistant.chat_lead import ChatLead
from lolapy.assistant.state.base_state_provider import BaseChatStateProvider
from loguru import logger as log

#  Store levels
#  prefix:tenant_id:lead_id

class RedisChatStateProvider(BaseChatStateProvider):

    def __init__(self, redis: str | Redis, key_prefix: str = "s"):
        super().__init__()
        log.debug("Create: RedisChatStateProvider")
        self.client = redis if isinstance(redis, Redis) else Redis.from_url(redis)
        self.prefix = key_prefix
        
    def get_key(self, lead):
        tenantId = lead.tenant_id
        sessionId = lead.get_token()
        assistantId = lead.assistant_id
        return f"{self.prefix}:{tenantId}:{assistantId}:{sessionId}"
    
    def __get_tenant_prefix(self, lead: ChatLead):
        tenantId = lead.tenant_id
        return f"{self.prefix}:{tenantId}:"
        
    def __get_assistant_prefix(self, lead: ChatLead):
        tenantId = lead.tenant_id
        assistantId = lead.assistant_id
        return f"{self.prefix}:{tenantId}:{assistantId}:"

    def set_key_value(self, lead, key, value, ttl_in_seconds=None):
        hash_key = self.get_key(lead)
        self.client.hset(hash_key, key, json.dumps(value))
        if ttl_in_seconds:
            self.client.expire(hash_key, ttl_in_seconds)

    def get_key_value(self, lead, key):
        hash_key = self.get_key(lead)
        value = self.client.hget(hash_key, key)
        if not value:
            return None
        return json.loads(value)

    def clear_store(self, lead):
        hash_key = self.get_key(lead)
        self.client.delete(hash_key)

    def clear_all_stores(self, lead: ChatLead):
        hash_key = self.__get_assistant_prefix(lead) + "*"
        keys = self.client.keys(hash_key)
        if not keys:
            return
        for key in keys:
            self.client.delete(key)

    def get_store(self, lead):
        hash_key = self.get_key(lead)
        store = self.client.hgetall(hash_key)
        if not store:
            return None
        s = {k.decode('utf-8'): json.loads(store[k]) for k in store}
        return s
    
        

    def set_store(self, lead, store, ttl=None):
        hash_key = self.get_key(lead)
        for key in store:
            self.client.hset(hash_key, key, json.dumps(store[key]))
        if ttl:
            self.client.expire(hash_key, ttl)


