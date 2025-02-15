import scrapy
import json
import os
from urllib.parse import urlparse

class SitemapSpider(scrapy.Spider):
    name = "sitemap"

    def __init__(self, start_url=None, output_file='sitemap.json', max_pages=50, *args, **kwargs):
        super(SitemapSpider, self).__init__(*args, **kwargs)
        if start_url:
            self.start_urls = [start_url]
        #else:
        #    self.start_urls = []
        
        # Extract domain from the start_url to create a directory
        parsed_url = urlparse(start_url)
        domain_name = parsed_url.netloc  # e.g., "example.com"
        self.output_dir = os.path.join('crawled_data', domain_name)

        # Create the output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.output_file = os.path.join(self.output_dir, output_file)  # Full path for the output file
        
        self.urls = set()  # Initialize a set to hold unique URLs

        self.max_pages = max_pages  # Maximum number of pages to crawl
        self.crawled_pages = 0  # Counter to track crawled pages
        

    def parse(self, response):

        # Stop crawling if max_pages is reached
        if self.crawled_pages >= self.max_pages:
            self.logger.info("Reached max pages limit: %d", self.max_pages)
            return

        domain = urlparse(response.url).netloc
        
        # Extract all links from the page
        for href in response.css('a::attr(href)').getall():
            absolute_url = response.urljoin(href)
            link_domain = urlparse(absolute_url).netloc
            
            # Check if the URL is internal, does not point to files or images,
            # and does not contain query parameters
            if (link_domain == domain and
                    not absolute_url.endswith(('.jpg', '.jpeg', '.png', '.gif', 
                                               '.pdf', '.doc', '.docx', '.xls', '.xlsx')) and
                    not '?' in absolute_url):  # Exclude URLs with query parameters
                
                # Only store unique URLs
                if absolute_url not in self.urls:
                    self.urls.add(absolute_url)
                    self.crawled_pages += 1

                    # Yield the URL to be collected by the main script
                    yield {'url': absolute_url}

                    # Stop crawling if the limit is reached after increment
                    if self.crawled_pages >= self.max_pages:
                        break

        # At the end of parsing, write URLs to the output file
        if response.url == self.start_urls[0]:  # Check if it's the first response to avoid duplicates
           self.save_to_file()

    def save_to_file(self):
        # Convert the set of URLs to a list
        url_list = list(self.urls)
        
        # Write the list to a JSON file
        with open(self.output_file, 'w') as f:
            json.dump(url_list, f, indent=4)