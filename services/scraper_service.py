import requests
from bs4 import BeautifulSoup

def scrape_url(url):
    """Scrape business-relevant data from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'iframe']):
            tag.decompose()
        
        # Extract relevant data
        title = soup.find('title').get_text() if soup.find('title') else ''
        
        headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])][:10]
        
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 50][:20]
        
        meta_desc = ''
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_desc = meta_tag.get('content', '')
        
        return {
            'title': title,
            'meta_description': meta_desc,
            'headings': headings,
            'content': '\n'.join(paragraphs)
        }
    
    except Exception as e:
        print(f"Scraping error: {e}")
        raise Exception("Failed to scrape URL")
