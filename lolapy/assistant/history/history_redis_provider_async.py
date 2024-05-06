import json
import redis
from lolapy.assistant.chat_lead import ChatLead
from lolapy.assistant.history.base_history_provider import BaseHistoryProvider
from lolapy.assistant.stores.key_value_store import ListStore


class RedisHistoryProviderAsync(BaseHistoryProvider):

    def __init__(self, store: ListStore):
        print(f"Create: RedisHistoryProviderAsync")
        self.store = store

    def get_key(self, lead: ChatLead):
        return f"h:{lead.get_token()}"

    async def append_to_history(self, lead: ChatLead, entry, metadata=None, ttl=None):
        key = self.get_key(lead)
        value = json.dumps(entry)
        await self.store.list_append(key, value, ttl)


    async def get_history(self, lead: ChatLead):
        key = self.get_key(lead)
        values = await self.store.list_get(key)
        res = [json.loads(v) for v in values]
        # remove None elements
        res = [r for r in res if r]
        return res
        

    async def clear_history(self, lead: ChatLead, keep_last_messages=None):
        key = self.get_key(lead)

        if keep_last_messages:
            # self.client.ltrim(key, 0, keep_last_messages)
            msgs = await self.store.list_get_last(key, keep_last_messages)
            await self.store.list_clear(key)
            for msg in msgs:
                await self.store.list_append(key, msg)
                
        else:
            await self.store.list_clear(key)


    async def get_last_messages(self, lead: ChatLead, count):
        key = self.get_key(lead)
        # history = self.client.lrange(key, -count, -1)
        history = await self.store.list_get_last(key, count)
        return [json.loads(h) for h in history]

    async def close_conversation(self, lead: ChatLead):
        raise NotImplementedError("Method not implemented.")
    

