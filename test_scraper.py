#!/usr/bin/env python3
"""
Simple test script to verify URL scraping works independently
"""

import sys
from services.scraper_service import scrape_url

def test_scraping(url):
    """Test scraping a URL"""
    print(f"\n🔍 Testing URL: {url}")
    print("="*50)
    
    try:
        result = scrape_url(url)
        
        print(f"✅ SUCCESS!")
        print(f"Title: {result.get('title', 'No title')}")
        print(f"Meta Description: {result.get('meta_description', 'No description')}")
        print(f"Headings ({len(result.get('headings', []))}): {result.get('headings', [])[:3]}")
        print(f"Content Length: {len(result.get('content', ''))}")
        print(f"Content Preview: {result.get('content', '')[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    # Test URLs
    test_urls = [
        "https://nfsu.ac.in/",
        "https://www.google.com/",
        "https://www.github.com/",
        "https://www.python.org/"
    ]
    
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    print("🧪 URL Scraper Test")
    print("="*50)
    
    success_count = 0
    for url in test_urls:
        if test_scraping(url):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{len(test_urls)} URLs scraped successfully")