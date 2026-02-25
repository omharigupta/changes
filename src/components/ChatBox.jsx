import React, { useState, useRef, useEffect } from 'react';
import { processUserInput } from '../services/chatService';
import './ChatBox.css';

function ChatBox({ messages, setMessages, setKnowledgeData }) {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      const response = await processUserInput(currentInput, messages);
      setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);
      
      if (response.knowledgeUpdate) {
        setKnowledgeData(prev => {
          const updated = { ...prev };
          
          if (response.knowledgeUpdate.businessUnderstanding?.length > 0) {
            updated.businessUnderstanding = [
              ...prev.businessUnderstanding,
              ...response.knowledgeUpdate.businessUnderstanding
            ];
          }
          
          if (response.knowledgeUpdate.objectives?.length > 0) {
            updated.objectives = [
              ...prev.objectives,
              ...response.knowledgeUpdate.objectives
            ];
          }
          
          if (response.knowledgeUpdate.constraints?.length > 0) {
            updated.constraints = [
              ...prev.constraints,
              ...response.knowledgeUpdate.constraints
            ];
          }
          
          if (response.knowledgeUpdate.summary) {
            updated.summary = response.knowledgeUpdate.summary;
          }
          
          return updated;
        });
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, something went wrong. Please check your API key and try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbox">
      <div className="messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>Hi there! Tell me about your business.</h3>
            <p>You can paste a URL to scrape business data, or just start chatting.</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content typing">Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="What would you like to know?"
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatBox;
