# scoring/trust_score.py
# Calculates a trust score (0.0 to 1.0) for each scraped source.
# Formula: author_credibility(0.25) + citation_count(0.20) +
#          domain_authority(0.25) + recency(0.15) + medical_disclaimer(0.15)

from datetime import datetime

# --- Domain Authority Scores ---
# Pre-defined scores based on known source credibility
DOMAIN_AUTHORITY = {
    "nutritionsource.hsph.harvard.edu": 0.97,
    "zoe.com": 0.85,
    "pubmed.ncbi.nlm.nih.gov": 0.99,
    "fairygutmother.com": 0.18,
    "youtube.com": 0.60,  # base score, adjusted by channel
}

# --- Author Credibility Scores ---
AUTHOR_CREDIBILITY = {
    # High credibility — verified medical professionals
    "zhang y et al.": 0.95,
    "andrew huberman": 0.88,
    "the diary of a ceo": 0.75,
    "alysha owen": 0.72,
    # Low credibility — wellness influencers / unknown
    "carley smith": 0.22,
    "admin": 0.35,
    "unknown": 0.10,
}

# --- YouTube Channel Credibility ---
YOUTUBE_CHANNEL_SCORES = {
    "andrew huberman": 0.88,
    "huberman lab": 0.88,
    "the diary of a ceo": 0.75,
    "diary of a ceo": 0.75,
}

# --- Medical Disclaimer Keywords ---
DISCLAIMER_KEYWORDS = [
    "consult", "physician", "doctor", "medical advice",
    "healthcare provider", "not a substitute", "professional",
    "medically reviewed", "clinical", "diagnosis"
]

# --- SEO Spam / Low Quality Indicators ---
SPAM_INDICATORS = [
    "buy now", "click here", "limited offer", "miracle",
    "cure", "guaranteed", "detox", "cleanse your gut in"
]


def score_recency(published_date):
    """Scores content based on how recent it is. Max 1.0, decays with age."""
    if not published_date or published_date == "Unknown":
        return 0.3  # penalty for missing date

    try:
        # Handle various date formats
        for fmt in ["%Y-%m-%d", "%Y %b", "%Y %B", "%Y"]:
            try:
                date = datetime.strptime(published_date.strip(), fmt)
                break
            except ValueError:
                continue
        else:
            return 0.3

        age_years = (datetime.now() - date).days / 365.0

        if age_years < 1:
            return 1.0
        elif age_years < 2:
            return 0.92
        elif age_years < 3:
            return 0.80
        elif age_years < 5:
            return 0.65
        elif age_years < 8:
            return 0.45
        else:
            return 0.25

    except Exception:
        return 0.3


def score_medical_disclaimer(content_chunks):
    """Checks if the content contains medical disclaimers or professional language."""
    if not content_chunks:
        return 0.0

    full_text = " ".join(content_chunks[:5]).lower()

    matches = sum(1 for keyword in DISCLAIMER_KEYWORDS if keyword in full_text)

    if matches >= 3:
        return 1.0
    elif matches == 2:
        return 0.75
    elif matches == 1:
        return 0.50
    else:
        return 0.0


def score_domain_authority(url):
    """Returns domain authority score based on known source credibility."""
    for domain, score in DOMAIN_AUTHORITY.items():
        if domain in url:
            return score

    # Unknown domain — apply moderate penalty
    return 0.30


def score_author_credibility(author, source_type, url):
    """Scores the author based on known credibility mappings."""
    if not author or author == "Unknown":
        return 0.10

    author_lower = author.lower().strip()

    # Direct match in our credibility table
    for known_author, score in AUTHOR_CREDIBILITY.items():
        if known_author in author_lower:
            return score

    # For YouTube, check channel scores
    if source_type == "youtube":
        for channel, score in YOUTUBE_CHANNEL_SCORES.items():
            if channel in author_lower:
                return score

    # For PubMed, any named author gets a moderate-high score
    if source_type == "pubmed":
        if author != "Unknown" and len(author) > 3:
            return 0.85

    # For blogs, check domain first — institutional sources get high score
    if source_type == "blog":
        if "harvard.edu" in url or "nih.gov" in url or "cdc.gov" in url:
            return 0.92
        if any(title in author_lower for title in ["md", "phd", "dr.", "rdn", "rd"]):
            return 0.80
        if author_lower in ["admin", "editor", "staff"]:
            return 0.30

    return 0.40  # default for unrecognized authors


