import React from 'react';
import './Sidebar.css';

function Sidebar({ currentView, setCurrentView }) {
  return (
    <div className="sidebar">
      <h2 className="sidebar-title">Datasynth</h2>
      <nav className="sidebar-nav">
        <button 
          className={currentView === 'chat' ? 'active' : ''}
          onClick={() => setCurrentView('chat')}
        >
          Chat
        </button>
        <button 
          className={currentView === 'plan' ? 'active' : ''}
          onClick={() => setCurrentView('plan')}
        >
          Plan
        </button>
        <button 
          className={currentView === 'visualization' ? 'active' : ''}
          onClick={() => setCurrentView('visualization')}
        >
          Visualization
        </button>
      </nav>
    </div>
  );
}

export default Sidebar;
