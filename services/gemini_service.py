import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

SYSTEM_PROMPT = """You are a business analyst assistant. Your job is to:
1. Extract business understanding, objectives, and constraints from conversations
2. Ask clarifying questions to build a complete picture
3. Summarize business requirements clearly

When analyzing scraped data, focus only on business-relevant information.

Always respond with valid JSON in this format:
{
    "response": "your message to the user",
    "knowledge_update": {
        "business_understanding": ["point 1", "point 2"],
        "objectives": ["objective 1"],
        "constraints": ["constraint 1"],
        "summary": "brief summary"
    }
}"""

def analyze_with_gemini(user_input, history=None, context=''):
    """Analyze user input with Gemini AI"""
    model = genai.GenerativeModel('gemini-pro')
    
    history_text = ''
    if history:
        history_text = '\n'.join([f"{m['role']}: {m['content']}" for m in history[-5:]])
    
    prompt = f"""{SYSTEM_PROMPT}

{f"Context from knowledge base: {context}" if context else ""}

Conversation history:
{history_text}

User: {user_input}

Respond with JSON only."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean markdown code blocks if present
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        
        return json.loads(text)
    
    except json.JSONDecodeError:
        return {
            'response': response.text,
            'knowledge_update': None
        }
    except Exception as e:
        print(f"Gemini API error: {e}")
        raise
