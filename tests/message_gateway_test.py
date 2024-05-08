
# load env variables from ../example/.env
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger as log
from lolapy.assistant.gateway import LolaMessageGateway
from lolapy.assistant.gateway.message_gateway import LolaContext    

load_dotenv(dotenv_path="./example/.env")



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")    
INIT_STATE: dict = {
    "name": "Lola"  
}

# prompt
prompt = """Create an assistant called {{state.name}}
    <function name="get_cryptocurrency_price" description="Get the current cryptocurrency price">
        <parameters type="object">
            <param name="cryptocurrency" type="string" description="The cryptocurrency abbreviation eg. BTC, ETH"/>
            <param name="currency" type="string" enum="USD,ARG" />
        </parameters>
    </function>
"""


def outgoing_message_callback(data):
    log.warning(f"Outgoing message: {data}")

log.info("Starting Lola Plugin")
lola = LolaMessageGateway("123", 
                          prompt, 
                          OPENAI_API_KEY, 
                          init_state=INIT_STATE, 
                          on_outgoing_message=outgoing_message_callback
                        )

@lola.on_command('get_cryptocurrency_price')
async def handle_get_cryptocurrency_price(session, ctx: LolaContext, cmd):
    log.warning(f'Got command!')
    cryptocurrency = cmd['data']['args']['cryptocurrency']
    currency = cmd['data']['args']['currency']
    log.warning(f'User wants to know the price of {cryptocurrency} in {currency}')
    
    return f"The {cryptocurrency} price is $1000"

@lola.on_event('onNewConversation')
async def handle_text_message(session, ctx: LolaContext, msg):
    log.warning(f'Got new conversation: {msg["text"]}')
    state = ctx.state.get() or {}
    log.warning(f'State: {state}')
    state['presence'] = "I am here"
    ctx.state.set(state)

@lola.on_event('onTextMessage')
def handle_text_message(session, ctx: LolaContext, msg):
    log.warning(f'Got text message: {msg["text"]}')
    state = ctx.state.get()
    log.warning(f'State: {state}')
    


lola.agent.clear_history(lola.lead)

async def main1():
    log.critical("----------------------------------------------------------")
    async for text in lola.add_message("Your name is?", new_state={"name": "Lola Flores"}):
        print(text, end="")

async def main2():
    log.critical("----------------------------------------------------------")
    async for text in lola.add_message("What is the Bitcoin price in USD."):
        print(text, end="")

async def main3():
    log.critical("----------------------------------------------------------")
    async for text in lola.add_message("tell me how much is 3+3"):
        print(text, end="")

async def main4():
    log.critical("----------------------------------------------------------")
    async for text in lola.add_message("knock knock"):
        print(text, end="")


# Run each main in sequence, avoid parallel execution
asyncio.run(main1())
# asyncio.run(main2())
asyncio.run(main3())

# lola.agent.set_state(lola.lead, {"name": "Lola Flores"})
# s = lola.agent.get_state(lola.lead)
# log.warning(f"State: {s}")

print("\n")
log.critical("---------------------------DONE-------------------------------")