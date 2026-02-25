import { analyzeWithGemini } from './geminiService';
import { scrapeUrl } from './scraperService';
import { storeInChroma, queryChroma } from './chromaService';

const URL_REGEX = /(https?:\/\/[^\s]+)/g;

export async function processUserInput(input, conversationHistory) {
  const urls = input.match(URL_REGEX);
  
  // Scenario 1: URL provided
  if (urls && urls.length > 0) {
    return await handleUrlScenario(urls[0], conversationHistory);
  }
  
  // Scenario 2: Regular conversation
  return await handleConversationScenario(input, conversationHistory);
}

// Predefined questions flow
const QUESTIONS = [
  "Hi! What do you sell?",
  "Tell me about your business model and how you make money.",
  "What are your main business goals?",
  "What constraints or challenges are you facing?"
];

async function handleUrlScenario(url, history) {
  try {
    const scrapedData = await scrapeUrl(url);
    const analysis = await analyzeWithGemini(
      `Extract business-related information from this scraped content: ${scrapedData.content.slice(0, 2000)}`,
      history
    );
    
    await storeInChroma({
      text: JSON.stringify(analysis),
      metadata: { source: url, type: 'scraped' }
    });

    return {
      message: analysis.response || `I've analyzed the URL and extracted key business information.`,
      knowledgeUpdate: analysis.knowledgeUpdate
    };
  } catch (error) {
    return {
      message: 'I had trouble accessing that URL. Could you tell me about your business instead?',
      knowledgeUpdate: null
    };
  }
}

async function handleConversationScenario(input, history) {
  try {
    const context = await queryChroma(input);
    const analysis = await analyzeWithGemini(input, history, context);
    
    await storeInChroma({
      text: input,
      metadata: { type: 'conversation', timestamp: Date.now() }
    });

    return {
      message: analysis.response || "I understand. Could you tell me more?",
      knowledgeUpdate: analysis.knowledgeUpdate || null
    };
  } catch (error) {
    console.error('Conversation error:', error);
    return {
      message: "I'm having trouble processing that. Could you rephrase?",
      knowledgeUpdate: null
    };
  }
}
