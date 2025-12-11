"""
Script to verify patient 2 exists and check appointment constraints
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Patient, Appointment, Staff

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/CarePoint'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        try:
            # Check if patient 2 exists
            patient2 = Patient.query.get(2)
            if patient2:
                print(f"✓ Patient 2 exists: {patient2.full_name}")
            else:
                print("✗ Patient 2 does not exist")
            
            # List all patients with their IDs
            print("\nAll patients:")
            patients = Patient.query.all()
            for p in patients:
                print(f"  ID: {p.id}, Username: {p.username}, Name: {p.full_name}")
            
            # Try to create an appointment for patient 2
            if patient2:
                doctor = Staff.query.filter_by(role="doctor").first()
                if doctor:
                    print(f"\nTesting appointment creation with doctor: {doctor.name}")
                    test_appt = Appointment(
                        patient_id=2,
                        staff_id=None,
                        doctor_name=doctor.name,
                        date="2025-12-15",
                        time="10:00",
                        status="Pending"
                    )
                    db.session.add(test_appt)
                    db.session.commit()
                    print("✓ Test appointment created successfully")
                    # Delete it
                    db.session.delete(test_appt)
                    db.session.commit()
                    print("✓ Test appointment deleted")
                else:
                    print("✗ No doctors found")
            else:
                print("✗ Cannot test - patient 2 does not exist")
                
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error: {type(e).__name__}: {e}")
