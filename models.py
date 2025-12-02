class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    password = db.Column(db.String(200), nullable=False)  # Password should be hashed for security

    def __repr__(self):
        return f'<Patient {self.full_name}>'
=======
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    password = db.Column(db.String(200), nullable=False)  # Password should be hashed for security

    def __repr__(self):
        return f'<Patient {self.full_name}>'
=======

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
>>>>>>> 5d5b58595dc080e871b640fed38ae6d74734e1f5
