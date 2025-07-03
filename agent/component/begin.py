from functools import partial
import pandas as pd
from agent.component.base import ComponentBase, ComponentParamBase


class BeginParam(ComponentParamBase):

    """
    Define the Begin component parameters.
    """
    def __init__(self):
        super().__init__()
        self.prologue = "Hi! I'm your smart assistant. What can I do for you?"
        self.query = []

    def check(self):
        return True


class Begin(ComponentBase):
    component_name = "Begin"

    def _run(self, history, **kwargs):
        if kwargs.get("stream"):
            return partial(self.stream_output)
        return pd.DataFrame([{"content": self._param.prologue}])

    def stream_output(self):
        res = {"content": self._param.prologue}
        yield res
        self.set_output(self.be_output(res))



