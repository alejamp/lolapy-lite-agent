from dataclasses import dataclass
from pybars import Compiler
from lolapy_lite_agent.chat_lead import ChatLead
from lolapy_lite_agent.handlebars_helpers import get_handlebars_compiler, get_helpers
from lolapy_lite_agent.history.history_redis_provider import RedisHistoryProvider
from lolapy_lite_agent.nlp_job import AgentJob
from lolapy_lite_agent.pml.function_plugin import PmlFunctionsPlugin
from lolapy_lite_agent.pml.pml_builder import PMLBuilder
from lolapy_lite_agent.state.state_redis_provider import RedisChatStateProvider

@dataclass
class PromptCompiled:
    prompt: str
    settings: dict
    functions: list
    context: dict


class PromptCompiler:
    def __init__(self, job: AgentJob, prompt, historyStore: RedisHistoryProvider, stateStore: RedisChatStateProvider):
        self.prompt = prompt
        self.historyStore = historyStore
        self.stateStore = stateStore
        self.job = job

    
    def context(self, init_state={}, new_state={}):
        """Context for handlebars temaplating"""
        history = self.historyStore.get_history(self.job.lead)
        state = self.stateStore.get_store(self.job.lead) or {}
        new_state = new_state or {}

        # merge the initial state with the state from the store
        # init_state will be overwritten by the state dict from the store
        state = {**(init_state or {}), **state}
        # merge the new state with the state from the store
        # new_state will overwrite the state dict from the store
        state = {**state, **new_state}



        return {
            'history': history,
            'state': state,
            'message': self.job.message,
        }


    def process(self, init_state=None, new_state=None) -> PromptCompiled:
        hbc = get_handlebars_compiler()        
        template = hbc.compile(self.prompt)
        ctx = self.context(init_state, new_state)
        pml = template(ctx, helpers=get_helpers())

        # create a PML Builder
        pml_builder = PMLBuilder(pml)
        # register plugin functions
        
        functions = []
        # add a lambda function to the plugin which will be called when the plugin is processed
        # this function will append the function to the functions list
        plugin = PmlFunctionsPlugin(None, lambda func: functions.append(func))
        pml_builder.register_plugin(plugin)
            
        res = pml_builder.compile()

        return {
            'prompt': res['prompt'],
            'settings': res['settings'],
            'functions': functions,
            'context': ctx
        }


        


if __name__ == "__main__":
    prompt = "Hello {{state.name}}"
    lead = ChatLead("123", "test", "tenant", "assistant")
    job = AgentJob("j123", lead, "Hello")

    stateStore = RedisChatStateProvider()
    historyStore = RedisHistoryProvider()

    prompt_compiler = PromptCompiler(job, prompt, historyStore, stateStore)
        

    res = prompt_compiler.process({
        'name': 'John Doe'
    }, {
        'name': 'Jane Doe'
    })

    print(res)
    
