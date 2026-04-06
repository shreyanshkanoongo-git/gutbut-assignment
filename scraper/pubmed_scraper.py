# scraper/pubmed_scraper.py
# Fetches structured data from PubMed using Biopython Entrez API.

from Bio import Entrez, Medline
from utils.chunking import chunk_text
from utils.tagging import generate_tags
from langdetect import detect

Entrez.email = "gutbut.scraper@example.com"

def extract_pubmed_id(url):
    return url.rstrip('/').split('/')[-1]

def scrape_pubmed(url):
    print(f"Scraping PubMed: {url}")

    result = {
        "source_url": url,
        "source_type": "pubmed",
        "title": "Unknown",
        "author": "Unknown",
        "published_date": "Unknown",
        "language": "en",
        "region": "Academic/Scientific",
        "topic_tags": [],
        "trust_score": 0.0,
        "content_chunks": []
    }

    try:
        pmid = extract_pubmed_id(url)
        print(f"  PubMed ID: {pmid}")

        handle = Entrez.efetch(
            db="pubmed",
            id=pmid,
            rettype="medline",
            retmode="text"
        )
        records = list(Medline.parse(handle))
        handle.close()

        if not records:
            print("  No records found.")
            return result

        record = records[0]

        title = record.get("TI", "Unknown")
        result["title"] = title

        authors = record.get("AU", [])
        if authors:
            if len(authors) <= 3:
                result["author"] = ", ".join(authors)
            else:
                result["author"] = f"{authors[0]} et al."

        result["published_date"] = record.get("DP", "Unknown")

        journal = record.get("JT", record.get("TA", "Unknown Journal"))
        result["region"] = f"Journal: {journal}"

        abstract = record.get("AB", "")
        full_text = f"{title}\n\n{abstract}"

        try:
            if abstract:
                result["language"] = detect(abstract[:500])
        except Exception:
            result["language"] = "en"

        result["topic_tags"] = generate_tags(full_text)
        result["content_chunks"] = chunk_text(abstract, min_length=50)

        print(f"  Title: {title[:80]}...")
        print(f"  Authors: {result['author']}")
        print(f"  Date: {result['published_date']}")
        print(f"  Journal: {journal}")
        print(f"  Tags: {result['topic_tags']}")
        print(f"  Chunks: {len(result['content_chunks'])}")

    except Exception as e:
        print(f"  Error: {e}")

    return result
