from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()



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




class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="staff")  # e.g., 'doctor', 'nurse', etc.
    specialization = db.Column(db.String(100), nullable=True)  # e.g., 'Cardiology', 'Pediatrics', etc.

    # Relationship for appointments where this staff is the doctor
    appointments = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', backref='doctor', lazy=True)
    # Relationship for appointments where this staff is additional staff (nurse)
    additional_appointments = db.relationship('Appointment', foreign_keys='Appointment.staff_id', backref='additional_staff', lazy=True)

    def __repr__(self):
        return f"<Staff {self.name} - {self.specialization}>"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)  # Primary doctor assigned to appointment
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)  # Additional staff (nurse)
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


    

