from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import timedelta
from flask_bcrypt import Bcrypt
import MySQLdb

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days = 7)
bcrypt = Bcrypt(app)

def get_data_from_db():
    db = MySQLdb.connect("localhost", "root", "", "portfolio")
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    db.close()
    return data

def create_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="user_password",
            database="portfolio"
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

@app.route('/')
def index():
    if 'user' not in session:
        # If there is an active session, redirect to index
        return redirect(url_for('login'))
    user = session['user']
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        # If there is an active session, redirect to index
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Process the login form data here
        email = request.form['email']
        password = request.form['password']
        # Authenticate user (this is a simple example, implement secure authentication in production)
        db = MySQLdb.connect("localhost", "root", "", "portfolio")
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        db.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = user
            
            return redirect(url_for('index'))
        else:
            flash('Invalid Credentials')
            return  redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['confirm-password']
        
        if password != repeat_password:
            return "Passwords do not match!"
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        db = MySQLdb.connect("localhost", "root", "", "portfolio")
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        db.commit()
        db.close()
        
        session['user'] = email
        flash("Registration successful! You are now logged in.")
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

