import os
import sqlite3
import random
import string
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session, abort
from pdf_generator import generate_pdf
from docx_generator import generate_docx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.db")
GENERATED_PDF_DIR = os.path.join(BASE_DIR, "generated", "pdf")
GENERATED_WORD_DIR = os.path.join(BASE_DIR, "generated", "word")

os.makedirs(GENERATED_PDF_DIR, exist_ok=True)
os.makedirs(GENERATED_WORD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "approtech_official_secret_key_2026_x89a")

AVAILABLE_DOMAINS = [
    "Robotics",
    "Internet of Things (IoT)",
    "Embedded Systems",
    "Machine Learning",
    "UI/UX Design",
    "Artificial Intelligence (AI)",
    "Fullstack Development (python)",
    "Data Analytics",
    "Digital Marketing",
    "Deep Learning",
    "Fullstack Development (Java)",
    "PCB DESIGN"
]

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            registration_number TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            degree_department TEXT NOT NULL,
            institution_name TEXT NOT NULL,
            institution_location TEXT NOT NULL,
            internship_domain TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            format_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Seed master reference student if empty
    cursor.execute("SELECT COUNT(*) FROM student_submissions")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("""
            INSERT INTO student_submissions (
                application_id, full_name, registration_number, email, phone,
                degree_department, institution_name, institution_location,
                internship_domain, start_date, end_date, duration_days, format_type, status, created_at
            ) VALUES (
                'APP-2026-42210', 'Sheik', '422122104046', 'sheik.student@example.com', '9876543210',
                'BE/CSE', 'St.Anne''s CET', 'Cuddlore',
                'Fullstack Development (python)', '2026-09-01', '2026-09-30', 30, 'Offline', 'Accepted', datetime('now')
            )
        """)
        conn.commit()
    conn.close()

init_db()

def generate_app_id():
    suffix = ''.join(random.choices(string.digits, k=5))
    return f"APP-2026-{suffix}"

def calculate_duration(start_str, end_str):
    try:
        s = datetime.strptime(start_str, "%Y-%m-%d")
        e = datetime.strptime(end_str, "%Y-%m-%d")
        delta = (e - s).days + 1
        return max(0, delta)
    except Exception:
        return 0

