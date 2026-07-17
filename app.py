from flask import send_from_directory, send_file
from flask import Flask, render_template, request, redirect, session, url_for, flash
from config import db, cursor
import qrcode
from reportlab.pdfgen import canvas
import os
from datetime import datetime,date
from flask_mail import Mail, Message
import random
import time

app = Flask(__name__)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "your_email@gmail.com"
app.config["MAIL_PASSWORD"] = "your_app_password"

mail = Mail(app)

app.secret_key = "your_secret_key"

@app.route("/")
def home():

    current_date = datetime.now().strftime("%d %B %Y")

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM registrations")
    total_registrations = cursor.fetchone()[0]

    total_certificates = total_registrations

    return render_template(
        "index.html",
        current_date=current_date,
        total_students=total_students,
        total_events=total_events,
        total_registrations=total_registrations,
        total_certificates=total_certificates
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        register_no = request.form["register_no"]
        department = request.form["department"]
        year = request.form["year"]
        email = request.form["email"]
        password = request.form["password"]

        sql = """
        INSERT INTO students
        (name, register_no, department, year, email, password)
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        values = (name, register_no, department, year, email, password)

        cursor.execute(sql, values)
        db.commit()

        return redirect("/")

    return render_template("register.html")


@app.route("/student_login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        sql = "SELECT * FROM students WHERE email=%s AND password=%s"

        cursor.execute(sql, (email, password))

        student = cursor.fetchone()

        if student:

            session["student_id"] = student[0]

            # If the student came from scanning a QR code
            if "pending_event_id" in session:
                event_id = session.pop("pending_event_id")
                return redirect(url_for("qr_attendance", event_id=event_id))

            return redirect("/student_dashboard")

        else:

            flash("Invalid Email or Password")
            return redirect(url_for("student_login"))

    return render_template("login.html")

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]
        register_no = request.form["register_no"]

        cursor.execute("""
        SELECT * FROM students
        WHERE email=%s AND register_no=%s
        """, (email, register_no))

        student = cursor.fetchone()

        if student:

            otp = str(random.randint(100000, 999999))

            session["reset_otp"] = otp
            session["reset_email"] = email
            session["otp_time"] = time.time()


            msg = Message(
                "Smart Campus Password Reset OTP",
                sender=app.config["MAIL_USERNAME"],
                recipients=[email]
            )

            msg.subject = "Smart Campus Event Management System - Password Reset"

            msg.body = f"""
            UNIVERSITY COLLEGE OF ENGINEERING, ARNI

            SMART CAMPUS EVENT MANAGEMENT SYSTEM

            Dear Student,

            We received a request to reset your password.

            Your One-Time Password (OTP) is:

            {otp}

            This OTP is valid for 5 minutes.

            If you did not request this password reset, please ignore this email.

            Regards,
            Smart Campus Team
            """

            mail.send(msg)

            return redirect("/verify_otp")

        else:
            return "Student Details Not Found"

    return render_template("forgot_password.html")

@app.route("/student_dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT * FROM admin WHERE username=%s AND password=%s"

        cursor.execute(sql, (username, password))

        admin = cursor.fetchone()

        if admin:
            return redirect("/admin_dashboard")
        else:
            return "Invalid Username or Password"

    return render_template("admin_login.html")


@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/create_event", methods=["GET", "POST"])
def create_event():

    if request.method == "POST":

        event_name = request.form["event_name"]
        event_type = request.form["event_type"]
        event_date = request.form["event_date"]
        venue = request.form["venue"]
        organizer = request.form["organizer"]
        registration_fee = request.form["registration_fee"]
        max_participants = request.form["max_participants"]
        description = request.form["description"]

        sql = """
        INSERT INTO events
        (event_name, event_type, event_date, venue,
         organizer, registration_fee, max_participants, description)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            event_name,
            event_type,
            event_date,
            venue,
            organizer,
            registration_fee,
            max_participants,
            description
        )

        cursor.execute(sql, values)
        db.commit()
        event_id = cursor.lastrowid
        qr_data = f"http://localhost/qr_attendance/{event_id}"

        qr = qrcode.make(qr_data)

        qr_path = os.path.join("qr_codes", f"event_{event_id}.png")
        qr.save(qr_path)
        return redirect("/admin_dashboard")

    return render_template("create_event.html")

@app.route("/view_events")
def view_events():

    sql = "SELECT * FROM events"

    cursor.execute(sql)

    events = cursor.fetchall()

    return render_template("view_events.html", events=events)

@app.route("/delete_event/<int:id>")
def delete_event(id):

    sql = "DELETE FROM events WHERE id=%s"

    cursor.execute(sql, (id,))

    db.commit()

    return redirect("/view_events")

