from abc import ABC
from agent.component.base import ComponentBase, ComponentParamBase


class ConcentratorParam(ComponentParamBase):
    """
    Define the Concentrator component parameters.
    """

    def __init__(self):
        super().__init__()

    def check(self):
        return True


class Concentrator(ComponentBase, ABC):
    component_name = "Concentrator"

    def _run(self, history, **kwargs):
        return Concentrator.be_output("")