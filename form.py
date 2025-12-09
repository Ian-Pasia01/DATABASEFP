from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange



class LoginForm(FlaskForm):
    username = StringField(
        "Username",  # Label that shows up next to the box
        validators=[DataRequired()]  # Makes sure the user doesn’t leave it empty
    )
    password = PasswordField(
        "Password",  # Label for password box
        validators=[DataRequired()]  # Cannot be empty
    )
    submit = SubmitField("Login")  # The button that says "Login"

class AdminLog(FlaskForm):
    AdminUser = StringField(
        "AdminUser",
        validators=[DataRequired()]
    )
    passw = PasswordField(
        "Pass",  # Label for password box
        validators=[DataRequired()]  # Cannot be empty
    )
    submit = SubmitField("Login")  # The button that says "Login"




class AppointmentForm(FlaskForm):
    patient_id = SelectField(
        "Patient",
        coerce=int,  # ensures patient_id is an integer
        validators=[DataRequired()]
    )
    doctor_name = StringField(
        "Doctor Name",
        validators=[DataRequired()]
    )
    date = StringField(
        "Date (YYYY-MM-DD)",
        validators=[DataRequired()]
    )
    time = StringField(
        "Time (HH:MM)",
        validators=[DataRequired()]
    )
    submit = SubmitField("Book Appointment")

class StaffLoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()]
    )
    password = PasswordField(
        "Password",
    )

class StaffLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")