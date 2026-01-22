from flask import Flask, render_template, request, Response
import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import io
import phonenumbers

app = Flask(__name__)

# Realistic browser headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Common false-positive email domains to filter
IGNORE_EMAIL_DOMAINS = {'example.com', 'example.org', 'test.com', 'domain.com', 'email.com', 'yoursite.com', 'sentry.io', 'wixpress.com'}


def fetch_with_retry(url, max_retries=3):
    """Fetch URL with retry logic and exponential backoff."""
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                timeout=15,
                headers=HEADERS,
                allow_redirects=True
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            last_error = 'Connection timed out - the server took too long to respond'
        except requests.exceptions.ConnectionError:
            last_error = 'Could not connect to the server - check the URL'
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                last_error = 'Access denied (403) - the site may be blocking scrapers'
            elif e.response.status_code == 404:
                last_error = 'Page not found (404)'
            else:
                last_error = f'HTTP error: {e.response.status_code}'
            break  # Don't retry HTTP errors
        except requests.exceptions.RequestException as e:
            last_error = f'Failed to fetch URL: {str(e)}'

        if attempt < max_retries - 1:
            time.sleep(1 * (attempt + 1))  # Exponential backoff

    return {'error': last_error}


def detect_tech_stack(html_content):
    """Detect the website's tech stack from HTML signatures."""
    html_lower = html_content.lower()

    # Check for WordPress
    if 'wp-content' in html_lower or 'wordpress' in html_lower or 'wp-includes' in html_lower:
        return 'WordPress'

    # Check for Shopify
    if 'shopify' in html_lower or 'cdn.shopify.com' in html_lower:
        return 'Shopify'

    # Check for Wix
    if 'wix.com' in html_lower or 'wixstatic.com' in html_lower:
        return 'Wix'

    # Check for Squarespace
    if 'squarespace' in html_lower or 'sqsp.com' in html_lower:
        return 'Squarespace'

    # Check for Webflow
    if 'webflow' in html_lower:
        return 'Webflow'

    # Check for Framer
    if 'framer' in html_lower:
        return 'Framer'

    return 'Unknown'


def extract_emails(soup, page_text):
    """Extract emails from mailto links and page text with filtering."""
    emails = set()

    # From mailto: links
    for mailto_link in soup.find_all('a', href=re.compile(r'^mailto:', re.I)):
        email = mailto_link['href'].replace('mailto:', '').split('?')[0].strip()
        if email:
            emails.add(email.lower())

    # From page text using improved regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    for email in re.findall(email_pattern, page_text):
        emails.add(email.lower())

    # Also check href attributes that might contain obfuscated emails
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '@' in href and not href.startswith('mailto:'):
            matches = re.findall(email_pattern, href)
            for email in matches:
                emails.add(email.lower())

    # Filter out false positives
    filtered = set()
    for email in emails:
        domain = email.split('@')[-1] if '@' in email else ''
        if domain not in IGNORE_EMAIL_DOMAINS and not email.startswith('test@'):
            filtered.add(email)

    return list(filtered)


def normalize_phone(phone_str, default_region='US'):
    """Normalize a phone number to E164 format for deduplication."""
    try:
        parsed = phonenumbers.parse(phone_str, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass
    return None


def extract_phones(soup, page_text):
    """Extract and deduplicate phone numbers using phonenumbers library."""
    raw_phones = set()

    # From tel: links
    for tel_link in soup.find_all('a', href=re.compile(r'^tel:', re.I)):
        phone = tel_link['href'].replace('tel:', '').strip()
        if phone:
            raw_phones.add(phone)

    # Phone patterns to find in text
    phone_patterns = [
        r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US: (555) 123-4567
        r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
        r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',  # Simple: 555-123-4567
        r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',  # (555) 123-4567
        r'0\d{4}\s?\d{6}',  # UK: 07305 859070
        r'\+44\s?\d{4}\s?\d{6}',  # UK with country code
    ]

    for pattern in phone_patterns:
        for phone in re.findall(pattern, page_text):
            raw_phones.add(phone.strip())

    # Normalize and deduplicate
    normalized_map = {}  # E164 -> display format
    for phone in raw_phones:
        e164 = normalize_phone(phone)
        if e164:
            # Keep the nicest looking format (prefer ones with + prefix)
            if e164 not in normalized_map or phone.startswith('+'):
                # Format nicely for display
                try:
                    parsed = phonenumbers.parse(phone, 'US')
                    display = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    normalized_map[e164] = display
                except:
                    normalized_map[e164] = phone

    return list(normalized_map.values())


def extract_socials(soup):
    """Extract social media profile URLs."""
    social_domains = {
        'linkedin.com': 'LinkedIn',
        'twitter.com': 'Twitter',
        'x.com': 'X',
        'facebook.com': 'Facebook',
        'instagram.com': 'Instagram',
        'youtube.com': 'YouTube',
        'tiktok.com': 'TikTok',
        'github.com': 'GitHub',
    }

    socials = []
    seen_urls = set()

    for link in soup.find_all('a', href=True):
        href = link['href']
        for domain, platform in social_domains.items():
            if domain in href.lower() and href not in seen_urls:
                # Skip share/intent/sharer links
                skip_patterns = ['/share', '/intent', '/sharer', 'share?', 'dialog/share']
                if any(p in href.lower() for p in skip_patterns):
                    continue
                socials.append({'platform': platform, 'url': href})
                seen_urls.add(href)
                break

    return socials


def scrape_url(url):
    """Fetch URL and extract SEO vitals and contact information."""
    result = fetch_with_retry(url)

    if isinstance(result, dict) and 'error' in result:
        return result

    response = result
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Detect tech stack before removing elements
    tech_stack = detect_tech_stack(html_content)

    # Remove script and style elements for cleaner text extraction
    for element in soup(['script', 'style', 'noscript']):
        element.decompose()

    page_text = soup.get_text(separator=' ')

    # Extract SEO vitals
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    h1_tag = soup.find('h1')
    h1 = h1_tag.get_text(strip=True) if h1_tag else None

    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_desc_tag.get('content', '').strip() if meta_desc_tag else None

    return {
        'title': title,
        'h1': h1,
        'meta_description': meta_description,
        'tech_stack': tech_stack,
        'emails': extract_emails(soup, page_text),
        'phones': extract_phones(soup, page_text),
        'socials': extract_socials(soup),
        'final_url': response.url,
    }


@app.route("/")
def index():
    """Render the home page with URL input form."""
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    """Accept URL from form and return scraped result."""
    url = request.form.get("url", "")
    result = scrape_url(url)
    return render_template("index.html", url=url, scanned=True, result=result)


@app.route("/export", methods=["POST"])
def export():
    """Export scan results as CSV."""
    url = request.form.get("url", "")
    result = scrape_url(url)

    if 'error' in result:
        return Response(f"Error: {result['error']}", mimetype='text/plain')

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Field', 'Value'])
    writer.writerow(['URL', url])
    writer.writerow(['Tech Stack', result.get('tech_stack', 'Unknown')])
    writer.writerow(['Title', result.get('title', '')])
    writer.writerow(['H1', result.get('h1', '')])
    writer.writerow(['Meta Description', result.get('meta_description', '')])
    writer.writerow(['Emails', ', '.join(result.get('emails', []))])
    writer.writerow(['Phones', ', '.join(result.get('phones', []))])
    writer.writerow(['Social Links', ', '.join([s['url'] for s in result.get('socials', [])])])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=scan-results.csv'}
    )


if __name__ == "__main__":
    app.run(debug=True)
