from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_bcrypt import Bcrypt
import secrets
from datetime import timedelta, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/portfolio'
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://jimuell12:portfolio@jimuell12.mysql.pythonanywhere-services.com/jimuell12$portfolio"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Define the User model
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

# Routes

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')
        
        # Query the database for the user with the provided email
        userDetails = users.query.filter_by(email=email).first()

        if userDetails:
            # If userDetails is not None, check the password 
            if bcrypt.check_password_hash(userDetails.password, password):
                # Store user attributes in session
                session['user'] = {
                    'id': userDetails.id,
                    'name': userDetails.name,
                    'email': userDetails.email
                }

                if remember:
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(days=120)
                return redirect(url_for('index'))
        else:
            flash('No account was found in our system')
            return redirect(url_for('login'))
        # If user details are not found or password check fails, show error
        flash('Invalid email or password')
        return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['confirm-password']
        
        if password != repeat_password:
            flash("Password didn't match!")
            return redirect(url_for('register'))
        
        existing_user = users.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists. Please use a different email.')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = users(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        session['user'] = {
            'id': new_user.id,
            'name': new_user.name,
            'email': new_user.email
        }
        flash("Registration successful! You are now logged in.")
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/history')
def history():
    seven_days_ago = datetime.now() - timedelta(days=7)
    all_users = users.query.all()
    user_counts = db.session.query(
        func.date(users.created_at).label('date'),
        func.count(users.id).label('count')
    ).filter(users.created_at >= seven_days_ago).\
    group_by(func.date(users.created_at)).all()
    
    total_counts = users.query.count()

    user_counts_list = [{'date': date.strftime('%Y-%m-%d'), 'count': count} for date, count in user_counts]

    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    return render_template('history.html', user=user, users=all_users, user_counts=user_counts_list, total_counts=total_counts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=5000, debug=True)
