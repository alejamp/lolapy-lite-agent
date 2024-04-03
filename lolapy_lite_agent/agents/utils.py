from enum import Enum
from typing import Iterable, Optional, Required, TypedDict, Literal


# ChatGPTMessageRole = Enum("MessageRole", ["system", "user", "assistant", "function"])


# {"role": "user", "content": "What is the weather like in Boston?"},
# {"role": "assistant", "content": null, "function_call": {"name": "get_current_weather", "arguments": "{ \"location\": \"Boston, MA\"}"}},
# {"role": "function", "name": "get_current_weather", "content": "{\"temperature\": "22", \"unit\": \"celsius\", \"description\": \"Sunny\"}"}

def create_prompt_message(content: str):
    return {
        "role": "system",
        "content": content
    }

def create_user_message(content: str, name: str= None):
    # Add name to the user message only if it is not None
    output = {
        "content": content,
        "role": "user"
    }
    if name:
        output["name"] = name

    return output


def create_assistant_message(content: str, name: str = None, function_call: dict = None):
    # Add name to the assistant message only if it is not None
    output = {
        "content": content,
        "role": "assistant"
    }
    if name:
        output["name"] = name
    if function_call:
        output["function_call"] = function_call

    return output


# def create_function_call(name: str, arguments: str):
#     return {
#         "name": name,
#         "arguments": arguments
#     }

def create_function_call_message(name: str, arguments: str): 
    output = {
        "role": "assistant",
        "content": "",
        "function_call": {
            "name": name,
            "arguments": arguments
        }
    }
    return output

def create_function_response_message(name: str, response: str):
    output = {
        "role": "function",
        "name": name,
        "content": response
    }
    return output


if __name__ == "__main__":
    pass
