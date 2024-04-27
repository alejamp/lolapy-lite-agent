import asyncio
from loguru import logger as log
import uuid
from collections.abc import Callable
from lolapy_lite_agent.agents.lola import LolaAgent
from lolapy_lite_agent.chat_lead import ChatLead
from lolapy_lite_agent.client_command import ClientCommand, parse_client_command
from lolapy_lite_agent.nlp_job import AgentJob

# on_function_call is a callable that will be called when a function call is detected
# has 3 arguments: lead, function_name, function_arguments
# and should return a response string

class AgentController:
    def __init__(self, 
                 prompt: str, 
                 user_id: str, 
                 openai_api_key: str,
                 on_text_received: callable = None,
                 on_function_call: Callable[[ChatLead, str, str], str] = None,
                 on_update_state: callable = None,
                 redis_url: str = None,
                 init_state: dict = None):
        # prompt
        self.prompt = prompt
        self.user_id = user_id
        self.openai_api_key = openai_api_key
        self.on_text_received = on_text_received
        self.on_function_call = on_function_call
        self.init_state = init_state
        self.on_update_state = on_update_state
        self.processing = False

        # ChatLead
        self.lead = ChatLead(user_id, "rtc", "tenant1", "assistant1")


        # LolaAgent
        self.agent = LolaAgent(api_key=self.openai_api_key, 
                        on_text_received=self.on_text_received,
                        on_function_call=self.on_function_call,
                        redis_url=redis_url,
                    )



    def process_message(self, message: str):
        cmd = parse_client_command(message)

        if cmd:
            self.process_client_command(cmd)
            return

        job = self.create_user_message_agent_job(message)

        self._update_processing_state(True)
        # process job
        res = asyncio.run(self.agent.process_results_coro(self.agent.process(job)))
        content = res.get("content")
        function_call = res.get("function_call")

        if function_call:
            # process function call
            self.agent.add_function_call_message(self.lead, function_call)
            # TODO: process function call
            if self.on_function_call:
                function_response = self.on_function_call(self.lead, function_call.get("name"), function_call.get("arguments"))
                self.agent.add_function_response_message(self.lead, function_call, function_response)

            # remove message from job, so that the agent can process the function call
            job.message = None
            # reprocess job
            res = asyncio.run(self.agent.process_results_coro(self.agent.process(job)))

            content = res.get("content")
            function_call = res.get("function_call")
        
        self._update_processing_state(False)
        return content



    def create_user_message_agent_job(self, message: str):
        # generate job_id using uuid short
        job_id = str(uuid.uuid4())[:8]
        job = AgentJob(job_id, 
                        self.lead, 
                        prompt=self.prompt, 
                        message=message, 
                        init_state=self.init_state
                    )

        return job
    

    def process_client_command(self, cmd: ClientCommand):
        
        # process client command
        if cmd.command == "/reset":
            if cmd.args == ["all"]:
                self.agent.clear_history(self.lead)
                self.agent.clear_state(self.lead)
                log.warning("Resetting all")
            else:
                self.agent.clear_history(self.lead)
                log.warning("Resetting history")

        elif cmd.command == "/state":
            if cmd.args == ["set"]:
                key = cmd.args[1]
                value = cmd.args[2]
                self.agent._stateStore.set_key_value(self.lead, key, value)
                log.warning(f"Setting state: {key}={value}")
        else:
            log.warning(f"Unknown command: {cmd.command}")
            return None

    def _update_processing_state(self, processing = False):
        self.processing = processing
        if self.on_update_state:
            self.on_update_state(processing)
            



if __name__ == "__main__":

    # load env variables from ../example/.env
    from dotenv import load_dotenv
    import os
    load_dotenv(dotenv_path="./example/.env")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # prompt
    prompt = """
    <settings
        model="gpt-4-0613"
        temperature="0.0"
        top_p="0.0"
        max_tokens="800"
        max_history_length="10"
    ></settings>    
    Create an assistant called {{state.name}}
        <function name="get_cryptocurrency_price" description="Get the current cryptocurrency price">
            <parameters type="object">
                <param name="cryptocurrency" type="string" description="The cryptocurrency abbreviation eg. BTC, ETH"/>
                <param name="currency" type="string" enum="USD,ARG" />
            </parameters>
        </function>
    """

    def on_function_call(lead, function_name, function_arguments):
        print(">>>>>> ",function_name)
        return f"The Bitcoin price is $1000"

    ctr = AgentController(prompt, "123", OPENAI_API_KEY, 
                          on_function_call=on_function_call, 
                          on_text_received=lambda x: print(x, end=""),
                          on_update_state=lambda x: log.info(f"Processing: {x}"))
    
    ctr.process_client_command(ClientCommand("/reset", ["all"]))

    ctr.process_message("Tell me the price of BTC in USD.")