import fakeredis
import pytest
from lolapy.assistant.chat_lead import ChatLead
from lolapy.assistant.state.state_redis_provider import RedisChatStateProvider

@pytest.fixture
def lead():
    lead = ChatLead('123', 'test', 'tenant1', 'assistant1')
    return lead

@pytest.fixture
def redis_client():
    redis_client = fakeredis.FakeRedis()
    return redis_client

@pytest.fixture
def store(redis_client):
    return RedisChatStateProvider(redis_client, 's')

def test_set_key_value(store: RedisChatStateProvider, lead):
    store.set_key_value(lead, 'key1', 'value1')
    v = store.get_key_value(lead, 'key1')
    assert v == 'value1'
    
def test_get_store(store: RedisChatStateProvider, lead):
    store.set_key_value(lead, 'key0', 'value0')
    store.set_key_value(lead, 'key1', 'value1')
    s = store.get_store(lead)
    assert s == {'key0': 'value0', 'key1': 'value1'}

def test_clear_store(store: RedisChatStateProvider, lead):
    store.set_key_value(lead, 'key0', 'value0')
    store.set_key_value(lead, 'key1', 'value1')
    s = store.get_store(lead)
    assert s == {'key0': 'value0', 'key1': 'value1'}
    store.clear_store(lead)
    s = store.get_store(lead)
    assert s == None

def test_clear_all_stores(store: RedisChatStateProvider):
    lead1 = ChatLead('123', 'test', 'tenant1', 'assistant1')
    lead2 = ChatLead('abc', 'test', 'tenant2', 'assistant2')
    store.set_key_value(lead1, 'key0', 'value0')
    store.set_key_value(lead1, 'key1', 'value1')
    store.set_key_value(lead2, 'key0', 'value0')
    store.set_key_value(lead2, 'key1', 'value1')
    
    store.clear_all_stores(lead1)
    s = store.get_store(lead1)
    assert s == None
    
    s = store.get_store(lead2)
    assert s == {'key0': 'value0', 'key1': 'value1'}
