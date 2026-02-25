import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatBox from './components/ChatBox';
import KnowledgeBase from './components/KnowledgeBase';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [knowledgeData, setKnowledgeData] = useState({
    businessUnderstanding: [],
    objectives: [],
    constraints: [],
    summary: ''
  });
  const [currentView, setCurrentView] = useState('chat');

  return (
    <div className="app">
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
      <ChatBox 
        messages={messages} 
        setMessages={setMessages}
        setKnowledgeData={setKnowledgeData}
      />
      <KnowledgeBase knowledgeData={knowledgeData} setKnowledgeData={setKnowledgeData} />
    </div>
  );
}

export default App;
