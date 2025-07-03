import logging
from abc import ABC
from duckduckgo_search import DDGS
import pandas as pd
from agent.component.base import ComponentBase, ComponentParamBase


class DuckDuckGoParam(ComponentParamBase):
    """
    Define the DuckDuckGo component parameters.
    """

    def __init__(self):
        super().__init__()
        self.top_n = 10
        self.channel = "text"

    def check(self):
        self.check_positive_integer(self.top_n, "Top N")
        self.check_valid_value(self.channel, "Web Search or News", ["text", "news"])


class DuckDuckGo(ComponentBase, ABC):
    component_name = "DuckDuckGo"

    def _run(self, history, **kwargs):
        ans = self.get_input()
        ans = " - ".join(ans["content"]) if "content" in ans else ""
        if not ans:
            return DuckDuckGo.be_output("")

        try:
            if self._param.channel == "text":
                with DDGS() as ddgs:
                    # {'title': '', 'href': '', 'body': ''}
                    duck_res = [{"content": '<a href="' + i["href"] + '">' + i["title"] + '</a>    ' + i["body"]} for i
                                in ddgs.text(ans, max_results=self._param.top_n)]
            elif self._param.channel == "news":
                with DDGS() as ddgs:
                    # {'date': '', 'title': '', 'body': '', 'url': '', 'image': '', 'source': ''}
                    duck_res = [{"content": '<a href="' + i["url"] + '">' + i["title"] + '</a>    ' + i["body"]} for i
                                in ddgs.news(ans, max_results=self._param.top_n)]
        except Exception as e:
            return DuckDuckGo.be_output("**ERROR**: " + str(e))

        if not duck_res:
            return DuckDuckGo.be_output("")

        df = pd.DataFrame(duck_res)
        logging.debug("df: {df}")
        return df
