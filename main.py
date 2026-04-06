# main.py
# Master runner for the GutBut Data Scraping Assignment.
# Scrapes all 6 sources, scores them, and saves output JSON files.

import json
import os
from scraper.blog_scraper import scrape_blog
from scraper.youtube_scraper import scrape_youtube
from scraper.pubmed_scraper import scrape_pubmed
from scoring.trust_score import calculate_trust_score

# === SOURCE URLS ===
BLOG_URLS = [
    "https://nutritionsource.hsph.harvard.edu/microbiome/",
    "https://zoe.com/learn/how-to-improve-gut-health",
    "https://www.fairygutmother.com/blog/2024/6/20/4-ways-to-maintain-gut-health-during-summer-travel"
]

YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=ouCWNRvPk20",
    "https://www.youtube.com/watch?v=qqabbfk9wV8"
]

PUBMED_URLS = [
    "https://pubmed.ncbi.nlm.nih.gov/39568773/"
]


def save_json(data, filepath):
    """Saves data to a JSON file with pretty formatting."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {filepath}")


def run():
    print("=" * 60)
    print("GUTBUT DATA SCRAPING PIPELINE")
    print("=" * 60)

    all_results = []

    # --- SCRAPE BLOGS ---
    print("\n[1/3] Scraping blogs...")
    blog_results = []
    for url in BLOG_URLS:
        data = scrape_blog(url)
        data["trust_score"] = calculate_trust_score(data)
        blog_results.append(data)
        all_results.append(data)
        print()

    save_json(blog_results, "output/blogs.json")

    # --- SCRAPE YOUTUBE ---
    print("\n[2/3] Scraping YouTube videos...")
    youtube_results = []
    for url in YOUTUBE_URLS:
        data = scrape_youtube(url)
        data["trust_score"] = calculate_trust_score(data)
        youtube_results.append(data)
        all_results.append(data)
        print()

    save_json(youtube_results, "output/youtube.json")

    # --- SCRAPE PUBMED ---
    print("\n[3/3] Scraping PubMed articles...")
    pubmed_results = []
    for url in PUBMED_URLS:
        data = scrape_pubmed(url)
        data["trust_score"] = calculate_trust_score(data)
        pubmed_results.append(data)
        all_results.append(data)
        print()

    save_json(pubmed_results, "output/pubmed.json")

    # --- SAVE COMBINED OUTPUT ---
    save_json(all_results, "output/scraped_data.json")

    # --- FINAL SUMMARY ---
    print("\n" + "=" * 60)
    print("FINAL TRUST SCORE SUMMARY")
    print("=" * 60)
    for source in all_results:
        print(f"{source['source_type'].upper():8} | Score: {source['trust_score']:.4f} | {source['source_url'][:60]}")

    print("\nAll done. Output saved to output/ folder.")


if __name__ == "__main__":
    run()
