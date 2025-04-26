from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt
import time
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    profile_pic = db.Column(db.String(120), default='default.jpg')
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with certificates
    certificates = db.relationship('Certificate', backref='issuer', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Service {self.title}>'

class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(50), nullable=False)  # e.g., "3 months", "6 months"
    stipend = db.Column(db.String(50))
    requirements = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with applications
    applications = db.relationship('Application', backref='internship', lazy='dynamic')
    
    def __repr__(self):
        return f'<Internship {self.title}>'

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    college = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    resume_filename = db.Column(db.String(100))
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), nullable=False)
    
    # Relationship with certificates
    certificate = db.relationship('Certificate', backref='application', uselist=False)
    
    def __repr__(self):
        return f'<Application {self.applicant_name} for {self.internship.title}>'

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(50), unique=True, nullable=False)
    recipient_name = db.Column(db.String(100), nullable=False)
    certificate_type = db.Column(db.String(20), nullable=False)  # internship, work_experience
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    position = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50), nullable=False)  # e.g., "3 months"
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    qr_code_path = db.Column(db.String(150))
    
    # Foreign keys
    issuer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    
    def generate_verification_token(self, expires_in=31536000):  # 1 year default expiry
        payload = {
            'cert_id': self.certificate_id,
            'recipient': self.recipient_name,
            'iat': int(time.time()),
            'exp': int(time.time()) + expires_in
        }
        token = jwt.encode(
            payload,
            os.environ.get('SECRET_KEY', 'dev_key'),
            algorithm='HS256'
        )
        return token
    
    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(
                token,
                os.environ.get('SECRET_KEY', 'dev_key'),
                algorithms=['HS256']
            )
            return Certificate.query.filter_by(certificate_id=payload['cert_id']).first()
        except:
            return None
    
    def __repr__(self):
        return f'<Certificate {self.certificate_id} for {self.recipient_name}>'

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    company = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), default='default-profile.jpg')
    is_featured = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Testimonial from {self.name}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Contact from {self.name}>'