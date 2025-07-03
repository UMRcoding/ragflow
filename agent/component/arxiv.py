import logging
from abc import ABC
import arxiv
import pandas as pd
from agent.component.base import ComponentBase, ComponentParamBase

class ArXivParam(ComponentParamBase):
    """
    Define the ArXiv component parameters.
    """

    def __init__(self):
        super().__init__()
        self.top_n = 6
        self.sort_by = 'submittedDate'

    def check(self):
        self.check_positive_integer(self.top_n, "Top N")
        self.check_valid_value(self.sort_by, "ArXiv Search Sort_by",
                               ['submittedDate', 'lastUpdatedDate', 'relevance'])


class ArXiv(ComponentBase, ABC):
    component_name = "ArXiv"

    def _run(self, history, **kwargs):
        ans = self.get_input()
        ans = " - ".join(ans["content"]) if "content" in ans else ""
        if not ans:
            return ArXiv.be_output("")

        try:
            sort_choices = {"relevance": arxiv.SortCriterion.Relevance,
                            "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
                            'submittedDate': arxiv.SortCriterion.SubmittedDate}
            arxiv_client = arxiv.Client()
            search = arxiv.Search(
                query=ans,
                max_results=self._param.top_n,
                sort_by=sort_choices[self._param.sort_by]
            )
            arxiv_res = [
                {"content": 'Title: ' + i.title + '\nPdf_Url: <a href="' + i.pdf_url + '"></a> \nSummary: ' + i.summary} for
                i in list(arxiv_client.results(search))]
        except Exception as e:
            return ArXiv.be_output("**ERROR**: " + str(e))

        if not arxiv_res:
            return ArXiv.be_output("")

        df = pd.DataFrame(arxiv_res)
        logging.debug(f"df: {str(df)}")
        return df
