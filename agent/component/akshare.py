from abc import ABC
import pandas as pd
from agent.component.base import ComponentBase, ComponentParamBase


class AkShareParam(ComponentParamBase):
    """
    Define the AkShare component parameters.
    """

    def __init__(self):
        super().__init__()
        self.top_n = 10

    def check(self):
        self.check_positive_integer(self.top_n, "Top N")


class AkShare(ComponentBase, ABC):
    component_name = "AkShare"

    def _run(self, history, **kwargs):
        import akshare as ak
        ans = self.get_input()
        ans = ",".join(ans["content"]) if "content" in ans else ""
        if not ans:
            return AkShare.be_output("")

        try:
            ak_res = []
            stock_news_em_df = ak.stock_news_em(symbol=ans)
            stock_news_em_df = stock_news_em_df.head(self._param.top_n)
            ak_res = [{"content": '<a href="' + i["新闻链接"] + '">' + i["新闻标题"] + '</a>\n 新闻内容: ' + i[
                "新闻内容"] + " \n发布时间:" + i["发布时间"] + " \n文章来源: " + i["文章来源"]} for index, i in stock_news_em_df.iterrows()]
        except Exception as e:
            return AkShare.be_output("**ERROR**: " + str(e))

        if not ak_res:
            return AkShare.be_output("")

        return pd.DataFrame(ak_res)
