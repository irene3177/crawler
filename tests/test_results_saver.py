import os
import asyncio
import unittest
import logging
from unittest.mock import AsyncMock, patch
import aiofiles
from src.results_saver import ensure_directory_exists, save_markdown, save_metadata  

# Setup logging for tests
logging.basicConfig(level=logging.DEBUG)

class TestResultsSaver(unittest.TestCase):

    @patch('os.makedirs')  # Mock os.makedirs to avoid actual directory creation
    def test_ensure_directory_exists(self, mock_makedirs):
        """Test the ensure_directory_exists function."""
        base_output_dir = '/dummy/path'
        url = 'https://example.com'
        expected_directory = os.path.join(base_output_dir, 'example.com')

        # Call the function
        directory = asyncio.run(ensure_directory_exists(base_output_dir, url))

        # Assertions
        self.assertEqual(directory, expected_directory)
        mock_makedirs.assert_called_once_with(expected_directory, exist_ok=True)

    @patch('aiofiles.open', new_callable=AsyncMock)  # Mock aiofiles.open
    @patch('src.results_saver.ensure_directory_exists')  # Mock ensure_directory_exists
    async def test_save_markdown(self, mock_ensure_exists, mock_open):
        """Test the save_markdown function."""
        mock_ensure_exists.return_value = '/dummy/path/example.com'  # Mock expected directory output
        url = "https://example.com"
        content = "Sample Markdown Content"
        output_dir = "/dummy/path"

        # Simulate saving to markdown file
        mock_open.return_value.__aenter__.return_value.write = AsyncMock()

        # Call the function
        file_path = await save_markdown(url, content, output_dir)

        # Assertions
        self.assertIn("example.com", file_path)  # Ensure the file path includes the domain
        mock_open.return_value.__aenter__.return_value.write.assert_called()  # Ensure write was called

    @patch('aiofiles.open', new_callable=AsyncMock)  # Mock aiofiles.open
    @patch('src.results_saver.ensure_directory_exists')  # Mock ensure_directory_exists
    async def test_save_metadata(self, mock_ensure_exists, mock_open):
        """Test the save_metadata function with relevant scenarios."""
        mock_ensure_exists.return_value = '/dummy/path/example.com'  # Mock expected directory output
        output_dir = "/dummy/path"
        url = "https://example.com"
        
        metadata = [{'url': 'https://example.com/page1', 'markdown_file': 'page1.md'}]

        # Mock file read for existing metadata
        mock_open.return_value.__aenter__.return_value.read = AsyncMock(return_value=json.dumps([]))  # Simulate empty JSON

        # Call the function
        metadata_file_path = await save_metadata(metadata, output_dir, url)

        # Assertions
        self.assertIn("crawl_metadata.json", metadata_file_path)  # Check if the path is correct
        mock_open.return_value.__aenter__.return_value.write.assert_called()  # Ensure write was called

if __name__ == "__main__":
    unittest.main()