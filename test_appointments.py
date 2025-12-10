import os
from app import app, db
from models import Appointment, Staff, Patient

with app.app_context():
    print("\n=== CHECKING APPOINTMENTS ===\n")
    
    # Get all appointments
    appointments = Appointment.query.all()
    print(f"Total appointments in database: {len(appointments)}\n")
    
    # Display each appointment
    for appt in appointments:
        print(f"Appointment ID: {appt.id}")
        print(f"  Patient ID: {appt.patient_id}")
        print(f"  Staff ID: {appt.staff_id}")
        print(f"  Doctor Name: {appt.doctor_name}")
        print(f"  Date: {appt.date}")
        print(f"  Time: {appt.time}")
        print(f"  Status: {appt.status}")
        print()
    
    # Check all staff members
    print("\n=== CHECKING STAFF MEMBERS ===\n")
    staff_members = Staff.query.all()
    print(f"Total staff members: {len(staff_members)}\n")
    
    for staff in staff_members:
        print(f"Staff ID: {staff.id}, Name: {staff.name}, Role: {staff.role}, Username: {staff.username}")
        # Check appointments for this staff member
        staff_appointments = Appointment.query.filter_by(staff_id=staff.id).all()
        print(f"  Appointments assigned to this staff: {len(staff_appointments)}")
        print()
