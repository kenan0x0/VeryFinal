from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from MFA.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)],render_kw={"placeholder": "User Name"})
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder": "Email"})
    phone = StringField('Phone Number', validators=[Length(min=10,max=10),DataRequired()],render_kw={"placeholder": "Phone Number in this form : 0611111111"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('That phone is already used. Please choose a different phone number.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "E-mail"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class QRForm(FlaskForm):
    key = StringField('key', validators=[DataRequired()], render_kw={"placeholder": "Scan and Insert Key"})
    submit = SubmitField('Further')

class SMSForm(FlaskForm):
    key1 = StringField('key1', validators=[DataRequired()], render_kw={"placeholder": "Insert code recieved per SMS"})
    submit = SubmitField('Further')

class ResetForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()], render_kw={"placeholder": "Enter Your Email Address"})
    submit = SubmitField('Send reset link')

class ResetPWForm(FlaskForm):
    passwd = PasswordField('passwd', validators=[DataRequired()], render_kw={"placeholder": "New Password"})
    submit = SubmitField('Reset')
