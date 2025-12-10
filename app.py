import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Patient, Admin, Staff, Appointment, MedicalRecord
from form import LoginForm, AdminLog, StaffLoginForm

# -----------------------
# Flask App Configuration
# -----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sikretongmalupet'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/CarePoint'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# -----------------------
# HOME ROUTES
# -----------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/announcement")
def announcement():
    return render_template("announcement.html")

# -----------------------
# ADMIN LOGIN
# -----------------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    form = AdminLog()
    if form.validate_on_submit():
        admin = User.query.filter_by(username=form.AdminUser.data, role='admin').first()
        if admin and check_password_hash(admin.password, form.passw.data):
            session['user'] = admin.username
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        flash("Invalid admin credentials", "danger")
    return render_template("admin_login.html", form=form)

# -----------------------
# ADMIN DASHBOARD
# -----------------------
@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    patients = Patient.query.all()
    appointments = Appointment.query.all()
    staff = Staff.query.all()
    return render_template("admin_dashboard.html", patients=patients, appointments=appointments, staff=staff)

# -----------------------
# ADMIN REPORTS
# -----------------------
@app.route("/admin/reports")
def admin_reports():
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    patients = Patient.query.all()
    appointments = Appointment.query.all()
    staff = Staff.query.all()
    from datetime import date
    today = date.today()
    todays_appointments = [appt for appt in appointments if appt.date == today]
    return render_template("admin_reports.html",
                           patients=patients,
                           appointments=appointments,
                           staff=staff,
                           todays_appointments_count=len(todays_appointments))

# -----------------------
# VIEW PATIENTS
# -----------------------
@app.route("/admin/view_patients")
def view_patients():
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    patients = Patient.query.all()
    return render_template("view_patients.html", patients=patients)

