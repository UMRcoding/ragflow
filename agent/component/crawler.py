from abc import ABC
import asyncio
from crawl4ai import AsyncWebCrawler
from agent.component.base import ComponentBase, ComponentParamBase
from api.utils.web_utils import is_valid_url


class CrawlerParam(ComponentParamBase):
    """
    Define the Crawler component parameters.
    """

    def __init__(self):
        super().__init__()
        self.proxy = None
        self.extract_type = "markdown"
    
    def check(self):
        self.check_valid_value(self.extract_type, "Type of content from the crawler", ['html', 'markdown', 'content'])


class Crawler(ComponentBase, ABC):
    component_name = "Crawler"

    def _run(self, history, **kwargs):
        ans = self.get_input()
        ans = " - ".join(ans["content"]) if "content" in ans else ""
        if not is_valid_url(ans):
            return Crawler.be_output("URL not valid")
        try:
            result = asyncio.run(self.get_web(ans))

            return Crawler.be_output(result)
            
        except Exception as e:
            return Crawler.be_output(f"An unexpected error occurred: {str(e)}")

    async def get_web(self, url):
        proxy = self._param.proxy if self._param.proxy else None
        async with AsyncWebCrawler(verbose=True, proxy=proxy) as crawler:
            result = await crawler.arun(
                url=url,
                bypass_cache=True
            )
            
            if self._param.extract_type == 'html':
                return result.cleaned_html
            elif self._param.extract_type == 'markdown':
                return result.markdown
            elif self._param.extract_type == 'content':
                result.extracted_content
            return result.markdown
