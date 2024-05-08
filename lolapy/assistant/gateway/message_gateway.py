# Copyright 2023 Leapfinancial LLC
# Author: Alejandro Pirola - alejamp@gmail.com

import asyncio
import json
from typing import AsyncIterable
from collections.abc import Callable
from loguru import logger as log
from lolapy.assistant.agents.lola import LolaAgent
from lolapy.assistant import AgentJob, ChatLead
from lolapy.assistant.gateway.context import LolaContext
from lolapy.assistant.gateway.gateway import Gateway
from lolapy.assistant.utils import get_invariant_hash



class LolaMessageGateway (Gateway):
    """Lola Lite Message Gateway"""

    def __init__(self, 
                 session_id: str,
                 prompt: str, 
                 openai_api_key: str, 
                 redis_url: str = None,
                 on_text_received: callable = None,
                 on_function_call: Callable[[ChatLead, str, str], str] = None,
                 on_outgoing_message: Callable[[ChatLead, str], None] = None,
                 init_state: dict = {}):
        """
        Args:
            prompt (str): Lola PML compatible prompt
        """

        self.on_function_call = on_function_call
        # def on_function_call_handler(lead, function_name, function_arguments):
        #     log.critical(f"Function call: {function_name}")
        #     if self.on_function_call is not None:
        #         return self.on_function_call(lead, function_name, function_arguments)
            

        self.agent = LolaAgent(
            openai_api_key, 
            redis_url=redis_url,
            on_text_received=on_text_received)
        
        self._first_message = None
                           
        self.prompt = prompt
        self.init_state = init_state

        self.on_outgoing_message = on_outgoing_message
        self._producing_response = False
        self._needs_interrupt = False
        self.session_id = session_id
         # ChatLead
        self.lead = ChatLead(session_id, "test", "tenant", "assistant")
        self.events = []
        self.cmd_handlers = {}        
        self.client_cmd_handlers = {}
        self.event_handlers = {}
        self.notification_handlers = {}
        self.timeout_handler = None
        self.callback_handlers = {}

    def process_message(self, message: str):
        self.agent.process_message(message)


    def interrupt(self):
        """Interrupt a currently streaming response (if there is one)"""
        if self._producing_response:
            self._needs_interrupt = True

    async def aclose(self):
        pass


    # first_message getter and setter
    @property
    def first_message(self):
        if self._first_message is None:
            self._first_message = self.agent.is_first_message(self.lead)
        return self._first_message
    
    @first_message.setter
    def first_message(self, value):
        self._first_message = value

    async def add_outgoing_message(self, message: str, appendToHistory=False, isPrivate=False, blend=False):

        if isPrivate:
            log.critical(f"Sending private message not implemented yet")

        if blend:
            log.info(f"Blending message into context")
            message = await self.agent.blend_message_into_context(self.lead, message)

        if appendToHistory:
            self.agent.add_user_message(self.lead, message)

        try: 
            if self.on_outgoing_message:
                self.on_outgoing_message(self.lead, message)

        except Exception as e:
            log.error(f"Error on outgoing message: {e}")

        

    async def add_message(
        self, message: str, new_state: dict = None, job_id: str = None
    ) -> AsyncIterable[str]:
        """Add a message to the chat and generate a streamed response
        Args:
            message (ChatGPTMessage): The message to add
        Returns:
            AsyncIterable[str]: Streamed ChatGPT response
        """

        if self.first_message:
            await self._call_event("onNewConversation", {
                "lead": self.lead,
                "text": message
            })
            self._first_message = False
        else:
            await self._call_event("onTextMessage", {
                "lead": self.lead,
                "text": message
            })

        # Agentjob
        # TODO: job_id should be unique
        job = AgentJob(job_id or "123",
                        self.lead,
                        prompt=self.prompt, 
                        message=message,
                        init_state=self.init_state,
                        new_state=new_state
                    )   

        async for text in self.handle_lola_stream(job):
            yield text
            
    def get_agent(self):
        return self.agent
    
    def get_lead(self):
        return self.lead

    def clear_history(self):
        """Clear the chat history"""
        log.warning("Clearing chat history")
        self._first_message = None
        self.agent.clear_history(self.lead)

    def add_message_to_history(self, role: str, message: str):
        if role == "user":
            self.agent.add_user_message(self.lead, message)
        elif role == "assistant":
            self.agent.add_assistant_message(self.lead, message)

    def get_context(self):
        return LolaContext(self)

    async def _call_function(self, function_name: str, function_arguments: dict) -> str:
        log.info(f"Calling function {function_name} with arguments: {function_arguments}")

        if self.on_function_call is not None:
            self.on_function_call(self.lead, function_name, function_arguments)

        ctx = self.get_context()
        if function_name in self.cmd_handlers:
            args = json.loads(function_arguments)
            external_function = self.cmd_handlers[function_name]
            # external function is async?
            res = ""
            if asyncio.iscoroutinefunction(external_function):
                res = await self.cmd_handlers[function_name](self.__buildSession(), ctx, {
                    "data": {
                        "name": function_name,
                        "args": args 
                        }
                    })
            else: 
                res =  self.cmd_handlers[function_name](self.__buildSession(), ctx, {
                    "data": {
                        "name": function_name,
                        "args": args 
                        }
                    })
            log.info(f"Function {function_name} called with response: {res}")
            return res
        

    async def _call_event(self, event_name: str, event_arguments: dict):
        log.info(f"Handling event {event_name} with arguments: {event_arguments}")
        ctx = self.get_context()
        if event_name in self.event_handlers:
            session = self.__buildSession()
            handler = self.event_handlers[event_name]
            res = ""
            if asyncio.iscoroutinefunction(handler):
                res = await self.event_handlers[event_name](session, ctx, event_arguments)
            else:
                res = self.event_handlers[event_name](session, ctx, event_arguments)
                
                
            log.info(f"Event {event_name} handled with response: {res}")

        return

    async def handle_lola_stream(self, job) -> AsyncIterable[str]:
        """Handle a Lola stream """

        self._producing_response = True
        complete_content = ""
        async for delta_dict in self.agent.process(job):
            content = delta_dict.get("content")
            function_call = delta_dict.get("function_call")

            if content:
                complete_content += content
                yield content

        # There was a function call?
        if function_call:
            self.agent.add_function_call_message(self.lead, function_call)

            # TODO: process function call
            # self.agent.add_function_response_message(self.lead, function_call, "BTC price is $69,124")

            # if self.on_function_call:
            # function_response = self.on_function_call(self.lead, function_call.get("name"), function_call.get("arguments"))
            function_response = await self._call_function(function_call.get("name"), function_call.get("arguments"))
            self.agent.add_function_response_message(self.lead, function_call, function_response)

            # clone job dataclass instance, remove message
            new_job = AgentJob(
                job_id=job.job_id, 
                lead=job.lead, 
                prompt=job.prompt, 
                message=None, 
                init_state=job.init_state)
            
            complete_content = ''
            async for delta in self.agent.process(new_job):
                content = delta.get("content")
                if content:
                    complete_content += content
                    yield content


        # add assistant response message
        # self.agent.add_assistant_message(self.lead, complete_content)
        self._producing_response = False

    def __buildSession(self):
        # generate hash as a unique identifier for this lead
        hlead = get_invariant_hash(self.lead)
        session = {
            'id': hlead,
            'lead': self.lead,
        }
        return session

    def on_command(self, name):
        def decorator(handler):
            self.cmd_handlers[name] = handler
            return handler
        return decorator
    
    # CLIENT_COMMAND by Ale
    def on_client_command(self, name):
        def decorator(handler):
            self.client_cmd_handlers[name] = handler
            return handler
        return decorator
    
    def on_event(self, name):
        def decorator(handler):
            self.event_handlers[name] = handler
            return handler
        return decorator
    
    def on_notification(self, name):
        def decorator(handler):
            self.notification_handlers[name] = handler
            return handler
        return decorator
    
    # TODO: Implement timeout handler
    # def on_timeout(self):
    #     def decorator(handler):
    #         print ('LolaSDK -> Setting timeout handler')
    #         self.timeout = LolaTimeout(handler)
    #         return handler
    #     return decorator




if __name__ == "__main__":
    

    # load env variables from ../example/.env
    import os
    from dotenv import load_dotenv
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

    log.info("Starting Lola Plugin")

    lola = LolaMessageGateway("123", prompt, OPENAI_API_KEY, init_state=INIT_STATE)

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
    # asyncio.run(main3())
    print("\n")
    log.critical("---------------------------DONE-------------------------------")