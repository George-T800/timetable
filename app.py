from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management
bcrypt = Bcrypt(app)

# Initialize the database for users and timetable
def init_db():
    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                    )''')

    # Create timetable table
    cursor.execute('''CREATE TABLE IF NOT EXISTS timetable (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        day TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        time TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )''')
    conn.commit()
    conn.close()

# Route for the homepage (redirect to login if not logged in)
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = sqlite3.connect('timetable.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another one.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('timetable.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

# Route to display the timetable (only accessible to logged-in users)
@app.route('/timetable')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, day, subject, time FROM timetable WHERE user_id = ?", (session['user_id'],))
    timetable = cursor.fetchall()
    conn.close()

    return render_template('timetable.html', timetable=timetable)

# Route to add subjects to the timetable (only for logged-in users)
@app.route('/add', methods=['POST'])
def add_subject():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    day = request.form['day']
    subjects = request.form['subjects'].split(',')
    time = request.form['time']

    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    for subject in subjects:
        cursor.execute("INSERT INTO timetable (user_id, day, subject, time) VALUES (?, ?, ?, ?)", (session['user_id'], day, subject.strip(), time))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

# Route to delete a subject from the timetable
@app.route('/delete/<int:id>', methods=['POST'])
def delete_subject(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM timetable WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

# Route to modify a subject in the timetable
@app.route('/modify/<int:id>', methods=['POST'])
def modify_subject(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    new_subject = request.form['subject']
    new_time = request.form['time']

    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE timetable SET subject = ?, time = ? WHERE id = ? AND user_id = ?", (new_subject, new_time, id, session['user_id']))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Route to log out
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Initialize the database when the app starts
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
