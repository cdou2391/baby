from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_mail import Mail, Message
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'uyvdyu26gfr68348gf8x2fyb348g643grfx'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///suggestions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cedricrugamba@gmail.com'
app.config['MAIL_PASSWORD'] = 'rmfl sdox clbv thjb'
app.config['MAIL_DEFAULT_SENDER'] = 'cedricrugamba@gmail.com'

# Initialize SQLAlchemy
db = SQLAlchemy(app)
mail = Mail(app)

# Set up logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/system.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Your application startup')

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('contactName')
    email = request.form.get('contactEmail')
    message = request.form.get('contactMessage')

    msg = Message("Message from Your Site",
                  recipients=["rugambacedric@gmail.com"],
                  body=f"Name: {name}\nEmail: {email}\nMessage: {message}")
    
    try:
        mail.send(msg)
        flash('Your message has been sent successfully!', 'success')
    except Exception as e:
        flash('An error occurred while sending your message. Please try again.', 'error')
        app.logger.error(f"Failed to send message: {e}")

    return redirect(url_for('home'))

# Define your model with an upvotes column
class NameSuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    name_suggestion = db.Column(db.String(100), nullable=False)
    meaning_reason = db.Column(db.Text, nullable=True)
    your_name = db.Column(db.String(100), nullable=False)
    upvotes = db.Column(db.Integer, default=0, nullable=False)

with app.app_context():
    db.create_all()

def get_top_upvoted_names():
    top_general = NameSuggestion.query \
        .filter_by(category='general') \
        .order_by(NameSuggestion.upvotes.desc()) \
        .limit(5).all()

    top_kinyarwanda = NameSuggestion.query \
        .filter_by(category='kinyarwanda') \
        .order_by(NameSuggestion.upvotes.desc()) \
        .limit(5).all()

    return top_general, top_kinyarwanda

def get_random_names():
    random_general = NameSuggestion.query \
        .filter_by(category='general') \
        .order_by(func.random()) \
        .limit(10).all()

    random_kinyarwanda = NameSuggestion.query \
        .filter_by(category='kinyarwanda') \
        .order_by(func.random()) \
        .limit(10).all()

    return random_general, random_kinyarwanda

@app.route('/', methods=['GET', 'POST'])
def home():
    user_ip = request.remote_addr
    user_agent = request.user_agent.string
    browser = request.user_agent.browser
    platform = request.user_agent.platform
    app.logger.info(f"Access from IP: {user_ip}, Browser: {browser}, Platform: {platform}, User Agent: {user_agent}")
    
    if request.method == 'POST':
        # Extract form data
        category = request.form.get('categorySelection')
        name_suggestion = request.form.get('nameSuggestion')
        meaning_reason = request.form.get('meaningReason', '')  # Provide a default empty string if not present
        your_name = request.form.get('yourName')

        # Check if the name suggestion already exists for the given category
        existing_suggestion = NameSuggestion.query.filter_by(category=category, name_suggestion=name_suggestion).first()
        if existing_suggestion:
            # Flash a message to the user about the duplicate
            flash('This name suggestted has already been submitted.', 'error')
        else:
            # Create a new NameSuggestion instance and add it to the database
            new_suggestion = NameSuggestion(
                category=category,
                name_suggestion=name_suggestion,
                meaning_reason=meaning_reason,
                your_name=your_name,
                upvotes=0  # Default value
            )
            db.session.add(new_suggestion)
            db.session.commit()
            flash('Your name suggestion has been submitted successfully!', 'success')

        # Redirect to home to prevent form re-submission on refresh
        return redirect(url_for('home'))
    else:
        top_general, top_kinyarwanda = get_top_upvoted_names()
        random_general, random_kinyarwanda = get_random_names()
        return render_template('home.html', top_general=top_general, top_kinyarwanda=top_kinyarwanda,
                               random_general=random_general, random_kinyarwanda=random_kinyarwanda)

@app.route('/upvote/<int:name_id>', methods=['POST'])
def upvote(name_id):
    try:
        name_suggestion = NameSuggestion.query.get(name_id)
        if name_suggestion:
            name_suggestion.upvotes += 1
            db.session.commit()
            flash(f"'{name_suggestion.name_suggestion}' has been upvoted. Thank you!", 'success')
            return jsonify(success=True, message=f"'{name_suggestion.name_suggestion}' has been upvoted. Thank you!", new_upvotes=name_suggestion.upvotes)
        else:
            flash("The name suggestion could not be found.", 'error')
            return jsonify(success=False, message="The name suggestion could not be found."), 404
    except Exception as e:
        flash("An error occurred while upvoting. Please try again.", 'error')
        return jsonify(success=False, message="An error occurred while upvoting. Please try again."), 500

if __name__ == '__main__':
    app.run()