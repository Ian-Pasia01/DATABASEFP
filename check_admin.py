from app import app
from models import db, User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("Admin exists")
    else:
        print("Admin does not exist")
