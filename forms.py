from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional, Regexp
import re
from models import User
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            print(f"Registration attempted with existing email: {email.data}")
            raise ValidationError(f'Email "{email.data}" is already registered. Please try logging in or use a different email.')

class ServiceForm(FlaskForm):
    title = StringField('Service Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    icon = StringField('Icon Class (e.g., bi bi-code)', validators=[DataRequired(), Length(max=50)])

class InternshipForm(FlaskForm):
    title = StringField('Internship Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    duration = StringField('Duration (e.g., 3 months)', validators=[DataRequired(), Length(max=50)])
    stipend = StringField('Stipend (e.g., $500/month)', validators=[Length(max=50)])
    requirements = TextAreaField('Requirements')

class ApplicationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    college = StringField('College/University', validators=[Length(max=100)])
    graduation_year = IntegerField('Graduation Year', validators=[Optional(), NumberRange(min=2000, max=2100)])
    resume = FileField('Resume (PDF, DOC, DOCX)', validators=[FileAllowed(['pdf', 'doc', 'docx'])])
    cover_letter = TextAreaField('Cover Letter')

class CertificateForm(FlaskForm):
    recipient_name = StringField('Recipient Name', validators=[DataRequired(), Length(max=100)])
    certificate_type = SelectField('Certificate Type', choices=[
        ('internship', 'Internship Certificate'),
        ('work_experience', 'Work Experience Certificate')
    ], validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired(), Length(max=100)])
    duration = StringField('Duration (e.g., 3 months)', validators=[DataRequired(), Length(max=50)])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    
    def validate_end_date(self, end_date):
        if end_date.data < self.start_date.data:
            raise ValidationError('End date must be after start date.')
        
        if end_date.data > datetime.now().date():
            raise ValidationError('End date cannot be in the future.')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=2, max=100),
        Regexp(r'^[a-zA-Z\s]*$', message="Name can only contain letters and spaces")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(min=5, max=150),
        Regexp(r'^[a-zA-Z0-9\s\-_.,!?]*$', message="Subject contains invalid characters")
    ])
    message = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=10, max=2000)
    ])

class TestimonialForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    position = StringField('Position', validators=[Length(max=100)])
    company = StringField('Company', validators=[Length(max=100)])
    content = TextAreaField('Testimonial', validators=[DataRequired()])
    image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    is_featured = BooleanField('Featured on Homepage')