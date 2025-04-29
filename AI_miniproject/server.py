from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import re
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coping.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    coping_history = db.relationship('CopingHistory', backref='user', lazy=True)
    progress = db.relationship('Progress', backref='user', lazy=True)

class CopingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    emotion = db.Column(db.String(50), nullable=False)
    stressor = db.Column(db.String(50), nullable=False)
    physical = db.Column(db.String(50))
    time = db.Column(db.String(20))
    support = db.Column(db.String(20))
    environment = db.Column(db.String(20))
    suggestions = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    emotion = db.Column(db.String(50), nullable=False)
    stressor = db.Column(db.String(50), nullable=False)
    effectiveness = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    recent_history = CopingHistory.query.filter_by(user_id=current_user.id)\
        .order_by(CopingHistory.timestamp.desc())\
        .limit(3).all()
    
    return render_template('dashboard.html', recent_history=recent_history)

@app.route('/history')
@login_required
def history():
    history = CopingHistory.query.filter_by(user_id=current_user.id)\
        .order_by(CopingHistory.timestamp.desc())\
        .all()
    return render_template('history.html', history=history)

@app.route('/progress')
@login_required
def progress():
    progress_data = Progress.query.filter_by(user_id=current_user.id)\
        .order_by(Progress.timestamp.desc())\
        .all()
    
    # Calculate statistics
    total_entries = len(progress_data)
    if total_entries > 0:
        average_effectiveness = sum(entry.effectiveness for entry in progress_data) / total_entries
        
        # Find most common emotion
        emotion_counts = {}
        for entry in progress_data:
            emotion_counts[entry.emotion] = emotion_counts.get(entry.emotion, 0) + 1
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
    else:
        average_effectiveness = 0
        most_common_emotion = "No data yet"
    
    return render_template('progress.html',
                         progress_data=progress_data,
                         average_effectiveness=average_effectiveness,
                         total_entries=total_entries,
                         most_common_emotion=most_common_emotion)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check if username is already taken by another user
        existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
        if existing_user:
            flash('Username already taken', 'error')
            return redirect(url_for('profile'))

        # Check if email is already taken by another user
        existing_email = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_email:
            flash('Email already taken', 'error')
            return redirect(url_for('profile'))

        # Update username and email
        current_user.username = username
        current_user.email = email

        # Handle password change if provided
        if current_password and new_password and confirm_password:
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('profile'))
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('profile'))
            
            current_user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))

    # Get user statistics
    total_suggestions = CopingHistory.query.filter_by(user_id=current_user.id).count()
    total_progress = Progress.query.filter_by(user_id=current_user.id).count()

    return render_template('profile.html',
                         total_suggestions=total_suggestions,
                         total_progress=total_progress)

@app.route('/get_suggestion', methods=['POST'])
@login_required
def get_suggestion():
    data = request.json
    stressor = data.get('stressor')
    emotion = data.get('emotion')
    physical = data.get('physical', 'none')
    time = data.get('time', 'afternoon')
    support = data.get('support', 'unavailable')
    environment = data.get('environment', 'home')

    if not emotion or not stressor:
        return jsonify({
            'error': 'Emotion and stressor are required fields',
            'suggestions': ['deep_breathing', 'talk_to_a_therapist']
        })

    query = f"respond('{emotion}', '{stressor}', '{physical}', '{time}', '{support}', '{environment}', Suggestions)."

    try:
        result = subprocess.run(
            ['C:\\Program Files\\swipl\\bin\\swipl.exe', '-s', 'coping_bot.pl', '-g', query, '-t', 'halt'],
            capture_output=True, text=True
        )

        output = result.stdout.strip()
        print(f"Prolog output: {output}")

        match = re.search(r'\[(.*?)\]', output)
        if match:
            suggestions_str = match.group(1)
            suggestions = [s.strip().strip("'") for s in suggestions_str.split(',')]
            
            # Save to history
            history = CopingHistory(
                user_id=current_user.id,
                emotion=emotion,
                stressor=stressor,
                physical=physical,
                time=time,
                support=support,
                environment=environment,
                suggestions=', '.join(suggestions)
            )
            db.session.add(history)
            db.session.commit()
        else:
            suggestions = ['deep_breathing', 'talk_to_a_therapist']

        return jsonify({
            'suggestions': suggestions,
            'parameters': {
                'emotion': emotion,
                'stressor': stressor,
                'physical': physical,
                'time': time,
                'support': support,
                'environment': environment
            }
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your request',
            'suggestions': ['deep_breathing', 'talk_to_a_therapist']
        })

@app.route('/save_progress', methods=['POST'])
@login_required
def save_progress():
    data = request.json
    emotion = data.get('emotion')
    stressor = data.get('stressor')
    effectiveness = data.get('effectiveness')

    progress = Progress(
        user_id=current_user.id,
        emotion=emotion,
        stressor=stressor,
        effectiveness=effectiveness
    )
    db.session.add(progress)
    db.session.commit()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    with app.app_context():
        # Only create tables if they don't exist
        db.create_all()
        
        # Create a test user only if no users exist
        if not User.query.first():
            test_user = User(
                username='test',
                email='test@example.com',
                password_hash=generate_password_hash('test123')
            )
            db.session.add(test_user)
            db.session.commit()
            
    app.run(debug=True, port=5000)
