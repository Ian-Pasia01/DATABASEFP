from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/CarePoint'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create all tables
with app.app_context():
    db.create_all()

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    password = db.Column(db.String(200), nullable=False)  # In production, hash passwords!

    def __repr__(self):
        return f'<Patient {self.full_name}>'

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        # Handle admin login logic here
        username = request.form.get("username")
        password = request.form.get("password")
        # For now, just redirect to home (implement authentication later)
        return redirect(url_for("home"))
    return render_template("admin_login.html")

@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        # Handle user login logic here
        username = request.form.get("username")
        password = request.form.get("password")
        # For now, just redirect to home (implement authentication later)
        return redirect(url_for("home"))
    return render_template("user_login.html")

@app.route("/user/signup", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        address = request.form.get("address")
        gender = request.form.get("gender")
        date_of_birth_str = request.form.get("date_of_birth")
        password = request.form.get("password")

        date_of_birth = None
        if date_of_birth_str:
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

        new_patient = Patient(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            address=address,
            gender=gender,
            date_of_birth=date_of_birth,
            password=password  # In production, hash this!
        )
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("user_signup.html")

if __name__ == "__main__":
    app.run(debug=True)
