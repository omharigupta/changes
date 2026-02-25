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
    try:
        # Try different model names
        model_names = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro', 'models/gemini-pro']
        
        model = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"Successfully loaded model: {model_name}")
                break
            except Exception as e:
                print(f"Failed to load model {model_name}: {e}")
                continue
        
        if not model:
            # If no model works, return a simple response
            return {
                'response': f"I've received your input: {user_input}. AI analysis is currently unavailable, but I've noted this information.",
                'knowledge_update': None
            }
        
        # Build conversation history
        history_text = ''
        if history:
            history_text = '\n'.join([f"{m['role']}: {m['content']}" for m in history[-5:]])
        
        prompt = f"""{SYSTEM_PROMPT}

{f"Context from knowledge base: {context}" if context else ""}

Conversation history:
{history_text}

User: {user_input}

Please analyze and respond with valid JSON."""

        # Generate response
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
            'response': response.text if 'response' in locals() else user_input,
            'knowledge_update': None
        }
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {
            'response': f"I understand your input about: {user_input}. Let me help you with that.",
            'knowledge_update': None
        }

def test_gemini_connection():
    """Test if Gemini API is working"""
    try:
        result = analyze_with_gemini("Hello, this is a test.")
        return result.get('response', 'No response')
    except Exception as e:
        return f"Error: {e}"