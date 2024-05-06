import json
from redis import Redis
from lolapy.assistant.chat_lead import ChatLead
from lolapy.assistant.history.base_history_provider import BaseHistoryProvider
from loguru import logger as log


class RedisHistoryProvider(BaseHistoryProvider):

    def __init__(self, redis: str | Redis, key_prefix: str = "h"):
        self.client = redis if isinstance(redis, Redis) else Redis.from_url(redis)
        self.key_prefix = key_prefix
        log.debug(f"Create: RedisHistoryProvider")

    def get_key(self, lead: ChatLead):
        return f"{self.key_prefix}:{lead.get_token()}"

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
    

