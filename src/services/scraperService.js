import axios from 'axios';

export async function scrapeUrl(url) {
  try {
    // Use a CORS proxy or backend API for scraping
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 10000
    });

    // Basic text extraction without cheerio
    const html = response.data;
    const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
    const title = titleMatch ? titleMatch[1] : '';
    
    // Extract text content (simplified)
    const textContent = html
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();

    return {
      title,
      content: textContent.slice(0, 5000)
    };
  } catch (error) {
    console.error('Scraping error:', error);
    throw new Error('Failed to scrape URL. CORS may be blocking the request.');
  }
}
