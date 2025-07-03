from abc import ABC
from agent.component.base import ComponentBase, ComponentParamBase


class IterationParam(ComponentParamBase):
    """
    Define the Iteration component parameters.
    """

    def __init__(self):
        super().__init__()
        self.delimiter = ","

    def check(self):
        self.check_empty(self.delimiter, "Delimiter")


class Iteration(ComponentBase, ABC):
    component_name = "Iteration"

    def get_start(self):
        for cid in self._canvas.components.keys():
            if self._canvas.get_component(cid)["obj"].component_name.lower() != "iterationitem":
                continue
            if self._canvas.get_component(cid)["parent_id"] == self._id:
                return self._canvas.get_component(cid)

    def _run(self, history, **kwargs):
        return self.output(allow_partial=False)[1]

