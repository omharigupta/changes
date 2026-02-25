import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings for problematic sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_url(url):
    """Scrape business-relevant data from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Add session for better handling
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url, timeout=15, allow_redirects=True, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'iframe']):
            tag.decompose()
        
        # Extract relevant data with fallbacks
        title = ''
        if soup.find('title'):
            title = soup.find('title').get_text().strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        
        # Get headings
        headings = []
        for h in soup.find_all(['h1', 'h2', 'h3', 'h4'])[:15]:
            text = h.get_text().strip()
            if text and len(text) > 3:
                headings.append(text)
        
        # Get paragraphs and content
        paragraphs = []
        for p in soup.find_all(['p', 'div', 'span']):
            text = p.get_text().strip()
            if text and len(text) > 30 and len(text) < 500:
                paragraphs.append(text)
            if len(paragraphs) >= 15:  # Limit content
                break
        
        # Get meta description
        meta_desc = ''
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if not meta_tag:
            meta_tag = soup.find('meta', attrs={'property': 'og:description'})
        if meta_tag:
            meta_desc = meta_tag.get('content', '').strip()
        
        # Ensure we have some content
        content = '\n'.join(paragraphs) if paragraphs else 'Content could not be extracted'
        title = title if title else 'Title not found'
        
        return {
            'title': title,
            'meta_description': meta_desc,
            'headings': headings,
            'content': content
        }
    
    except requests.exceptions.SSLError:
        print(f"SSL Error for {url}")
        raise Exception(f"SSL certificate issue with {url}")
    except requests.exceptions.ConnectionError:
        print(f"Connection Error for {url}")
        raise Exception(f"Cannot connect to {url}")
    except requests.exceptions.Timeout:
        print(f"Timeout Error for {url}")
        raise Exception(f"Timeout while accessing {url}")
    except Exception as e:
        print(f"Scraping error for {url}: {e}")
        raise Exception(f"Failed to scrape {url}: {str(e)}")
