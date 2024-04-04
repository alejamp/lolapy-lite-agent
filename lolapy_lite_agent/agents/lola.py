

import asyncio
import os
import time
from typing import AsyncIterable
import openai
from lolapy_lite_agent.agents.utils import create_assistant_message, create_function_call_message, create_function_response_message, create_prompt_message, create_user_message
from lolapy_lite_agent.chat_lead import ChatLead
from lolapy_lite_agent.history.history_redis_provider import RedisHistoryProvider
from lolapy_lite_agent.nlp_job import AgentJob
from lolapy_lite_agent.prompt_compiler import PromptCompiled, PromptCompiler
from lolapy_lite_agent.state.state_redis_provider import RedisChatStateProvider
import logging
from loguru import logger as log

DEFAULT_MODEL = "gpt-4-1106-preview"
DEFAULT_MAX_TOKENS = 1500
DEFAULT_MAX_HISTORY = 10

class LolaAgent:

    def __init__(self, 
                 api_key, 
                 default_model=None, 
                 on_text_received: callable = None,
                 on_function_call: callable = None):
        self._stateStore = RedisChatStateProvider()
        self._historyStore = RedisHistoryProvider()
        self._api_key = api_key
        self._default_model = default_model or DEFAULT_MODEL
        self._client = openai.AsyncOpenAI(api_key=self._api_key)
        self._producing_response = False
        self._needs_interrupt = False
        self._on_text_received = on_text_received
        self._on_function_call = on_function_call

    async def process(self, job: AgentJob):
        # impact message history
        if job.message:
            self.add_user_message(job.lead, job.message)

        # compile prompt
        prompt_compiler = PromptCompiler(job, job.prompt, self._historyStore, self._stateStore) 
        ctx = prompt_compiler.process(init_state=job.init_state, new_state=job.new_state)

        # request stream
        async for text in self.request_stream(job, ctx):
            yield text        

    def clear_history(self, lead: ChatLead):
        self._historyStore.clear_history(lead)

    def clear_state(self, lead: ChatLead):
        self._stateStore.clear_store(lead)

    def set_state(self, lead: ChatLead, state: dict):
        self._stateStore.set_store(lead, state)

    def get_state(self, lead: ChatLead):
        return self._stateStore.get_store(lead)
    
    def set_state_value(self, lead: ChatLead, key: str, value):
        state = self._stateStore.set_key_value(lead, key, value)
        return state


    def add_user_message(self, lead: ChatLead, message: str):
        msg = create_user_message(message)
        self._historyStore.append_to_history(lead, msg)

    def add_assistant_message(self, lead: ChatLead, message: str):
        msg = create_assistant_message(message)
        self._historyStore.append_to_history(lead, msg)

    def add_function_call_message(self, lead: ChatLead, function_call: dict):
        msg = create_function_call_message(function_call.get("name"), function_call.get("arguments"))
        self._historyStore.append_to_history(lead, msg)

    def add_function_response_message(self, lead: ChatLead, function_call: dict, response: str):
        msg = create_function_response_message(function_call.get("name"), response)
        self._historyStore.append_to_history(lead, msg)

    async def request_stream(self, job: AgentJob, ctx: PromptCompiled) -> AsyncIterable[dict]:

        # get model from settings
        model = ctx.get("settings", {}).get("model", self._default_model)
        max_tokens = ctx.get("settings", {}).get("max_tokens", DEFAULT_MAX_TOKENS)
        max_history =  int(ctx.get("settings", {}).get("max_history_length", DEFAULT_MAX_HISTORY))


        chat_messages = []
        chat_messages.append(create_prompt_message(
            content=ctx.get("prompt", "")
        ))

        # get history messages up to max_history
        
        history_messages = self._historyStore.get_last_messages(job.lead, max_history)

        # append history messages to the chat messages
        for message in history_messages:
            chat_messages.append(message)

        # show history messages in log idx -> content. Message is a dictionary
        # for idx, message in enumerate(history_messages):
        #     log.info(f"{idx} -> {message}")
            

        try:
            chat_stream = await asyncio.wait_for(
                self._client.chat.completions.create(
                    model=model,
                    n=1,
                    stream=True,
                    messages=chat_messages,
                    max_tokens=int(max_tokens or DEFAULT_MAX_TOKENS),
                    functions=ctx.get("functions", []),
                ),
                10,
            )
        except TimeoutError:
            yield "Sorry, I'm taking too long to respond. Please try again later."
            return

        self._producing_response = True
        complete_response = ""
        func_call = {
            "name": None,
            "arguments": "",
        }

        async def anext_util(aiter):
            async for item in aiter:
                return item

            return None

        while True:
            try:
                chunk = await asyncio.wait_for(anext_util(chat_stream), 5)
            except TimeoutError:
                break
            except asyncio.CancelledError:
                self._producing_response = False
                self._needs_interrupt = False
                break

            if chunk is None:
                break

            content = None
            delta = chunk.choices[0].delta
            if delta.function_call:
                if delta.function_call.name:
                    func_call["name"] = delta.function_call.name
                if delta.function_call.arguments:
                    func_call["arguments"] += delta.function_call.arguments
            if delta.content:
                content = delta.content

            if chunk.choices[0].finish_reason == "function_call":
                # function call here using func_call
                # print("Function call: ", func_call)
                yield {
                    "content": None,
                    "function_call": func_call
                }
                break             

            if self._needs_interrupt:
                self._needs_interrupt = False
                logging.info("ChatGPT interrupted")
                break

            if content is not None:
                complete_response += content
                if self._on_text_received:
                    self._on_text_received(content)
                yield {
                    "content": content
                }




        if complete_response:
            self.add_assistant_message(job.lead, complete_response)

        self._producing_response = False        


    async def process_results_coro(self, stream):
        response = {
            "content": "",
            "function_call": None
        }
        async for res in stream:

            if res.get("content"):
                response["content"] += res.get("content")

            if res.get("function_call"):
                # TODO: process function call
                # print(res.get("function_call"))
                response["function_call"] = res.get("function_call")
                # if self._on_function_call:
                    # self._on_function_call(res.get("function_call"))
        

        if not response["content"]:
            response.pop("content")

        if not response["function_call"]:
            response.pop("function_call")
            
        return response    



if __name__ == "__main__":
    
    # load env variables from ../example/.env
    from dotenv import load_dotenv
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

    # Agentjob
    job = AgentJob("123", 
                   lead, 
                   prompt=prompt, 
                   message="Tell me the price of BTC in USD.", 
                   init_state={"name": "Lola"}
                   )

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

    agent.add_user_message(lead, "Hello! my name is John Doe")

    # process job
    res = asyncio.run(agent.process_results_coro(agent.process(job)))
    content = res.get("content")
    function_call = res.get("function_call")

    if function_call:
        print("-------------- Begin Function Call --------------")
        # process function call
        agent.add_function_call_message(lead, function_call)
        # TODO: process function call
        agent.add_function_response_message(lead, function_call, "BTC price is $50,000")

        # remove message from job, so that the agent can process the function call
        job.message = None
        # reprocess job
        res = asyncio.run(agent.process_results_coro(agent.process(job)))

        content = res.get("content")
        function_call = res.get("function_call")
        print("-------------- End Function Call --------------")
        
    print("-------------- DONE! --------------")