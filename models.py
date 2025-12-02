from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password =db.Column(db.String(200), nullable = False)    
    role = db.Column(db.String(10), nullable=False)


class patient(db.Model):
    Patient_Id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(100), nullable=False)
    Name = db.Column(db.String(100), nullable=False)
    Gender = db.Column(db.String(10), nullable=False)
    Address = db.Column(db.Text, nullable=False)
    Contact_Number = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Date_of_Creation = db.Column(db.Date, nullable=True)
    Date_of_Birth= db.Column(db.Date, nullable=True) 
    Country_Origin = db.Column(db.String(100), nullable=False)  # In production, hash passwords!

    def __repr__(self):
        return f'<Patient {self.Username}>'


     # In production, hash passwords!
