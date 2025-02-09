# Web Crawler

A simple asynchronous web crawler designed to scrape web pages and generate Markdown documents using the Crawl4AI functionality. This application fetches URLs from a sitemap, respects `robots.txt`, and saves scraped content as Markdown files.

## Features

- Fetch URLs from a sitemap or scrape them directly from the website.
- Respect `robots.txt` rules and filter out disallowed URLs.
- Generate and save Markdown files for each crawled page.
- Asynchronous crawling using asyncio for better performance.
- Options to crawl all pages or just the specified base URL.
- Configurable maximum number of pages to crawl.
- Logging for debugging and monitoring the crawling process.



## Usage

Run the application from the command line using the following syntax:

```
python -m src.main <url> [--crawl-all] [--max-pages <number>]
```

## Parameters

- `<url>`: The base URL to crawl.
- `--crawl-all`: Optional flag to crawl all pages found in the sitemap and generate Markdown for each.
- `--max-pages`: Set the maximum number of pages to crawl (default is 10).


## Example

To crawl a site and generate Markdown files for all URLs from the sitemap:

```
python -m src.main https://example.com --crawl-all --max-pages 50
```

To only crawl the specified base URL and generate a Markdown file:

```
python -m src.main https://example.com
```

## Output

Crawled data will be saved as Markdown files in the crawled_data directory located in the parent directory of the script.

## Docker Usage

This application can also be run using Docker and Docker Compose.

### Building the Docker Image

To build the Docker image without using the cache, run the following command:

```
docker-compose build --no-cache
```

### Running the Docker Container

To run the crawler within a Docker container, use the following command:

```
docker-compose run crawler https://example.com --crawl-all --max-pages 5
```

In this command:

- Replace `https://example.com` with the base URL you want to crawl.
- The `--crawl-all` flag tells the crawler to fetch all pages found in the sitemap.
- The `--max-pages` 5 argument limits the crawling process to a maximum of 5 pages.


## Markdown Generation

The application integrates with Crawl4AI to create Markdown documents based on the scraped content from each page. The Markdown files will include relevant information extracted during the crawl.