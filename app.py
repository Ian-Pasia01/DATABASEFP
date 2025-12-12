import logging
from datetime import datetime, date
from flask import Flask, render_template, redirect, url_for, session, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Patient, Staff, Appointment, MedicalRecord
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
        admin = Staff.query.filter_by(username=form.AdminUser.data, role='admin').first()
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
        doctor_id = request.form.get("doctor_id")
        staff_id = request.form.get("staff_id")
        date = request.form.get("date")
        time = request.form.get("time")

        # Get doctor information from selected doctor
        doctor = Staff.query.get_or_404(doctor_id)
        doctor_name = doctor.name

        # --- Handle additional staff assignment ---
        # Additional staff (nurse) is optional
        if not staff_id or (isinstance(staff_id, str) and staff_id.strip() == ""):
            staff_id = None
        else:
            staff_id = int(staff_id) if staff_id else None

        # --- Validate patient ---
        if not patient_id or not patient_id.isdigit():
            flash("Please select a valid patient.", "danger")
            return redirect(url_for("add_appointment"))

        # --- Create appointment safely ---
        appointment = Appointment(
            patient_id=int(patient_id),
            doctor_id=int(doctor_id),
            staff_id=staff_id,
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
    doctors = Staff.query.filter_by(role="doctor").all()
    # Only fetch nurses for additional staff assignment
    nurses = Staff.query.filter_by(role="nurse").all()
    return render_template("add_appointment.html", patients=patients, doctors=doctors, staff=nurses)


@app.route("/admin/appointments/edit/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin_login"))
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == "POST":
        appointment.patient_id = request.form.get("patient_id")
        
        # Get doctor from selected doctor_id
        doctor_id = request.form.get("doctor_id")
        doctor = Staff.query.get_or_404(doctor_id)
        appointment.doctor_id = int(doctor_id)
        appointment.doctor_name = doctor.name
        
        # Handle additional staff (optional)
        staff_id = request.form.get("staff_id")
        if not staff_id or (isinstance(staff_id, str) and staff_id.strip() == ""):
            appointment.staff_id = None
        else:
            appointment.staff_id = int(staff_id) if staff_id else None
        
        appointment.date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
        appointment.time = request.form.get("time")
        appointment.status = request.form.get("status")
        db.session.commit()
        flash("Appointment updated!", "success")
        return redirect(url_for("view_appointments"))
    patients = Patient.query.all()
    doctors = Staff.query.filter_by(role="doctor").all()
    # Only fetch nurses for additional staff assignment
    nurses = Staff.query.filter_by(role="nurse").all()
    return render_template("edit_appointment.html", appointment=appointment, patients=patients, doctors=doctors, staff=nurses)

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
        patient = Patient.query.filter_by(username=username).first()
        if patient and check_password_hash(patient.password, password):
            session["user"] = patient.username
            session["role"] = "viewer"
            flash("Login successful!", "success")
            return redirect(url_for("patient_dashboard_home"))
        flash("Invalid credentials", "danger")
    return render_template("user_login.html")

# -----------------------
# PATIENT DASHBOARD
# -----------------------
@app.route("/patient/dashboard")
def patient_dashboard_home():
    if session.get("role") != "viewer":
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    patient = Patient.query.filter_by(username=session.get("user")).first()
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("user_login"))
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    medical_records = MedicalRecord.query.filter_by(patient_id=patient.id).all()
    return render_template("patient_dashboard_home.html", patient=patient, appointments=appointments, medical_records=medical_records)

@app.route("/patient/appointments")
def patient_appointments():
    if session.get("role") != "viewer":
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    patient = Patient.query.filter_by(username=session.get("user")).first()
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("user_login"))
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    return render_template("appointments_patients.html", patient=patient, appointments=appointments)

