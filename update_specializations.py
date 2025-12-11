from flask import Flask
from models import db, Staff

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/CarePoint'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Update specializations based on user input
    specializations = {
        9: 'Dentist',
        6: 'Registered Nurse',
        4: 'Family Medicine',
        7: 'Pediatrician',
        5: 'Dentist',
        8: 'Family Medicine'
    }

    for staff_id, specialization in specializations.items():
        staff = Staff.query.get(staff_id)
        if staff:
            staff.specialization = specialization
            print(f"Updated {staff.name} (ID: {staff_id}) with specialization: {specialization}")
        else:
            print(f"Staff with ID {staff_id} not found")

    db.session.commit()
    print("All specializations updated successfully!")
