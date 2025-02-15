import os
import json
import logging
import re
import aiofiles
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

async def ensure_directory_exists(base_output_dir: str, url: str) -> str:
    """Ensures the directory exists for the given URL and returns the full directory path."""
    # Extract domain name from the URL
    domain = urlparse(url).netloc
    
    # Create a specific directory for this website
    website_dir = os.path.join(base_output_dir, domain)
    
    # Create the directory if it doesn't exist
    os.makedirs(website_dir, exist_ok=True)
    
    return website_dir


async def save_markdown(url: str, content: str, output_dir: str) -> str:
    """Asynchronously saves the Markdown content to a file and returns the file path."""
    # Ensure the appropriate directory exists for the website
    website_dir = await ensure_directory_exists(output_dir, url)

    # Generating the filename from the URL
    safe_filename = f"{url.replace('http://', '').replace('https://', '').replace('/', '_')}.md"

    # Replace any characters that might not be safe for filenames
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', safe_filename)
    
    file_path = os.path.join(website_dir, safe_filename)


    # Write Markdown content to the file
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.write(f"## {url}\n\n")  # Adding the URL as a header
        await f.write(content)

    logger.info("Saved markdown content for URL %s at %s", url, file_path)
    return file_path


async def save_metadata(new_metadata: list, output_dir: str, url: str) -> str:
    """Asynchronously saves metadata to a JSON file, appending new entries if the file exists, and returns the file path."""
    # Ensure the directory for the specific website exists
    website_dir = await ensure_directory_exists(output_dir, url)

    metadata_file_path = os.path.join(website_dir, 'crawl_metadata.json')

    existing_metadata = []
    try:
        # Load existing metadata if the file already exists
        if os.path.exists(metadata_file_path):
            async with aiofiles.open(metadata_file_path, 'r', encoding='utf-8') as f:
                existing_metadata = json.loads(await f.read())
    except Exception as e:
        logger.error("Failed to load existing metadata: %s", e)

    # Convert existing metadata to a dictionary for unique URL checking
    existing_metadata_dict = {item['url']: item for item in existing_metadata}

    # Combine existing metadata entries with new ones, avoiding duplicates
    for new_entry in new_metadata:
        if new_entry['url'] not in existing_metadata_dict:  # Check if the URL is already stored
            existing_metadata_dict[new_entry['url']] = new_entry  # Add new entry

    # Convert back to a list for writing to file
    combined_metadata = list(existing_metadata_dict.values())

    try:
        # Write the combined metadata back to the JSON file
        async with aiofiles.open(metadata_file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(combined_metadata, ensure_ascii=False, indent=4))
        logger.info("Saved metadata for URLs to %s", metadata_file_path)
    except Exception as e:
        logger.error("Failed to save metadata for URLs to %s: %s", metadata_file_path, e)
        raise  # Re-raise the exception after logging it

    return metadata_file_path
