
import os
import time
from dotenv import load_dotenv
from lola import LolaAgent
from loguru import logger as log
from lolapy.assistant.chat_lead import ChatLead

load_dotenv(dotenv_path="./example/.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# prompt
prompt = """Create an assistant called {{state.name}}
    <function name="get_cryptocurrency_price" description="Get the current cryptocurrency price">
        <parameters type="object">
            <param name="cryptocurrency" type="string" description="The cryptocurrency abbreviation eg. BTC, ETH"/>
            <param name="currency" type="string" enum="USD,ARG" />
        </parameters>
    </function>
"""

# ChatLead
lead = ChatLead("123", "test", "tenant", "assistant")

def on_text_received(text):
    print(text, end="")
    time.sleep(0.02)

def on_function_call(function_call):
    print(">>>>>> ",function_call.get("name"))

# LolaAgent
agent = LolaAgent(api_key=OPENAI_API_KEY, 
                on_text_received=on_text_received,
                on_function_call=on_function_call
            )

# clear history
agent.clear_history(lead)


# blend message into context
async def test():
    agent.add_user_message(lead, "Hola Lola! Como estas?")
    res = await agent.blend_message_into_context(lead, "tell me how much is 2+2")
    log.info(res)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())