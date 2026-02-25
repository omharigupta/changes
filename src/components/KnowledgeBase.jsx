import React from 'react';
import './KnowledgeBase.css';

function KnowledgeBase({ knowledgeData, setKnowledgeData }) {
  const handleEdit = () => {
    // Edit mode logic
  };

  const handleSave = () => {
    // Save to ChromaDB
  };

  return (
    <div className="knowledge-base">
      <div className="kb-header">
        <h2>Knowledge Base</h2>
        <button className="close-btn">×</button>
      </div>

      <div className="kb-content">
        <section className="kb-section">
          <h3>Business Understanding:</h3>
          <ul>
            {knowledgeData.businessUnderstanding.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
            {knowledgeData.businessUnderstanding.length === 0 && (
              <>
                <li>Information extracted from conversation</li>
                <li>Important details and context</li>
                <li>Another point</li>
              </>
            )}
          </ul>
        </section>

        <section className="kb-section">
          <h3>Objectives:</h3>
          <ul>
            {knowledgeData.objectives.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
            {knowledgeData.objectives.length === 0 && (
              <>
                <li>Outcome desired by user</li>
                <li>Another thing that the user wants to know</li>
                <li>Another point</li>
              </>
            )}
          </ul>
        </section>

        <section className="kb-section">
          <h3>Constraints:</h3>
          <ul>
            {knowledgeData.constraints.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
            {knowledgeData.constraints.length === 0 && (
              <>
                <li>Constraint 1</li>
                <li>Constraint 2</li>
              </>
            )}
          </ul>
        </section>

        <section className="kb-section">
          <h3>Summary:</h3>
          <p>
            {knowledgeData.summary || 
              "A short summary that clearly shows the agent's understanding of the user problem statement and requirements."}
          </p>
        </section>
      </div>

      <div className="kb-actions">
        <button className="edit-btn" onClick={handleEdit}>✏️ Edit</button>
        <button className="save-btn" onClick={handleSave}>💾 Save</button>
      </div>
    </div>
  );
}

export default KnowledgeBase;