@app.route("/patient/appointments/add", methods=["GET", "POST"])
def add_patient_appointment():
    if session.get("role") != "viewer":
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    patient = Patient.query.filter_by(username=session.get("user")).first()
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("user_login"))
    
    if request.method == "POST":
        doctor_id = request.form.get("doctor_id")
        staff_id = request.form.get("staff_id")
        appt_date = request.form.get("date")
        appt_time = request.form.get("time")
        
        # Verify patient still exists before creating appointment
        patient = Patient.query.get(patient.id)
        if not patient:
            flash("Patient record not found.", "danger")
            return redirect(url_for("user_login"))
        
        # Get doctor information from selected doctor
        doctor = Staff.query.get_or_404(doctor_id)
        doctor_name = doctor.name
        
        # Handle nullable staff_id (for additional staff assignment)
        if not staff_id or (isinstance(staff_id, str) and staff_id.strip() == ""):
            staff_id = None
        else:
            staff_id = int(staff_id) if staff_id else None
        
        try:
            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=int(doctor_id),
                staff_id=staff_id,
                doctor_name=doctor_name,
                date=datetime.strptime(appt_date, "%Y-%m-%d").date(),
                time=appt_time,
                status="Pending"
            )
            db.session.add(appointment)
            db.session.commit()
            flash("Appointment request submitted!", "success")
            return redirect(url_for("patient_appointments"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating appointment: {str(e)}", "danger")
            return redirect(url_for("add_patient_appointment"))
    
    # Get doctors (staff with role 'doctor')
    doctors = Staff.query.filter_by(role="doctor").all()
    # Get only nurses for additional staff assignment
    nurses = Staff.query.filter_by(role="nurse").all()
    return render_template("add_appointment_patient.html", doctors=doctors, staff=nurses)

@app.route("/patient/appointments/edit/<int:appointment_id>", methods=["GET", "POST"])
def edit_patient_appointment(appointment_id):
    if session.get("role") != "viewer":
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    patient = Patient.query.filter_by(username=session.get("user")).first()
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("user_login"))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.patient_id != patient.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("patient_appointments"))
    
    if request.method == "POST":
        doctor_id = request.form.get("doctor_id")
        staff_id = request.form.get("staff_id")
        
        # Get doctor information from selected doctor
        doctor = Staff.query.get_or_404(doctor_id)
        appointment.doctor_id = int(doctor_id)
        appointment.doctor_name = doctor.name
        
        if not staff_id or (isinstance(staff_id, str) and staff_id.strip() == ""):
            appointment.staff_id = None
        else:
            appointment.staff_id = int(staff_id) if staff_id else None
        
        try:
            appointment.date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
            appointment.time = request.form.get("time")
            db.session.commit()
            flash("Appointment updated!", "success")
            return redirect(url_for("patient_appointments"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating appointment: {str(e)}", "danger")
            return redirect(url_for("edit_patient_appointment", appointment_id=appointment_id))
    
    doctors = Staff.query.filter_by(role="doctor").all()
    # Get only nurses for additional staff assignment
    nurses = Staff.query.filter_by(role="nurse").all()
    return render_template("edit_appointment_patient.html", appointment=appointment, doctors=doctors, staff=nurses)

@app.route("/patient/appointments/delete/<int:appointment_id>")
def delete_patient_appointment(appointment_id):
    if session.get("role") != "viewer":
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    patient = Patient.query.filter_by(username=session.get("user")).first()
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("user_login"))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.patient_id != patient.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("patient_appointments"))
    
    try:
        db.session.delete(appointment)
        db.session.commit()
        flash("Appointment deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the appointment.", "danger")
    return redirect(url_for("patient_appointments"))

@app.route("/patient/records")
def patient_dashboard_records():
    if session.get("role") != "viewer":
        flash("Access denied.", "danger")
        return redirect(url_for("user_login"))
    patient = Patient.query.filter_by(username=session.get("user")).first()
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("user_login"))
    medical_records = MedicalRecord.query.filter_by(patient_id=patient.id).all()
    return render_template("patient_records.html", patient=patient, medical_records=medical_records)