@app.route("/edit_event/<int:id>", methods=["GET", "POST"])
def edit_event(id):

    if request.method == "POST":

        event_name = request.form["event_name"]
        event_type = request.form["event_type"]
        date = request.form["date"]
        venue = request.form["venue"]
        organizer = request.form["organizer"]
        participants = request.form["participants"]
        description = request.form["description"]

        sql = """
        UPDATE events
        SET event_name=%s,
            event_type=%s,
            event_date=%s,
            venue=%s,
            organizer=%s,
            max_participants=%s,
            description=%s
        WHERE id=%s
        """

        cursor.execute(sql, (
            event_name,
            event_type,
            date,
            venue,
            organizer,
            participants,
            description,
            id
        ))

        db.commit()

        return redirect("/view_events")

    cursor.execute("SELECT * FROM events WHERE id=%s", (id,))
    event = cursor.fetchone()

    return render_template("edit_event.html", event=event)

@app.route("/student_events")
def student_events():

    cursor.execute("SELECT * FROM events")

    events = cursor.fetchall()

    return render_template("student_events.html", events=events)

@app.route("/payment/<int:event_id>")
def payment(event_id):

    cursor.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    event = cursor.fetchone()

    return render_template("payment.html", event=event)

@app.route("/payment_success/<int:event_id>", methods=["POST"])
def payment_success(event_id):

    student_id = session["student_id"]

    cursor.execute(
        "SELECT * FROM registrations WHERE student_id=%s AND event_id=%s",
        (student_id, event_id)
    )

    already_registered = cursor.fetchone()

    if already_registered:
        return """
        <script>
            alert("You have already registered for this event.");
            window.location.href="/student_events";
        </script>
        """

    cursor.execute(
        """
        INSERT INTO registrations (student_id, event_id, attendance)
        VALUES (%s, %s, %s)
        """,
        (student_id, event_id, "Absent")
    )

    db.commit()

    return """
    <script>
        alert("✅ Payment Successful!");
        window.location.href="/student_events";
    </script>
    """

@app.route("/register_event/<int:event_id>")
def register_event(event_id):

    student_id = session["student_id"]

    cursor.execute(
        "SELECT * FROM registrations WHERE student_id=%s AND event_id=%s",
        (student_id, event_id)
    )

    already_registered = cursor.fetchone()

    if already_registered:
        return "You have already registered for this event."

    cursor.execute(

        """
        INSERT INTO registrations (student_id, event_id, attendance)
        VALUES (%s, %s, %s)
        """,
        (student_id, event_id, "Absent")
    )

    db.commit()

    return redirect("/student_events")

@app.route("/generate_certificate/<int:registration_id>")
def generate_certificate(registration_id):

    cursor.execute("""
    SELECT students.name,
           events.event_name,
           registrations.attendance
    FROM registrations
    JOIN students ON registrations.student_id = students.id
    JOIN events ON registrations.event_id = events.id
    WHERE registrations.id = %s
    """, (registration_id,))

    data = cursor.fetchone()

    if data is None:
        return "Registration not found"

    student_name = data[0]
    event_name = data[1]
    attendance = data[2]

    if attendance != "Present":
        return """
        <script>
        alert("Certificate can only be generated for students whose attendance is marked as Present.");
        window.history.back();
        </script>
        """

    filename = f"certificates/{student_name}.pdf"

    c = canvas.Canvas(filename)

    c.drawImage(
        "static/images/border.png",
        0,
        0,
        width=595,
        height=842
    )

    c.drawImage(
        "static/images/logo.png",
        260,
        730,
        width=80,
        height=80,
        preserveAspectRatio=True
    )

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(300, 690, "UNIVERSITY COLLEGE OF ENGINEERING ARNI")

    c.setFont("Times-Bold", 30)
    c.drawCentredString(300, 630, "CERTIFICATE OF PARTICIPATION")

    c.setFont("Helvetica", 16)
    c.drawCentredString(300, 575, "This is to certify that")

    c.setFont("Times-Bold", 28)
    c.drawCentredString(300, 530, student_name)

    c.setFont("Helvetica", 15)
    c.drawCentredString(300, 490, "has successfully participated in the event")

    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(300, 450, event_name)

    c.setFont("Helvetica", 14)
    c.drawCentredString(300, 410, f"Date: {date.today().strftime('%d-%m-%Y')}")

    c.line(80, 110, 180, 110)
    c.drawString(130, 90, "Coordinator")

    c.line(420, 110, 520, 110)
    c.drawRightString(470, 90, "Principal")

    c.save()

    return send_file(filename, as_attachment=True)

@app.route("/view_registrations")
def view_registrations():

    sql = """
    SELECT
    registrations.id,
    students.name,
    students.register_no,
    events.event_name,
    registrations.attendance,
    registrations.attendance_date,
    registrations.attendance_time

    FROM registrations

    JOIN students
    ON registrations.student_id = students.id

    JOIN events
    ON registrations.event_id = events.id
    """

    cursor.execute(sql)
    registrations = cursor.fetchall()

    return render_template(
        "view_registrations.html",
        registrations=registrations
    )

@app.route("/mark_attendance/<int:id>/<status>")
def mark_attendance(id, status):

    cursor.execute("""
    UPDATE registrations
    SET attendance=%s
    WHERE id=%s
    """, (status, id))

    db.commit()

    return redirect("/view_registrations")

