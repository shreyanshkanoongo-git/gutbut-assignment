# utils/tagging.py
# Auto-generates topic tags from content using RAKE algorithm.
# Used by all three scrapers to fill the topic_tags field.

import nltk
from rake_nltk import Rake

# Download required NLTK data on first run
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

def generate_tags(text, max_tags=8):
    """
    Extracts the most relevant topic tags from text.

    Args:
        text: The article or transcript content
        max_tags: Maximum number of tags to return

    Returns:
        A list of keyword/topic strings
    """
    if not text or len(text.strip()) < 50:
        return []

    try:
        rake = Rake()
        rake.extract_keywords_from_text(text)
        # Get ranked phrases - highest score first
        phrases = rake.get_ranked_phrases()
        # Clean and deduplicate
        tags = []
        seen = set()
        for phrase in phrases:
            cleaned = phrase.lower().strip()
            # Only keep short, meaningful phrases — filter junk
            if cleaned not in seen and 2 <= len(cleaned.split()) <= 4 and not cleaned.startswith('g .') and len(cleaned) > 5:
                tags.append(cleaned)
                seen.add(cleaned)
            if len(tags) >= max_tags:
                break
        return tags
    except Exception as e:
        print(f"Tagging error: {e}")
        return []
