from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from form import LoginForm, AdminLog
from models import db, User, Patient
from datetime import datetime

app = Flask(__name__)

@app.route('/patient_dashboard')
def patient_dashboard():
    if session.get('role') not in ['viewer', 'patient']:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    return render_template('patient_dashboard.html')


app.config['SECRET_KEY'] = 'sikretongmalupet' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/CarePoint'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




db.init_app(app)

# Create all tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        # Handle user login logic here
        username = request.form.get("username")
        password = request.form.get("password")
        # For now, just redirect to home (implement authentication later)
        return redirect(url_for("home"))
    return render_template("user_login.html")
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  

    if form.validate_on_submit():
        
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            session['user'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success') 
            
            
            if session['role'] == 'viewer':
                return redirect(url_for('user_login'))  
            elif session['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))  
        else:
            flash('Invalid credentials', 'danger')
    
    
    return render_template('login.html', form=form, title='Login')


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    # Since admin login handled in /login, redirect all attempts to login
    return redirect(url_for('login'))


@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_login'))

    logs = Patient.query.all()
    return render_template('admin_dashboard.html', logs=logs)




from werkzeug.security import generate_password_hash

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
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

        new_patient = Patient(
            username=username,
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            address=address,
            gender=gender,
            date_of_birth=date_of_birth,
            country_origin=country_origin,
            password=generate_password_hash(password)  # Hash password securely
        )
        db.session.add(new_patient)

        # Create corresponding User record for authentication
        new_user = User(
            username=username,  # Use username as username
            password=generate_password_hash(password),
            role='viewer'  # Assign role 'viewer' to patients
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("user_signup.html")

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

        # If there’s no admin or viewer user yet, create them automatically
        if not User.query.filter_by(username='admin').first():
            admin1 = User(username='admin', password=generate_password_hash('admin01'), role='admin')
            db.session.add_all([admin1])
            db.session.commit()

    app.run(debug=True)
