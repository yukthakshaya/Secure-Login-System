from flask import Flask, request, redirect, session, render_template_string
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

bcrypt = Bcrypt(app)

# Create database
def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# Home Page
@app.route('/')
def home():
    if 'user' in session:
        return f'''
        <h2>Welcome {session["user"]}</h2>
        <a href="/logout">Logout</a>
        '''
    return redirect('/login')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if len(password) < 8:
            return "Password must be at least 8 characters"

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            conn = sqlite3.connect('users.db')
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO users(username,password) VALUES (?,?)",
                (username, hashed)
            )

            conn.commit()
            conn.close()

            return redirect('/login')

        except:
            return "Username already exists"

    return render_template_string('''
    <h2>Register</h2>
    <form method="POST">
        Username:<br>
        <input type="text" name="username" required><br><br>

        Password:<br>
        <input type="password" name="password" required><br><br>

        <button type="submit">Register</button>
    </form>

    <a href="/login">Login</a>
    ''')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        cur.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        user = cur.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user[0], password):
            session['user'] = username
            return redirect('/')

        return "Invalid Username or Password"

    return render_template_string('''
    <h2>Login</h2>
    <form method="POST">
        Username:<br>
        <input type="text" name="username" required><br><br>

        Password:<br>
        <input type="password" name="password" required><br><br>

        <button type="submit">Login</button>
    </form>

    <a href="/register">Register</a>
    ''')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)