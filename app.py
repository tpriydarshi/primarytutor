from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    subjects = [
        'English Language',
        'English Literature',
        'Mathematics',
        'Science',
        'History & Civics',
        'Geography',
        'Hindi',
        'Computer Studies'
    ]
    return jsonify(subjects)

if __name__ == '__main__':
    app.run(debug=True)
