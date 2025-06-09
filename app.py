import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the page
st.set_page_config(
    page_title="TalentScout - AI Hiring Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: flex-start;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        flex-direction: row-reverse;
    }
    .chat-message.assistant {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    .chat-message .avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        margin: 0 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .user .avatar {
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    .assistant .avatar {
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    .sidebar-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .info-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .tech-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        margin: 0.2rem;
        font-size: 0.8rem;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    .status-active { background-color: #4caf50; }
    .status-pending { background-color: #ff9800; }
    .status-complete { background-color: #2196f3; }
</style>
""", unsafe_allow_html=True)

class HiringAssistant:
    def __init__(self):
        """Initialize the Hiring Assistant with Gemini API from .env"""
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.conversation_stage = "greeting"
            self.candidate_info = {}
            self.tech_questions = []
            self.questions_asked = 0
            self.conversation_active = True
        except Exception as e:
            st.error(f"Failed to initialize Gemini API: {str(e)}")
            raise
        
    def get_system_prompt(self) -> str:
        """Define the comprehensive system prompt for the hiring assistant"""
        return """You are an AI Hiring Assistant for TalentScout, a prestigious technology recruitment agency. 
        Your role is to conduct professional, thorough, and engaging initial candidate screening interviews.

        CORE OBJECTIVES:
        1. Create a welcoming, professional interview experience
        2. Systematically collect all required candidate information
        3. Assess technical competency through targeted questions
        4. Maintain conversation flow and handle edge cases gracefully
        5. Provide clear next steps and professional closure

        CONVERSATION STAGES:
        1. GREETING: Professional welcome, explain purpose and process (2-3 minutes)
        2. INFO_GATHERING: Systematic collection of candidate details (5-7 minutes)
        3. TECH_STACK: Deep dive into technical skills and experience (3-4 minutes)
        4. TECH_QUESTIONS: 4-5 targeted technical assessment questions (8-10 minutes)
        5. CONCLUSION: Professional wrap-up with clear next steps (2 minutes)

        REQUIRED INFORMATION TO COLLECT:
        ✓ Full Name (First and Last)
        ✓ Professional Email Address
        ✓ Phone Number (with country code if international)
        ✓ Years of Professional Experience
        ✓ Desired Position/Role (specific titles)
        ✓ Current Location (City, Country)
        ✓ Comprehensive Tech Stack:
          - Programming Languages (proficiency levels)
          - Frameworks and Libraries
          - Databases and Data Technologies
          - Cloud Platforms and DevOps Tools
          - Development Tools and IDEs
          - Methodologies (Agile, DevOps, etc.)

        INTERACTION GUIDELINES:
        - Maintain professional yet approachable tone throughout
        - Ask ONE focused question at a time for better user experience
        - Acknowledge and confirm information as it's provided
        - Use natural conversation flow, avoid robotic responses
        - Handle incomplete or unclear responses with gentle clarification
        - Adapt question difficulty based on stated experience level
        - Generate technical questions that are:
          * Relevant to their specific tech stack
          * Appropriate for their experience level
          * Mix of conceptual and practical scenarios
          * Professional interview-standard quality

        CONVERSATION ENDING:
        - Detect keywords: "bye", "goodbye", "exit", "quit", "done", "finish"
        - Provide professional summary and next steps
        - Thank candidate for their time

        STAY FOCUSED:
        - Only discuss hiring, recruitment, and technical assessment topics
        - Politely redirect off-topic conversations back to the interview
        - Handle unexpected inputs gracefully with professional responses

        Respond conversationally, never as lists or bullet points unless specifically formatting technical questions."""

    def get_conversation_status(self) -> Dict[str, str]:
        """Get current conversation status for UI display"""
        stages = {
            "greeting": ("🎯", "Initial Welcome"),
            "info_gathering": ("📝", "Collecting Information"),
            "tech_stack": ("💻", "Technical Skills Assessment"),
            "tech_questions": ("🧠", "Technical Interview"),
            "conclusion": ("✅", "Interview Complete")
        }
        return {
            "icon": stages.get(self.conversation_stage, ("❓", "Unknown"))[0],
            "status": stages.get(self.conversation_stage, ("❓", "Unknown"))[1]
        }

    def generate_response(self, user_input: str, conversation_history: str) -> str:
        """Generate response using Gemini based on conversation stage and history"""
        
        # Check for conversation-ending keywords
        ending_keywords = ["bye", "goodbye", "exit", "quit", "end", "stop", "done", "finish"]
        if any(keyword in user_input.lower().strip() for keyword in ending_keywords):
            self.conversation_stage = "conclusion"
            self.conversation_active = False
            return self.generate_farewell_message()
        
        # Prepare the comprehensive prompt with context
        full_prompt = f"""
        {self.get_system_prompt()}
        
        CURRENT CONTEXT:
        - Conversation Stage: {self.conversation_stage.upper()}
        - Questions Asked: {self.questions_asked}/4
        - Conversation Active: {self.conversation_active}
        
        COLLECTED CANDIDATE INFORMATION:
        {json.dumps(self.candidate_info, indent=2) if self.candidate_info else "None yet"}
        
        RECENT CONVERSATION HISTORY:
        {conversation_history}
        
        CANDIDATE'S LATEST RESPONSE: "{user_input}"
        
        INSTRUCTIONS FOR THIS RESPONSE:
        1. Process the candidate's input and extract any relevant information
        2. Update conversation stage if appropriate
        3. Provide a natural, professional response
        4. Ask the next logical question or provide technical questions if ready
        5. If generating technical questions, make them specific to their tech stack
        
        Generate your response now:
        """
        
        try:
            response = self.model.generate_content(full_prompt)
            return self.process_response(response.text, user_input)
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Could you please repeat your response? (Error: Connection issue)"

    def process_response(self, response: str, user_input: str) -> str:
        """Process the response and update conversation stage/candidate info"""
        
        # Extract information from user input based on current stage
        if self.conversation_stage == "greeting":
            self.conversation_stage = "info_gathering"
            
        elif self.conversation_stage == "info_gathering":
            self.extract_candidate_info(user_input)
            
            # Check if we have sufficient basic info to proceed
            required_basic_fields = ["name", "email", "experience"]
            collected_fields = len([f for f in required_basic_fields if f in self.candidate_info])
            
            if collected_fields >= 2 and "tech" in user_input.lower():
                self.conversation_stage = "tech_stack"
                
        elif self.conversation_stage == "tech_stack":
            self.extract_tech_stack(user_input)
            if "tech_stack" in self.candidate_info:
                self.conversation_stage = "tech_questions"
                
        elif self.conversation_stage == "tech_questions":
            # Track questions asked and generate new ones if needed
            if not self.tech_questions and "tech_stack" in self.candidate_info:
                self.tech_questions = self.generate_technical_questions()
            self.questions_asked += 1
            
            # Move to conclusion after sufficient questioning
            if self.questions_asked >= 4:
                self.conversation_stage = "conclusion"
                
        return response

    def extract_candidate_info(self, user_input: str) -> None:
        """Extract candidate information using advanced parsing techniques"""
        
        # Extract email with improved pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        email_match = re.search(email_pattern, user_input)
        if email_match:
            self.candidate_info["email"] = email_match.group()
            
        # Extract phone number with international support
        phone_patterns = [
            r'(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})',  # US format
            r'(\+\d{1,3}[-.\s]?)?\d{8,15}',  # International format
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, user_input)
            if phone_match:
                self.candidate_info["phone"] = phone_match.group()
                break
                
        # Extract years of experience with multiple patterns
        exp_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*(?:years?|yrs?)',
            r'experienced?\s*(?:for\s*)?(\d+)\s*(?:years?|yrs?)'
        ]
        for pattern in exp_patterns:
            exp_match = re.search(pattern, user_input.lower())
            if exp_match:
                years = exp_match.group(1)
                self.candidate_info["experience"] = f"{years} years"
                break
                
        # Extract name with better logic
        if "name" not in self.candidate_info:
            # Look for "I'm" or "My name is" patterns
            name_patterns = [
                r"(?:i'm|i am|name is|call me)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
                r"([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s|$)"
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, user_input)
                if name_match:
                    self.candidate_info["name"] = name_match.group(1)
                    break
                
        # Extract position/role with expanded keywords
        position_keywords = [
            "developer", "engineer", "programmer", "architect", "analyst", "manager", 
            "lead", "senior", "junior", "full stack", "backend", "frontend", "devops",
            "data scientist", "ml engineer", "software engineer", "web developer"
        ]
        for keyword in position_keywords:
            if keyword in user_input.lower():
                self.candidate_info["position"] = user_input.strip()
                break
                
        # Extract location
        if any(word in user_input.lower() for word in ["from", "live", "based", "located"]):
            # Simple location extraction
            words = user_input.split()
            for i, word in enumerate(words):
                if word.lower() in ["from", "in", "at"] and i + 1 < len(words):
                    location = " ".join(words[i+1:i+3])  # Take next 1-2 words
                    if location and not any(char.isdigit() for char in location):
                        self.candidate_info["location"] = location.strip(".,!")
                        break

    def extract_tech_stack(self, user_input: str) -> None:
        """Extract comprehensive technology stack information"""
        technologies = {
            "programming_languages": {
                "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", 
                "php", "ruby", "kotlin", "swift", "scala", "r", "matlab", "perl", "dart"
            },
            "web_frameworks": {
                "react", "angular", "vue", "django", "flask", "spring", "express", 
                "laravel", "rails", "asp.net", "fastapi", "nextjs", "nuxt", "svelte"
            },
            "mobile_frameworks": {
                "react native", "flutter", "ionic", "xamarin", "cordova", "native android", "native ios"
            },
            "databases": {
                "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", 
                "sql server", "cassandra", "elasticsearch", "firebase", "dynamodb"
            },
            "cloud_platforms": {
                "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean", 
                "linode", "alibaba cloud", "oracle cloud"
            },
            "devops_tools": {
                "docker", "kubernetes", "jenkins", "gitlab ci", "github actions", 
                "terraform", "ansible", "chef", "puppet", "vagrant"
            },
            "development_tools": {
                "git", "svn", "jira", "confluence", "slack", "teams", "vscode", 
                "intellij", "eclipse", "postman", "swagger"
            }
        }
        
        found_tech = {}
        user_lower = user_input.lower()
        
        for category, tech_set in technologies.items():
            found_items = []
            for tech in tech_set:
                if tech in user_lower:
                    found_items.append(tech)
            if found_items:
                found_tech[category] = found_items
                
        if found_tech:
            self.candidate_info["tech_stack"] = found_tech
        else:
            # Store raw input for manual processing
            self.candidate_info["tech_stack_raw"] = user_input

    def generate_technical_questions(self) -> List[str]:
        """Generate sophisticated technical questions based on candidate's profile"""
        if "tech_stack" not in self.candidate_info:
            return ["I'll ask you some general technical questions since I need more details about your tech stack."]
            
        tech_stack = self.candidate_info["tech_stack"]
        experience = self.candidate_info.get("experience", "0 years")
        
        questions_prompt = f"""
        Generate exactly 4 professional technical interview questions for a candidate with:
        
        Tech Stack: {json.dumps(tech_stack, indent=2)}
        Experience Level: {experience}
        Position Interest: {self.candidate_info.get('position', 'Software Developer')}
        
        Requirements for questions:
        1. Mix of conceptual understanding and practical application
        2. Appropriate difficulty for their experience level
        3. Specific to their mentioned technologies
        4. Real-world scenario based
        5. Allow for detailed explanations
        
        Format as:
        Q1: [Question 1]
        Q2: [Question 2]
        Q3: [Question 3]
        Q4: [Question 4]
        
        Make questions professional, clear, and interview-appropriate.
        """
        
        try:
            response = self.model.generate_content(questions_prompt)
            questions = []
            for line in response.text.split('\n'):
                if line.strip().startswith(('Q1:', 'Q2:', 'Q3:', 'Q4:')):
                    questions.append(line.strip())
            return questions if len(questions) == 4 else [response.text]
        except Exception as e:
            return [f"Let me ask you about your experience with {list(tech_stack.keys())[0] if tech_stack else 'programming'}."]

    def generate_farewell_message(self) -> str:
        """Generate a comprehensive farewell message with next steps"""
        summary = self.get_candidate_summary()
        
        return f"""🎉 **Thank you for completing the initial screening interview!**

{summary}

**What happens next:**

🔍 **Review Process** (24-48 hours)
- Our technical team will review your responses
- We'll assess your fit for available positions
- Your information will be matched with suitable opportunities

📧 **Next Communication** 
- You'll receive an email update within 2 business days
- If selected, we'll schedule a detailed technical interview
- Additional requirements or portfolio requests may follow

🚀 **Potential Next Steps**
- Technical deep-dive interview with our client companies
- Code review or technical assignment
- Final interview with hiring managers

**Contact Information:**
- Email: careers@talentscout.com
- Phone: +1-555-TALENT
- LinkedIn: TalentScout Recruitment

Thank you for your interest in opportunities through TalentScout. We're excited about the possibility of working together!

---
*This interview session is now complete. Feel free to close this window.*"""

    def get_candidate_summary(self) -> str:
        """Generate a brief summary of collected information"""
        if not self.candidate_info:
            return "We've had a great conversation about your background and interests."
            
        summary_parts = []
        
        if "name" in self.candidate_info:
            summary_parts.append(f"**{self.candidate_info['name']}**")
            
        if "experience" in self.candidate_info:
            summary_parts.append(f"• {self.candidate_info['experience']} of experience")
            
        if "position" in self.candidate_info:
            summary_parts.append(f"• Interested in {self.candidate_info['position']}")
            
        if "tech_stack" in self.candidate_info:
            tech_count = sum(len(v) for v in self.candidate_info['tech_stack'].values())
            summary_parts.append(f"• Proficient in {tech_count}+ technologies")
            
        return "**Interview Summary:**\n" + "\n".join(summary_parts) if summary_parts else "Thank you for sharing your background with us."

def display_candidate_info(candidate_info: Dict) -> None:
    """Display collected candidate information in the sidebar"""
    if not candidate_info:
        st.markdown("*No information collected yet*")
        return
        
    for key, value in candidate_info.items():
        if key == "tech_stack" and isinstance(value, dict):
            st.markdown("**🛠️ Tech Stack:**")
            for category, techs in value.items():
                if techs:
                    category_display = category.replace('_', ' ').title()
                    st.markdown(f"*{category_display}:*")
                    for tech in techs:
                        st.markdown(f'<span class="tech-badge">{tech}</span>', unsafe_allow_html=True)
        elif key != "tech_stack_raw":
            display_key = key.replace('_', ' ').title()
            st.markdown(f"**{display_key}:** {value}")

def main():
    st.markdown('<h1 class="main-header">🤖 TalentScout AI Hiring Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration and information
    with st.sidebar:
        
        if not GEMINI_API_KEY:
            st.error("⚠️ Gemini API key not found in .env file. Please add GEMINI_API_KEY to your .env.")
            st.stop()
        
        # Display current status
        if 'assistant' in st.session_state:
            status = st.session_state.assistant.get_conversation_status()
            st.markdown(f"### {status['icon']} Current Stage")
            st.markdown(f"**{status['status']}**")
            
            # Progress indicator
            stages = ["greeting", "info_gathering", "tech_stack", "tech_questions", "conclusion"]
            current_stage_idx = stages.index(st.session_state.assistant.conversation_stage)
            progress = (current_stage_idx + 1) / len(stages)
            st.progress(progress)
            
            st.markdown("---")
            
        # Purpose and guidelines
        st.markdown("""
<div class="sidebar-info">
#### 🎯 Interview Purpose
I conduct initial screenings for technology positions, collecting your information and assessing technical skills through targeted questions.

#### 📋 What I'll Ask
- Personal & contact details
- Experience & desired roles
- Technical expertise
- Relevant technical questions

#### ⏱️ Duration
Approximately 10-15 minutes
</div>
""", unsafe_allow_html=True)
        
        # Display collected information
        if 'assistant' in st.session_state and st.session_state.assistant.candidate_info:
            st.markdown("### 📋 Collected Information")
            display_candidate_info(st.session_state.assistant.candidate_info)
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
    if 'assistant' not in st.session_state:
        try:
            st.session_state.assistant = HiringAssistant()
            # Add comprehensive greeting message
            greeting = """👋 **Welcome to TalentScout's AI Hiring Assistant!**

I'm here to conduct your initial screening interview for technology positions. This process will take about 10-15 minutes and helps us understand your background and technical expertise.

**Here's what we'll cover:**
1. 📝 Personal and professional information
2. 💼 Your experience and career interests  
3. 🛠️ Technical skills and expertise
4. 🧠 A few relevant technical questions
5. 🎯 Next steps in the process

I'll guide you through each step, so just respond naturally to my questions. Ready to get started?

**Let's begin - what's your full name?**"""
            
            st.session_state.messages.append({"role": "assistant", "content": greeting})
        except Exception as e:
            st.error(f"Failed to initialize the assistant. Please check your API key in .env. Error: {str(e)}")
    
    # Display chat messages with enhanced styling
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input with enhanced UX
    if 'assistant' in st.session_state:
        # Check if conversation is still active
        if st.session_state.assistant.conversation_active:
            if prompt := st.chat_input("💬 Type your response here...", key="chat_input"):
                # Add user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate assistant response
                conversation_history = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in st.session_state.messages[-6:]  # Last 6 messages for context
                ])
                
                with st.chat_message("assistant"):
                    with st.spinner("🤔 Processing your response..."):
                        response = st.session_state.assistant.generate_response(prompt, conversation_history)
                    st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        else:
            st.info("🎉 Interview completed! Thank you for your time. You can close this window or refresh to start a new session.")
            if st.button("🔄 Start New Interview"):
                # Clear session state for new interview
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    else:
        st.error("Gemini API key not found in .env file. Please add GEMINI_API_KEY to your .env.")
        
        # Show demo information while waiting for API key
        st.markdown("""
        ### 🚀 Getting Started
        
        1. **Get API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) 
        2. **Enter Key**: Paste it in the sidebar
        3. **Start Interview**: Begin your screening process
        
        ### 🔒 Privacy & Security
        - Your data is processed securely
        - No information is permanently stored
        - GDPR compliant handling
        """)

    # Enhanced footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🤖 Powered by**")
        st.markdown("Google Gemini AI")
        
    with col2:
        st.markdown("**🏢 Built for**")
        st.markdown("TalentScout Agency")
        
    with col3:
        st.markdown("**📊 Version**")
        st.markdown("v2.0 Enhanced")

if __name__ == "__main__":
    main()