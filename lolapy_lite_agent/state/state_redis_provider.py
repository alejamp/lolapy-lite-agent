import json
import redis
from lolapy_lite_agent.chat_lead import ChatLead
from lolapy_lite_agent.state.base_state_provider import BaseChatStateProvider


class RedisChatStateProvider(BaseChatStateProvider):

    def __init__(self, redis_url=None):
        super().__init__()
        self.redis_url = redis_url if redis_url else "localhost"
        print("RedisChatStateProvider -> Connecting to redis")
        self.client = redis.Redis.from_url(self.redis_url)
        
    def get_key(self, lead):
        return "s:" + lead.get_token()

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


if __name__ == "__main__":
    provider = RedisChatStateProvider(redis_url="redis://localhost:6379/0")
    lead = ChatLead("123", "test", "tenant", "assistant")

    provider.set_key_value(lead, "key1", "value1")
    provider.set_key_value(lead, "key2", "value2")

    print(provider.get_key_value(lead, "key1"))
    print(provider.get_key_value(lead, "key2"))

    provider.clear_store(lead)
    
    state = provider.get_store(lead) or {}
    print(state)
    state['test'] = "test_value"
    provider.set_store(lead, state)
    print("--------------------------")
    state = provider.get_store(lead)
    print(state)
    print(state.get('test'))

