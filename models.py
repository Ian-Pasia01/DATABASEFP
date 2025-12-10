from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()



class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)

class Patient(db.Model):
    __tablename__ = "patient"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    blood_type = db.Column(db.String(5))
    height = db.Column(db.String(20))   # height as string
    age = db.Column(db.Integer)
    country_origin = db.Column(db.String(50))
    password = db.Column(db.String(200), nullable=False)  # hashed password

    appointments = db.relationship('Appointment', backref='patient', lazy=True)

    def __repr__(self):
        return f"<Patient {self.full_name}>"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(125), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="staff")  # e.g., 'doctor', 'nurse', etc.

    appointments = db.relationship('Appointment', backref='staff', lazy=True)

    def __repr__(self):
        return f"<Staff {self.name}>"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    doctor_name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="Pending")


class MedicalRecord(db.Model):
    __tablename__ = "medical_records"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    lab_result = db.Column(db.Text)
    record_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationship back to Patient
    patient = db.relationship('Patient', backref='medical_records', lazy=True)

    def __repr__(self):
        return f"<MedicalRecord {self.id} for Patient {self.patient_id}>"


    

