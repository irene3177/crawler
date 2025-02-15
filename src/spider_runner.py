import logging
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher
from .sitemap_spider import SitemapSpider

logger = logging.getLogger(__name__)

class SpiderRunner:
    def __init__(self):
        self.urls = []

    def run_spider(self, start_url, output_file='sitemap.json', max_pages=50):
        """Starts the sitemap spider to crawl URLs."""
        process = CrawlerProcess(get_project_settings())
        
        # Connect to the item scraped signal
        dispatcher.connect(self.collect_urls, signal=scrapy.signals.item_scraped)
        
        # Start the crawler
        process.crawl(SitemapSpider, start_url=start_url, output_file=output_file, max_pages=max_pages)
        process.start()  # The script will block here until the crawling is finished
        return self.urls

    def collect_urls(self, item, response, **kwargs):
        """Collects URLs from the scraped items."""
        url = item['url']
        self.urls.append(url)