def score_citation_count(source_type, content_chunks):
    """
    Estimates citation quality based on source type and content.
    PubMed articles are peer-reviewed. Blogs vary. YouTube rarely cites.
    """
    if source_type == "pubmed":
        return 0.95  # peer-reviewed by definition

    if not content_chunks:
        return 0.0

    full_text = " ".join(content_chunks).lower()

    # Count citation indicators
    citation_markers = [
        "study", "research", "journal", "published", "found that",
        "according to", "evidence", "clinical trial", "meta-analysis",
        "peer-reviewed", "ncbi", "pubmed", "doi"
    ]
    count = sum(1 for marker in citation_markers if marker in full_text)

    if source_type == "blog":
        if count >= 5:
            return 0.80
        elif count >= 3:
            return 0.60
        elif count >= 1:
            return 0.40
        else:
            return 0.15

    if source_type == "youtube":
        if count >= 5:
            return 0.70
        elif count >= 2:
            return 0.50
        else:
            return 0.30

    return 0.30


def abuse_prevention_penalty(content_chunks, author, url):
    """
    Detects and penalizes low-quality, misleading, or spam content.
    Returns a penalty multiplier (1.0 = no penalty, lower = penalized).
    """
    penalty = 1.0

    if not content_chunks:
        return 0.7

    full_text = " ".join(content_chunks[:10]).lower()

    # Penalize SEO spam content
    spam_count = sum(1 for indicator in SPAM_INDICATORS if indicator in full_text)
    if spam_count >= 2:
        penalty *= 0.6
    elif spam_count == 1:
        penalty *= 0.85

    # Penalize missing author
    if not author or author.lower() in ["unknown", "admin", "editor"]:
        penalty *= 0.90

    # Penalize very low domain authority sites
    domain_score = score_domain_authority(url)
    if domain_score < 0.25:
        penalty *= 0.80

    return penalty


def calculate_trust_score(source):
    """
    Main function. Calculates the final trust score for a scraped source.

    Args:
        source: Dictionary with scraped source data

    Returns:
        Float between 0.0 and 1.0
    """
    url = source.get("source_url", "")
    source_type = source.get("source_type", "blog")
    author = source.get("author", "Unknown")
    published_date = source.get("published_date", "Unknown")
    content_chunks = source.get("content_chunks", [])

    # Calculate each component
    author_score = score_author_credibility(author, source_type, url)
    citation_score = score_citation_count(source_type, content_chunks)
    domain_score = score_domain_authority(url)
    recency_score = score_recency(published_date)
    disclaimer_score = score_medical_disclaimer(content_chunks)

    # Weighted formula
    raw_score = (
        author_score      * 0.25 +
        citation_score    * 0.20 +
        domain_score      * 0.25 +
        recency_score     * 0.15 +
        disclaimer_score  * 0.15
    )

    # Apply abuse prevention penalty
    penalty = abuse_prevention_penalty(content_chunks, author, url)
    final_score = raw_score * penalty

    # Clamp between 0.0 and 1.0
    final_score = round(max(0.0, min(1.0, final_score)), 4)

    print(f"  Trust Score Breakdown for {source_type} - {url[:50]}")
    print(f"    Author credibility:    {author_score:.2f} x 0.25")
    print(f"    Citation quality:      {citation_score:.2f} x 0.20")
    print(f"    Domain authority:      {domain_score:.2f} x 0.25")
    print(f"    Recency:               {recency_score:.2f} x 0.15")
    print(f"    Medical disclaimer:    {disclaimer_score:.2f} x 0.15")
    print(f"    Abuse penalty:         {penalty:.2f}")
    print(f"    FINAL TRUST SCORE:     {final_score}")

    return final_score
