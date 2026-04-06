# Data Scraping and Trust Scoring Report

Shreyansh Kanoongo | GutBut AI Builder Fellowship | April 2026

---

## Scraping Strategy

The goal was to collect gut health content from three different types of sources and demonstrate that a single pipeline can handle all of them cleanly.

**Blogs**

I used trafilatura for blog scraping because it is built specifically for extracting article content from web pages. It handles the hard part automatically: identifying the main content block and stripping out navigation, ads, sidebars, and footers. I tested it against all three blog URLs before writing any scraping code to confirm it worked cleanly on each one.

The three blogs were chosen to span a wide credibility range. Harvard T.H. Chan School of Public Health represents institutional, faculty-level content. ZOE Science represents a well-funded health company with named authors and peer-reviewed backing. Fairy Gutmother represents the kind of wellness influencer content that GutBut's trust system needs to identify and rank lower.

**YouTube**

YouTube required two separate tools. yt-dlp handles metadata: channel name, upload date, and video description. youtube-transcript-api handles the transcript. I ran into a breaking change in the transcript API where the old class method was replaced with an instance method in version 1.2.4. This was caught during testing and fixed before the final run.

Transcripts are the most valuable part of a YouTube scrape. A 2-hour episode with Dr. Justin Sonnenburg produces over 130,000 characters of spoken content on gut microbiome science. That is far more useful for a health AI than a video description.

**PubMed**

PubMed does not require scraping. NCBI provides an official API called Entrez. Biopython wraps this API cleanly. I pass the PubMed ID extracted from the URL, request the record in MEDLINE format, and parse out the title, authors, journal, abstract, and date. This is the cleanest and most reliable of the three scraping approaches because it uses structured data from the source, not HTML parsing.

---

## Topic Tagging Method

I used RAKE (Rapid Automatic Keyword Extraction) via the rake-nltk library. RAKE works by identifying phrases that appear frequently and co-occur with other important terms. It does not require a trained model, which makes it fast and portable.

The output is a ranked list of phrases. I filter this list to keep only phrases that are between 2 and 4 words long, which removes single-word noise and overly long fragments. I also deduplicate and cap the output at 8 tags per source.

The tags are not perfect. On pages with complex layouts, RAKE occasionally picks up navigation fragments. This is a known limitation documented in the README. A production version of this system would use a classification model trained on gut health terminology to produce cleaner, more consistent tags.

---

## Trust Score Algorithm

The trust score formula is:
Trust Score = (
author_credibility    x 0.25 +
citation_count        x 0.20 +
domain_authority      x 0.25 +
recency               x 0.15 +
medical_disclaimer    x 0.15
) x abuse_penalty

I chose these five factors because they map directly to the questions a health-conscious reader would ask about a piece of content: Who wrote it? Is it backed by evidence? Where is it published? Is it current? Does it recommend consulting a doctor?

**author_credibility and domain_authority both carry 0.25** because in health content, source credibility is the most important signal. A peer-reviewed paper from an academic institution is fundamentally different from a blog post by a nutrition coach, regardless of what the content says.

**citation_count at 0.20** rewards content that references research. For PubMed articles this is 0.95 by definition. For blogs and YouTube, the system scans for citation language like "study", "clinical trial", and "peer-reviewed".

**recency at 0.15** applies a decay curve. Content published this year scores 1.0. Content older than 8 years scores 0.25. Health guidance changes and outdated recommendations can cause harm.

**medical_disclaimer at 0.15** rewards sources that acknowledge they are not a substitute for professional medical advice. This is a weak signal on its own but adds meaningful differentiation between responsible health communication and overconfident wellness content.

The final scores across all 6 sources are:

| Source | Score |
|---|---|
| Fairy Gutmother (wellness blog) | 0.2120 |
| Harvard T.H. Chan (institutional blog) | 0.5985 |
| Huberman Lab (YouTube) | 0.6075 |
| ZOE Science (science blog) | 0.6500 |
| Diary of a CEO ft. Dr. B (YouTube) | 0.6725 |
| MedComm 2024 (PubMed paper) | 0.8025 |

The spread from 0.21 to 0.80 shows the system is working. It correctly identifies the peer-reviewed paper as the most trustworthy source and the wellness influencer blog as the least.

---

## Edge Case Handling

**Missing author:** Several pages either do not list an author or list a generic name like "Admin". The system handles this in two ways. If the domain is a known institution like Harvard, the domain score compensates. If the domain is unknown, the author credibility defaults to 0.10 and the abuse penalty multiplier applies.

**Missing date:** If no publication date is found, the recency score defaults to 0.30, which is a moderate penalty. The system does not assume content is recent just because no date is present.

**No transcript:** The system is designed to fall back to the video description if a transcript cannot be retrieved, so content is never empty. Transcripts are prioritised over descriptions because they contain substantially more spoken content, but the fallback ensures the scraper does not fail silently on videos with disabled captions.

**Multiple authors:** PubMed articles often have many authors. The system formats this as "First Author et al." and uses the combined author score rather than the score of any single author.

**Non-English content:** Language is detected automatically using langdetect on the first 500 characters of content. All 6 sources in this submission are in English, but the system is ready for multilingual content.

**Long articles:** ZOE's blog post produces 96 chunks. The chunker handles this without any issues. The three-tier fallback (double newline, single newline, word-level) ensures that content is always split into meaningful pieces regardless of how the source page is formatted.

**Abuse prevention:** The system checks for SEO spam keywords, missing authors, and very low domain authority. Any combination of these triggers a penalty multiplier that reduces the final score. This is designed to prevent low-quality content from scoring artificially high by gaming any single factor.

---

Built by Shreyansh Kanoongo for the GutBut AI Builder Fellowship.
