# scraper/youtube_scraper.py
# Fetches YouTube video metadata and transcripts for gut health videos.

import subprocess
import json
from youtube_transcript_api import YouTubeTranscriptApi
from utils.chunking import chunk_text
from utils.tagging import generate_tags
from langdetect import detect

def extract_video_id(url):
    """Extracts YouTube video ID from URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url.split("/")[-1]

def get_metadata(video_id):
    """Fetches video metadata using yt-dlp."""
    try:
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            f"https://www.youtube.com/watch?v={video_id}"
        ]
        output = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if output.returncode == 0:
            return json.loads(output.stdout)
    except Exception as e:
        print(f"  Metadata error: {e}")
    return {}

def get_transcript(video_id):
    """Fetches video transcript using youtube_transcript_api."""
    try:
        fetcher = YouTubeTranscriptApi()
        transcript_list = fetcher.fetch(video_id)
        full_text = " ".join([entry.text for entry in transcript_list])
        return full_text
    except Exception as e:
        print(f"  Transcript error: {e}")
        return ""

def scrape_youtube(url):
    """
    Scrapes a YouTube video and returns structured data.

    Args:
        url: YouTube video URL

    Returns:
        A dictionary matching the GutBut JSON schema
    """
    print(f"Scraping YouTube: {url}")

    result = {
        "source_url": url,
        "source_type": "youtube",
        "title": "Unknown",
        "author": "Unknown",
        "published_date": "Unknown",
        "language": "en",
        "region": "Unknown",
        "topic_tags": [],
        "trust_score": 0.0,
        "content_chunks": []
    }

    video_id = extract_video_id(url)
    print(f"  Video ID: {video_id}")

    # Step 1: Get metadata
    print("  Fetching metadata...")
    metadata = get_metadata(video_id)

    if metadata:
        result["title"] = metadata.get("title", "Unknown")
        result["author"] = metadata.get("uploader", metadata.get("channel", "Unknown"))
        upload_date = metadata.get("upload_date", "")
        if upload_date and len(upload_date) == 8:
            result["published_date"] = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
        description = metadata.get("description", "")
        result["region"] = metadata.get("channel", "Unknown")
    else:
        description = ""

    # Step 2: Get transcript
    print("  Fetching transcript...")
    transcript = get_transcript(video_id)

    # Step 3: Use transcript if available, else use description
    content = transcript if transcript else description

    if content:
        import re
        content = re.sub(r"\[.*?\]", "", content)
        content = re.sub(r"  +", " ", content).strip()

        try:
            result["language"] = detect(content[:500])
        except Exception:
            result["language"] = "en"

        result["topic_tags"] = generate_tags(content[:3000])
        result["content_chunks"] = chunk_text(content)
    else:
        print("  Warning: No content available.")

    print(f"  Title: {result['title']}")
    print(f"  Channel: {result['author']}")
    print(f"  Date: {result['published_date']}")
    print(f"  Language: {result['language']}")
    print(f"  Transcript length: {len(transcript)} chars")
    print(f"  Tags: {result['topic_tags'][:3]}")
    print(f"  Chunks: {len(result['content_chunks'])}")

    return result
