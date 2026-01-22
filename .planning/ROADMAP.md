# Roadmap: Lead X-Ray

## Overview

Build a simple Flask web scraper that extracts SEO vitals and contact information from URLs, then deploy to Fly.io. The scraper is the vehicle for learning Fly.io deployment.

## Domain Expertise

None

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Foundation** - Flask app structure with form UI and Tailwind styling
- [ ] **Phase 2: Scraping** - Extract SEO vitals and contact information from URLs
- [ ] **Phase 3: Deployment** - Configure and deploy to Fly.io

## Phase Details

### Phase 1: Foundation
**Goal**: Working Flask app with URL input form and clean UI
**Depends on**: Nothing (first phase)
**Research**: Unlikely (standard Flask patterns)
**Plans**: TBD

Plans:
- [ ] 01-01: Flask app setup with form and basic routing

### Phase 2: Scraping
**Goal**: Extract SEO vitals (title, H1, meta) and contact info (emails, phones, socials)
**Depends on**: Phase 1
**Research**: Unlikely (BeautifulSoup is established)
**Plans**: TBD

Plans:
- [ ] 02-01: Scraping logic and results display

### Phase 3: Deployment
**Goal**: Working deployment on Fly.io with zero post-deploy setup
**Depends on**: Phase 2
**Research**: Likely (Fly.io is the learning target)
**Research topics**: Fly.io CLI setup, fly.toml configuration, Procfile vs Dockerfile approach
**Plans**: TBD

Plans:
- [ ] 03-01: Fly.io configuration and deployment

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/1 | Not started | - |
| 2. Scraping | 0/1 | Not started | - |
| 3. Deployment | 0/1 | Not started | - |
