import unittest
from unittest.mock import patch, AsyncMock
import logging
import asyncio
from src.main import main  # Replace with your actual module name where main is defined

# Setup logging for tests (optional)
logging.basicConfig(level=logging.DEBUG)

class TestMainFunction(unittest.TestCase):

    @patch('src.url_check.check_url')  # Mock the check_url function
    @patch('src.robots_parser.fetch_robots_txt')  # Mock the fetch_robots_txt function
    @patch('src.sitemap_parser.fetch_sitemap_urls', new_callable=AsyncMock)  # Mock the fetch_sitemap_urls function
    @patch('src.sitemap_parser.get_sitemap_urls', new_callable=AsyncMock)  # Mock the get_sitemap_urls function
    @patch('src.scrap_static.scrap_website', new_callable=AsyncMock)  # Mock the scrap_website function
    @patch('src.crawl_parallel.crawl_parallel', new_callable=AsyncMock)  # Mock the crawl_parallel function
    async def test_main_crawl_all(self, mock_crawl_parallel, mock_scrap_website, mock_get_sitemap_urls,
                                   mock_fetch_sitemap_urls, mock_fetch_robots_txt, mock_check_url):
        # Set up mocks
        url = "https://example.com"
        mock_check_url.return_value = {'valid': True, 'url': url, 'message': ''}
        
        # Mock robots.txt content
        robots_rules = {
            'allow': ['/public'],
            'disallow': ['/private'],
            'sitemap': ['https://example.com/sitemap.xml']
        }
        mock_fetch_robots_txt.return_value = robots_rules
        
        # Mock sitemap URLs to return a simulated response
        sitemap_urls = robots_rules['sitemap']
        mock_fetch_sitemap_urls.side_effect = [AsyncMock(return_value=['https://example.com/page1']),
                                                AsyncMock(return_value=['https://example.com/page2'])]

        # Call the main function
        await main()

        # Assertions can be done here
        mock_check_url.assert_called_once_with(url)  # Ensure check_url was called
        mock_fetch_robots_txt.assert_called_once_with(url)  # Ensure fetch_robots_txt was called
        mock_fetch_sitemap_urls.assert_called()  # Ensure fetch_sitemap_urls was called
        mock_crawl_parallel.assert_called()  # Ensure crawl_parallel was called

    @patch('src.url_check.check_url')  # Mock the check_url function
    @patch('src.robots_parser.fetch_robots_txt')  # Mock the fetch_robots_txt function
    async def test_main_single_crawl(self, mock_fetch_robots_txt, mock_check_url):
        # Set the URL for testing
        url = "https://example.com"
        mock_check_url.return_value = {'valid': True, 'url': url, 'message': ''}

        # Mock robots.txt content but no sitemap
        robots_rules = {
            'allow': ['/public'],
            'disallow': ['/private'],
            'sitemap': []
        }
        mock_fetch_robots_txt.return_value = robots_rules
        
        # Call the main function
        await main()

        # Ensure the single page is attempted to be crawled
        # Add assertions related to crawling logic here based on your implementation
        
if __name__ == "__main__":
    unittest.main()  # Run the tests