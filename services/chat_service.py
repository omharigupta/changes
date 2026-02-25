import re
from services.gemini_service import analyze_with_gemini
from services.scraper_service import scrape_url
from services.chroma_service import store_in_chroma, query_chroma

URL_REGEX = r'https?://[^\s]+'

def process_user_input(user_input, conversation_history):
    """Process user input and determine scenario"""
    urls = re.findall(URL_REGEX, user_input)
    
    # Scenario 1: URL provided
    if urls:
        return handle_url_scenario(urls[0], conversation_history)
    
    # Scenario 2: Regular conversation
    return handle_conversation_scenario(user_input, conversation_history)

def handle_url_scenario(url, history):
    """Handle URL scraping scenario"""
    try:
        scraped_data = scrape_url(url)
        
        analysis_input = f"""Extract business-related information from this scraped data:
Title: {scraped_data['title']}
Description: {scraped_data['meta_description']}
Headings: {', '.join(scraped_data['headings'])}
Content: {scraped_data['content'][:1000]}"""
        
        analysis = analyze_with_gemini(analysis_input, history)
        
        # Store in ChromaDB
        store_in_chroma(
            text=scraped_data['content'],
            metadata={'source': url, 'type': 'scraped'}
        )
        
        return {
            'message': f"I've analyzed the URL and extracted key business information:\n\n{analysis.get('response', 'Analysis complete.')}",
            'knowledge_update': analysis.get('knowledge_update')
        }
    
    except Exception as e:
        return {
            'message': "I had trouble accessing that URL. Could you tell me about your business instead?",
            'knowledge_update': None
        }

def handle_conversation_scenario(user_input, history):
    """Handle regular conversation scenario"""
    try:
        # Query ChromaDB for context
        context = query_chroma(user_input)
        
        # Analyze with Gemini
        analysis = analyze_with_gemini(user_input, history, context)
        
        # Store conversation in ChromaDB
        store_in_chroma(
            text=user_input,
            metadata={'type': 'conversation'}
        )
        
        return {
            'message': analysis.get('response', 'I understand. Please tell me more.'),
            'knowledge_update': analysis.get('knowledge_update')
        }
    
    except Exception as e:
        print(f"Conversation error: {e}")
        return {
            'message': "Sorry, something went wrong. Please try again.",
            'knowledge_update': None
        }
