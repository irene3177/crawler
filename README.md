# Web Crawler

A simple asynchronous web crawler designed to scrape web pages and generate Markdown documents using the Crawl4AI functionality. This application fetches URLs from a sitemap, respects `robots.txt`, and saves scraped content as Markdown files.

## Main Logic

The web crawling process follows a systematic approach:

1. **URL Validation**:
   - The crawler begins by verifying the provided URL for correctness and checking for any potentially malicious data to ensure a safe crawling experience.

2. **Checking for `robots.txt`**:
   - Once the URL is validated, the crawler retrieves the `robots.txt` file for the target website if the `--check-robots` parameter is passed. This file specifies which parts of the site should not be crawled.

3. **Retrieving Sitemap Information**:
   - The crawler checks for the presence of a sitemap URL within the `robots.txt`. If a sitemap is provided, it follows that URL (in case it is not standard one as `sitemap.xml`).
   - If no specific sitemap URL is found in the `robots.txt`, the crawler appends "sitemap.xml" to the base URL and attempts to access it.

4. **URL Collection from Sitemap**:
   - If URLs are obtained from the sitemap, those links are collected for crawling. If no URLs are found, the crawler resorts to scraping the website directly using Scrapy to construct a sitemap programmatically.
   - If no URLs are found from the sitemap or scraping, the crawler defaults to crawling the current page.

5. **Crawling Logic**:
   - If the `--crawl-all` flag is specified, the crawler processes all pages collected from the sitemap in parallel, respecting the optional `--max-pages` parameter to limit the total number of pages crawled.
   - If the `--crawl-all` flag is not set, the crawler focuses on scraping only the current page.

6. **Markdown Generation**:
   - The crawler uses Crawl4AI to scrape the content from each page and generate Markdown files.
   - The generated Markdown files are saved in the `crawled_data` directory.

7. **Logging**:
   - The crawler provides logging to track the progress of the crawling process, including any encountered errors.


## Features

- **Primary Fetching**: Attempt to fetch URLs from the specified `sitemap.xml` if available.
- **Fallback Scraping**: If the `sitemap.xml` is not available, directly scrape the provided URL for available links.
- **Respect for `robots.txt`**: The crawler adheres to `robots.txt` rules and filters out disallowed URLs.
- **Markdown Generation**: Generates and saves Markdown files for each crawled page.
- **Configurable Crawling Options**: Options to crawl all pages or just the specified base URL, along with a configurable maximum number of pages to crawl.
- **Logging**: Includes logging for debugging and monitoring the crawling process.

## Storing Results

Results from the crawling process are temporarily stored in a dedicated `crawled_data` directory at the root of the project. For each website processed, a unique folder is created to organize the collected data.

### Directory Structure

- Each folder is named according to a sanitized version of the website's URL.
- Within each website's folder, a JSON file named `crawl_metadata.json` is generated. This file contains the following structure:

```json
{
  "url": "https://example.com/",
  "markdown_file": "path/to/markdown/file"
}
```

## Usage

- From Command Line: Run the application from the command line using the following syntax:

```bash
python -m src.main <url> [--crawl-all] [--max-pages <number>] [--check-robots]
```

- As a Module: You can directly import and call run_crawler() from any other module:

```python
from src.main import run_crawler
asyncio.run(run_crawler("https://www.example.com/", crawl_all=True, max_pages=5))
```

## Parameters

- `<url>`: The base URL to crawl.
- `--crawl-all`: Optional flag to crawl all pages found in the sitemap and generate Markdown for each.
- `--max-pages`: Set the maximum number of pages to crawl (default is 50).
- `--check-robots`: Optional flag to check the `robots.txt` rules and filter out disallowed URLs.


## Example

To crawl a site and generate Markdown files for all URLs from the sitemap and respect the `robots.txt` rules:

```bash
python -m src.main https://example.com --crawl-all --max-pages 50 --check-robots
```

To only crawl the specified base URL and generate a Markdown file:

```bash
python -m src.main https://example.com
```

## Output

Crawled data will be saved as Markdown files in the crawled_data directory located in the parent directory of the script.

## Docker Usage

This application can also be run using Docker and Docker Compose.

### Building the Docker Image

To build the Docker image without using the cache, run the following command:

```bash
docker-compose build --no-cache
```

### Running the Docker Container

To run the crawler within a Docker container, use the following command:

```bash
docker-compose run crawler https://example.com --crawl-all --max-pages 5
```

In this command:

- Replace `https://example.com` with the base URL you want to crawl.
- The `--crawl-all` flag tells the crawler to fetch all pages found in the sitemap.
- The `--max-pages` 5 argument limits the crawling process to a maximum of 5 pages.


## Markdown Generation

The application integrates with Crawl4AI to create Markdown documents based on the scraped content from each page. The Markdown files will include relevant information extracted during the crawl.


## Testing

The project includes test files that ensure the functionality of the web crawler is robust and reliable. You can run the tests to validate the implementation and behavior of the crawler. To run the tests, simply execute:

```bash 
python -m unittest discover -s tests
```