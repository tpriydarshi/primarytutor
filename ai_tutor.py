import os
import openai
from googleapiclient.discovery import build
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize YouTube API
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

class AITutor:
    def __init__(self):
        self.conversation_history = []
        self.current_topic = None
        self.current_subject = None
        self.learning_objectives = None

    def start_lesson(self, subject, topic, learning_objectives):
        """Initialize a new lesson"""
        self.current_subject = subject
        self.current_topic = topic
        self.learning_objectives = learning_objectives
        self.conversation_history = []
        return self.explain_concept()

    def explain_concept(self):
        """Step 1: Explain the concept with examples and interactive elements"""
        prompt = f"""You are tutoring an 11-year-old student about {self.current_topic} in {self.current_subject}. 
        Learning objectives: {self.learning_objectives}
        
        Explain the concept in an engaging way suitable for an 11-year-old. Include:
        1. A simple explanation with real-world examples
        2. Visual descriptions that help understand the concept
        3. 2-3 interactive questions to check understanding
        
        Format your response in markdown, using emojis and clear sections."""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly and engaging tutor for an 11-year-old student."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        explanation = response.choices[0].message['content']
        self.conversation_history.append({"role": "assistant", "content": explanation})
        return {
            "type": "explanation",
            "content": explanation
        }

    def find_youtube_videos(self):
        """Step 2: Find relevant YouTube videos"""
        try:
            search_query = f"{self.current_topic} {self.current_subject} explanation for students"
            request = youtube.search().list(
                part="snippet",
                q=search_query,
                type="video",
                videoDuration="short",
                maxResults=2,
                order="relevance"
            )
            response = request.execute()

            videos = []
            for item in response['items']:
                videos.append({
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                })
            
            return {
                "type": "videos",
                "content": videos
            }
        except Exception as e:
            print(f"Error fetching YouTube videos: {e}")
            return {
                "type": "videos",
                "content": []
            }

    def answer_question(self, question):
        """Step 3: Answer follow-up questions"""
        self.conversation_history.append({"role": "user", "content": question})
        
        messages = [
            {"role": "system", "content": "You are a friendly and engaging tutor for an 11-year-old student."},
            {"role": "user", "content": f"Context: We are learning about {self.current_topic} in {self.current_subject}."},
            *self.conversation_history
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )

        answer = response.choices[0].message['content']
        self.conversation_history.append({"role": "assistant", "content": answer})
        return {
            "type": "answer",
            "content": answer
        }

    def create_assessment(self):
        """Create an assessment to test understanding"""
        prompt = f"""Create an engaging assessment for an 11-year-old student about {self.current_topic} in {self.current_subject}.
        Include:
        1. 3 multiple choice questions
        2. 1 short answer question
        3. 1 practical application question
        
        Format the questions in a fun and encouraging way, suitable for the age group.
        Return the response in JSON format with the following structure:
        {{
            "multiple_choice": [
                {{"question": "", "options": [], "correct_answer": "", "explanation": ""}}
            ],
            "short_answer": {{"question": "", "sample_answer": "", "key_points": []}},
            "practical": {{"question": "", "hints": [], "solution_approach": ""}}
        }}"""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are creating an assessment for an 11-year-old student."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        try:
            assessment = json.loads(response.choices[0].message['content'])
            return {
                "type": "assessment",
                "content": assessment
            }
        except json.JSONDecodeError:
            return {
                "type": "error",
                "content": "Error creating assessment. Please try again."
            }

    def evaluate_answer(self, question_type, student_answer, correct_answer):
        """Evaluate student's answer and provide feedback"""
        prompt = f"""Evaluate this answer from an 11-year-old student:
        Question Type: {question_type}
        Student's Answer: {student_answer}
        Correct Answer: {correct_answer}
        
        Provide encouraging feedback and explanation in a friendly tone.
        If the answer is incorrect, explain why and provide hints for improvement."""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are providing feedback to an 11-year-old student."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return {
            "type": "feedback",
            "content": response.choices[0].message['content']
        }