# -----------------------
# STAFF LOGIN & DASHBOARD
# -----------------------
@app.route("/staff_login", methods=["GET", "POST"])
def staff_login():
    form = StaffLoginForm()
    if form.validate_on_submit():
        staff = Staff.query.filter_by(username=form.username.data).first()
        if staff and check_password_hash(staff.password, form.password.data):
            session['user'] = staff.username
            session['staff_id'] = staff.id
            if staff.role == 'admin':
                session['role'] = 'admin'
                flash("Admin login successful!", "success")
                return redirect(url_for('admin_dashboard'))
            else:
                session['role'] = 'staff'
                flash("Staff login successful!", "success")
                return redirect(url_for('staff_dashboard'))
        flash("Invalid staff credentials", "danger")
    return render_template("staff_login.html", form=form)

@app.route("/staff/dashboard")
def staff_dashboard():
    if session.get("role") != "staff":
        flash("Access denied.", "danger")
        return redirect(url_for("staff_login"))
    staff_id = session.get("staff_id")
    staff_member = Staff.query.get_or_404(staff_id)
    
    # Get appointments based on staff role
    if staff_member.role == "doctor":
        # Doctors see appointments where they are the primary doctor
        appointments = Appointment.query.filter_by(doctor_id=staff_id).all()
    else:  # nurse or other roles
        # Nurses see appointments where they are assigned as additional staff
        appointments = Appointment.query.filter_by(staff_id=staff_id).all()
    
    # Get unique patients for this staff member from their appointments
    patient_ids = [appt.patient_id for appt in appointments]
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []
    
    # Get medical records for all of the staff member's patients
    medical_records = MedicalRecord.query.filter(MedicalRecord.patient_id.in_(patient_ids)).all() if patient_ids else []
    
    return render_template("staff_dashboard.html", staff=staff_member, appointments=appointments, patients=patients, medical_records=medical_records)


@app.route('/staff/appointments/update_status/<int:appointment_id>', methods=['POST'])
def staff_update_appointment_status(appointment_id):
    if session.get('role') != 'staff':
        flash('Access denied.', 'danger')
        return redirect(url_for('staff_login'))
    staff_id = session.get('staff_id')
    staff_member = Staff.query.get_or_404(staff_id)
    appointment = Appointment.query.get_or_404(appointment_id)
    # Check if staff is the doctor or assigned nurse
    has_access = False
    if staff_member.role == "doctor" and appointment.doctor_id == staff_id:
        has_access = True
    elif staff_member.role != "doctor" and appointment.staff_id == staff_id:
        has_access = True
    
    if not has_access:
        flash("You don't have permission to modify this appointment.", 'danger')
        return redirect(url_for('staff_dashboard'))
    # only allow updating status (and optional date/time if provided)
    status = request.form.get('status')
    if status:
        appointment.status = status
    # optional date/time
    date = request.form.get('date')
    time = request.form.get('time')
    if date:
        try:
            appointment.date = datetime.strptime(date, '%Y-%m-%d').date()
        except Exception:
            pass
    if time:
        appointment.time = time
    db.session.commit()
    flash('Appointment updated.', 'success')
    return redirect(url_for('staff_dashboard'))


@app.route('/staff/appointments/delete/<int:appointment_id>', methods=['POST'])
def staff_delete_appointment(appointment_id):
    if session.get('role') != 'staff':
        flash('Access denied.', 'danger')
        return redirect(url_for('staff_login'))
    staff_id = session.get('staff_id')
    staff_member = Staff.query.get_or_404(staff_id)
    appointment = Appointment.query.get_or_404(appointment_id)
    # Check if staff is the doctor or assigned nurse
    has_access = False
    if staff_member.role == "doctor" and appointment.doctor_id == staff_id:
        has_access = True
    elif staff_member.role != "doctor" and appointment.staff_id == staff_id:
        has_access = True
    
    if not has_access:
        flash("You don't have permission to delete this appointment.", 'danger')
        return redirect(url_for('staff_dashboard'))
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted.', 'success')
    return redirect(url_for('staff_dashboard'))

