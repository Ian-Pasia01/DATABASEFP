import os
from app import app, db
from models import Appointment, Staff

with app.app_context():
    print("\n=== UPDATING APPOINTMENT ===\n")
    
    # Get the appointment
    appt = Appointment.query.get(1)
    
    if appt:
        print(f"Original appointment:")
        print(f"  Patient ID: {appt.patient_id}")
        print(f"  Staff ID: {appt.staff_id}")
        print(f"  Doctor Name: {appt.doctor_name}\n")
        
        # Get the doctor by name to find their staff ID
        doctor = Staff.query.filter_by(name=appt.doctor_name).first()
        
        if doctor:
            print(f"Found doctor: {doctor.name} (Staff ID: {doctor.id})\n")
            
            # Update the appointment to assign it to the correct doctor
            appt.staff_id = doctor.id
            db.session.commit()
            
            print(f"Updated appointment:")
            print(f"  Patient ID: {appt.patient_id}")
            print(f"  Staff ID: {appt.staff_id}")
            print(f"  Doctor Name: {appt.doctor_name}\n")
            print("✓ Appointment updated successfully!")
        else:
            print(f"✗ Could not find doctor with name: {appt.doctor_name}")
    else:
        print("✗ Appointment not found")
