import sys
import os
import asyncio
import unittest
import logging
from unittest.mock import patch, AsyncMock
from aiohttp import ClientSession

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sitemap_parser import fetch_sitemap_urls, get_sitemap_urls  

# Setup logging for tests (optional)
logging.basicConfig(level=logging.DEBUG)

class TestSitemapParser(unittest.TestCase):

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    async def test_fetch_sitemap_urls(self, mock_get):
        # Simulate the response for a sitemap URL
        mock_response_content = """
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap-image/1.1">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
            <url>
                <loc>https://example.com/page2</loc>
            </url>
            <sitemap>
                <loc>https://example.com/sitemap2.xml</loc>
            </sitemap>
        </urlset>
        """
        # Set up the mock response
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value=mock_response_content)
        mock_get.return_value.__aenter__.return_value.status = 200

        # Test fetching URLs from the sitemap
        sitemap_url = "https://example.com/sitemap.xml"
        urls = await fetch_sitemap_urls(sitemap_url)

        expected_urls = [
            'https://example.com/page1',
            'https://example.com/page2',
            'https://example.com/sitemap2.xml'  # Nested sitemap
        ]
        self.assertEqual(urls, expected_urls)
        logging.info("Sitemap URLs fetched successfully.")

    @patch('src.url_check.is_valid_format', return_value=True)  # Mock is_valid_format to always return True
    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    async def test_get_sitemap_urls(self, mock_get, mock_is_valid):
        mock_response_content = """
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap-image/1.1">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
        </urlset>
        """
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value=mock_response_content)
        mock_get.return_value.__aenter__.return_value.status = 200

        url = "https://example.com"
        
        # Test fetching the sitemap URLs
        urls = await get_sitemap_urls(url)

        expected_urls = ['https://example.com/page1']
        self.assertEqual(urls, expected_urls)
        logging.info("Fetched sitemap URLs using get_sitemap_urls successfully.")

if __name__ == "__main__":
    unittest.main()

