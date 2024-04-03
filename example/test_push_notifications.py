import sys
import os
import time

from event_generator import gen_event
from lolapy_lite_agent.caching.cache_aside_redis import MemRedisCacheAside


# -------------------------------------------------------------
# Get the parent directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python module search path
sys.path.append(parent_dir)
sys.path.append(parent_dir + '/lolapy-notifications')

from lolapy import LolaSDK
from lolapy_lite_agent import NotificationsManager
from dotenv import dotenv_values
# -------------------------------------------------------------

config = {
    **dotenv_values("example/.env"),    # load development variables
    **os.environ,               # override loaded values with environment variables
}


lola = LolaSDK(
    lola_token=config['ASSISTANT_TOKEN'],
    prompter_url=config['PROMPTER_URL'],
    host=config['HOST'],  
    port=int(config['PORT']),
    webhook_url=config['WEBHOOK_URL'],
)

# Don't start the server
# lola.listen(debug=False)


# Create NoficationManager
# --------------------------------------------------------
m = NotificationsManager()

store = MemRedisCacheAside(
        redis_url=config['REDIS_URL'], 
        key_prefix='lola:cguru:push:',
        memory_maxsize=1000,
        wait_for_redis=True
    )
m.configure(
    redis_url=config['REDIS_URL'],
    lola=lola,
    get_id=lambda x: x.get('lead', {}).get('signature'),
    key_prefix='lola:cguru:push',
    store=store
)

# Register the middleware for Notifiations
# --------------------------------------------------------
lola.register_middleware(
    m.get_middleware()
)



@lola.on_event('onTextMessage')
def handle_text_message(session, ctx, msg):
    print(f'Got new text message: {msg["text"]}')


def get_user_session(id):
    return NotificationsManager().get_middleware().search_user_by_id(id)


print("Testing performance write/read 10 keys.")
print("wait_for_redis=True")
print("---------------------------------------------------")
store.set_wait_for_redis(True)
start = time.time()
for i in range(10):
    e = gen_event(str(i))
    user_id = e['lead']['signature']

    lola.process_event(e)
    session = get_user_session(user_id)
    
end = time.time()
print(f"Time spent for 10 events: {end - start}")


print("\n\n\n")
print("Testing performance write/read 10 keys.")
print("wait_for_redis=False")
print("---------------------------------------------------")
store.set_wait_for_redis(False)
start = time.time()
for i in range(10):
    e = gen_event(str(i))
    user_id = e['lead']['signature']

    lola.process_event(e)
    session = get_user_session(user_id)
    
end = time.time()
print(f"Time spent for 10 events: {end - start}")


print('-----------------TEST NOT FOUND-------------------')
session = get_user_session('asdasdqd')
print(session)