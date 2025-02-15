import os
import json
import unittest
from scrapy.http import HtmlResponse, Request
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from src.sitemap_spider import SitemapSpider  

class SitemapSpiderTest(unittest.TestCase):

    def setUp(self):
        # Set up a temporary directory for output files
        self.output_dir = os.path.join('crawled_data', 'example.com')
        self.output_file = os.path.join(self.output_dir, 'sitemap.json')
        
        # Ensure the output directory is clean before each test
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, file))
            os.rmdir(self.output_dir)

    def test_spider_initialization(self):
        # Test spider initialization with a start URL
        start_url = 'https://example.com'
        spider = SitemapSpider(start_url=start_url)
        
        self.assertEqual(spider.start_urls, [start_url])
        self.assertEqual(spider.output_file, self.output_file)
        self.assertEqual(spider.max_pages, 50)
        self.assertEqual(spider.crawled_pages, 0)
        self.assertEqual(len(spider.urls), 0)

    def test_parse_method(self):
        # Test the parse method of the spider
        start_url = 'https://example.com'
        spider = SitemapSpider(start_url=start_url)

        # Create a fake HTML response with some links
        fake_html = """
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
                <a href="https://example.com/page3">Page 3</a>
                <a href="https://external.com/page4">External Page</a>
                <a href="https://example.com/image.jpg">Image</a>
                <a href="https://example.com/page5?query=param">Page with Query</a>
            </body>
        </html>
        """
        response = HtmlResponse(url=start_url, body=fake_html, encoding='utf-8')

        # Call the parse method
        results = list(spider.parse(response))

        # Check that only valid internal URLs are parsed
        expected_urls = [
            'https://example.com/page1',
            'https://example.com/page2',
            'https://example.com/page3',
        ]
        self.assertEqual(len(results), len(expected_urls))
        for result in results:
            self.assertIn(result['url'], expected_urls)

        # Check that the URLs are added to the set
        self.assertEqual(len(spider.urls), len(expected_urls))
        for url in expected_urls:
            self.assertIn(url, spider.urls)

    def test_save_to_file(self):
        # Test the save_to_file method
        start_url = 'https://example.com'
        spider = SitemapSpider(start_url=start_url)

        # Add some URLs to the spider's set
        spider.urls.add('https://example.com/page1')
        spider.urls.add('https://example.com/page2')

        # Call the save_to_file method
        spider.save_to_file()

        # Check that the file was created and contains the correct data
        self.assertTrue(os.path.exists(self.output_file))
        with open(self.output_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertIn('https://example.com/page1', data)
            self.assertIn('https://example.com/page2', data)

    def test_max_pages_limit(self):
        # Test that the spider stops after reaching max_pages
        start_url = 'https://example.com'
        spider = SitemapSpider(start_url=start_url, max_pages=2)

        # Create a fake HTML response with multiple links
        fake_html = """
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
                <a href="/page3">Page 3</a>
            </body>
        </html>
        """
        response = HtmlResponse(url=start_url, body=fake_html, encoding='utf-8')

        # Call the parse method
        results = list(spider.parse(response))

        # Check that only 2 URLs were parsed
        self.assertEqual(len(results), 2)
        self.assertEqual(spider.crawled_pages, 2)

    def tearDown(self):
        # Clean up the output directory after each test
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, file))
            os.rmdir(self.output_dir)

if __name__ == '__main__':
    unittest.main()