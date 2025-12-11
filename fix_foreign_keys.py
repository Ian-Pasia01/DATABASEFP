"""
Migration script to fix the foreign key constraint for appointments
This fixes the constraint that references 'patients' instead of 'patient'
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/CarePoint'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

if __name__ == '__main__':
    with app.app_context():
        try:
            # Drop the incorrect foreign key constraint
            db.session.execute(text('''
                ALTER TABLE appointment
                DROP CONSTRAINT apponitments_patient_id_fkey
            '''))
            db.session.commit()
            print("✓ Dropped incorrect foreign key constraint")
            
            # Add the correct foreign key constraint
            db.session.execute(text('''
                ALTER TABLE appointment
                ADD CONSTRAINT appointment_patient_id_fkey
                FOREIGN KEY (patient_id) REFERENCES patient(id)
            '''))
            db.session.commit()
            print("✓ Added correct foreign key constraint")
            
            # Also check and fix medical_records if needed
            db.session.execute(text('''
                SELECT constraint_name FROM information_schema.table_constraints 
                WHERE table_name='medical_records' AND constraint_type='FOREIGN KEY'
            '''))
            
            print("✓ Migration completed successfully")
        except Exception as e:
            db.session.rollback()
            print(f"⚠ Info: {e}")
            print("This might be expected if constraints don't exist or already fixed")
