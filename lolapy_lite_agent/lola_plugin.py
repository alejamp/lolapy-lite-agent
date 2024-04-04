# Copyright 2023 Leapfinancial LLC
# Author: Alejandro Pirola - alejamp@gmail.com

import asyncio
from typing import AsyncIterable, List, Optional
from collections.abc import Callable
from loguru import logger as log
from lolapy_lite_agent.agent_controller import AgentController
from lolapy_lite_agent.agents.lola import LolaAgent
from lolapy_lite_agent.chat_lead import ChatLead
from lolapy_lite_agent.client_command import ClientCommand
from lolapy_lite_agent.nlp_job import AgentJob



class LolaPlugin:
    """Lola Lite Agent Plugin"""

    def __init__(self, 
                 user_id: str, 
                 prompt: str, 
                 openai_api_key: str, 
                 on_text_received: callable = None,
                 on_function_call: Callable[[ChatLead, str, str], str] = None,
                 init_state: dict = {}):
        """
        Args:
            prompt (str): Lola PML compatible prompt
        """
        def on_function_call(lead, function_name, function_arguments):
            print(">>>>>> ",function_name)
            return f"The Bitcoin price is $1000"

        self.agent = LolaAgent(openai_api_key, on_text_received=on_text_received)
                               
        self.prompt = prompt
        self.init_state = init_state
        self.on_function_call = on_function_call
        self._producing_response = False
        self._needs_interrupt = False
        self.user_id = user_id
         # ChatLead
        self.lead = ChatLead(user_id, "test", "tenant", "assistant")

    def process_message(self, message: str):
        self.agent.process_message(message)


    def interrupt(self):
        """Interrupt a currently streaming response (if there is one)"""
        if self._producing_response:
            self._needs_interrupt = True

    async def aclose(self):
        pass

    # async def send_system_prompt(self) -> AsyncIterable[str]:
    #     """Send the system prompt to the chat and generate a streamed response

    #     Returns:
    #         AsyncIterable[str]: Streamed ChatGPT response
    #     """
    #     async for text in self.add_message(None):
    #         yield text

    async def add_message(
        self, message: str
    ) -> AsyncIterable[str]:
        """Add a message to the chat and generate a streamed response
        Args:
            message (ChatGPTMessage): The message to add
        Returns:
            AsyncIterable[str]: Streamed ChatGPT response
        """

        # Agentjob
        job = AgentJob("123",
                    self.lead,
                    prompt=self.prompt, 
                    message=message,
                    init_state=self.init_state
                    )        

        async for text in self.handle_lola_stream(job):
            yield text



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
            self.agent.add_function_response_message(self.lead, function_call, "BTC price is $50,000")

            if self.on_function_call:
                function_response = self.on_function_call(self.lead, function_call.get("name"), function_call.get("arguments"))
            # self.agent.add_function_response_message(self.lead, function_call, function_response)            

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


if __name__ == "__main__":
    

    # load env variables from ../example/.env
    import os
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

    log.info("Starting Lola Plugin")

    lola = LolaPlugin("123", prompt, OPENAI_API_KEY)

    lola.agent.clear_history(lola.lead)

    async def main1():
        log.critical("----------------------------------------------------------")
        async for text in lola.add_message("tell me how much is 2+2"):
            print(text, end="")

    

    async def main2():
        log.critical("----------------------------------------------------------")
        async for text in lola.add_message("What is the Bitcoin price in USD."):
            print(text, end="")
    
    async def main3():
        log.critical("----------------------------------------------------------")
        async for text in lola.add_message("tell me how much is 3+3"):
            print(text, end="")
    
        # history = lola.agent._historyStore.get_history(lola.lead)

        # print(history)

    # Run each main in sequence, avoid parallel execution
    asyncio.run(main1())
    asyncio.run(main2())
    asyncio.run(main3())
    
    log.critical("---------------------------DONE-------------------------------")