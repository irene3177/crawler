import unittest
from unittest.mock import patch, AsyncMock
import logging
import asyncio
from src.main import main  
from src.url_check import check_url
from src.robots_parser import fetch_robots_txt

class TestCrawler(unittest.TestCase):

    @patch('src.main.check_url')
    @patch('src.main.fetch_robots_txt', new_callable=AsyncMock)
    @patch('src.main.fetch_urls_for_crawling', new_callable=AsyncMock)
    @patch('src.main.crawl_single_url', new_callable=AsyncMock)
    @patch('src.main.crawl_urls', new_callable=AsyncMock)
    def test_main_crawl_all_successfully(self, mock_crawl_urls, mock_crawl_single_url, mock_fetch_urls, mock_fetch_robots, mock_check_url):
        # Setup mock responses
        mock_check_url.return_value = {'valid': True, 'url': 'https://example.com'}
        mock_fetch_robots.return_value = {'sitemap': ['https://example.com/sitemap.xml']}
        mock_fetch_urls.return_value = ['https://example.com/page1', 'https://example.com/page2']

        # Mock sys.argv to simulate command line arguments
        with patch('sys.argv', ['app_name', 'https://example.com', '--crawl-all']):
            # Run the main coroutine
            asyncio.run(main())

        # Assert that the correct functions were called
        mock_check_url.assert_called_once_with('https://example.com')
        mock_fetch_robots.assert_called_once_with('https://example.com')
        mock_fetch_urls.assert_called_once()
        mock_crawl_urls.assert_called_once_with(['https://example.com/page1', 'https://example.com/page2'], 'https://example.com')

    @patch('src.main.check_url')
    @patch('src.main.fetch_robots_txt', new_callable=AsyncMock)
    @patch('src.main.fetch_urls_for_crawling', new_callable=AsyncMock)
    @patch('src.main.crawl_single_url', new_callable=AsyncMock)
    def test_main_crawl_single_url_when_no_urls_found(self, mock_crawl_single_url, mock_fetch_urls, mock_fetch_robots, mock_check_url):
        # Setup mock responses
        mock_check_url.return_value = {'valid': True, 'url': 'https://example.com'}
        mock_fetch_robots.return_value = {'sitemap': ['https://example.com/sitemap.xml']}
        mock_fetch_urls.return_value = []  # No URLs found

        # Mock sys.argv to simulate command line arguments
        with patch('sys.argv', ['app_name', 'https://example.com', '--crawl-all']):
            # Run the main coroutine
            asyncio.run(main())

        # Assert that the crawl_single_url was called with the correct arguments
        mock_crawl_single_url.assert_called_once_with('https://example.com', {'sitemap': ['https://example.com/sitemap.xml']})

    @patch('src.main.check_url', return_value={'valid': False, 'message': 'Invalid URL'})
    def test_invalid_url(self, mock_check_url):
        with self.assertLogs('src.main', level='ERROR') as log:
            # Mock sys.argv to simulate command line arguments
            with patch('sys.argv', ['app_name', 'invalid-url']):
                asyncio.run(main())

            self.assertIn("Invalid URL: Invalid URL", log.output[0])

if __name__ == '__main__':
    unittest.main()