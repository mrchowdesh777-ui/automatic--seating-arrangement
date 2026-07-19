# ============================================
# AUTOMATIC SEATING ARRANGEMENT SYSTEM
# app.py - Updated with Create User + Forgot Password
# ============================================
import os
import traceback
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import csv
import io
from werkzeug.utils import secure_filename
from algorithm import generate_seating

app = Flask(__name__)
app.secret_key = "seating_secret_key_2024"
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    return mysql.connector.connect(
        host="mysql-12f67626-mrchowdesh777-08c5.g.aivencloud.com",
        port=14476,
        user="avnadmin",
        password=os.environ.get("DB_PASSWORD"),
        database="defaultdb",
        ssl_disabled=False,
        ssl_verify_cert=False
    )
    
    return db



# ============================================
# ROUTE 1: LOGIN
# ============================================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )

            user = cursor.fetchone()
            db.close()

            if user:
                session['logged_in'] = True
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password!', 'error')

        except Exception as e:
            return str(e)

    return render_template('login.html', active_tab='login')

# ============================================
# ROUTE 2: LOGOUT
# ============================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ============================================
# ROUTE 3: CREATE USER (Register)
# ============================================
@app.route('/register', methods=['POST'])
def register():
    full_name        = request.form['full_name'].strip()
    new_username     = request.form['new_username'].strip()
    email            = request.form['email'].strip()
    new_password     = request.form['new_password']
    confirm_password = request.form['confirm_password']
    role             = request.form['role']

    # ---- Validations ----
    if len(new_username) < 3:
        flash('Username must be at least 3 characters!', 'error')
        return render_template('login.html', active_tab='register')

    if new_password != confirm_password:
        flash('Passwords do not match!', 'error')
        return render_template('login.html', active_tab='register')

    if len(new_password) < 6:
        flash('Password must be at least 6 characters!', 'error')
        return render_template('login.html', active_tab='register')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Check username duplicate
    cursor.execute("SELECT * FROM users WHERE username=%s", (new_username,))
    if cursor.fetchone():
        flash(f'Username "{new_username}" already exists!', 'error')
        db.close()
        return render_template('login.html', active_tab='register')

    # Check email duplicate
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        flash('This email is already registered!', 'error')
        db.close()
        return render_template('login.html', active_tab='register')

    # Insert new user
    cursor.execute(
        "INSERT INTO users (full_name, username, email, password, role) VALUES (%s,%s,%s,%s,%s)",
        (full_name, new_username, email, new_password, role)
    )
    db.commit()
    db.close()

    flash(f'User "{new_username}" created successfully! They can now login.', 'success')
    return render_template('login.html', active_tab='register')

# ============================================
# ROUTE 4: FORGOT PASSWORD - Verify identity
# ============================================
@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    forgot_username = request.form['forgot_username'].strip()
    forgot_email    = request.form['forgot_email'].strip()

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Check if username + email match in database
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND email=%s",
        (forgot_username, forgot_email)
    )
    user = cursor.fetchone()
    db.close()

    if user:
        # Save username in session for password reset step
        session['reset_user'] = forgot_username
        flash('Identity verified! Now set your new password below.', 'success')
        return render_template('login.html', active_tab='forgot', show_reset=True)
    else:
        flash('Username and email do not match our records!', 'error')
        return render_template('login.html', active_tab='forgot', show_reset=False)

# ============================================
# ROUTE 5: RESET PASSWORD - Save new password
# ============================================
@app.route('/reset_password', methods=['POST'])
def reset_password():
    # Check session
    if not session.get('reset_user'):
        flash('Session expired. Please try again.', 'error')
        return redirect(url_for('login'))

    new_password     = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash('Passwords do not match!', 'error')
        return render_template('login.html', active_tab='forgot', show_reset=True)

    if len(new_password) < 6:
        flash('Password must be at least 6 characters!', 'error')
        return render_template('login.html', active_tab='forgot', show_reset=True)

    # Get username from session and clear it
    username = session.pop('reset_user')

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "UPDATE users SET password=%s WHERE username=%s",
        (new_password, username)
    )
    db.commit()
    db.close()

    flash(f'Password reset successfully! Login with your new password.', 'success')
    return redirect(url_for('login'))

