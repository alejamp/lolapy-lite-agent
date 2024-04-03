from typing import Callable, Dict, Any
from lolapy_lite_agent.chat_lead import ChatLead
from lolapy_lite_agent.pml.pml_builder import PMLBuilder

class PmlFunctionsPlugin:
    def __init__(self, lead: ChatLead, callback: Callable[[Any], Any]) -> None:
        self.name = "Function"
        self.description = "Function Plugin Implementation"
        self.element_name = "function"
        self.lead = lead
        self.callback = callback

    def process(self, element: Any, attrs: Dict[str, str], inner_text: str, context: PMLBuilder) -> str:
        func = {
            'name': '',
            'description': '',
            'parameters': {
                'type': 'object',
                'properties': {},
                'required': []
            }
        }

        try:
            func['name'] = attrs.get('name', '')
            func['description'] = attrs.get('description', '')
            parameters = [e for e in element.children if e.name == 'parameters']

            if parameters:
                params = [e for e in parameters[0].children if e.name == 'param']

                if params:
                    for param in params:
                        attributes = param.attrs
                        attr = attributes.copy()

                        if attr.get('required', '').lower() == 'true':
                            del attr['required']
                            func['parameters']['required'].append(attr['name'])

                        if 'enum' in attributes:
                            attr['enum'] = attributes['enum'].split(',')

                        func['parameters']['properties'][attr['name']] = attr

            if self.callback:
                result = self.callback(func)
                return result

        except Exception as error:
            print(f"Error: {error}")

        return ''
    


if __name__ == "__main__":
    import json 
    

    pml = """
    <function name="get_cryptocurrency_price" description="Get the current cryptocurrency price">
    <parameters type="object">
        <param name="cryptocurrency" type="string" description="The cryptocurrency abbreviation eg. BTC, ETH" required/>
        <param name="currency" type="string" enum="USD,ARG" />
        </parameters>
    </function>
"""


    builder = PMLBuilder(pml)

    functions = []
    # add a lambda function to the plugin which will be called when the plugin is processed
    # this function will append the function to the functions list
    plugin = PmlFunctionsPlugin(None, lambda func: functions.append(func))
    builder.register_plugin(plugin)
    builder.compile()

    print("Functions:")
    for f in functions:
        print("-------------------------------------------------------------")
        print(json.dumps(f, indent=4))
    