@app.route("/view_qr/<int:event_id>")
def view_qr(event_id):

    filename = f"event_{event_id}.png"

    return render_template("view_qr.html", filename=filename)


@app.route("/qr_codes/<filename>")
def qr_image(filename):

    return send_from_directory("qr_codes", filename)

@app.route("/dashboard")
def dashboard():

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM registrations")
    total_registrations = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM registrations WHERE attendance='Present'")
    total_present = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM registrations WHERE attendance='Absent'")
    total_absent = cursor.fetchone()[0]

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_events=total_events,
        total_registrations=total_registrations,
        total_present=total_present,
        total_absent=total_absent
    )

@app.route("/qr_attendance/<int:event_id>")
def qr_attendance(event_id):

    if "student_id" not in session:
        session["pending_event_id"]=event_id
        return redirect("/student_login")

    student_id = session["student_id"]

    cursor.execute("""
    SELECT * FROM registrations
    WHERE student_id=%s AND event_id=%s
    """, (student_id, event_id))

    registration = cursor.fetchone()

    if registration:

        # Check if attendance is already marked
        if registration[3] == "Present":

            return """
            <script>
            alert("Attendance Already Marked!");
            window.location.href="/student_dashboard";
            </script>
            """

        current_date = datetime.now().date()
        current_time = datetime.now().time().strftime("%H:%M:%S")

        cursor.execute("""
        UPDATE registrations
        SET attendance='Present',
            attendance_date=%s,
            attendance_time=%s
        WHERE student_id=%s AND event_id=%s
        """, (current_date, current_time, student_id, event_id))

        db.commit()

        return """
        <script>
        alert("Attendance Marked Successfully!");
        window.location.href="/student_dashboard";
        </script>
        """

    else:

        return "You are not registered for this event."

@app.route("/my_registrations")
def my_registrations():

    student_id = session["student_id"]

    sql = """
    SELECT
    events.event_name,
    events.event_date,
    events.venue,
    registrations.attendance

    FROM registrations

    JOIN events
    ON registrations.event_id = events.id

    WHERE registrations.student_id = %s
    """

    cursor.execute(sql, (student_id,))
    registrations = cursor.fetchall()

    return render_template(
        "my_registrations.html",
        registrations=registrations
    )

@app.route("/student_profile")
def student_profile():

    student_id = session["student_id"]

    cursor.execute(
        "SELECT name, register_no, department, year, email FROM students WHERE id=%s",
        (student_id,)
    )
    student = cursor.fetchone()

    return render_template("student_profile.html", student=student)

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    student_id = session["student_id"]

    if request.method == "POST":

        name = request.form["name"]
        department = request.form["department"]
        year = request.form["year"]
        email = request.form["email"]

        cursor.execute("""
        UPDATE students
        SET name=%s,
            department=%s,
            year=%s,
            email=%s
        WHERE id=%s
        """, (name, department, year, email, student_id))

        db.commit()

        return redirect("/student_profile")

    cursor.execute("""
    SELECT name, department, year, email
    FROM students
    WHERE id=%s
    """, (student_id,))

    student = cursor.fetchone()

    return render_template("edit_profile.html", student=student)

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/events")
def events():

    current_date = datetime.now().strftime("%d %B %Y")

    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()

    return render_template(
        "events.html",
        current_date=current_date,
        events=events
    )

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        entered_otp = request.form["otp"]

        if time.time() - session.get("otp_time", 0) > 300:
            flash("OTP has expired. Please request a new OTP.")
            return redirect("/forgot_password")

        if entered_otp == session.get("reset_otp"):

            return redirect("/reset_password")

        else:

            flash("Invalid OTP")

            return redirect("/verify_otp")

    return render_template("verify_otp.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():

    if request.method == "POST":

        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("Passwords do not match")
            return redirect("/reset_password")

        email = session.get("reset_email")

        cursor.execute("""
        UPDATE students
        SET password=%s
        WHERE email=%s
        """, (new_password, email))

        db.commit()

        session.pop("reset_otp", None)
        session.pop("reset_email", None)

        flash("Password updated successfully. Please login.")

        return redirect("/student_login")

    return render_template("reset_password.html")

@app.route("/resend_otp")
def resend_otp():

    email = session.get("reset_email")

    if not email:
        flash("Session expired. Please try again.")
        return redirect("/forgot_password")

    otp = str(random.randint(100000, 999999))

    session["reset_otp"] = otp
    session["otp_time"] = time.time()

    msg = Message(
        "Smart Campus Event Management System - Password Reset",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    msg.body = f"""
UNIVERSITY COLLEGE OF ENGINEERING, ARNI

SMART CAMPUS EVENT MANAGEMENT SYSTEM

Dear Student,

Your new OTP for password reset is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this password reset, please ignore this email.

Regards,
Smart Campus Team
"""

    mail.send(msg)

    flash("A new OTP has been sent to your email.")

    return redirect("/verify_otp")
  
if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000 , debug = True)
    
    