# ============================================
# ROUTE 6: DASHBOARD
# ============================================
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as count FROM rooms")
    room_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM branches")
    branch_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM students")
    student_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM allotment")
    allotment_count = cursor.fetchone()['count']
    db.close()
    return render_template('dashboard.html',
        room_count=room_count, branch_count=branch_count,
        student_count=student_count, allotment_count=allotment_count)

# ============================================
# ROUTE 7: ROOMS
# ============================================
@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            room_name = request.form['room_name']
            rows = int(request.form['rows'])
            cols = int(request.form['cols'])
            capacity = rows * cols
            cursor.execute(
                "INSERT INTO rooms (room_name, num_rows, num_cols, capacity) VALUES (%s,%s,%s,%s)",
                (room_name, rows, cols, capacity))
            db.commit()
            flash(f'Room "{room_name}" added!', 'success')
        elif action == 'delete':
            room_id = request.form['room_id']
            try:
                cursor.execute("DELETE FROM allotment WHERE room_id=%s", (room_id,))
                cursor.execute("DELETE FROM rooms WHERE room_id=%s", (room_id,))
                db.commit()
                flash('Room deleted!', 'success')
            except Exception as e:
                db.rollback()
                flash(f'Error: {str(e)}', 'error')
    cursor.execute("SELECT * FROM rooms ORDER BY room_id")
    all_rooms = cursor.fetchall()
    db.close()
    return render_template('rooms.html', rooms=all_rooms)

# ============================================
# ROUTE 8: BRANCHES
# ============================================
@app.route('/branches', methods=['GET', 'POST'])
def branches():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            branch_name = request.form['branch_name'].upper()
            cursor.execute("SELECT * FROM branches WHERE branch_name=%s", (branch_name,))
            if cursor.fetchone():
                flash(f'Branch "{branch_name}" already exists!', 'error')
            else:
                cursor.execute("INSERT INTO branches (branch_name, total_students) VALUES (%s,%s)", (branch_name, 0))
                db.commit()
                flash(f'Branch "{branch_name}" added!', 'success')
        elif action == 'delete':
            branch_id = request.form['branch_id']
            cursor.execute("DELETE FROM students WHERE branch_id=%s", (branch_id,))
            cursor.execute("DELETE FROM branches WHERE branch_id=%s", (branch_id,))
            db.commit()
            flash('Branch deleted!', 'success')
    cursor.execute("""SELECT b.*, COUNT(s.student_id) as actual_students
        FROM branches b LEFT JOIN students s ON b.branch_id=s.branch_id
        GROUP BY b.branch_id ORDER BY b.branch_id""")
    all_branches = cursor.fetchall()
    db.close()
    return render_template('branches.html', branches=all_branches)

# ============================================
# ROUTE 9: UPLOAD STUDENTS (Paste)
# ============================================
@app.route('/upload_students', methods=['GET', 'POST'])
def upload_students():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        branch_id = request.form['branch_id']
        pin_list_raw = request.form['pin_list']
        pins = [p.strip() for p in pin_list_raw.replace('\n', ',').split(',') if p.strip()]
        cursor.execute("DELETE FROM students WHERE branch_id=%s", (branch_id,))
        data = [(pin, branch_id) for pin in pins]
        cursor.executemany("INSERT INTO students (pin_number, branch_id) VALUES (%s,%s)", data)
        cursor.execute("UPDATE branches SET total_students=%s WHERE branch_id=%s", (len(pins), branch_id))
        db.commit()
        flash(f'{len(pins)} students uploaded!', 'success')
    cursor.execute("SELECT * FROM branches ORDER BY branch_id")
    all_branches = cursor.fetchall()
    cursor.execute("SELECT branch_id, COUNT(*) as count FROM students GROUP BY branch_id")
    counts = {row['branch_id']: row['count'] for row in cursor.fetchall()}
    db.close()
    return render_template('upload_students.html', branches=all_branches, counts=counts)

