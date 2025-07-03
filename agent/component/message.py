import random
from abc import ABC
from functools import partial
from agent.component.base import ComponentBase, ComponentParamBase


class MessageParam(ComponentParamBase):

    """
    Define the Message component parameters.
    """
    def __init__(self):
        super().__init__()
        self.messages = []

    def check(self):
        self.check_empty(self.messages, "[Message]")
        return True


class Message(ComponentBase, ABC):
    component_name = "Message"

    def _run(self, history, **kwargs):
        if kwargs.get("stream"):
            return partial(self.stream_output)

        res = Message.be_output(random.choice(self._param.messages))
        self.set_output(res)
        return res

    def stream_output(self):
        res = None
        if self._param.messages:
            res = {"content": random.choice(self._param.messages)}
            yield res

        self.set_output(res)


