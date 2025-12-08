import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Patient, Admin
from form import LoginForm, AdminLog

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


# -----------------------
# ADMIN LOGIN
# -----------------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    form = AdminLog()

    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.AdminUser.data).first()

        if admin and check_password_hash(admin.password, form.passw.data):
            session['user'] = admin.username
            session['role'] = 'admin'

            flash("Admin login successful!", "success")
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
    return render_template("admin_dashboard.html", patients=patients)





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

        patient.country_origin = request.form.get("country_origin")

        db.session.commit()

        flash("Patient updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_patient.html", patient=patient)


# -----------------------
# USER SIGNUP
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
        country_origin = request.form.get("country_origin")
        password = request.form.get("password")

        date_of_birth = None
        if date_of_birth_str:
            date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()

        # Add patient
        new_patient = Patient(
            username=username,
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            address=address,
            gender=gender,
            date_of_birth=date_of_birth,
            country_origin=country_origin,
            password=generate_password_hash(password)
        )
        db.session.add(new_patient)

        # Create login credentials
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role="viewer"
        )
        db.session.add(new_user)

        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for("home"))

    return render_template("user_signup.html")


# -----------------------
# USER LOGIN (VIEWER)
# -----------------------
@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            session["role"] = user.role

            flash("Login successful!", "success")
            if user.role == "viewer":
                return redirect(url_for("patient_dashboard"))
            else:
                return redirect(url_for("admin_dashboard"))

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
    return render_template("patient_dashboard.html")


# -----------------------
# LOGOUT
# -----------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))


# -----------------------
# STARTUP (DB CREATE)
# -----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Auto-create admin login if not exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password=generate_password_hash('admin01'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()

    app.run(debug=True)
    