# ============================================
# ROUTE 10: UPLOAD FILE (CSV/Excel)
# ============================================
@app.route('/upload_file', methods=['POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    branch_id = request.form.get('branch_id')
    if not branch_id:
        flash('Please select a branch!', 'error')
        return redirect(url_for('upload_students'))
    if 'keylist_file' not in request.files:
        flash('No file selected!', 'error')
        return redirect(url_for('upload_students'))
    file = request.files['keylist_file']
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file!', 'error')
        return redirect(url_for('upload_students'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    pins = []
    filename = file.filename.lower()
    try:
        if filename.endswith('.csv') or filename.endswith('.txt'):
            content = file.stream.read().decode('UTF-8')
            stream = io.StringIO(content)
            if ',' in content:
                for row in csv.reader(stream):
                    for cell in row:
                        cell = cell.strip()
                        if cell: pins.append(cell)
            else:
                for line in content.splitlines():
                    line = line.strip()
                    if line: pins.append(line)
        elif filename.endswith('.xlsx'):
            import openpyxl
            wb = openpyxl.load_workbook(file)
            ws = wb.active
            for row in ws.iter_rows(min_row=1, values_only=True):
                if row[0]: pins.append(str(row[0]).strip())
        if not pins:
            flash('No PIN numbers found!', 'error')
            return redirect(url_for('upload_students'))
        cursor.execute("DELETE FROM students WHERE branch_id=%s", (branch_id,))
        data = [(pin, branch_id) for pin in pins]
        cursor.executemany("INSERT INTO students (pin_number, branch_id) VALUES (%s,%s)", data)
        cursor.execute("UPDATE branches SET total_students=%s WHERE branch_id=%s", (len(pins), branch_id))
        db.commit()
        flash(f'{len(pins)} students uploaded from "{file.filename}"!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    db.close()
    return redirect(url_for('upload_students'))

# ============================================
# ROUTE 11: GENERATE SEATING PLAN
# ===========================
@app.route('/generate', methods=['GET', 'POST'])
@app.route('/generate', methods=['GET', 'POST'])
def generate():

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:

        # Clear old allotment
        cursor.execute("DELETE FROM allotment")

        # Get branch names
        cursor.execute("""
            SELECT branch_name
            FROM branches
            ORDER BY branch_id
        """)
        branch_rows = cursor.fetchall()
        branch_names = [row["branch_name"] for row in branch_rows]

        # Get students branch-wise
        students_by_branch = {}

        for branch in branch_names:

            cursor.execute("""
                SELECT s.student_id, s.pin_number
                FROM students s
                JOIN branches b
                    ON s.branch_id = b.branch_id
                WHERE b.branch_name = %s
                ORDER BY s.student_id
            """, (branch,))

            students_by_branch[branch] = cursor.fetchall()

        # Get rooms
        cursor.execute("""
            SELECT room_id, num_rows, num_cols
            FROM rooms
            ORDER BY room_id
        """)
        rooms = cursor.fetchall()

        # Generate seating
        allotment = generate_seating(
            branch_names,
            students_by_branch,
            rooms
        )

        print("Total Seats Generated =", len(allotment))

        # Prepare bulk insert
        data = []

        for seat in allotment:
            data.append((
                seat["room_id"],
                seat["num_row"],
                seat["num_col"],
                seat["student_id"],
                seat["pin"],
                seat["branch"]
            ))

        if data:
            cursor.executemany("""
                INSERT INTO allotment
                (room_id, row_no, col_no, student_id, pin_number, branch_name)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, data)

        db.commit()

        flash(f"{len(data)} seats allotted successfully!", "success")

        return redirect(url_for("view_chart"))

    except Exception as e:

        db.rollback()

        print("========== FULL ERROR ==========")
        traceback.print_exc()

        flash(str(e), "error")

        return redirect(url_for("generate"))

    finally:

        cursor.close()
        db.close()

# ============================================
# ROUTE 12: VIEW SEATING CHART
# ============================================
@app.route('/view_chart')
def view_chart():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms ORDER BY room_id")
    all_rooms = cursor.fetchall()
    seating_data = {}
    for room in all_rooms:
        cursor.execute(
            "SELECT * FROM allotment WHERE room_id=%s ORDER BY row_no, col_no",
            (room['room_id'],))
        seats = cursor.fetchall()
        grid = {}
        for seat in seats:
            grid[(seat['row_no'], seat['col_no'])] = seat
        seating_data[room['room_id']] = {'room': room, 'grid': grid}
    db.close()
    return render_template('seating_chart.html', seating_data=seating_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
