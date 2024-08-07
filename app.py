from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_bcrypt import Bcrypt
import secrets
from datetime import timedelta, datetime
from flask_mail import Mail, Message
from cryptography.fernet import Fernet
import base64

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'showcasestudent2@gmail.com'
app.config['MAIL_PASSWORD'] = 'mebw sqjw nvdg ydhb'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

cipher_key = b'mQTigr-git4dy0YBQpEoC09k7xRkMEXvi3-WxvrGgsA='
cipher = Fernet(cipher_key)

app.config['SECRET_KEY'] = secrets.token_hex(16)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/portfolio'
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://jimuell12:portfolio@jimuell12.mysql.pythonanywhere-services.com/jimuell12$portfolio"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    return render_template('index.html', user=user)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        userDetails = users.query.filter_by(email=email).first()

        if userDetails:
            encrypted_email = cipher.encrypt(email.encode())
            reset_link = url_for('reset_password', token=base64.urlsafe_b64encode(encrypted_email).decode(), _external=True)
            print(reset_link)
            msg = Message(
                subject='Forgot Password Reset!', 
                sender='StudentShowcase@gmail.com',
                recipients=[userDetails.email]
            )
            msg.html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                        <h1 style="color: #333;">Password Reset Request</h1>
                        <p>Hello,</p>
                        <p>We received a request to reset your password. If you did not make this request, you can ignore this email.</p>
                        <p>To reset your password, click the link below:</p>
                        <p>
                            <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; color: #fff; background-color: #007BFF; text-decoration: none; border-radius: 5px;">Reset Password</a>
                        </p>
                        <p>If the above button doesn't work, copy and paste the following link into your web browser:</p>
                        <p><a href="{reset_link}">{reset_link}</a></p>
                        <p>Thank you,<br/>The Student Showcase Team</p>
                    </body>
                </html>
            """
            mail.send(msg)

            flash('Password reset link was sent!', 'success')
            return redirect(url_for('forgot_password'))
        else:
            flash('This email is not in our system!', 'error')
            redirect(url_for('forgot_password'))

    return render_template('forgot.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        decrypted_token = base64.urlsafe_b64decode(token.encode())
        email = cipher.decrypt(decrypted_token).decode()
    except:
        return 'The reset link is invalid.'

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user = users.query.filter_by(email=email).first()
        user.password = hashed_password
        db.session.commit()

        flash('Password reset successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset.html', token=token)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')
        
        userDetails = users.query.filter_by(email=email).first()

        if userDetails:
            if bcrypt.check_password_hash(userDetails.password, password):
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
            flash('No account was found in our system', 'error')
            return redirect(url_for('login'))

        flash('Invalid email or password', 'error')
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
