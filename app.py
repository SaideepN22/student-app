from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'

# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            usn TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------
USERNAME = "admin"
PASSWORD = "admin123"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials!", "error")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))


# ---------------- HOME ----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    search_query = request.args.get('search', '')

    if request.method == 'POST':
        name = request.form['name']
        usn = request.form['usn']

        if not name or not usn:
            flash("All fields are required!", "error")
        else:
            conn.execute("INSERT INTO students (name, usn) VALUES (?, ?)", (name, usn))
            conn.commit()
            flash("Student added successfully!", "success")

    if search_query:
        students = conn.execute(
            "SELECT * FROM students WHERE name LIKE ? OR usn LIKE ?",
            ('%' + search_query + '%', '%' + search_query + '%')
        ).fetchall()
    else:
        students = conn.execute("SELECT * FROM students").fetchall()

    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()

    return render_template(
        'index.html',
        students=students,
        total=total,
        search_query=search_query
    )


# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Student deleted!", "success")
    return redirect(url_for('index'))


# ---------------- EDIT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    if request.method == 'POST':
        name = request.form['name']
        usn = request.form['usn']

        if not name or not usn:
            flash("Fields cannot be empty!", "error")
        else:
            conn.execute(
                "UPDATE students SET name = ?, usn = ? WHERE id = ?",
                (name, usn, id)
            )
            conn.commit()
            flash("Student updated!", "success")
            conn.close()
            return redirect(url_for('index'))

    student = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
    conn.close()

    return render_template('edit.html', student=student)


# ---------------- PROFILE ----------------
@app.route('/profile/<int:id>')
def profile(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
    conn.close()

    return render_template('profile.html', student=student)


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
