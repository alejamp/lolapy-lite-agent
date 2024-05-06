import json
from redis import Redis
from lolapy.assistant.chat_lead import ChatLead
from lolapy.assistant.state.base_state_provider import BaseChatStateProvider
from loguru import logger as log
from lolapy.assistant.stores.key_value_store import KeyValueStore



class ChatStateStoreProvider(BaseChatStateProvider):

    def __init__(self, store: KeyValueStore):
        super().__init__()
        log.debug("Create: RedisChatStateProvider")
        self.store = store
        
    def get_key(self, lead):
        return lead.get_token()

    def set_key_value(self, lead, key, value, ttl_in_seconds=None):
        hash_key = self.get_key(lead)
        self.store.set(key, value, ttl_in_seconds)

    def get_key_value(self, lead, key):
        hash_key = self.get_key(lead)
        value = self.client.hget(hash_key, key)
        if not value:
            return None
        return json.loads(value)

    def clear_store(self, lead):
        hash_key = self.get_key(lead)
        self.client.delete(hash_key)

    def clear_all_stores(self, tenant_id, assistant_id):
        hash_key = "s:" + tenant_id + ":" + assistant_id + ":*"
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
        return {k.decode('utf-8'): json.loads(store[k]) for k in store}
    
        

    def set_store(self, lead, store, ttl=None):
        hash_key = self.get_key(lead)
        for key in store:
            self.client.hset(hash_key, key, json.dumps(store[key]))
        if ttl:
            self.client.expire(hash_key, ttl)


