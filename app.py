from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from curriculum import CURRICULUM
from ai_tutor import AITutor

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize AI Tutor
tutor = AITutor()

# User model for storing student information
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    last_subject = db.Column(db.String(50))
    last_topic = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    concept_progress = db.Column(db.Integer, default=0)
    practice_progress = db.Column(db.Integer, default=0)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/save_user', methods=['POST'])
def save_user():
    data = request.json
    
    # Create new user or update existing
    user = User(
        name=data['name'],
        age=data['age'],
        grade=data['grade'],
        last_subject=data['subject'],
        last_topic=data['topic'],
        concept_progress=0,
        practice_progress=0
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'user_id': user.id,
        'redirect': url_for('dashboard')
    })

@app.route('/get_user_data')
def get_user_data():
    # For now, get the latest user
    user = User.query.order_by(User.id.desc()).first()
    
    if user:
        return jsonify({
            'name': user.name,
            'grade': user.grade,
            'subject': user.last_subject,
            'topic': user.last_topic,
            'progress': {
                'concepts': user.concept_progress,
                'practice': user.practice_progress
            }
        })
    
    return jsonify({
        'error': 'No user found'
    }), 404

@app.route('/get_subjects')
def get_subjects():
    # ICSE subjects for 6th grade
    return jsonify(list(CURRICULUM.keys()))

@app.route('/get_chapters/<subject>')
def get_chapters(subject):
    if subject in CURRICULUM:
        chapters = [chapter['name'] for chapter in CURRICULUM[subject]['chapters']]
        return jsonify(chapters)
    return jsonify({'error': 'Subject not found'}), 404

@app.route('/get_topics/<subject>/<chapter>')
def get_topics(subject, chapter):
    if subject in CURRICULUM:
        for chap in CURRICULUM[subject]['chapters']:
            if chap['name'] == chapter:
                return jsonify({
                    'topics': chap['topics'],
                    'learning_objectives': chap['learning_objectives']
                })
    return jsonify({'error': 'Chapter not found'}), 404

@app.route('/learning')
def learning():
    return render_template('learning.html')

@app.route('/get_explanation', methods=['POST'])
def get_explanation():
    data = request.json
    subject = data.get('subject')
    topic = data.get('topic')
    
    # Get learning objectives from curriculum
    learning_objectives = None
    for chapter in CURRICULUM[subject]['chapters']:
        if topic in chapter['topics']:
            learning_objectives = chapter['learning_objectives']
            break
    
    result = tutor.start_lesson(subject, topic, learning_objectives)
    return jsonify(result)

@app.route('/get_videos', methods=['POST'])
def get_videos():
    result = tutor.find_youtube_videos()
    return jsonify(result)

@app.route('/ask_question', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    result = tutor.answer_question(question)
    return jsonify(result)

@app.route('/get_assessment', methods=['POST'])
def get_assessment():
    result = tutor.create_assessment()
    return jsonify(result)

@app.route('/submit_assessment', methods=['POST'])
def submit_assessment():
    data = request.json
    answers = data.get('answers')
    assessment = data.get('assessment')
    
    # Evaluate each answer type
    feedback = []
    
    # Multiple choice
    for i, answer in enumerate(answers['multiple_choice']):
        correct = assessment['multiple_choice'][i]['correct_answer']
        result = tutor.evaluate_answer('multiple_choice', answer, correct)
        feedback.append(result)
    
    # Short answer
    result = tutor.evaluate_answer('short_answer', 
                                 answers['short_answer'],
                                 assessment['short_answer']['sample_answer'])
    feedback.append(result)
    
    # Practical
    result = tutor.evaluate_answer('practical',
                                 answers['practical'],
                                 assessment['practical']['solution_approach'])
    feedback.append(result)
    
    return jsonify({'feedback': feedback})

if __name__ == '__main__':
    app.run(debug=True)
