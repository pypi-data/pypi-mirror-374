import io
import requests
from twisted.python.failure import Failure

from vital_llm_reasoner.tool.ensemble_tool import EnsembleTool
from scrapy_playwright.page import PageMethod
from markitdown import MarkItDown
from enum import Enum
from dataclasses import dataclass
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError


class WebExtractStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

@dataclass
class WebExtractResult:
    status: WebExtractStatus
    url: str
    text: str

class WebExtractSpider(scrapy.Spider):
    name = "web_extract_spider"

    def __init__(self, urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls if urls else []
        self.md_converter = MarkItDown()

        self.error_list = []


    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "CONCURRENT_REQUESTS": 5,
        "DOWNLOAD_TIMEOUT": 10,
        "LOG_LEVEL": "INFO"
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [PageMethod("wait_for_load_state", "networkidle")],
                },
                callback=self.parse,
                errback=self.handle_failure
            )

    def parse(self, response, **kwargs):
        html_content = response.body
        try:
            fake_response = requests.Response()
            fake_response.raw = io.BytesIO(html_content)

            markdown_content = self.md_converter.convert(fake_response).text_content

            yield WebExtractResult(
                status=WebExtractStatus.SUCCESS,
                url=response.url,
                text=markdown_content
            )
        except Exception as e:
            self.logger.error(f"Error converting HTML to Markdown for {response.url}: {e}")
            yield WebExtractResult(
                status=WebExtractStatus.FAILURE,
                url=response.url,
                text=""
            )

    def handle_failure(self, failure: Failure):
        self.logger.error(f"Request failed with {failure.value}")

        try:

            if failure.check(HttpError):

                response = failure.value.response

                error_result = WebExtractResult(
                    status=WebExtractStatus.FAILURE,
                    url=response.url,
                    text=""
                )

                self.error_list.append(error_result)

                self.logger.error('HTTPError on %s', response.url)

            elif failure.check(DNSLookupError):
                # This is the original request
                request = failure.request

                error_result = WebExtractResult(
                    status=WebExtractStatus.FAILURE,
                    url=request.url,
                    text=""
                )

                self.error_list.append(error_result)

                self.logger.error('DNSLookupError on %s', request.url)

            elif failure.check(TimeoutError, TCPTimedOutError):
                request = failure.request

                error_result = WebExtractResult(
                    status=WebExtractStatus.FAILURE,
                    url=request.url,
                    text=""
                )

                self.error_list.append(error_result)

                self.logger.error('TimeoutError on %s', request.url)

        except Exception as e:
            self.logger.error(f"Error handling failure: {e}")



class WebExtractTool(EnsembleTool):
    @classmethod
    def extract(cls, urls):
        settings = Settings()
        settings.set("PLAYWRIGHT_BROWSER_TYPE", "chromium")
        settings.set("PLAYWRIGHT_LAUNCH_OPTIONS", {"headless": True})
        settings.set("LOG_LEVEL", "INFO")
        settings.set("CONCURRENT_REQUESTS", 16)
        settings.set("DOWNLOAD_TIMEOUT", 2)

        process = CrawlerProcess(settings)
        results = []

        def store_result(item, response, spider):
            if isinstance(item, WebExtractResult):
                results.append(item)

        process.crawl(WebExtractSpider, urls=urls)

        spider_list = []

        for crawler in process.crawlers:
            if isinstance(crawler.spider, WebExtractSpider):
                spider_instance = crawler.spider
                spider_list.append(spider_instance)

            crawler.signals.connect(store_result, signal=scrapy.signals.item_scraped)

        process.start()

        for spider in spider_list:
            results.extend(spider.error_list)

        return results
