# GutBut Data Scraping Assignment

Shreyansh Kanoongo | GutBut AI Builder Fellowship | April 2026

---

## What this does

This project scrapes gut health content from 6 sources across 3 platforms, cleans and structures it into JSON, and scores each source for trustworthiness on a scale of 0 to 1.

The sources are:
- 3 blog posts (ranging from Harvard to a wellness influencer)
- 2 YouTube videos (from credentialed doctors)
- 1 peer-reviewed PubMed paper

The trust score intentionally spans a wide range, from 0.21 to 0.80, to show the system can tell the difference between a scientific paper and a blog selling meal prep.

---

## Folder structure

\`\`\`
gutbut-assignment/
├── scraper/
│   ├── __init__.py
│   ├── blog_scraper.py
│   ├── youtube_scraper.py
│   └── pubmed_scraper.py
├── scoring/
│   ├── __init__.py
│   └── trust_score.py
├── utils/
│   ├── __init__.py
│   ├── tagging.py
│   └── chunking.py
├── output/
│   ├── blogs.json
│   ├── youtube.json
│   ├── pubmed.json
│   └── scraped_data.json
├── docs/
│   └── report.md
├── main.py
├── requirements.txt
└── README.md
\`\`\`

---

## Sources and trust scores

| Source | Type | Trust Score |
|---|---|---|
| Harvard T.H. Chan School of Public Health | Blog | 0.4703 |
| ZOE Science | Blog | 0.6500 |
| Fairy Gutmother | Blog | 0.2144 |
| Huberman Lab ft. Dr. Justin Sonnenburg | YouTube | 0.6075 |
| Diary of a CEO ft. Dr. Will Bulsiewicz | YouTube | 0.6725 |
| Gut microbiota in health and disease, MedComm 2024 | PubMed | 0.8130 |

Harvard scores the lowest of the three blogs because the article was published in 2017. Eight years of recency decay pulls it significantly below more recent sources. The system correctly penalises outdated health information regardless of the source's institutional credibility.

---

## Libraries used

| Library | What it does |
|---|---|
| requests | Downloads raw HTML from blog URLs |
| beautifulsoup4 | Parses HTML |
| trafilatura | Extracts clean article text, strips ads and navigation |
| youtube-transcript-api | Pulls full transcripts from YouTube videos |
| yt-dlp | Gets YouTube channel name, publish date, description |
| biopython | Connects to PubMed API and fetches article data |
| langdetect | Detects the language of the content automatically |
| rake-nltk | Extracts topic tags from text |
| nltk | Required by rake-nltk |
| lxml-html-clean | Required by trafilatura for HTML cleaning |

---

## How scraping works

**A note on the region field**

The assignment defines region as "geographic region if available." In practice, most online health content does not explicitly state a geographic origin. Where a site name, channel name, or journal name is available, that is used as the closest meaningful identifier. This is acknowledged in Known Limitations.

**Blogs**

trafilatura fetches the page and strips out everything that is not article content. Navigation, ads, footers, cookie banners are all removed. The remaining text is split into chunks. If the page does not use standard paragraph breaks, the chunker falls back to single newlines, then to splitting by word count.

**YouTube**

yt-dlp fetches the video metadata: channel name, upload date, and description. youtube-transcript-api fetches the full transcript. Transcript artifacts like [Music] and [Applause] are removed with regex. The transcript is then chunked the same way as blog content.

**PubMed**

Biopython's Entrez module connects directly to NCBI's official API. No scraping involved. The API returns the article title, authors, journal name, abstract, and publication date in structured format.

---

## How the trust score works
Trust Score = (
author_credibility    x 0.25 +
citation_count        x 0.20 +
domain_authority      x 0.25 +
recency               x 0.15 +
medical_disclaimer    x 0.15
) x abuse_penalty

**author_credibility (0.25)**
Checks the author or channel name against a known credibility table. A Stanford professor scores 0.88. A nutritional therapist selling meal prep scores 0.22. Missing or generic authors (Admin, Unknown) score 0.10.

**citation_count (0.20)**
For PubMed this is 0.95 by definition since the content is peer-reviewed. For blogs and YouTube, the system scans the content for citation language: "study", "research", "journal", "clinical trial", "peer-reviewed". More matches means a higher score.

**domain_authority (0.25)**
Pre-defined scores based on the source domain. Harvard scores 0.97. PubMed scores 0.99. Fairy Gutmother scores 0.18. Unknown domains default to 0.30.

**recency (0.15)**
Content published in the last 12 months scores 1.0. Content older than 8 years scores 0.25. Health information changes and outdated advice can be harmful.

**medical_disclaimer (0.15)**
Scans the first few chunks for words like "consult", "physician", "not a substitute for medical advice", "medically reviewed". Sources that include this language score higher because they are acknowledging the limits of their advice.

**abuse_penalty**
A multiplier that reduces the final score for sources that contain SEO spam language ("miracle", "cure", "guaranteed"), have missing authors, or have very low domain authority. Prevents the score from being gamed by low-quality content.

---

## Edge cases handled

| Situation | What happens |
|---|---|
| Author not listed | Credibility defaults to 0.10 |
| Date not found | Recency defaults to 0.30 |
| No transcript available | Falls back to video description |
| Multiple authors | Formatted as "First Author et al." |
| Non-English content | Language detected automatically via langdetect |
| Very long articles | Three-tier chunking handles them |
| Institutional author listed as Admin | Domain is checked instead of author name |
| SEO spam keywords detected | Abuse penalty multiplier applied |
| No medical disclaimer | That component scores 0.00 |

---

## How to run
```bash
git clone https://github.com/shreyanshkanoongo-git/gutbut-assignment
cd gutbut-assignment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Output files will be saved to the output/ folder. Runtime is approximately 2-3 minutes. Requires Python 3.9 or higher.

