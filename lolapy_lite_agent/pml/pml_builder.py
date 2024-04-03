import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from bs4 import Comment

class PMLBuilder:
    def __init__(self, pml: str):
        self.hpml = pml
        self.root = BeautifulSoup(pml, 'lxml')
        self.params = []
        self.settings = {}
        self.parser_settings = {'recognizeSelfClosing': False, 'xmlMode': True, 'decodeEntities': False}
        self.system_tags = [
            "settings",
            "script",
            "command",
            "test",
            "mood",
        ]
        self.plugins = []

    def set_params(self, params: Optional[List[Dict[str, Any]]]):
        self.params = params or []

    def get_settings(self):
        return self.settings

    def load_settings(self):
        elements = self.root.find_all("settings")
        if elements:
            self.settings = elements[0].attrs

    def process_tag(self, tag: str, tag_function):
        tags = self.root.find_all(tag)
        for tag in tags:
            attrs = tag.attrs
            innerText = tag.string
            tag.replace_with(tag_function(attrs, innerText))

    def remove_system_tags(self):
        for tag in self.system_tags:
            for match in self.root.findAll(tag):
                match.decompose()

    def remove_comments(self):
        # BeautifulSoup remove all comments from self.root
        comments = self.root.findAll(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

    def prepare_text(self, text: str):
        text = re.sub(r'<!--[\s\S]*?-->', '', text)
        text = re.sub(r'(\r\n|\r|\n){2,}', '$1', text)
        text = re.sub(r'<br\s*\/?>', '\n', text)
        text = text.strip()
        return text

    def process_plugins(self):
        for plugin in self.plugins:
            elements = self.root.find_all(plugin.element_name)
            for element in elements:
                try:
                    attrs = element.attrs
                    innerText = element.string
                    res = plugin.process(element, attrs, innerText, self)
                    element.replace_with(res)
                except Exception as e:
                    print(e)

    def register_plugin(self, plugin):
        self.plugins.append(plugin)

    def compile(self):
        try:
            self.load_settings()
            self.remove_system_tags()
            self.remove_comments()

            self.process_plugins()

            # res = str(self.root)
            res = self.root.get_text()
            res = self.prepare_text(res)
            return {
                'prompt': res,
                'params': {},
                'settings': self.settings
            }
        except Exception as e:
            print(e)
            return {
                'error': str(e)
            }
        

if __name__ == "__main__":
    # load sample pml from file sample_prompt.hbr
    with open("lolapy_lite_agent/pml/sample_prompt.pml", "r") as f:
        pml = f.read()


    builder = PMLBuilder(pml)

    # register function plugin
    from lolapy_lite_agent.pml.function_plugin import PmlFunctionsPlugin
    functions = []
    # add a lambda function to the plugin which will be called when the plugin is processed
    # this function will append the function to the functions list
    plugin = PmlFunctionsPlugin(None, lambda func: functions.append(func))
    builder.register_plugin(plugin)
    


    res = builder.compile()
    print(json.dumps(res, indent=4))

    print('Functions: --------------------------------------------')
    for func in functions:
        print(json.dumps(func, indent=4))