import unittest
from unittest.mock import patch, MagicMock
import asyncio
from src.main import main, fetch_urls_for_crawling, crawl_single_url, crawl_urls

class TestCrawler(unittest.TestCase):

    @patch('src.main.check_url')
    @patch('src.main.fetch_robots_txt')
    @patch('src.main.fetch_sitemap_urls')
    @patch('src.main.get_sitemap_urls')
    @patch('src.main.crawl_one')
    @patch('src.main.crawl_parallel')
    async def test_main_with_check_robots(self, mock_crawl_parallel, mock_crawl_one, mock_get_sitemap_urls, mock_fetch_sitemap_urls, mock_fetch_robots_txt, mock_check_url):
        # Mock URL validation
        mock_check_url.return_value = {'valid': True, 'url': 'https://example.com'}
        
        # Mock robots.txt fetching
        mock_fetch_robots_txt.return_value = {'sitemap': ['https://example.com/sitemap.xml']}
        
        # Mock sitemap fetching
        mock_fetch_sitemap_urls.return_value = ['https://example.com/page1', 'https://example.com/page2']
        mock_get_sitemap_urls.return_value = []
        
        # Run the main application
        with patch('argparse.parse_args', return_value=MagicMock(url='https://example.com', crawl_all=True, max_pages=5, check_robots=True)):
            await main()

        mock_check_url.assert_called_once_with('https://example.com')
        mock_fetch_robots_txt.assert_called_once_with('https://example.com')
        mock_fetch_sitemap_urls.assert_called_once()
        mock_crawl_parallel.assert_called_once()

    @patch('src.main.check_url')
    @patch('src.main.fetch_sitemap_urls')
    @patch('src.main.get_sitemap_urls')
    @patch('src.main.crawl_one')
    @patch('src.main.crawl_parallel')
    async def test_main_without_check_robots(self, mock_crawl_parallel, mock_crawl_one, mock_get_sitemap_urls, mock_fetch_sitemap_urls, mock_check_url):
        # Mock URL validation
        mock_check_url.return_value = {'valid': True, 'url': 'https://example.com'}
        
        # Mock sitemap fetching
        mock_fetch_sitemap_urls.return_value = []
        mock_get_sitemap_urls.return_value = ['https://example.com/page1', 'https://example.com/page2']

        # Run the main application without robots checking
        with patch('argparse.parse_args', return_value=MagicMock(url='https://example.com', crawl_all=True, max_pages=5, check_robots=False)):
            await main()

        mock_check_url.assert_called_once_with('https://example.com')
        mock_fetch_sitemap_urls.assert_called_once()
        mock_get_sitemap_urls.assert_called_once_with('https://example.com', max_pages=5)
        mock_crawl_parallel.assert_called_once()

    @patch('src.main.crawl_one')
    async def test_crawl_single_url_allowed(self, mock_crawl_one):
        mock_crawl_one.return_value = None  # Simulate successful crawl

        await crawl_single_url('https://example.com', None)  # No robots rules provided

        mock_crawl_one.assert_called_once_with('https://example.com', 'crawled_data')  # Check if the single URL was crawled

    @patch('src.main.crawl_one')
    async def test_crawl_single_url_disallowed(self, mock_crawl_one):
        mock_crawl_one.return_value = None  # Simulate successful crawl but no call should be made
        # Simulating disallowed URL crawling (assuming robots rules prevent this)
        
        robots_rules = {'disallow': ['/']}
        await crawl_single_url('https://forbidden.com', robots_rules)

        mock_crawl_one.assert_not_called()  # Ensure crawl_one was never called since the URL is disallowed

    @patch('src.main.fetch_sitemap_urls')
    @patch('src.main.get_sitemap_urls')
    async def test_fetch_urls_for_crawling_with_sitemap(self, mock_get_sitemap_urls, mock_fetch_sitemap_urls):
        mock_fetch_sitemap_urls.return_value = ['https://example.com/page1', 'https://example.com/page2']        
        urls = await fetch_urls_for_crawling('https://example.com', 'https://example.com/sitemap.xml', None, 5, True)

        self.assertEqual(len(urls), 2)  # Check that we retrieved the correct number of URLs
        mock_fetch_sitemap_urls.assert_called_once_with('https://example.com/sitemap.xml', max_pages=5)

    @patch('src.main.fetch_sitemap_urls')
    @patch('src.main.get_sitemap_urls')
    async def test_fetch_urls_for_crawling_without_sitemap(self, mock_get_sitemap_urls, mock_fetch_sitemap_urls):
        mock_fetch_sitemap_urls.return_value = []  # Simulate no URLs found
        mock_get_sitemap_urls.return_value = ['https://example.com/page1', 'https://example.com/page2']

        urls = await fetch_urls_for_crawling('https://example.com', None, None, 5, True)

        self.assertEqual(len(urls), 2)  # Check that we retrieved the correct number of URLs
        mock_get_sitemap_urls.assert_called_once_with('https://example.com', max_pages=5)

if __name__ == '__main__':
    asyncio.run(unittest.main())