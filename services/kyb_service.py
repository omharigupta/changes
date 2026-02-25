import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class KYBManager:
    """Manage Know Your Business (KYB) files and workflow"""
    
    def __init__(self, kyb_dir: str = "kyb_files"):
        self.kyb_dir = kyb_dir
        if not os.path.exists(kyb_dir):
            os.makedirs(kyb_dir)
    
    def create_kyb_file(self, session_id: str, business_info: Dict) -> str:
        """Create a new KYB file for a session"""
        kyb_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "business_info": business_info,
            "conversation_history": [],
            "knowledge_extracted": {
                "business_understanding": [],
                "objectives": [],
                "constraints": [],
                "key_insights": []
            },
            "status": "active",
            "completeness_score": 0.0
        }
        
        filename = f"kyb_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.kyb_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(kyb_data, f, indent=2)
        
        return filepath
    
    def update_kyb_file(self, filepath: str, new_data: Dict) -> Dict:
        """Update existing KYB file with new information"""
        with open(filepath, 'r') as f:
            kyb_data = json.load(f)
        
        # Update timestamp
        kyb_data["updated_at"] = datetime.now().isoformat()
        
        # Merge new knowledge
        if "knowledge_extracted" in new_data:
            for key, value in new_data["knowledge_extracted"].items():
                if key in kyb_data["knowledge_extracted"] and isinstance(value, list):
                    kyb_data["knowledge_extracted"][key].extend(value)
                else:
                    kyb_data["knowledge_extracted"][key] = value
        
        # Add conversation history
        if "conversation_entry" in new_data:
            kyb_data["conversation_history"].append(new_data["conversation_entry"])
        
        # Update completeness score
        kyb_data["completeness_score"] = self._calculate_completeness(kyb_data)
        
        with open(filepath, 'w') as f:
            json.dump(kyb_data, f, indent=2)
        
        return kyb_data
    
    def is_kyb_full(self, filepath: str, threshold: float = 0.8) -> bool:
        """Check if KYB file has sufficient information"""
        with open(filepath, 'r') as f:
            kyb_data = json.load(f)
        
        return kyb_data.get("completeness_score", 0.0) >= threshold
    
    def summarize_kyb(self, filepath: str) -> Dict:
        """Create a summary of the KYB file"""
        with open(filepath, 'r') as f:
            kyb_data = json.load(f)
        
        summary = {
            "business_overview": kyb_data["business_info"],
            "key_insights": kyb_data["knowledge_extracted"]["key_insights"][-5:],  # Last 5 insights
            "main_objectives": kyb_data["knowledge_extracted"]["objectives"],
            "constraints": kyb_data["knowledge_extracted"]["constraints"],
            "completeness": kyb_data["completeness_score"],
            "total_conversations": len(kyb_data["conversation_history"])
        }
        
        return summary
    
    def _calculate_completeness(self, kyb_data: Dict) -> float:
        """Calculate completeness score based on available information"""
        score = 0.0
        max_score = 5.0
        
        # Business info provided
        if kyb_data.get("business_info", {}).get("what_they_sell"):
            score += 1.0
        
        # Has objectives
        if kyb_data["knowledge_extracted"]["objectives"]:
            score += 1.0
        
        # Has constraints
        if kyb_data["knowledge_extracted"]["constraints"]:
            score += 1.0
        
        # Has insights
        if kyb_data["knowledge_extracted"]["key_insights"]:
            score += 1.0
        
        # Has meaningful conversations
        if len(kyb_data["conversation_history"]) >= 3:
            score += 1.0
        
        return score / max_score

    def get_kyb_data(self, filepath: str) -> Dict:
        """Get KYB data from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None