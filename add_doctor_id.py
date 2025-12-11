"""
Migration script to add doctor_id column to appointment table
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
            # Add the doctor_id column if it doesn't exist
            db.session.execute(text('''
                ALTER TABLE appointment
                ADD COLUMN doctor_id INTEGER
            '''))
            db.session.commit()
            print("✓ Successfully added doctor_id column to appointment table")
            
            # Add foreign key constraint for doctor_id
            db.session.execute(text('''
                ALTER TABLE appointment
                ADD CONSTRAINT appointment_doctor_id_fkey
                FOREIGN KEY (doctor_id) REFERENCES staff(id)
            '''))
            db.session.commit()
            print("✓ Successfully added foreign key constraint for doctor_id")
            
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            if "already exists" in error_msg or "duplicate key" in error_msg:
                print("⚠ Column or constraint already exists (this is OK)")
            else:
                print(f"✗ Error: {e}")
