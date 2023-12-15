from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage


import prompts
import schema
import utils

class Model(object):
    def __init__(self):
        self.messages = [prompts.get_system_message()]
        self.model = None

    def prompt(self, prompt: HumanMessage) -> AIMessage:
        if not self.model:
            raise AttributeError("Attribute 'model' is missing")
        self.messages.append(prompt)
        response = self.model(self.messages)
        self.messages.append(response)
        return response


class OpenAIChatModel(Model):
    def __init__(self, model_name: str):
        super().__init__()
        self.model = ChatOpenAI(
            model_name=model_name,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

