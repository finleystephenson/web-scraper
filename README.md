# Lead X-Ray

A web scraping tool for agency lead generation. Extract SEO vitals, contact information, and tech stack data from any website.

**Live Demo:** [https://web-contact-seo-scraper.fly.dev](https://web-contact-seo-scraper.fly.dev)

## Features

### Tech Stack Detection
Automatically identifies the website's platform:
- WordPress
- Shopify
- Wix
- Squarespace
- Webflow
- Framer

### SEO Vitals
- Page Title
- H1 Tag
- Meta Description

### Contact Information
- **Emails** - Extracted from mailto links and page text
- **Phone Numbers** - Normalized and deduplicated using the `phonenumbers` library
- **Social Links** - Full profile URLs for LinkedIn, Twitter/X, Facebook, Instagram, YouTube, TikTok, GitHub

### Deep Search
If no emails are found on the homepage, Lead X-Ray automatically:
1. Scans navigation links for "Contact", "About", or similar pages
2. Fetches the most likely contact page
3. Extracts emails from that page
4. Marks results with a "via Contact Page" badge

### Export
Download results as a CSV file for import into your CRM or spreadsheet.

## Tech Stack

- **Backend:** Python, Flask
- **Scraping:** BeautifulSoup, Requests
- **Phone Parsing:** phonenumbers
- **Styling:** Tailwind CSS (via CDN)
- **Hosting:** Fly.io

## Local Development

### Prerequisites
- Python 3.9+

### Setup

```bash
# Clone the repository
git clone https://github.com/finleystephenson/web-scraper.git
cd web-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
flask run
```

Visit `http://localhost:5000` in your browser.

## Deployment

### Fly.io

The app is configured for Fly.io deployment with:
- `Procfile` - Gunicorn configuration
- `fly.toml` - Fly.io app configuration (auto-generated)

To deploy your own instance:

```bash
# Install Fly CLI
brew install flyctl

# Login to Fly.io
fly auth login

# Deploy
fly launch
```

## Project Structure

```
.
├── app.py              # Flask application with scraping logic
├── templates/
│   └── index.html      # Jinja2 template with Tailwind CSS
├── requirements.txt    # Python dependencies
├── Procfile            # Gunicorn configuration for production
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with URL input form |
| `/scan` | POST | Scan a URL and display results |
| `/export` | POST | Export scan results as CSV |

## Configuration

### Browser Headers
The scraper uses realistic Chrome browser headers to avoid being blocked by websites.

### Email Filtering
Common false-positive domains are automatically filtered out (e.g., `example.com`, `sentry.io`).

### Retry Logic
Failed requests are automatically retried up to 3 times with exponential backoff.

## Limitations

- **JavaScript-rendered content:** The scraper uses BeautifulSoup and does not execute JavaScript. Sites that load content dynamically may not be fully scraped.
- **Rate limiting:** Some sites may block repeated requests. Consider adding delays between scans.
- **CAPTCHA:** Sites with CAPTCHA protection cannot be scraped.

## License

MIT

## Author

Built by [Finley Stephenson](https://github.com/finleystephenson)
