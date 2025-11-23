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