# -----------------------
# STAFF MEDICAL RECORDS ROUTES
# -----------------------
@app.route("/staff/add_medical_record/<int:patient_id>", methods=["GET", "POST"])
def staff_add_medical_record(patient_id):
    if session.get("role") != "staff":
        flash("Access denied.", "danger")
        return redirect(url_for("staff_login"))
    
    staff_id = session.get("staff_id")
    staff_member = Staff.query.get_or_404(staff_id)
    
    # Only doctors can add medical records
    if staff_member.role != "doctor":
        flash("Only doctors can add medical records.", "danger")
        return redirect(url_for("staff_dashboard"))
    
    # Verify this patient is assigned to this doctor
    appointment = Appointment.query.filter_by(patient_id=patient_id, doctor_id=staff_id).first()
    
    if not appointment:
        flash("You don't have access to this patient.", "danger")
        return redirect(url_for("staff_dashboard"))
    
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == "POST":
        diagnosis = request.form.get("diagnosis")
        prescription = request.form.get("prescription")
        lab_result = request.form.get("lab_result")
        
        medical_record = MedicalRecord(
            patient_id=patient_id,
            diagnosis=diagnosis,
            prescription=prescription,
            lab_result=lab_result
        )
        
        db.session.add(medical_record)
        db.session.commit()
        
        flash("Medical record added successfully!", "success")
        return redirect(url_for("staff_dashboard"))
    
    return render_template("staff_add_medical_record.html", patient=patient)

@app.route("/staff/edit_medical_record/<int:record_id>", methods=["GET", "POST"])
def staff_edit_medical_record(record_id):
    if session.get("role") != "staff":
        flash("Access denied.", "danger")
        return redirect(url_for("staff_login"))
    
    staff_id = session.get("staff_id")
    staff_member = Staff.query.get_or_404(staff_id)
    medical_record = MedicalRecord.query.get_or_404(record_id)
    
    # Only doctors can edit medical records
    if staff_member.role != "doctor":
        flash("Only doctors can edit medical records.", "danger")
        return redirect(url_for("staff_dashboard"))
    
    # Verify this patient is assigned to this doctor
    appointment = Appointment.query.filter_by(patient_id=medical_record.patient_id, doctor_id=staff_id).first()
    
    if not appointment:
        flash("You don't have access to this record.", "danger")
        return redirect(url_for("staff_dashboard"))
    
    patient = medical_record.patient
    
    if request.method == "POST":
        medical_record.diagnosis = request.form.get("diagnosis")
        medical_record.prescription = request.form.get("prescription")
        medical_record.lab_result = request.form.get("lab_result")
        
        db.session.commit()
        
        flash("Medical record updated successfully!", "success")
        return redirect(url_for("staff_dashboard"))
    
    return render_template("staff_edit_medical_record.html", medical_record=medical_record, patient=patient)

@app.route("/staff/delete_medical_record/<int:record_id>", methods=["POST"])
def staff_delete_medical_record(record_id):
    if session.get("role") != "staff":
        flash("Access denied.", "danger")
        return redirect(url_for("staff_login"))
    
    staff_id = session.get("staff_id")
    staff_member = Staff.query.get_or_404(staff_id)
    medical_record = MedicalRecord.query.get_or_404(record_id)
    
    # Only doctors can delete medical records
    if staff_member.role != "doctor":
        flash("Only doctors can delete medical records.", "danger")
        return redirect(url_for("staff_dashboard"))
    
    # Verify this patient is assigned to this doctor
    appointment = Appointment.query.filter_by(patient_id=medical_record.patient_id, doctor_id=staff_id).first()
    
    if not appointment:
        flash("You don't have access to this record.", "danger")
        return redirect(url_for("staff_dashboard"))
    
    db.session.delete(medical_record)
    db.session.commit()
    
    flash("Medical record deleted successfully!", "success")
    return redirect(url_for("staff_dashboard"))

# -----------------------
# LOGOUT
# -----------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

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
        specialization = request.form.get("specialization")

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
            role=role,
            specialization=specialization
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
        staff_member.specialization = request.form.get("specialization")

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
    try:
        staff_member = Staff.query.get_or_404(staff_id)
        db.session.delete(staff_member)
        db.session.commit()
        flash("Staff deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting staff.", "danger")
    return redirect(url_for("view_staff"))

# -----------------------
# STARTUP
# -----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not Staff.query.filter_by(username='admin').first():
            admin_user = Staff(
                username='admin',
                name='Administrator',
                password=generate_password_hash('admin01'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
