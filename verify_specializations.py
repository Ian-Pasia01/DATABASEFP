from flask import Flask
from models import db, Staff

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/CarePoint'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    staff_members = Staff.query.all()
    print("Current Staff Members and Specializations:")
    for staff in staff_members:
        print(f"ID: {staff.id}, Name: {staff.name}, Role: {staff.role}, Specialization: '{staff.specialization}'")
        if not staff.specialization:
            print(f"  WARNING: Staff {staff.name} has no specialization!")
