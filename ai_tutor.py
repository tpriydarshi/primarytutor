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
        self.current_chapter = None
        self.learning_objectives = None

    def start_lesson(self, subject, chapter, topic, learning_objectives):
        """Initialize a new lesson"""
        self.current_subject = subject
        self.current_chapter = chapter
        self.current_topic = topic
        self.learning_objectives = learning_objectives
        self.conversation_history = []
        return self.explain_concept()

    def explain_concept(self):
        """Step 1: Explain the concept with examples and interactive elements"""
        prompt = f"""You are tutoring an 11-year-old student about {self.current_topic} in {self.current_subject} (Chapter: {self.current_chapter}). 
        Learning objectives: {self.learning_objectives}
        
        Explain the concept in an engaging way suitable for an 11-year-old. Include:
        1. A simple explanation with real-world examples
        2. Visual descriptions that help understand the concept
        3. 2-3 interactive questions to check understanding
        
        Format your response in markdown, using emojis and clear sections."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
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
            # Include grade level in search query
            search_query = f"{self.current_topic} {self.current_subject} grade 6 sixth grade explanation for students"
            # First search for videos
            request = youtube.search().list(
                part="snippet",
                q=search_query,
                type="video",
                maxResults=5,
                videoDuration="medium",
                order="relevance"
            )
            response = request.execute()

            # Get video IDs to fetch duration
            video_ids = [item['id']['videoId'] for item in response['items']]
            
            # Get video details including duration
            video_details = youtube.videos().list(
                part="contentDetails",
                id=','.join(video_ids)
            ).execute()

            videos = []
            for item, details in zip(response['items'], video_details['items']):
                # Convert duration to seconds
                duration_str = details['contentDetails']['duration']
                duration_str = duration_str[2:]  # Remove 'PT'
                minutes = 0
                seconds = 0
                
                if 'M' in duration_str:
                    minutes_str = duration_str.split('M')[0]
                    if minutes_str.isdigit():
                        minutes = int(minutes_str)
                    duration_str = duration_str.split('M')[1]
                
                if 'S' in duration_str:
                    seconds_str = duration_str.split('S')[0]
                    if seconds_str.isdigit():
                        seconds = int(seconds_str)

                duration_seconds = minutes * 60 + seconds

                # Only include videos longer than 1 minute
                if duration_seconds > 60:
                    videos.append({
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        'duration': f"{minutes}:{seconds:02d}"
                    })
            
            # Return top 2 videos that meet our criteria
            return {
                "type": "videos",
                "content": videos[:2]
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
            {"role": "user", "content": f"Context: We are learning about {self.current_topic} in {self.current_subject} (Chapter: {self.current_chapter})."},
            *self.conversation_history
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
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
        prompt = f"""Create an engaging assessment for an 11-year-old student about {self.current_topic} in {self.current_subject} (Chapter: {self.current_chapter}).
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
            model="gpt-4",
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

    def create_practice_questions(self):
        """Create practice questions for the current topic"""
        prompt = f"""Create 3 practice questions for a 6th-grade student about {self.current_topic} in {self.current_subject} (Chapter: {self.current_chapter}).
        Learning objectives: {self.learning_objectives}

        Format each question with:
        1. The question text
        2. 4 multiple choice options (A, B, C, D)
        3. The correct answer
        4. A brief explanation of why it's correct

        Make the questions progressively harder, starting with basic understanding and moving to application.
        Format your response in markdown."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are creating practice questions for a 6th-grade student."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return {
                "type": "practice",
                "content": response.choices[0].message['content']
            }
        except Exception as e:
            print(f"Error creating practice questions: {e}")
            return {
                "type": "practice",
                "content": "Failed to generate practice questions. Please try again."
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
            model="gpt-4",
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