# -----------------------
# EDIT PATIENT
# -----------------------
@app.route("/admin/edit_patient/<int:patient_id>", methods=["GET", "POST"])
def edit_patient(patient_id):
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    patient = Patient.query.get_or_404(patient_id)
    if request.method == "POST":
        patient.full_name = request.form.get("full_name")
        patient.email = request.form.get("email")
        patient.phone_number = request.form.get("phone_number")
        patient.address = request.form.get("address")
        patient.gender = request.form.get("gender")
        dob = request.form.get("date_of_birth")
        if dob:
            patient.date_of_birth = datetime.strptime(dob, "%Y-%m-%d").date()
        patient.blood_type = request.form.get("blood_type")
        height = request.form.get("height")
        if height:
            patient.height = float(height)
        age = request.form.get("age")
        if age:
            patient.age = int(age)
        patient.country_origin = request.form.get("country_origin")
        db.session.commit()
        flash("Patient updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("edit_patient.html", patient=patient)

# -----------------------
# APPOINTMENT ROUTES (ADMIN)
# -----------------------
@app.route("/admin/appointments")
def view_appointments():
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    appointments = Appointment.query.all()
    return render_template("appointments.html", appointments=appointments)

@app.route("/admin/appointments/add", methods=["GET", "POST"])
def add_appointment():
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        staff_id = request.form.get("staff_id")
        doctor_name = request.form.get("doctor_name")
        date = request.form.get("date")
        time = request.form.get("time")

        # --- FIX: Convert empty staff_id "" → None ---
        if not staff_id or staff_id.strip() == "":
            staff_id = None
        else:
            staff_id = int(staff_id)

        # --- Validate patient ---
        if not patient_id or not patient_id.isdigit():
            flash("Please select a valid patient.", "danger")
            return redirect(url_for("add_appointment"))

        # --- Create appointment safely ---
        appointment = Appointment(
            patient_id=int(patient_id),
            staff_id=staff_id,  # now safe for nullable integer
            doctor_name=doctor_name,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            time=time,
            status="Pending"
        )

        db.session.add(appointment)
        db.session.commit()

        flash("Appointment created!", "success")
        return redirect(url_for("view_appointments"))

    # GET request
    patients = Patient.query.all()
    staff = Staff.query.all()
    return render_template("add_appointment.html", patients=patients, staff=staff)


@app.route("/admin/appointments/edit/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == "POST":
        appointment.patient_id = request.form.get("patient_id")
        appointment.staff_id = request.form.get("staff_id")
        appointment.doctor_name = request.form.get("doctor_name")
        appointment.date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
        appointment.time = request.form.get("time")
        appointment.status = request.form.get("status")
        db.session.commit()
        flash("Appointment updated!", "success")
        return redirect(url_for("view_appointments"))
    patients = Patient.query.all()
    staff = Staff.query.all()
    return render_template("edit_appointment.html", appointment=appointment, patients=patients, staff=staff)

@app.route("/admin/appointments/delete/<int:appointment_id>")
def delete_appointment(appointment_id):
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash("Appointment deleted!", "success")
    return redirect(url_for("view_appointments"))

# -----------------------
# USER SIGNUP & LOGIN
# -----------------------
@app.route("/user/signup", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        username = request.form.get("username")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        address = request.form.get("address")
        gender = request.form.get("gender")
        date_of_birth_str = request.form.get("date_of_birth")
        blood_type = request.form.get("blood_type")
        height = request.form.get("height")
        age_str = request.form.get("age")
        country_origin = request.form.get("country_origin")
        password = request.form.get("password")

        existing_patient_username = Patient.query.filter_by(username=username).first()
        if existing_patient_username:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("user_signup"))
        existing_patient_email = Patient.query.filter_by(email=email).first()
        if existing_patient_email:
            flash("Email already exists. Please use a different email.", "danger")
            return redirect(url_for("user_signup"))

        date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date() if date_of_birth_str else None
        age = int(age_str) if age_str else None

        new_patient = Patient(
            username=username,
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            address=address,
            gender=gender,
            date_of_birth=date_of_birth,
            blood_type=blood_type,
            height=height,
            age=age,
            country_origin=country_origin,
            password=generate_password_hash(password)
        )
        db.session.add(new_patient)
        try:
            db.session.commit()
            flash("Account created successfully!", "success")
            return redirect(url_for("home"))
        except Exception:
            db.session.rollback()
            flash("An error occurred during signup. Please try again.", "danger")
            return redirect(url_for("user_signup"))
    return render_template("user_signup.html")

@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = User.query.filter_by(username=username, role='admin').first()
        if admin and check_password_hash(admin.password, password):
            session["user"] = admin.username
            session["role"] = "admin"
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        patient = Patient.query.filter_by(username=username).first()
        if patient and check_password_hash(patient.password, password):
            session["user"] = patient.username
            session["role"] = "viewer"
            flash("Login successful!", "success")
            return redirect(url_for("patient_dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("user_login.html")

# -----------------------
# PATIENT DASHBOARD
# -----------------------
@app.route("/patient_dashboard")
def patient_dashboard():
    if session.get("role") not in ["viewer", "patient"]:
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    username = session.get("user")
    patient = Patient.query.filter_by(username=username).first()
    return render_template("patient_dashboard_home.html", patient=patient)

@app.route("/patient_dashboard/about")
def patient_dashboard_about():
    if session.get("role") not in ["viewer", "patient"]:
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    return render_template("patient_dashboard_about.html")

@app.route("/patient_dashboard/services")
def patient_dashboard_services():
    if session.get("role") not in ["viewer", "patient"]:
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    return render_template("patient_dashboard_services.html")

@app.route("/patient_dashboard/announce")
def patient_dashboard_announce():
    if session.get("role") not in ["viewer", "patient"]:
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    return render_template("patient_dashboard_announce.html")

@app.route("/patient/appointments")
def view_appointments_patients():
    appointments = Appointment.query.all()
    return render_template("appointments_patients.html", appointments=appointments)

@app.route("/patient/records")
def patient_records():
    if session.get("role") not in ["viewer", "patient"]:
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    username = session.get("user")
    patient = Patient.query.filter_by(username=username).first()
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("patient_dashboard"))
    medical_records = MedicalRecord.query.filter_by(patient_id=patient.id).all()
    return render_template("patient_records.html", medical_records=medical_records)

@app.route("/add/appointment/patient", methods=["GET", "POST"])
def add_appointment_patient():
    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        staff_id = request.form.get("staff_id")
        doctor_name = request.form.get("doctor_name")
        date = request.form.get("date")
        time = request.form.get("time")

        # --- FIX: Convert empty staff_id "" → None ---
        if not staff_id or staff_id.strip() == "":
            staff_id = None
        else:
            staff_id = int(staff_id)

        # --- Validate patient ---
        if not patient_id or not patient_id.isdigit():
            flash("Please select a valid patient.", "danger")
            return redirect(url_for("add_appointment_patient"))

        # --- Create appointment safely ---
        appointment = Appointment(
            patient_id=int(patient_id),
            staff_id=staff_id,  # now safe for nullable integer
            doctor_name=doctor_name,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            time=time,
            status="Pending"
        )

        db.session.add(appointment)
        db.session.commit()

        flash("Appointment created!", "success")
        return redirect(url_for("patient_appointments"))

    # GET request
    patients = Patient.query.all()
    staff = Staff.query.all()
    return render_template("add_appointment_patient.html", patients=patients, staff=staff)

@app.route("/patient/appointments")
def patient_appointments():
    appointments = Appointment.query.all()
    return render_template("appointments_patient.html", appointments=appointments)

@app.route("/patient/appointments/edit/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment_patient(appointment_id):
    if session.get("role") not in ["viewer", "patient"]:
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    username = session.get("user")
    patient = Patient.query.filter_by(username=username).first()
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.patient_id != patient.id:
        flash("You can only edit your own appointments.", "danger")
        return redirect(url_for("view_appointments_patients"))
    if request.method == "POST":
        appointment.patient_id = request.form.get("patient_id")
        appointment.staff_id = request.form.get("staff_id")
        appointment.doctor_name = request.form.get("doctor_name")
        appointment.date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
        appointment.time = request.form.get("time")
        appointment.status = request.form.get("status")
        db.session.commit()
        flash("Appointment updated!", "success")
        return redirect(url_for("view_appointments_patients"))
    patients = Patient.query.all()
    staff = Staff.query.all()
    return render_template("edit_appointment_patient.html", appointment=appointment, patients=patients, staff=staff)

@app.route("/patient/appointments/delete/<int:appointment_id>")
def delete_appointment_patient(appointment_id):
    if session.get("role") not in ["viewer", "patient"]:
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    username = session.get("user")
    patient = Patient.query.filter_by(username=username).first()
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.patient_id != patient.id:
        flash("You can only delete your own appointments.", "danger")
        return redirect(url_for("view_appointments_patients"))
    db.session.delete(appointment)
    db.session.commit()
    flash("Appointment deleted!", "success")
    return redirect(url_for("view_appointments_patients"))

# -----------------------
# LOGOUT
# -----------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))

# -----------------------
# STAFF LOGIN & DASHBOARD
# -----------------------
@app.route("/staff/login", methods=["GET", "POST"])
def staff_login():
    form = StaffLoginForm()
    if form.validate_on_submit():
        staff = Staff.query.filter_by(username=form.username.data).first()
        if staff and check_password_hash(staff.password, form.password.data):
            session["role"] = "staff"
            session["staff_id"] = staff.id
            flash("Login successful!", "success")
            return redirect(url_for("staff_dashboard_view"))
        flash("Invalid username or password", "danger")
    return render_template("staff_login.html", form=form)

@app.route("/staff/dashboard")
def staff_dashboard_view():
    if session.get("role") != "staff":
        flash("Access denied.", "danger")
        return redirect(url_for("staff_login"))
    staff_id = session.get("staff_id")
    if not staff_id:
        flash("Session expired. Please log in again.", "danger")
        return redirect(url_for("staff_login"))
    staff = Staff.query.get(staff_id)
    if not staff:
        flash("Staff member not found.", "danger")
        return redirect(url_for("staff_login"))
    appointments = Appointment.query.filter_by(staff_id=staff_id).all()
    return render_template("staff_dashboard.html", staff=staff, appointments=appointments)

@app.route("/staff/appointments/update/<int:appointment_id>", methods=["POST"])
def staff_update_appointment_status(appointment_id):
    """Renamed to avoid endpoint conflict"""
    if session.get("role") != "staff":
        flash("Access denied.", "danger")
        return redirect(url_for("staff_login"))
    staff_id = session.get("staff_id")
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.staff_id != staff_id:
        flash("You cannot update this appointment.", "danger")
        return redirect(url_for("staff_dashboard_view"))
    new_status = request.form.get("status")
    if new_status in ["Pending", "In Progress", "Completed"]:
        appointment.status = new_status
        db.session.commit()
        flash("Appointment status updated!", "success")
    else:
        flash("Invalid status.", "danger")
    return redirect(url_for("staff_dashboard_view"))

# -----------------------
# STAFF MANAGEMENT ROUTES
# -----------------------
@app.route("/admin/view_staff")
def view_staff():
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    staff = Staff.query.all()
    return render_template("view_staff.html", staff=staff)

@app.route("/admin/add_staff", methods=["GET", "POST"])
def add_staff():
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        email = request.form.get("email")
        phone_number = request.form.get("phone")  # match form input name
        password = request.form.get("password")
        role = request.form.get("role")

        # Check if username exists
        existing_staff = Staff.query.filter_by(username=username).first()
        if existing_staff:
            flash("Username already exists.", "danger")
            return redirect(url_for("add_staff"))

        # Check if email exists (if provided)
        if email:
            existing_email = Staff.query.filter_by(email=email).first()
            if existing_email:
                flash("Email already exists.", "danger")
                return redirect(url_for("add_staff"))

        new_staff = Staff(
            username=username,
            name=name,
            email=email,
            phone_number=phone_number,  # <-- use phone_number here
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(new_staff)
        db.session.commit()

        flash("Staff added successfully!", "success")
        return redirect(url_for("view_staff"))

    return render_template("add_staff.html")



@app.route("/admin/edit_staff/<int:staff_id>", methods=["GET", "POST"])
def edit_staff(staff_id):
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))

    staff_member = Staff.query.get_or_404(staff_id)

    if request.method == "POST":
        # Update fields from form
        staff_member.username = request.form.get("username")
        staff_member.name = request.form.get("name")
        staff_member.email = request.form.get("email")  # optional
        staff_member.phone_number = request.form.get("phone_number")  # matches form 'name'
        staff_member.role = request.form.get("role")

        # Update password only if a new one is provided
        password = request.form.get("password")
        if password:
            staff_member.password = generate_password_hash(password)

        # Commit changes
        db.session.commit()
        flash("Staff updated successfully!", "success")
        return redirect(url_for("view_staff"))

    # Render template with staff_member object as 'member'
    return render_template("edit_staff.html", member=staff_member)


@app.route("/admin/delete_patient/<int:patient_id>")
def delete_patient(patient_id):
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient deleted successfully!", "success")
    return redirect(url_for("view_patients"))

@app.route("/admin/delete_staff/<int:staff_id>")
def delete_staff(staff_id):
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    staff_member = Staff.query.get_or_404(staff_id)
    db.session.delete(staff_member)
    db.session.commit()
    flash("Staff deleted successfully!", "success")
    return redirect(url_for("view_staff"))

# -----------------------
# STARTUP
# -----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password=generate_password_hash('admin01'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
