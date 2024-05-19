from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random string in production

DATABASE = 'library.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    conn = create_connection()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT NOT NULL,
            published_date TEXT NOT NULL,
            genre TEXT NOT NULL
        )""")
    conn.close()

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        role = request.form['role']

        conn = create_connection()
        with conn:
            conn.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.close()
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['username'] = username
            session['role'] = user[3]
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please check your credentials and try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session or session['role'] != 'librarian':
        flash('You must be logged in as a librarian to access the dashboard.', 'danger')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/view_books')
def view_books():
    if 'username' not in session or session['role'] != 'librarian':
        flash('You must be logged in as a librarian to view books.', 'danger')
        return redirect(url_for('login'))

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Books")
    books = cur.fetchall()
    conn.close()

    return render_template('view_books.html', books=books)

@app.route('/manage_users')
def manage_users():
    if 'username' not in session or session['role'] != 'librarian':
        flash('You must be logged in as a librarian to manage users.', 'danger')
        return redirect(url_for('login'))

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users")
    users = cur.fetchall()
    conn.close()

    return render_template('manage_users.html', users=users)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session or session['role'] != 'librarian':
        flash('You must be logged in as a librarian to add books.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        published_date = request.form['published_date']
        genre = request.form['genre']

        conn = create_connection()
        with conn:
            conn.execute("INSERT INTO Books (title, author, isbn, published_date, genre) VALUES (?, ?, ?, ?, ?)",
                         (title, author, isbn, published_date, genre))
        conn.close()
        flash('Book added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_book.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
