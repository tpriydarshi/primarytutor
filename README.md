# Primary Tutor - AI-Powered Educational Platform

An intelligent tutoring system designed specifically for 6th-grade students following the ICSE curriculum. This platform combines AI-powered explanations, interactive learning, and multimedia content to create an engaging educational experience.

## 🎯 Features

- **Personalized Learning Experience**
  - AI-powered tutoring adapted to student's level
  - Interactive concept explanations
  - Real-world examples and visual descriptions
  - Engaging question-answer sessions

- **Comprehensive Curriculum Coverage**
  - Mathematics
  - Science
  - English Language
  - English Literature
  - History & Civics
  - Geography
  - Computer Studies
  - Hindi

- **Multi-Modal Learning**
  - Text-based explanations
  - Curated educational videos
  - Interactive assessments
  - Immediate feedback system

- **Assessment System**
  - Multiple choice questions
  - Short answer questions
  - Practical application problems
  - Detailed feedback and explanations

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- OpenAI API key
- YouTube Data API key

### Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd primarytutor
```

2. Create a virtual environment:
```bash
pyenv virtualenv 3.12.1 primarytutor-env
pyenv local primarytutor-env
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **AI Integration**: OpenAI GPT-4
- **Video Content**: YouTube Data API

## 📖 Usage

1. Register with student details
2. Select a subject from the ICSE curriculum
3. Choose a specific chapter and topic
4. Engage with the AI tutor through:
   - Concept explanations
   - Video resources
   - Interactive Q&A
   - Assessments

## 🔒 Security

- API keys are stored securely in environment variables
- Student data is handled with privacy in mind
- Age-appropriate content filtering

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4 API
- Google for the YouTube Data API
- ICSE Board for curriculum structure

## 📬 Contact

For any queries or suggestions, please open an issue in the repository.