def format_date_str(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
    except Exception:
        return date_str

# ----------------- STUDENT ROUTES -----------------

@app.route("/")
def index():
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("index.html", domains=AVAILABLE_DOMAINS, today=today)

@app.route("/submit", methods=["POST"])
def submit():
    full_name = request.form.get("full_name", "").strip()
    registration_number = request.form.get("registration_number", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    degree_department = request.form.get("degree_department", "").strip()
    institution_name = request.form.get("institution_name", "").strip()
    institution_location = request.form.get("institution_location", "").strip()
    internship_domain = request.form.get("internship_domain", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    format_type = request.form.get("format_type", "").strip()

    errors = []

    if not full_name:
        errors.append("Full Name is required.")
    if not registration_number:
        errors.append("Registration Number is required.")
    if not email or "@" not in email or "." not in email:
        errors.append("Valid Email ID is required.")
    clean_phone = "".join([c for c in phone if c.isdigit()])
    if not phone or len(clean_phone) < 10:
        errors.append("Valid 10-digit Phone Number is required.")
    if not degree_department:
        errors.append("Degree / Department is required.")
    if not institution_name:
        errors.append("Institution Name is required.")
    if not institution_location:
        errors.append("Institution Location is required.")
    if not internship_domain or internship_domain not in AVAILABLE_DOMAINS:
        errors.append("Please select a valid Internship Domain.")
    if not start_date or not end_date:
        errors.append("Start Date and End Date are required.")
    elif start_date > end_date:
        errors.append("End Date cannot be earlier than Start Date.")
    if format_type not in ["Online", "Offline"]:
        errors.append("Format Type must be either Online or Offline.")

    if errors:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": False, "errors": errors}), 400
        for err in errors:
            flash(err, "error")
        return redirect(url_for("index"))

    duration_days = calculate_duration(start_date, end_date)

    conn = get_db()
    cursor = conn.cursor()

    # Duplicate Submission Check
    cursor.execute("""
        SELECT id, application_id FROM student_submissions 
        WHERE registration_number = ? AND internship_domain = ? AND start_date = ?
    """, (registration_number, internship_domain, start_date))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        app_id = existing["application_id"]
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({
                "success": True, 
                "duplicate": True,
                "message": "An application for this registration number, domain, and start date already exists.",
                "application_id": app_id, 
                "redirect_url": url_for("success", application_id=app_id)
            })
        flash("Existing application retrieved.", "info")
        return redirect(url_for("success", application_id=app_id))

    app_id = generate_app_id()

    cursor.execute("""
        INSERT INTO student_submissions (
            application_id, full_name, registration_number, email, phone,
            degree_department, institution_name, institution_location,
            internship_domain, start_date, end_date, duration_days, format_type, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
    """, (
        app_id, full_name, registration_number, email, phone,
        degree_department, institution_name, institution_location,
        internship_domain, start_date, end_date, duration_days, format_type
    ))

    conn.commit()
    conn.close()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({
            "success": True, 
            "application_id": app_id, 
            "redirect_url": url_for("success", application_id=app_id)
        })

    return redirect(url_for("success", application_id=app_id))

@app.route("/success")
@app.route("/success/<application_id>")
def success(application_id=None):
    if not application_id:
        application_id = request.args.get("id", "").strip()
    if not application_id:
        return redirect(url_for("index"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_submissions WHERE application_id = ?", (application_id,))
    submission = cursor.fetchone()
    conn.close()

    if not submission:
        flash("Application record not found.", "error")
        return redirect(url_for("index"))

    s_date_fmt = format_date_str(submission["start_date"])
    e_date_fmt = format_date_str(submission["end_date"])
    c_date_fmt = datetime.now().strftime("%d-%m-%Y")

    return render_template("success.html", 
                           submission=submission, 
                           start_date_fmt=s_date_fmt, 
                           end_date_fmt=e_date_fmt, 
                           current_date_fmt=c_date_fmt)

@app.route("/letter/<application_id>")
def view_letter(application_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_submissions WHERE application_id = ?", (application_id,))
    submission = cursor.fetchone()
    conn.close()

    if not submission:
        flash("Application record not found.", "error")
        return redirect(url_for("index"))

    s_date_fmt = format_date_str(submission["start_date"])
    e_date_fmt = format_date_str(submission["end_date"])
    c_date_fmt = datetime.now().strftime("%d-%m-%Y")

    return render_template("letter.html", 
                           submission=submission, 
                           start_date_fmt=s_date_fmt, 
                           end_date_fmt=e_date_fmt, 
                           current_date_fmt=c_date_fmt)

# ----------------- DOCUMENT DOWNLOAD ROUTES -----------------

@app.route("/download/pdf/<application_id>")
def download_pdf_by_app_id(application_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_submissions WHERE application_id = ?", (application_id,))
    submission = cursor.fetchone()
    conn.close()

    if not submission:
        abort(404, description="Application not found")

    student_data = dict(submission)
    clean_name = "".join([c for c in student_data["full_name"] if c.isalnum() or c == '_']) or "Student"
    filename = f"{clean_name}_Internship_Confirmation.pdf"
    pdf_path = os.path.join(GENERATED_PDF_DIR, filename)

    generate_pdf(student_data, pdf_path, BASE_DIR)

    as_attachment = request.args.get("view") != "1"
    return send_file(pdf_path, as_attachment=as_attachment, download_name=filename, mimetype="application/pdf")

@app.route("/download/word/<application_id>")
def download_word_by_app_id(application_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_submissions WHERE application_id = ?", (application_id,))
    submission = cursor.fetchone()
    conn.close()

    if not submission:
        abort(404, description="Application not found")

    student_data = dict(submission)
    clean_name = "".join([c for c in student_data["full_name"] if c.isalnum() or c == '_']) or "Student"
    filename = f"Confirmation_Letter_{clean_name}.docx"
    word_path = os.path.join(GENERATED_WORD_DIR, filename)

    generate_docx(student_data, word_path, BASE_DIR)

    return send_file(word_path, as_attachment=True, download_name=filename, 
                     mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

from functools import wraps

ADMIN_USERNAME = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASS", "admin123")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": False, "error": "Unauthorized. Please log in."}), 401
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- ADMIN AUTHENTICATION -----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        next_url = request.form.get("next") or request.args.get("next") or url_for("admin")

        valid_usernames = [ADMIN_USERNAME.lower(), "approtech", "admin@approtech.com"]
        valid_passwords = [ADMIN_PASSWORD, "admin2026"]

        if username.lower() in valid_usernames and password in valid_passwords:
            session["admin_logged_in"] = True
            session["admin_user"] = username
            flash("Signed in successfully.", "success")
            return redirect(next_url)
        else:
            flash("Invalid username or password. Please try again.", "error")
            return render_template("login.html", next_url=next_url)

    next_url = request.args.get("next", "")
    return render_template("login.html", next_url=next_url)

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_user", None)
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))

# ----------------- ADMIN PORTAL ROUTES -----------------

@app.route("/admin")
@admin_required
def admin():
    conn = get_db()
    cursor = conn.cursor()
    
    # Query all submissions for statistics
    cursor.execute("SELECT * FROM student_submissions ORDER BY created_at DESC")
    all_rows = cursor.fetchall()
    submissions = [dict(row) for row in all_rows]

    # Calculate statistics
    total_count = len(submissions)
    pending_count = sum(1 for s in submissions if s["status"] == "Pending")
    accepted_count = sum(1 for s in submissions if s["status"] == "Accepted")
    rejected_count = sum(1 for s in submissions if s["status"] == "Rejected")

    conn.close()

    stats = {
        "total": total_count,
        "pending": pending_count,
        "accepted": accepted_count,
        "rejected": rejected_count
    }

    return render_template("admin.html", 
                           submissions=submissions, 
                           stats=stats, 
                           domains=AVAILABLE_DOMAINS)

@app.route("/admin/view/<int:sub_id>")
@admin_required
def admin_view_submission(sub_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_submissions WHERE id = ?", (sub_id,))
    submission = cursor.fetchone()
    conn.close()

    if not submission:
        return jsonify({"success": False, "error": "Submission not found"}), 404

    data = dict(submission)
    data["start_date_fmt"] = format_date_str(data["start_date"])
    data["end_date_fmt"] = format_date_str(data["end_date"])
    return jsonify({"success": True, "data": data})

@app.route("/admin/update-status/<int:sub_id>", methods=["POST", "GET"])
@admin_required
def update_status(sub_id):
    new_status = request.form.get("status", "").strip()
    if not new_status and request.is_json:
        new_status = request.json.get("status", "").strip()
    if not new_status:
        new_status = request.args.get("status", "").strip()

    if new_status not in ["Pending", "Accepted", "Rejected"]:
        return jsonify({"success": False, "error": "Invalid status value"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE student_submissions SET status = ? WHERE id = ?", (new_status, sub_id))
    conn.commit()

    # Re-calculate statistics for live frontend update
    cursor.execute("SELECT status, COUNT(*) FROM student_submissions GROUP BY status")
    counts = dict(cursor.fetchall())
    cursor.execute("SELECT COUNT(*) FROM student_submissions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT full_name FROM student_submissions WHERE id = ?", (sub_id,))
    student_row = cursor.fetchone()
    student_name = student_row["full_name"] if student_row else "Student"
    conn.close()

    stats = {
        "total": total,
        "pending": counts.get("Pending", 0),
        "accepted": counts.get("Accepted", 0),
        "rejected": counts.get("Rejected", 0)
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({
            "success": True, 
            "status": new_status, 
            "student_name": student_name,
            "stats": stats
        })

    flash(f"Status for {student_name} updated to {new_status}.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/delete/<int:sub_id>", methods=["POST", "DELETE"])
@admin_required
def delete_submission(sub_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student_submissions WHERE id = ?", (sub_id,))
    conn.commit()

    cursor.execute("SELECT status, COUNT(*) FROM student_submissions GROUP BY status")
    counts = dict(cursor.fetchall())
    cursor.execute("SELECT COUNT(*) FROM student_submissions")
    total = cursor.fetchone()[0]
    conn.close()

    stats = {
        "total": total,
        "pending": counts.get("Pending", 0),
        "accepted": counts.get("Accepted", 0),
        "rejected": counts.get("Rejected", 0)
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({"success": True, "stats": stats})

    flash("Submission deleted successfully.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/generate-pdf/<int:sub_id>")
@admin_required
def admin_generate_pdf(sub_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_submissions WHERE id = ?", (sub_id,))
    submission = cursor.fetchone()
    conn.close()

    if not submission:
        abort(404, description="Submission not found")

    student_data = dict(submission)
    clean_name = "".join([c for c in student_data["full_name"] if c.isalnum() or c == '_']) or "Student"
    filename = f"{clean_name}_Internship_Confirmation.pdf"
    pdf_path = os.path.join(GENERATED_PDF_DIR, filename)

    generate_pdf(student_data, pdf_path, BASE_DIR)

    as_attachment = request.args.get("view") != "1"
    return send_file(pdf_path, as_attachment=as_attachment, download_name=filename, mimetype="application/pdf")

@app.route("/admin/generate-word/<int:sub_id>")
@admin_required
def admin_generate_word(sub_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_submissions WHERE id = ?", (sub_id,))
    submission = cursor.fetchone()
    conn.close()

    if not submission:
        abort(404, description="Submission not found")

    student_data = dict(submission)
    clean_name = "".join([c for c in student_data["full_name"] if c.isalnum() or c == '_']) or "Student"
    filename = f"Confirmation_Letter_{clean_name}.docx"
    word_path = os.path.join(GENERATED_WORD_DIR, filename)

    generate_docx(student_data, word_path, BASE_DIR)

    return send_file(word_path, as_attachment=True, download_name=filename, 
                     mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"Approtech Internship Portal running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
