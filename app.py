from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)


def scrape_url(url):
    """Fetch URL and extract SEO vitals and contact information."""
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; LeadXRay/1.0)'
        })
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return {'error': 'Connection timed out - the server took too long to respond'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Could not connect to the server - check the URL'}
    except requests.exceptions.HTTPError as e:
        return {'error': f'HTTP error: {e.response.status_code}'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to fetch URL: {str(e)}'}

    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text()

    # Extract SEO vitals
    title = soup.title.string.strip() if soup.title and soup.title.string else None

    h1_tag = soup.find('h1')
    h1 = h1_tag.get_text(strip=True) if h1_tag else None

    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_desc_tag.get('content', '').strip() if meta_desc_tag else None

    # Extract emails from mailto: links
    emails = set()
    for mailto_link in soup.find_all('a', href=re.compile(r'^mailto:', re.I)):
        email = mailto_link['href'].replace('mailto:', '').split('?')[0]
        if email:
            emails.add(email.lower())

    # Extract emails from page text using regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    for email in re.findall(email_pattern, page_text):
        emails.add(email.lower())

    # Extract phones from tel: links
    phones = set()
    for tel_link in soup.find_all('a', href=re.compile(r'^tel:', re.I)):
        phone = tel_link['href'].replace('tel:', '').strip()
        if phone:
            phones.add(phone)

    # Extract phones from page text using regex patterns
    phone_patterns = [
        r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
    ]
    for pattern in phone_patterns:
        for phone in re.findall(pattern, page_text):
            cleaned = re.sub(r'[^\d+]', '', phone)
            if len(cleaned) >= 10:
                phones.add(phone.strip())

    # Extract social media links
    social_domains = ['linkedin.com', 'twitter.com', 'x.com', 'facebook.com', 'instagram.com']
    socials = []
    seen_socials = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        for domain in social_domains:
            if domain in href.lower() and href not in seen_socials:
                platform = domain.replace('.com', '').replace('x', 'twitter') if domain == 'x.com' else domain.replace('.com', '')
                socials.append({'platform': platform.capitalize(), 'url': href})
                seen_socials.add(href)
                break

    return {
        'title': title,
        'h1': h1,
        'meta_description': meta_description,
        'emails': list(emails),
        'phones': list(phones),
        'socials': socials
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


if __name__ == "__main__":
    app.run(debug=True)
