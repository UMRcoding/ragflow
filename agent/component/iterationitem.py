from abc import ABC
import pandas as pd
from agent.component.base import ComponentBase, ComponentParamBase


class IterationItemParam(ComponentParamBase):
    """
    Define the IterationItem component parameters.
    """
    def check(self):
        return True


class IterationItem(ComponentBase, ABC):
    component_name = "IterationItem"

    def __init__(self, canvas, id, param: ComponentParamBase):
        super().__init__(canvas, id, param)
        self._idx = 0

    def _run(self, history, **kwargs):
        parent = self.get_parent()
        ans = parent.get_input()
        ans = parent._param.delimiter.join(ans["content"]) if "content" in ans else ""
        ans = [a.strip() for a in ans.split(parent._param.delimiter)]
        if not ans:
            self._idx = -1
            return pd.DataFrame()

        df = pd.DataFrame([{"content": ans[self._idx]}])
        self._idx += 1
        if self._idx >= len(ans):
            self._idx = -1
        return df

    def end(self):
        return self._idx == -1

