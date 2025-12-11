"""
Script to check database integrity and fix foreign key issues
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Patient, Appointment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/CarePoint'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        try:
            # Check all patients in database
            patients = Patient.query.all()
            print(f"✓ Found {len(patients)} patients in database:")
            for patient in patients:
                print(f"  - ID: {patient.id}, Username: {patient.username}, Name: {patient.full_name}")
            
            # Check for orphaned appointments (appointments with non-existent patient IDs)
            print("\nChecking for orphaned appointments...")
            appointments = Appointment.query.all()
            patient_ids = [p.id for p in patients]
            
            orphaned_count = 0
            for appt in appointments:
                if appt.patient_id not in patient_ids:
                    print(f"✗ Found orphaned appointment: ID {appt.id}, patient_id {appt.patient_id}")
                    orphaned_count += 1
            
            if orphaned_count == 0:
                print("✓ No orphaned appointments found")
            else:
                print(f"\n⚠ Found {orphaned_count} orphaned appointment(s)")
                
        except Exception as e:
            print(f"✗ Error: {e}")
