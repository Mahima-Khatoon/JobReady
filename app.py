from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "jobready_secret_key"


# ================= DATABASE =================

def get_db():
    conn = sqlite3.connect("jobready.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            job_role TEXT
        )
    """)

    conn.commit()
    conn.close()


# ================= HOME =================

@app.route("/")
def home():
    return render_template("index.html")


# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO students
                (name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, password)
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Email already registered!"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        student = conn.execute(
            """
            SELECT *
            FROM students
            WHERE email=? AND password=?
            """,
            (email, password)
        ).fetchone()

        conn.close()

        if student:

            session["student_id"] = student["id"]
            session["student_name"] = student["name"]

            return redirect("/dashboard")

        return "Invalid email or password!"

    return render_template("login.html")


# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["student_name"]
    )


# ================= PROFILE =================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "student_id" not in session:
        return redirect("/login")

    conn = get_db()

    message = None

    if request.method == "POST":

        job_role = request.form["job_role"]

        conn.execute(
            """
            UPDATE students
            SET job_role=?
            WHERE id=?
            """,
            (job_role, session["student_id"])
        )

        conn.commit()

        message = "Job role saved successfully!"

    student = conn.execute(
        """
        SELECT *
        FROM students
        WHERE id=?
        """,
        (session["student_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        student=student,
        message=message
    )


# ================= SKILL GAP ANALYZER =================

@app.route("/skills", methods=["GET", "POST"])
def skills():

    if "student_id" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":

        job = request.form["job"]

        excel = int(request.form["excel"])
        sql = int(request.form["sql"])
        python = int(request.form["python"])
        powerbi = int(request.form["powerbi"])
        statistics = int(request.form["statistics"])

        skills = {
            "Excel": excel,
            "SQL": sql,
            "Python": python,
            "Power BI": powerbi,
            "Statistics": statistics
        }

        weak_skills = []

        for skill, level in skills.items():

            if level < 3:
                weak_skills.append(skill)

        result = {
            "job": job,
            "skills": skills,
            "weak": weak_skills
        }

    return render_template(
        "skills.html",
        result=result
    )


# ================= LEARNING ROADMAP =================

@app.route("/roadmap")
def roadmap():

    if "student_id" not in session:
        return redirect("/login")

    return render_template("roadmap.html")


# ================= APTITUDE =================

@app.route("/aptitude")
def aptitude():

    if "student_id" not in session:
        return redirect("/login")

    return render_template("aptitude.html")


# ================= INTERVIEW =================

@app.route("/interview")
def interview():

    if "student_id" not in session:
        return redirect("/login")

    return render_template("interview.html")


# ================= PROGRESS =================

@app.route("/progress")
def progress():

    if "student_id" not in session:
        return redirect("/login")

    return render_template("progress.html")


# ================= ADMIN =================

@app.route("/admin")
def admin():

    conn = get_db()

    students = conn.execute(
        """
        SELECT id, name, email, job_role
        FROM students
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        students=students
    )


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ================= START APPLICATION =================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)