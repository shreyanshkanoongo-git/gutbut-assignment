# scraper/blog_scraper.py
# Scrapes gut health blog posts and returns structured JSON.
# Uses trafilatura for clean text extraction, langdetect for language detection.

import requests
import trafilatura
from langdetect import detect
from datetime import datetime
from utils.chunking import chunk_text
from utils.tagging import generate_tags

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_blog(url):
    """
    Scrapes a blog post URL and returns a structured dictionary.

    Args:
        url: The blog post URL to scrape

    Returns:
        A dictionary matching the GutBut JSON schema
    """
    print(f"Scraping blog: {url}")

    result = {
        "source_url": url,
        "source_type": "blog",
        "title": "Unknown",
        "author": "Unknown",
        "published_date": "Unknown",
        "language": "en",
        "region": "Unknown",
        "topic_tags": [],
        "trust_score": 0.0,
        "content_chunks": []
    }

    try:
        # Step 1: Fetch the raw HTML
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = response.text

        # Step 2: Extract clean article text using trafilatura
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            no_fallback=False
        )

        if not extracted:
            print(f"  Warning: No content extracted from {url}")
            return result

        # Step 3: Extract metadata using trafilatura
        metadata = trafilatura.extract_metadata(html)

        if metadata:
            if metadata.title:
                result["title"] = metadata.title
            if metadata.author:
                result["author"] = metadata.author
            if metadata.date:
                result["published_date"] = metadata.date
            if metadata.sitename:
                result["region"] = metadata.sitename

        # Step 4: Detect language
        try:
            result["language"] = detect(extracted[:500])
        except Exception:
            result["language"] = "en"

        # Step 5: Generate topic tags
        result["topic_tags"] = generate_tags(extracted)

        # Step 6: Split into chunks
        result["content_chunks"] = chunk_text(extracted)

        print(f"  Title: {result['title']}")
        print(f"  Author: {result['author']}")
        print(f"  Date: {result['published_date']}")
        print(f"  Language: {result['language']}")
        print(f"  Tags: {result['topic_tags']}")
        print(f"  Chunks: {len(result['content_chunks'])}")

    except requests.exceptions.RequestException as e:
        print(f"  Request error: {e}")
    except Exception as e:
        print(f"  Unexpected error: {e}")

    return result


def scrape_all_blogs(urls):
    """
    Scrapes multiple blog URLs and returns a list of results.

    Args:
        urls: List of blog post URLs

    Returns:
        List of structured blog dictionaries
    """
    results = []
    for url in urls:
        data = scrape_blog(url)
        results.append(data)
    return results
