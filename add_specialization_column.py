"""
Migration script to add specialization column to staff table
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
            # Add the specialization column if it doesn't exist
            db.session.execute(text('''
                ALTER TABLE staff
                ADD COLUMN specialization VARCHAR(100)
            '''))
            db.session.commit()
            print("✓ Successfully added specialization column to staff table")
        except Exception as e:
            print(f"✗ Error: {e}")
            db.session.rollback()
