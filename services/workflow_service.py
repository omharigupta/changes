from typing import Dict, List, Optional, Tuple
from services.gemini_service import analyze_with_gemini
from services.scraper_service import scrape_url
import uuid
import re
import json
import os

class WorkflowManager:
    """Manage the KYB conversation workflow with exact 8-step pattern"""
    
    # Core questions for the workflow
    CORE_QUESTIONS = [
        "Tell me more about your AI OS - what makes it special?",
        "What are your main business goals with this AI OS?", 
        "What challenges are you currently facing?",
        "Who is your target audience?",
        "What would success look like for you?"
    ]
    
    def __init__(self):
        self.url_pattern = r'https?://[^\s]+'
        self.current_question_index = 0
        
    def get_initial_message(self) -> str:
        """Return the initial greeting message - Step 1"""
        return "Hi! 👋 What do you sell? (You can also paste a URL to scrape your business website)"
    
    def process_workflow_step(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Process input following exact 8-step workflow pattern"""
        
        # Initialize session state if needed
        if 'workflow_step' not in session_state:
            session_state['workflow_step'] = 1
            session_state['session_id'] = str(uuid.uuid4())
            session_state['kyb_data'] = {
                'business_understanding': [],
                'objectives': [],
                'constraints': [],
                'summary': '',
                'scraped_data': []
            }
            session_state['current_question'] = 0
        
        # Check if input contains a URL (only scrape if URL detected)
        urls = re.findall(self.url_pattern, user_input)
        if urls and self._is_valid_url(urls[0]):
            print(f"🔍 URL detected in input: {urls[0]}")
            return self._handle_url_input(urls[0], user_input, session_state)
        
        current_step = session_state['workflow_step']
        
        if current_step == 1:
            return self._step1_ask_what_you_sell(session_state)
        elif current_step == 2:
            return self._step2_user_responds(user_input, session_state)  # "I make AI OS"
        elif current_step == 3:
            return self._step3_create_kyb_file(session_state)
        elif current_step == 4:
            return self._step4_update_kyb_file(user_input, session_state)
        elif current_step == 5:
            return self._step5_chat_next(session_state)
        elif current_step == 6:
            return self._step6_update_kyb_file(user_input, session_state)
        elif current_step == 7:
            return self._step7_chat_next(session_state)
        elif current_step == 8:
            return self._step8_check_if_kyb_full(user_input, session_state)
        else:
            return self._ongoing_conversation(user_input, session_state)
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if the URL looks valid and worth scraping"""
        try:
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                return False
            if len(url) < 10:  # Too short
                return False
            if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
                return False
            return True
        except:
            return False
    
    def _step1_ask_what_you_sell(self, session_state: Dict) -> Tuple[str, Dict]:
        """Step 1: Initial greeting asking what they sell - then advance to step 2"""
        session_state['workflow_step'] = 2  # Advance to step 2 so next input goes to step 2 logic
        return self.get_initial_message(), session_state
    
    def _step2_user_responds(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 2: User responds with what they sell (e.g., 'I make AI OS')"""
        session_state['what_they_sell'] = user_input
        session_state['workflow_step'] = 3
        
        response = f"Great! You make **{user_input}**. Let me create your business profile..."
        return response, session_state
    
    def _step3_create_kyb_file(self, session_state: Dict) -> Tuple[str, Dict]:
        """Step 3: Create KYB file"""
        self._create_kyb_file(session_state)
        session_state['workflow_step'] = 4
        
        response = "✅ Business profile created! Now tell me more about your AI OS - what makes it special?"
        return response, session_state
    
    def _step4_update_kyb_file(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 4: Update KYB file with user response"""
        # Add to business understanding
        session_state['kyb_data']['business_understanding'].append(f"Product details: {user_input}")
        self._update_kyb_file(session_state, user_input, step=4)
        session_state['workflow_step'] = 5
        
        response = "📝 Information saved!"
        return response, session_state
    
    def _step5_chat_next(self, session_state: Dict) -> Tuple[str, Dict]:
        """Step 5: Ask next question (chat next)"""
        question_index = session_state.get('current_question', 0)
        
        if question_index < len(self.CORE_QUESTIONS):
            question = self.CORE_QUESTIONS[question_index]
            session_state['current_question'] = question_index
            session_state['workflow_step'] = 6
            
            response = f"Next question: {question}"
        else:
            # No more questions, go to step 8 to check completion
            session_state['workflow_step'] = 8
            response = "Let me check if I have enough information..."
        
        return response, session_state
    
    def _step6_update_kyb_file(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 6: Update KYB file with response to current question"""
        question_index = session_state.get('current_question', 0)
        
        # Categorize the response based on question type
        if question_index == 0:  # About the product
            session_state['kyb_data']['business_understanding'].append(f"Special features: {user_input}")
        elif question_index == 1:  # Business goals
            session_state['kyb_data']['objectives'].append(user_input)
        elif question_index == 2:  # Challenges
            session_state['kyb_data']['constraints'].append(user_input)
        elif question_index == 3:  # Target audience
            session_state['kyb_data']['business_understanding'].append(f"Target audience: {user_input}")
        elif question_index == 4:  # Success definition
            session_state['kyb_data']['objectives'].append(f"Success metric: {user_input}")
        
        self._update_kyb_file(session_state, user_input, step=6)
        session_state['current_question'] += 1
        session_state['workflow_step'] = 7
        
        response = "💾 Response recorded!"
        return response, session_state
    
    def _step7_chat_next(self, session_state: Dict) -> Tuple[str, Dict]:
        """Step 7: Chat next - could ask another question or proceed to check"""
        session_state['workflow_step'] = 8
        response = "Let me check if your business profile is complete..."
        return response, session_state
    
    def _step8_check_if_kyb_full(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 8: Check if KYB is full - Yes: summarize, No: ask same question"""
        kyb_data = session_state['kyb_data']
        
        # Check if we have sufficient information (at least 2 items in each category)
        has_business = len(kyb_data['business_understanding']) >= 2
        has_objectives = len(kyb_data['objectives']) >= 1
        has_constraints = len(kyb_data['constraints']) >= 1
        
        if has_business and has_objectives and has_constraints:
            # YES - KYB is full: (old + new) -> summarize
            old_data = kyb_data.copy()
            new_summary = self._create_summary_from_data(old_data)
            
            session_state['kyb_data']['summary'] = new_summary
            self._update_kyb_file(session_state, "KYB Complete - Summary Generated", step=8)
            
            response = f"""
🎉 **Your Business Profile is Complete!**

**Business:** {session_state.get('what_they_sell', 'AI OS')}

**Understanding:**
{chr(10).join(['• ' + item for item in kyb_data['business_understanding']])}

**Objectives:**
{chr(10).join(['• ' + item for item in kyb_data['objectives']])}

**Challenges:**
{chr(10).join(['• ' + item for item in kyb_data['constraints']])}

**Summary:** {new_summary}

Now I can provide targeted assistance! What would you like to focus on?
"""
            
            session_state['workflow_step'] = 9  # Move to ongoing conversation
            
        else:
            # NO - Update KYB and ask same question (loop back)
            question_index = session_state.get('current_question', 0)
            
            if question_index < len(self.CORE_QUESTIONS):
                next_question = self.CORE_QUESTIONS[question_index]
                
                response = f"""
📋 I need more information to complete your business profile.

Missing: {', '.join([
                    'Business Details' if not has_business else '',
                    'Objectives' if not has_objectives else '',
                    'Challenges' if not has_constraints else ''
                ]).strip(', ')}

**Next Question:** {next_question}
"""
                
                # Go back to step 6 to collect more info
                session_state['workflow_step'] = 6
            else:
                # All questions asked but still not enough info
                response = """
📋 Could you provide more details about:
- What makes your AI OS unique compared to others?
- Your main business goals for the next 6 months?
- The biggest challenge you're facing right now?

This will complete your business profile.
"""
                session_state['workflow_step'] = 6
        
        return response, session_state
    
    def _handle_url_input(self, url: str, full_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Handle URL scraping and extract business data"""
        try:
            # Scrape the website
            scraped_data = scrape_url(url)
            
            # Use AI to extract business information from scraped data
            analysis_prompt = f"""
            Extract important business information from this website data:
            
            Title: {scraped_data.get('title', '')}
            Meta Description: {scraped_data.get('meta_description', '')}
            Headings: {', '.join(scraped_data.get('headings', []))}
            Content: {scraped_data.get('content', '')[:2000]}
            
            Extract and return:
            1. What the business sells/does
            2. Key products or services
            3. Business objectives or goals mentioned
            4. Target audience
            5. Unique value propositions
            6. Any challenges or problems they solve
            
            Format as structured business insights.
            """
            
            # Use Gemini AI to analyze the scraped data
            analysis_result = analyze_with_gemini(analysis_prompt, [])
            
            # Store scraped data in KYB
            session_state['kyb_data']['scraped_data'].append({
                'url': url,
                'title': scraped_data.get('title', ''),
                'content_summary': scraped_data.get('content', '')[:500],
                'analysis': analysis_result.get('response', 'Analysis completed')
            })
            
            # Update business understanding with scraped insights
            session_state['kyb_data']['business_understanding'].extend([
                f"Website: {scraped_data.get('title', url)}",
                f"Business Focus: {analysis_result.get('response', 'Web-based business')[:100]}..."
            ])
            
            # Move to next logical step
            session_state['workflow_step'] = 3
            
            response = f"""
✅ **Website Analyzed: {scraped_data.get('title', url)}**

I've extracted key business information from your website. Based on what I found, let me ask you some specific questions to complete your business profile.

{self.HARDCODED_QUESTIONS[3]}
"""
            
        except Exception as e:
            response = f"""
❌ I had trouble accessing that website ({str(e)}). 

No worries! Let's continue with the questions:

{self.HARDCODED_QUESTIONS.get(session_state['workflow_step'] + 1, 'Tell me more about your business.')}
"""
            session_state['workflow_step'] = min(session_state['workflow_step'] + 1, 7)
        
        return response, session_state
    
    def _step1_what_do_you_sell(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 1: What do you sell?"""
        # Store what they sell
        session_state['kyb_data']['business_understanding'].append(f"Business: {user_input}")
        session_state['what_they_sell'] = user_input
        
        # Move to step 2 - Create KYB file
        session_state['workflow_step'] = 2
        self._create_kyb_file(session_state)
        
        response = f"Great! You make **{user_input}**. I've created your business profile file.\n\n{self.HARDCODED_QUESTIONS[2]}"
        return response, session_state
    
    def _step2_tell_me_more(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 2: Tell me more about your product"""
        # Update KYB file
        session_state['kyb_data']['business_understanding'].append(f"Product Details: {user_input}")
        self._update_kyb_file(session_state, user_input, step=2)
        
        session_state['workflow_step'] = 3
        
        response = f"📝 Profile updated! {self.HARDCODED_QUESTIONS[3]}"
        return response, session_state
    
    def _step3_business_goals(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 3: Business goals"""
        # Update KYB file with objectives
        session_state['kyb_data']['objectives'].append(user_input)
        self._update_kyb_file(session_state, user_input, step=3)
        
        session_state['workflow_step'] = 4
        
        response = f"🎯 Goals noted! {self.HARDCODED_QUESTIONS[4]}"
        return response, session_state
    
    def _step4_challenges(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 4: Challenges and constraints"""
        # Update KYB file with constraints
        session_state['kyb_data']['constraints'].append(user_input)
        self._update_kyb_file(session_state, user_input, step=4)
        
        session_state['workflow_step'] = 5
        
        response = f"⚠️ Challenges recorded! {self.HARDCODED_QUESTIONS[5]}"
        return response, session_state
    
    def _step5_target_audience(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 5: Target audience"""
        session_state['kyb_data']['business_understanding'].append(f"Target Audience: {user_input}")
        self._update_kyb_file(session_state, user_input, step=5)
        
        session_state['workflow_step'] = 6
        
        response = f"👥 Target audience noted! {self.HARDCODED_QUESTIONS[6]}"
        return response, session_state
    
    def _step6_success_definition(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 6: Success definition"""
        session_state['kyb_data']['objectives'].append(f"Success metric: {user_input}")
        self._update_kyb_file(session_state, user_input, step=6)
        
        session_state['workflow_step'] = 7
        
        response = f"🏆 Success definition saved! {self.HARDCODED_QUESTIONS[7]}"
        return response, session_state
    
    def _step7_pain_points(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 7: Pain points"""
        session_state['kyb_data']['constraints'].append(f"Main pain point: {user_input}")
        self._update_kyb_file(session_state, user_input, step=7)
        
        session_state['workflow_step'] = 8
        
        response = "💡 Pain point noted! Let me check if I have enough information to provide comprehensive insights..."
        return response, session_state
    
    def _step8_check_if_kyb_full(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Step 8: Check if KYB is full and decide next steps"""
        kyb_data = session_state['kyb_data']
        
        # Check if we have sufficient information
        has_business = len(kyb_data['business_understanding']) >= 2
        has_objectives = len(kyb_data['objectives']) >= 2
        has_constraints = len(kyb_data['constraints']) >= 2
        
        if has_business and has_objectives and has_constraints:
            # KYB is full - create summary
            summary = self._create_summary(kyb_data)
            session_state['kyb_data']['summary'] = summary
            self._update_kyb_file(session_state, "KYB Complete - Summary Generated", step=8)
            
            response = f"""
🎉 **Your Business Profile is Complete!**

**Business:** {session_state.get('what_they_sell', 'AI OS')}

**Key Insights:**
{chr(10).join(['• ' + insight for insight in kyb_data['business_understanding'][-3:]])}

**Main Objectives:**
{chr(10).join(['• ' + obj for obj in kyb_data['objectives'][-3:]])}

**Key Challenges:**
{chr(10).join(['• ' + constraint for constraint in kyb_data['constraints'][-3:]])}

**Summary:** {summary}

Now I can provide targeted assistance! What specific area would you like help with?
"""
            
            session_state['workflow_step'] = 9  # Move to ongoing conversation
            
        else:
            # Need more information
            response = f"""
📋 I need a bit more information to provide the best insights.

Missing areas: {', '.join([
    'Business Details' if not has_business else '',
    'Objectives' if not has_objectives else '',
    'Challenges' if not has_constraints else ''
]).strip(', ')}

Could you elaborate on any of these areas? This will help me give you more targeted recommendations.
"""
            
            # Go back to collect more info
            session_state['workflow_step'] = 3
        
        return response, session_state
    def _ongoing_conversation(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Handle conversation after workflow completion"""
        # Continue normal conversation while still updating KYB if needed
        kyb_data = session_state.get('kyb_data', {})
        
        response = f"""Based on your **{session_state.get('what_they_sell', 'AI OS')}** business, here's my response to: "{user_input}"

{self._generate_contextual_response(user_input, kyb_data)}

Is there anything specific about your business I can help you with?"""
        
        return response, session_state
    
    def _create_kyb_file(self, session_state: Dict) -> None:
        """Create a KYB file for the session"""
        try:
            kyb_dir = "kyb_files"
            if not os.path.exists(kyb_dir):
                os.makedirs(kyb_dir)
            
            filename = f"kyb_{session_state['session_id']}.json"
            filepath = os.path.join(kyb_dir, filename)
            
            initial_data = {
                "session_id": session_state['session_id'],
                "business": session_state.get('what_they_sell', ''),
                "created_at": str(uuid.uuid4()),
                "workflow_step": session_state['workflow_step'],
                "kyb_data": session_state['kyb_data']
            }
            
            with open(filepath, 'w') as f:
                json.dump(initial_data, f, indent=2)
                
            session_state['kyb_filepath'] = filepath
            
        except Exception as e:
            print(f"Error creating KYB file: {e}")
    
    def _update_kyb_file(self, session_state: Dict, user_input: str, step: int) -> None:
        """Update the KYB file with new information"""
        try:
            if 'kyb_filepath' in session_state and os.path.exists(session_state['kyb_filepath']):
                
                with open(session_state['kyb_filepath'], 'r') as f:
                    data = json.load(f)
                
                # Update with new information
                data['kyb_data'] = session_state['kyb_data']
                data['workflow_step'] = session_state['workflow_step']
                data[f'step_{step}_response'] = user_input
                data['last_updated'] = str(uuid.uuid4())
                
                with open(session_state['kyb_filepath'], 'w') as f:
                    json.dump(data, f, indent=2)
                    
        except Exception as e:
            print(f"Error updating KYB file: {e}")
    
    def _create_summary(self, kyb_data: Dict) -> str:
        """Create a summary of the KYB data"""
        business_points = len(kyb_data.get('business_understanding', []))
        objective_points = len(kyb_data.get('objectives', []))
        constraint_points = len(kyb_data.get('constraints', []))
        
        summary = f"Comprehensive business profile with {business_points} business insights, {objective_points} objectives, and {constraint_points} challenges identified."
        
        if kyb_data.get('scraped_data'):
            summary += f" Includes data from {len(kyb_data['scraped_data'])} website(s)."
        
        return summary
    
    def _create_summary_from_data(self, kyb_data: Dict) -> str:
        """Create summary from old + new data (Step 8 requirement)"""
        business_count = len(kyb_data.get('business_understanding', []))
        objectives_count = len(kyb_data.get('objectives', []))
        constraints_count = len(kyb_data.get('constraints', []))
        
        summary = f"Complete business profile with {business_count} business insights, {objectives_count} objectives, and {constraints_count} challenges documented."
        
        if kyb_data.get('scraped_data'):
            summary += f" Includes website analysis from {len(kyb_data['scraped_data'])} source(s)."
        
        return summary
    
    def _handle_url_input(self, url: str, full_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Handle URL scraping at any step in the workflow - Scraping first, then AI"""
        try:
            print(f"Attempting to scrape: {url}")
            
            # STEP 1: Pure Python scraping (independent of AI)
            scraped_data = scrape_url(url)
            print(f"Successfully scraped: {scraped_data.get('title', 'No title')}")
            
            # STEP 2: Process scraped data without AI first
            title = scraped_data.get('title', 'Unknown Business')
            content = scraped_data.get('content', '')
            headings = scraped_data.get('headings', [])
            
            # Create basic business summary from scraped data
            basic_summary = f"Website: {title}"
            if headings:
                basic_summary += f"\nKey sections: {', '.join(headings[:3])}"
            if content:
                basic_summary += f"\nContent preview: {content[:200]}..."
            
            # Store scraped data (works without AI)
            session_state['kyb_data']['scraped_data'].append({
                'url': url,
                'title': title,
                'basic_summary': basic_summary,
                'full_content': content[:1000]  # Store first 1000 chars
            })
            
            # STEP 3: Try AI analysis (optional - fallback if fails)
            ai_analysis = "AI analysis unavailable - using basic content extraction"
            try:
                analysis_prompt = f"""
                Analyze this business website and extract key information:
                
                Title: {title}
                Headings: {', '.join(headings[:5])}
                Content: {content[:800]}
                
                What does this business do? Provide a brief summary.
                """
                
                analysis_result = analyze_with_gemini(analysis_prompt, [])
                if analysis_result and analysis_result.get('response'):
                    ai_analysis = analysis_result['response']
            except Exception as ai_error:
                print(f"AI analysis failed: {ai_error}")
                ai_analysis = f"Business analysis: {basic_summary}"
            
            # Auto-fill business information if we're at step 1 or 2
            if session_state['workflow_step'] <= 2:
                business_desc = f"{title}"
                session_state['what_they_sell'] = business_desc
                session_state['workflow_step'] = 3
                
                response = f"""
✅ **Website Successfully Scraped & Analyzed!**

**Website:** {title}

**Extracted Content:**
{basic_summary}

**AI Analysis:**
{ai_analysis}

Let me create your business profile now...
"""
            else:
                # Add as additional context to existing profile
                session_state['kyb_data']['business_understanding'].append(f"Website insight: {ai_analysis[:100]}...")
                response = f"""
✅ **Website Information Added to Profile!** 

**{title}**

**Analysis:** {ai_analysis}
"""
            
        except Exception as e:
            print(f"URL scraping failed: {str(e)}")
            # Provide more specific error message
            if "SSL" in str(e):
                response = f"❌ **SSL Certificate Issue** with that website. This is common with some sites. Please continue with our questions instead!"
            elif "connect" in str(e).lower():
                response = f"❌ **Cannot connect** to that website. It might be down or restricted. Let's continue with our questions!"
            elif "timeout" in str(e).lower():
                response = f"❌ **Website took too long** to respond. Let's continue with our questions instead!"
            else:
                response = f"❌ **Couldn't access that website** ({str(e)[:50]}). No worries, let's continue with the questions!"
        
        return response, session_state
    
    def _ongoing_conversation(self, user_input: str, session_state: Dict) -> Tuple[str, Dict]:
        """Handle conversation after workflow completion"""
        kyb_data = session_state.get('kyb_data', {})
        business = session_state.get('what_they_sell', 'your business')
        
        # Simple contextual responses based on keywords
        if any(word in user_input.lower() for word in ['help', 'assistance', 'support']):
            response = f"Based on your **{business}** profile, I can help you with strategy, marketing, technical challenges, or business development. What specific area interests you?"
        
        elif any(word in user_input.lower() for word in ['marketing', 'customers', 'sales']):
            response = f"For marketing your **{business}**, consider focusing on your unique value proposition and target audience we identified in your profile."
        
        elif any(word in user_input.lower() for word in ['funding', 'investment', 'money']):
            response = f"For funding your **{business}**, highlight the specific problems your AI OS solves and your competitive advantages."
        
        else:
            response = f"Regarding your question about **{user_input}** - based on your **{business}** profile, I can provide targeted guidance. What specific aspect would you like me to focus on?"
        
        return response, session_state