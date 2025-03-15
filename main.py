from flask import Flask, render_template, Response, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import threading
from eco_helpers.detection import detect_animals
from eco_helpers.tracking import track_objects
from eco_helpers.visualization import draw_tracks
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

# Password reset form
class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Corrected Camera Sources with embed links for YouTube
CAMERA_SOURCES = {
    "Nkorho Bush Lodge": "https://www.youtube.com/embed/dIChLG4_WNs",
    "Rosie Pan": "https://www.youtube.com/embed/ItdXaWUVF48",
    "African Watering Hole": "https://www.youtube.com/embed/KyQAB-TKOVA",
    "Lisbon Falls": "https://www.youtube.com/embed/9viZIxuonrI",
    "OL DONYO": "https://www.youtube.com/embed/XsOU8JnEpNM",
    "Gorilla Forest Corridor": "https://www.youtube.com/embed/yfSyjwY6zSQ"
}

# Stream generator function for live video feeds
def generate_frames(source):
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"❌ Failed to open camera source: {source}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Lost connection to {source}")
            break

        # Resize frame for improved performance
        frame = cv2.resize(frame, (640, 480))

        # Detect animals using YOLOv5
        detections = detect_animals(frame)

        # Track animals using DeepSORT
        tracks = track_objects(detections, frame)

        # Visualize results with bounding boxes and labels
        frame = draw_tracks(frame, tracks)

        # Encode the frame to JPEG for streaming
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame as a byte stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

# Route to render `index.html`
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Route to render `login.html`
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

# Route to render `register.html`
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}')
            app.logger.error(f'Registration error: {str(e)}')
    return render_template('register.html', form=form)

# Route to render `reset_password.html`
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Send password reset email (implementation not shown)
            flash('Password reset instructions sent to your email.')
        else:
            flash('Email not found.')
    return render_template('reset_password.html', form=form)

# Route to logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route to render `about.html`
@app.route('/about')
@login_required
def about():
    return render_template('about.html')

# Route for video feed display
@app.route('/video_feed/<camera_name>')
@login_required
def video_feed(camera_name):
    source = CAMERA_SOURCES.get(camera_name)
    
    if not source:
        return "❌ Camera feed not available", 404

    # Handling YouTube live streams (iframe rendering)
    if "youtube" in source:
        return render_template('camera_feed.html', camera_name=camera_name, camera_url=source)

    # For direct camera links (non-YouTube)
    return Response(generate_frames(source), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for YouTube feeds
@app.route('/camera_feed')
@login_required
def camera_feed():
    camera_url = request.args.get('url')
    camera_name = request.args.get('name')
    return render_template('camera_feed.html', camera_name=camera_name, camera_url=camera_url)

# Run the Flask app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 for smoother Render deployment
    app.run(host="0.0.0.0", port=port)