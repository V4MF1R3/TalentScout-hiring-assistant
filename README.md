# 🤖 TalentScout AI Hiring Assistant

An intelligent chatbot for initial candidate screening in technology recruitment, powered by Google Gemini AI.

## Project Overview

The TalentScout AI Hiring Assistant is a conversational AI system designed to streamline the initial screening process for technology candidates. It collects essential candidate information, identifies their tech stack, and generates relevant technical questions tailored to their expertise.

### Key Features
- **Intelligent Information Gathering**: Collects candidate details through natural conversation
- **Tech Stack Analysis**: Identifies programming languages, frameworks, and tools
- **Dynamic Question Generation**: Creates relevant technical questions based on candidate's skills
- **Context-Aware Conversations**: Maintains conversation flow and handles follow-ups
- **Professional Interface**: Clean, intuitive Streamlit-based UI
- **Privacy-Focused**: Secure handling of candidate information

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd hiring-assistant-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Enter your Gemini API key in the sidebar
   - Start the conversation!

### Alternative: Using Virtual Environment (Recommended)
```bash
python -m venv hiring_assistant_env
source hiring_assistant_env/bin/activate  # On Windows: hiring_assistant_env\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Usage Guide

### For Candidates
1. **Start Conversation**: The chatbot greets you and explains its purpose
2. **Provide Information**: Share your details when prompted:
   - Full name
   - Email address
   - Phone number
   - Years of experience
   - Desired position
   - Current location
   - Tech stack
3. **Answer Questions**: Respond to technical questions based on your expertise
4. **End Session**: Use keywords like "bye" or "goodbye" to conclude

### For Recruiters
- Monitor candidate information in the sidebar
- Review conversation flow and responses
- Access collected data for further processing

## Technical Architecture

### Core Components

#### 1. HiringAssistant Class
```python
class HiringAssistant:
    def __init__(self, api_key)           # Initialize Gemini AI
    def get_system_prompt()              # Define assistant behavior
    def generate_response()              # Process user input
    def extract_candidate_info()         # Parse candidate details
    def generate_technical_questions()   # Create relevant questions
```

#### 2. Conversation Flow Management
- **Greeting**: Welcome and purpose explanation
- **Info Gathering**: Systematic information collection
- **Tech Stack**: Technology expertise identification
- **Tech Questions**: Relevant question generation
- **Conclusion**: Professional wrap-up

#### 3. Information Extraction
- **Regex Patterns**: Email, phone, experience extraction
- **Keyword Matching**: Technology identification
- **Context Analysis**: Natural language understanding

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **AI Engine**: Google Gemini Pro API
- **Language**: Python 3.8+
- **Deployment**: Local/Cloud compatible

## Prompt Engineering Strategy

### System Prompt Design
The core system prompt guides the AI to:
- Maintain professional yet friendly tone
- Follow structured conversation flow
- Extract information accurately
- Generate relevant technical questions
- Handle edge cases gracefully

### Key Prompt Components
1. **Role Definition**: Clear identity as hiring assistant
2. **Conversation Stages**: Structured interaction flow
3. **Information Requirements**: Specific data to collect
4. **Guidelines**: Behavioral constraints and best practices
5. **Context Handling**: Maintaining conversation memory

### Dynamic Question Generation
```python
def generate_technical_questions(self):
    """
    Creates 4 relevant technical questions based on:
    - Candidate's tech stack
    - Experience level
    - Role requirements
    - Industry best practices
    """
```

## Features Deep Dive

### 1. Intelligent Information Extraction
- **Email Detection**: Regex pattern matching
- **Phone Parsing**: International format support
- **Experience Calculation**: Years of experience identification
- **Name Recognition**: Proper noun extraction
- **Tech Stack Analysis**: Multi-category technology identification

### 2. Context-Aware Conversations
- **Memory Management**: Maintains conversation history
- **Stage Tracking**: Knows current conversation phase
- **Fallback Handling**: Graceful error recovery
- **Exit Detection**: Natural conversation ending

### 3. Technical Question Generation
- **Adaptive Difficulty**: Matches candidate experience level
- **Stack-Specific**: Tailored to declared technologies
- **Comprehensive Coverage**: Multiple technical areas
- **Interview-Ready**: Professional question formatting

### 4. User Experience
- **Real-time Updates**: Sidebar information display
- **Professional Design**: Clean, modern interface
- **Responsive Layout**: Works on desktop and mobile
- **Error Handling**: User-friendly error messages

## Data Privacy & Security

### Privacy Measures
- **No Persistent Storage**: Data exists only during session
- **In-Memory Processing**: No file system writes
- **API Security**: Secure key handling
- **GDPR Compliance**: Privacy-by-design approach

### Data Handling
- All candidate information is processed in-memory
- No data is permanently stored or transmitted to third parties
- Session data is cleared when browser closes
- API communications are encrypted

## Deployment Options

### Local Deployment
```bash
streamlit run app.py
```

### Cloud Deployment

#### Streamlit Cloud (Recommended)
1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Add API key to secrets management
4. Deploy with one click

#### AWS/GCP/Azure
- Use containerization (Docker)
- Set up environment variables
- Configure API key management
- Deploy using cloud services

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## Testing & Quality Assurance

### Test Scenarios
- **Happy Path**: Complete information gathering flow
- **Edge Cases**: Incomplete information, invalid formats
- **Error Handling**: API failures, network issues
- **Conversation Endings**: Various exit keywords
- **Tech Stack Variations**: Different technology combinations

### Quality Metrics
- **Response Accuracy**: Information extraction precision
- **Conversation Flow**: Natural dialogue progression
- **Technical Relevance**: Question appropriateness
- **User Experience**: Interface usability

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify key is correct and active
   - Check API quota limits
   - Ensure key has Gemini Pro access

2. **Import Errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Check Python version compatibility
   - Verify virtual environment activation

3. **UI Issues**
   - Clear browser cache
   - Try different browser
   - Check network connectivity

### Performance Optimization
- **Response Time**: Optimize prompt length
- **Memory Usage**: Clear conversation history periodically
- **API Efficiency**: Batch requests when possible

## Future Enhancements

### Planned Features
- **Sentiment Analysis**: Gauge candidate emotions
- **Multilingual Support**: Multiple language conversations
- **Advanced Analytics**: Detailed candidate insights
- **Integration APIs**: CRM and ATS connectivity
- **Video Integration**: Face-to-face screening capability

### Scalability Improvements
- **Database Integration**: Persistent candidate storage
- **Multi-tenant Support**: Multiple organization support
- **Advanced Authentication**: Role-based access control
- **Batch Processing**: Handle multiple candidates simultaneously

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
git clone <repository-url>
cd hiring-assistant-chatbot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support

For questions, issues, or suggestions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the troubleshooting section above

## 🏆 Acknowledgments

- Google Gemini AI for powerful language processing
- Streamlit for the excellent web framework
- The open-source community for inspiration and tools

---

**Built with ❤️ for TalentScout Recruitment Agency**

*Last updated: [Current Date]*