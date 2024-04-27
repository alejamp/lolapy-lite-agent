import json
import redis
from lolapy_lite_agent.chat_lead import ChatLead
from lolapy_lite_agent.history.base_history_provider import BaseHistoryProvider


class RedisHistoryProvider(BaseHistoryProvider):

    def __init__(self, redis_url=None):
        self.redis_url = redis_url if redis_url else "localhost"
        print(f"RedisHistoryProvider -> Connecting to redis at {self.redis_url}")
        self.client = redis.Redis.from_url(self.redis_url)

    def get_key(self, lead: ChatLead):
        return f"h:{lead.get_token()}"

    def append_to_history(self, lead: ChatLead, entry, metadata=None, ttl=None):
        key = self.get_key(lead)
        value = json.dumps(entry)
        self.client.rpush(key, value)

        # set expiration to 24 hours
        self.client.expire(key, ttl if ttl else 86400)

    def get_history(self, lead: ChatLead):
        key = self.get_key(lead)
        values = self.client.lrange(key, 0, -1)
        res = [json.loads(v) for v in values]
        # remove None elements
        res = [r for r in res if r]

        return res
        

    def clear_history(self, lead: ChatLead, keep_last_messages=None):
        key = self.get_key(lead)
        if keep_last_messages:
            self.client.ltrim(key, 0, keep_last_messages)
        else:
            self.client.delete(key)

    def get_history_slice(self, lead: ChatLead, start, end):
        key = self.get_key(lead)
        history = self.client.lrange(key, start, end)
        return [json.loads(h) for h in history]

    def get_last_messages(self, lead: ChatLead, count):
        key = self.get_key(lead)
        history = self.client.lrange(key, -count, -1)
        return [json.loads(h) for h in history]

    def close_conversation(self, lead: ChatLead):
        raise NotImplementedError("Method not implemented.")
    

if __name__ == "__main__":
    provider = RedisHistoryProvider(redis_url="redis://localhost:6379/0")
    lead = ChatLead("123", "test", "tenant", "assistant")

    # provider.append_to_history(lead, "Hello")
    # provider.append_to_history(lead, "World")

    # print(provider.get_history(lead))

    provider.clear_history(lead)

    for i in range(15):
        provider.append_to_history(lead, f"Message {i}")

    # get the last 5 messages
    print(provider.get_last_messages(lead, 5))