---

## Known limitations

The RAKE algorithm occasionally pulls in navigation fragments as tags on pages with complex layouts. For example, Harvard's page produced a tag starting with "g .," which is a leftover from a navigation element. This is a known limitation of keyword extraction on web-scraped content.

For blog articles with a reference section, trafilatura sometimes includes bibliography entries in the extracted content. The ZOE article is an example — its content_chunks include citation URLs from the reference list at the bottom of the page. This is a known limitation of keyword-based content extraction on pages that do not use a clear structural boundary between article body and references.

YouTube transcripts are auto-generated captions in some cases, which means occasional transcription errors in the content chunks. YouTube transcripts are also delivered line-by-line rather than in paragraphs, so chunks can be shorter than those from blog posts. A production version would apply sentence-boundary detection to merge transcript lines into proper paragraph-sized segments.

The domain authority scores are pre-defined, not dynamically fetched. A production version of this system would pull real domain authority data from an API like Moz or Ahrefs.

The trust score system works on the assumption that institutional authors are credible. A bad actor could theoretically publish on a credible domain. A production version would need deeper author verification.

---

## What I would build next

The most useful next step would be an automated ingestion pipeline that runs these scrapers on a schedule, detects new content from trusted sources, and flags it for review before it enters GutBut's content database.

After that, I would build an author verification layer that cross-references author names against medical licensing databases. Right now the system relies on a pre-defined table. That works for known sources but would not scale as GutBut ingests content from hundreds of sources.

I would also improve the topic tagging. RAKE is good for extracting phrases but does not understand meaning. A classification model trained on gut health topics would produce cleaner tags like "gut microbiome", "probiotics", "IBS" instead of phrase fragments from the text.

Finally, I would add a feedback loop where GutBut users can flag misleading content. That signal would feed back into the trust score and help the system improve over time based on real user behaviour.

---

Built by Shreyansh Kanoongo for the GutBut AI Builder Fellowship.
