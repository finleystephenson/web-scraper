# Lead X-Ray

## What This Is

A simple web scraper tool that takes a URL, extracts SEO vitals (title, H1, meta description) and contact information (emails, phones, social links). Built with Flask and designed for learning Fly.io deployment.

## Core Value

Get a working deployment on Fly.io. The scraper is the vehicle for learning the deployment process.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Single-page Flask app with URL input and Scan button
- [ ] Extract SEO vitals: Page Title, H1 Tag, Meta Description
- [ ] Extract contact info: emails (mailto + regex), phones (tel + regex), social links (LinkedIn, Twitter/X, Facebook, Instagram)
- [ ] Display results in clean table/grid with Tailwind CSS
- [ ] Show "No contact info detected" when nothing found
- [ ] Deploy to Fly.io with zero post-deploy setup

### Out of Scope

- Database/persistence — stateless, each scan is one-off
- Authentication/rate limiting — open access
- Sophisticated error handling UI — basic errors are fine
- History/saving of past scans — not needed
- Advanced scraping (JavaScript rendering) — BeautifulSoup only

## Context

This is a learning project focused on understanding Fly.io deployment. The scraper functionality is intentionally simple to keep focus on the deployment pipeline. Must work immediately after deploy with no manual setup steps.

## Constraints

- **Framework**: Flask — user specified
- **Scraping**: BeautifulSoup + requests — no JS rendering
- **Styling**: Tailwind CSS via CDN — no build step
- **Hosting**: Fly.io — primary learning target
- **Dependencies**: requirements.txt (flask, requests, beautifulsoup4, gunicorn)
- **Deployment**: Procfile for Fly.io (web: gunicorn app:app)
- **Simplicity**: No database, stateless, quick to build

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Tailwind via CDN | No build step, keeps deployment simple | — Pending |
| Gunicorn for production | Standard Flask production server | — Pending |
| No database | Stateless keeps Fly.io config simple | — Pending |

---
*Last updated: 2026-01-22 after initialization*
