const API_KEY = import.meta.env.VITE_GEMINI_API_KEY || 'AIzaSyAMEowhAAXZcY4VrggpzX1Tw-3mb6-c9u4';

const SYSTEM_PROMPT = `You are a business analyst assistant. Your job is to:
1. Extract business understanding, objectives, and constraints from conversations
2. Ask clarifying questions to build a complete picture
3. Summarize business requirements clearly

When analyzing scraped data, focus only on business-relevant information.

IMPORTANT: Always respond with valid JSON in this exact format:
{
  "response": "your conversational message here",
  "knowledgeUpdate": {
    "businessUnderstanding": ["point 1", "point 2"],
    "objectives": ["objective 1"],
    "constraints": ["constraint 1"],
    "summary": "brief summary"
  }
}`;

export async function analyzeWithGemini(userInput, history = [], context = '') {
  try {
    const historyText = history.slice(-5).map(m => `${m.role}: ${m.content}`).join('\n');
    
    const prompt = `${SYSTEM_PROMPT}

${context ? `Previous context: ${context}\n` : ''}
${historyText ? `Recent conversation:\n${historyText}\n` : ''}

User input: ${userInput}

Analyze and respond with JSON only.`;

    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${API_KEY}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: prompt
          }]
        }],
        generationConfig: {
          temperature: 0.7,
          topK: 40,
          topP: 0.95,
          maxOutputTokens: 1024,
        }
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('API Error:', errorData);
      throw new Error(`API returned ${response.status}: ${JSON.stringify(errorData)}`);
    }

    const data = await response.json();
    const text = data.candidates[0].content.parts[0].text;
    
    // Clean up markdown code blocks if present
    const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    
    try {
      const parsed = JSON.parse(cleanText);
      return parsed;
    } catch (parseError) {
      console.warn('Failed to parse JSON, using fallback:', parseError);
      return {
        response: text,
        knowledgeUpdate: {
          businessUnderstanding: [],
          objectives: [],
          constraints: [],
          summary: ''
        }
      };
    }
  } catch (error) {
    console.error('Gemini API error:', error);
    
    // Fallback response
    return {
      response: "I'm having trouble connecting to the AI service. Let me help you manually. Could you tell me more about your business?",
      knowledgeUpdate: {
        businessUnderstanding: [],
        objectives: [],
        constraints: [],
        summary: ''
      }
    };
  }
}
