"""
Migration script to fix the foreign key constraint for medical_records
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
            # Drop the incorrect foreign key constraint for medical_records
            db.session.execute(text('''
                ALTER TABLE medical_records
                DROP CONSTRAINT medical_records_patient_id_fkey
            '''))
            db.session.commit()
            print("✓ Dropped incorrect foreign key constraint for medical_records")
            
            # Add the correct foreign key constraint
            db.session.execute(text('''
                ALTER TABLE medical_records
                ADD CONSTRAINT medical_records_patient_id_fkey
                FOREIGN KEY (patient_id) REFERENCES patient(id)
            '''))
            db.session.commit()
            print("✓ Added correct foreign key constraint for medical_records")
            
            print("✓ Migration completed successfully")
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            if "already exists" in error_msg or "duplicate key" in error_msg:
                print("⚠ Constraint already exists or was already fixed (this is OK)")
            else:
                print(f"⚠ Info: {e}")
