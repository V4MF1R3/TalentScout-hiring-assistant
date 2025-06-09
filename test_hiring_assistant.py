"""
Comprehensive Testing Suite for TalentScout AI Hiring Assistant
Tests core functionality, edge cases, and user experience flows
"""

import unittest
import sys
import os
import re
from unittest.mock import Mock, patch, MagicMock

# Add the main app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestHiringAssistant(unittest.TestCase):
    """Test cases for the HiringAssistant class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the Gemini API to avoid actual API calls during testing
        patcher1 = patch('google.generativeai.configure')
        patcher2 = patch('google.generativeai.GenerativeModel')
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.mock_configure = patcher1.start()
        self.mock_model_class = patcher2.start()
        self.mock_model = MagicMock()
        self.mock_model.generate_content.return_value = MagicMock(text="Mocked response")
        self.mock_model_class.return_value = self.mock_model

        from app import HiringAssistant
        self.HiringAssistant = HiringAssistant
        self.assistant = HiringAssistant("test_api_key")

    def test_initialization(self):
        """Test proper initialization of HiringAssistant"""
        self.assertEqual(self.assistant.conversation_stage, "greeting")
        self.assertEqual(self.assistant.candidate_info, {})
        self.assertTrue(self.assistant.conversation_active)
        self.assertEqual(self.assistant.questions_asked, 0)
        self.assertIsInstance(self.assistant.tech_questions, list)

    def test_extract_candidate_info_email(self):
        """Test email extraction from user input"""
        self.assistant.extract_candidate_info("My email is john.doe@example.com")
        self.assertEqual(self.assistant.candidate_info["email"], "john.doe@example.com")

    def test_extract_candidate_info_phone(self):
        """Test phone extraction from user input"""
        self.assistant.extract_candidate_info("You can reach me at +1 555-123-4567")
        self.assertIn("phone", self.assistant.candidate_info)
        self.assertTrue(re.match(r"\+1 555-123-4567", self.assistant.candidate_info["phone"]))

    def test_extract_candidate_info_experience(self):
        """Test years of experience extraction"""
        self.assistant.extract_candidate_info("I have 5 years of experience in software engineering.")
        self.assertEqual(self.assistant.candidate_info["experience"], "5 years")

    def test_extract_candidate_info_name(self):
        """Test name extraction from user input"""
        self.assistant.extract_candidate_info("My name is Jane Smith")
        self.assertEqual(self.assistant.candidate_info["name"], "Jane Smith")

    def test_extract_candidate_info_position(self):
        """Test position extraction from user input"""
        self.assistant.extract_candidate_info("I'm applying for Senior Backend Developer")
        self.assertIn("position", self.assistant.candidate_info)
        self.assertIn("Developer", self.assistant.candidate_info["position"])

    def test_extract_candidate_info_location(self):
        """Test location extraction from user input"""
        self.assistant.extract_candidate_info("I'm based in Berlin, Germany")
        self.assertIn("location", self.assistant.candidate_info)
        self.assertIn("Berlin", self.assistant.candidate_info["location"])

    def test_extract_tech_stack(self):
        """Test tech stack extraction"""
        self.assistant.extract_tech_stack("I have used Python, Django, React, and AWS.")
        self.assertIn("tech_stack", self.assistant.candidate_info)
        self.assertIn("programming_languages", self.assistant.candidate_info["tech_stack"])
        self.assertIn("python", self.assistant.candidate_info["tech_stack"]["programming_languages"])
        self.assertIn("web_frameworks", self.assistant.candidate_info["tech_stack"])
        self.assertIn("django", self.assistant.candidate_info["tech_stack"]["web_frameworks"])
        self.assertIn("cloud_platforms", self.assistant.candidate_info["tech_stack"])
        self.assertIn("aws", self.assistant.candidate_info["tech_stack"]["cloud_platforms"])

    def test_generate_response_greeting_to_info_gathering(self):
        """Test conversation stage transition from greeting to info_gathering"""
        self.assistant.conversation_stage = "greeting"
        response = self.assistant.generate_response("Hello!", "user: Hello!")
        self.assertEqual(self.assistant.conversation_stage, "info_gathering")
        self.assertIn("Mocked response", response)

    def test_generate_response_end_conversation(self):
        """Test conversation ending keywords"""
        self.assistant.conversation_stage = "tech_questions"
        response = self.assistant.generate_response("bye", "user: bye")
        self.assertEqual(self.assistant.conversation_stage, "conclusion")
        self.assertFalse(self.assistant.conversation_active)
        self.assertIn("Thank you for completing the initial screening interview", response)

    def test_generate_technical_questions(self):
        """Test technical question generation logic"""
        self.assistant.candidate_info["tech_stack"] = {
            "programming_languages": ["python"],
            "web_frameworks": ["django"]
        }
        self.assistant.candidate_info["experience"] = "3 years"
        self.mock_model.generate_content.return_value = MagicMock(
            text="Q1: What is Python?\nQ2: Explain Django ORM.\nQ3: How do you deploy Django apps?\nQ4: What is a Python decorator?"
        )
        questions = self.assistant.generate_technical_questions()
        self.assertEqual(len(questions), 4)
        self.assertTrue(all(q.startswith("Q") for q in questions))

    def test_get_candidate_summary(self):
        """Test candidate summary generation"""
        self.assistant.candidate_info = {
            "name": "Alice Example",
            "experience": "7 years",
            "position": "Lead Engineer",
            "tech_stack": {
                "programming_languages": ["python", "java"],
                "cloud_platforms": ["aws"]
            }
        }
        summary = self.assistant.get_candidate_summary()
        self.assertIn("Alice Example", summary)
        self.assertIn("7 years", summary)
        self.assertIn("Lead Engineer", summary)
        self.assertIn("technologies", summary)

if __name__ == "__main__":
    unittest.main()