from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from curriculum import CURRICULUM
from ai_tutor import AITutor
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generate a secure secret key
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize AI Tutor
tutor = AITutor()

# User model for storing student information
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    last_subject = db.Column(db.String(50))
    last_topic = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    concept_progress = db.Column(db.Integer, default=0)
    practice_progress = db.Column(db.Integer, default=0)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(
            username=data['username'],
            name=data['name'],
            age=int(data['age']),
            grade=data['grade'],
            last_subject=data.get('subject'),
            last_topic=data.get('topic')
        )
        user.set_password(data['password'])
        
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error during registration', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/get_subjects')
def get_subjects():
    return jsonify(list(CURRICULUM.keys()))

@app.route('/get_chapters/<subject>')
def get_chapters(subject):
    if subject in CURRICULUM:
        chapters = [chapter['name'] for chapter in CURRICULUM[subject]['chapters']]
        return jsonify(chapters)
    return jsonify([])

@app.route('/get_topics/<subject>/<chapter>')
def get_topics(subject, chapter):
    if subject in CURRICULUM:
        for chap in CURRICULUM[subject]['chapters']:
            if chap['name'] == chapter:
                return jsonify({
                    'topics': chap['topics'],
                    'learning_objectives': chap['learning_objectives']
                })
    return jsonify({'topics': [], 'learning_objectives': []})

@app.route('/learn/<subject>/<chapter>/<topic>')
@login_required
def learn(subject, chapter, topic):
    return render_template('learn.html', subject=subject, chapter=chapter, topic=topic)

@app.route('/save_user', methods=['POST'])
@login_required
def update_user_progress():
    data = request.json
    
    try:
        current_user.last_subject = data.get('subject', current_user.last_subject)
        current_user.last_topic = data.get('topic', current_user.last_topic)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'redirect': url_for('learn', subject=data['subject'], chapter=data['chapter'], topic=data['topic'])
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update progress'
        }), 500

@app.route('/get_explanation', methods=['POST'])
@login_required
def get_explanation():
    data = request.get_json()
    subject = data.get('subject')
    chapter = data.get('chapter')
    topic = data.get('topic')
    learning_objectives = data.get('learning_objectives', [])

    try:
        result = tutor.start_lesson(subject, chapter, topic, learning_objectives)
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_explanation: {e}")
        return jsonify({
            'type': 'error',
            'content': str(e)
        }), 500

@app.route('/get_videos', methods=['POST'])
@login_required
def get_videos():
    try:
        result = tutor.find_youtube_videos()
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_videos: {e}")
        return jsonify({
            'type': 'error',
            'content': str(e)
        }), 500

@app.route('/ask_question', methods=['POST'])
@login_required
def ask_question():
    data = request.json
    question = data.get('question')
    result = tutor.answer_question(question)
    return jsonify(result)

@app.route('/get_practice_questions', methods=['POST'])
@login_required
def get_practice_questions():
    try:
        result = tutor.create_practice_questions()
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_practice_questions: {e}")
        return jsonify({
            'type': 'error',
            'content': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
