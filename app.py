import os
import secrets
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import os.path

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def handle_db_error(e):
    db.session.rollback()
    flash('An error occurred. Please try again.', 'danger')
    logger.error(f"Database error: {str(e)}")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
# Use Replit's persistent key-value store for production
if os.environ.get('REPLIT_DB_URL'):
    from replit import db as replit_db
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///itservices.db"  # Keep SQLite for development
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///itservices.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Create upload folders if they don't exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'certificates'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'qrcodes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'signatures'), exist_ok=True)

# Import models after app is created to avoid circular imports
from models import User, Service, Internship, Application, Certificate, Testimonial, Contact
from forms import (LoginForm, RegistrationForm, ServiceForm, InternshipForm, 
                  ApplicationForm, CertificateForm, ContactForm, TestimonialForm)

# Add template context processor for current datetime
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    if not filename:
        return False
    if '/' in filename or '\\' in filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'] and \
           len(filename) < 200

def generate_certificate_image(certificate):
    # Create certificate image
    width, height = 1000, 750
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype('static/fonts/Montserrat-Bold.ttf', 40)
        main_font = ImageFont.truetype('static/fonts/Montserrat-Regular.ttf', 24)
        name_font = ImageFont.truetype('static/fonts/Montserrat-Bold.ttf', 36)
    except:
        # Use default font if custom fonts not available
        title_font = ImageFont.load_default()
        main_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
    
    # Draw border
    d.rectangle([(25, 25), (width-25, height-25)], outline=(0, 91, 187), width=3)
    
    # Draw certificate title
    cert_type = "INTERNSHIP CERTIFICATE" if certificate.certificate_type == "internship" else "WORK EXPERIENCE CERTIFICATE"
    title_width = d.textlength(cert_type, title_font)
    d.text(((width-title_width)/2, 60), cert_type, fill=(0, 91, 187), font=title_font)
    
    # Draw logo if exists
    try:
        logo = Image.open('static/img/logo.png')
        logo = logo.resize((150, 150))
        img.paste(logo, (width//2-75, 120), logo if logo.mode == 'RGBA' else None)
    except:
        # Draw a placeholder for the logo if it doesn't exist
        d.rectangle([(width//2-75, 120), (width//2+75, 270)], outline=(200, 200, 200))
        d.text((width//2-50, 180), "LOGO", fill=(200, 200, 200), font=main_font)
    
    # Certificate text
    d.text((100, 300), "This is to certify that", fill=(0, 0, 0), font=main_font)
    
    # Recipient name
    name_width = d.textlength(certificate.recipient_name, name_font)
    d.text(((width-name_width)/2, 350), certificate.recipient_name, fill=(0, 0, 0), font=name_font)
    
    # Certificate details
    details = f"has successfully completed {certificate.duration} of {certificate.position} "
    details_width = d.textlength(details, main_font)
    d.text(((width-details_width)/2, 420), details, fill=(0, 0, 0), font=main_font)
    
    details2 = f"from {certificate.start_date.strftime('%d %B, %Y')} to {certificate.end_date.strftime('%d %B, %Y')}"
    details2_width = d.textlength(details2, main_font)
    d.text(((width-details2_width)/2, 460), details2, fill=(0, 0, 0), font=main_font)
    
    # Draw issuer's signature if exists
    try:
        signature = Image.open(f"static/uploads/signatures/{certificate.issuer.username}.png")
        signature = signature.resize((150, 100))
        img.paste(signature, (150, 520), signature if signature.mode == 'RGBA' else None)
    except:
        d.rectangle([(150, 520), (300, 570)], outline=(200, 200, 200))
        d.text((180, 540), "SIGNATURE", fill=(200, 200, 200), font=main_font)
    
    # Issuer details
    d.text((150, 590), f"Issuer: {certificate.issuer.username}", fill=(0, 0, 0), font=main_font)
    d.text((150, 620), f"Date: {certificate.issue_date.strftime('%d %B, %Y')}", fill=(0, 0, 0), font=main_font)
    
    # Certificate ID and verification instructions
    d.text((550, 590), f"Certificate ID: {certificate.certificate_id}", fill=(0, 0, 0), font=main_font)
    d.text((550, 620), "Verify at: " + request.host_url + "verify", fill=(0, 0, 0), font=main_font)
    
    # Generate QR code
    verification_url = request.host_url + f"verify/{certificate.certificate_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((120, 120))
    
    # Paste QR code onto certificate
    img.paste(qr_img, (width-170, 500))
    
    # Save QR code separately
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], 'qrcodes', f"{certificate.certificate_id}.png")
    qr_img.save(qr_path)
    
    # Update certificate with QR code path
    certificate.qr_code_path = f"qrcodes/{certificate.certificate_id}.png"
    db.session.commit()
    
    # Save certificate image
    cert_path = os.path.join(app.config['UPLOAD_FOLDER'], 'certificates', f"{certificate.certificate_id}.png")
    img.save(cert_path)
    
    return cert_path

# Routes
@app.route('/')
def index():
    services = Service.query.filter_by(is_active=True).all()
    testimonials = Testimonial.query.filter_by(is_featured=True).all()
    return render_template('index.html', services=services, testimonials=testimonials)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    services = Service.query.filter_by(is_active=True).all()
    return render_template('services.html', services=services)

@app.route('/internships')
def internships():
    internships = Internship.query.filter_by(is_active=True).all()
    return render_template('internships.html', internships=internships)

@app.route('/internship/<int:internship_id>')
def internship_detail(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    form = ApplicationForm()
    return render_template('internship_detail.html', internship=internship, form=form)

@app.route('/apply/<int:internship_id>', methods=['GET', 'POST'])
def apply(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    form = ApplicationForm()
    
    if form.validate_on_submit():
        # Handle resume upload
        resume_file = form.resume.data
        resume_filename = None
        
        if resume_file and allowed_file(resume_file.filename):
            # Secure the filename and save the file
            resume_filename = secure_filename(f"{form.name.data}_{internship.title}_{secrets.token_hex(8)}.{resume_file.filename.rsplit('.', 1)[1].lower()}")
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', resume_filename)
            resume_file.save(resume_path)
        
        # Create application
        application = Application(
            applicant_name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            college=form.college.data,
            graduation_year=form.graduation_year.data,
            resume_filename=resume_filename,
            cover_letter=form.cover_letter.data,
            internship=internship
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash('Your application has been submitted successfully!', 'success')
        return redirect(url_for('internships'))
    
    return render_template('application_form.html', form=form, internship=internship)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    
    if form.validate_on_submit():
        contact = Contact(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        
        db.session.add(contact)
        db.session.commit()
        
        flash('Your message has been sent. We will get back to you soon!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', form=form)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        certificate_id = request.form.get('certificate_id')
        if certificate_id:
            certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()
            if certificate:
                return redirect(url_for('verify_certificate', certificate_id=certificate_id))
            else:
                flash('Invalid certificate ID. Please try again.', 'danger')
    
    return render_template('verify.html')

@app.route('/verify/<certificate_id>')
def verify_certificate(certificate_id):
    certificate = Certificate.query.filter_by(certificate_id=certificate_id).first_or_404()
    return render_template('verify_certificate.html', certificate=certificate)

@app.route('/certificate/<certificate_id>')
def view_certificate(certificate_id):
    certificate = Certificate.query.filter_by(certificate_id=certificate_id).first_or_404()
    
    # Generate or get certificate image path
    cert_path = os.path.join(app.config['UPLOAD_FOLDER'], 'certificates', f"{certificate.certificate_id}.png")
    
    if not os.path.exists(cert_path):
        cert_path = generate_certificate_image(certificate)
    
    return send_file(cert_path, as_attachment=False)

@app.route('/download/<certificate_id>')
def download_certificate(certificate_id):
    certificate = Certificate.query.filter_by(certificate_id=certificate_id).first_or_404()
    
    # Generate or get certificate image path
    cert_path = os.path.join(app.config['UPLOAD_FOLDER'], 'certificates', f"{certificate.certificate_id}.png")
    
    if not os.path.exists(cert_path):
        cert_path = generate_certificate_image(certificate)
    
    return send_file(cert_path, as_attachment=True, download_name=f"Certificate_{certificate.recipient_name}_{certificate.certificate_id}.png")

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# Admin routes
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    applications_count = Application.query.filter_by(status='pending').count()
    certificates_count = Certificate.query.count()
    users_count = User.query.count()
    messages_count = Contact.query.filter_by(is_read=False).count()
    
    return render_template('admin/dashboard.html', 
                          applications_count=applications_count,
                          certificates_count=certificates_count,
                          users_count=users_count,
                          messages_count=messages_count)

@app.route('/admin/applications')
@login_required
def admin_applications():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    applications = Application.query.order_by(Application.date_applied.desc()).all()
    return render_template('admin/applications.html', applications=applications)

@app.route('/admin/applications/<int:application_id>')
@login_required
def view_application(application_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    application = Application.query.get_or_404(application_id)
    return render_template('admin/view_application.html', application=application)

@app.route('/admin/applications/<int:application_id>/update_status/<status>')
@login_required
def update_application_status(application_id, status):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    application = Application.query.get_or_404(application_id)
    application.status = status
    db.session.commit()
    
    flash(f'Application status updated to {status}.', 'success')
    return redirect(url_for('view_application', application_id=application_id))

@app.route('/admin/certificates')
@login_required
def admin_certificates():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    certificates = Certificate.query.order_by(Certificate.issue_date.desc()).all()
    return render_template('admin/certificates.html', certificates=certificates)

@app.route('/admin/generate_certificate/<int:application_id>', methods=['GET', 'POST'])
@login_required
def generate_certificate(application_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    application = Application.query.get_or_404(application_id)
    form = CertificateForm()
    
    if form.validate_on_submit():
        # Generate unique certificate ID
        certificate_id = f"CERT-{secrets.token_hex(6).upper()}"
        
        # Create certificate
        certificate = Certificate(
            certificate_id=certificate_id,
            recipient_name=application.applicant_name,
            certificate_type=form.certificate_type.data,
            position=form.position.data,
            duration=form.duration.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            valid_until=datetime.utcnow() + timedelta(days=365*10),  # Valid for 10 years
            issuer=current_user,
            application=application
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        # Generate certificate image
        generate_certificate_image(certificate)
        
        flash('Certificate has been generated successfully.', 'success')
        return redirect(url_for('admin_certificates'))
    
    # Pre-fill the form with application data
    form.recipient_name.data = application.applicant_name
    
    return render_template('admin/generate_certificate.html', form=form, application=application)

@app.route('/admin/services', methods=['GET', 'POST'])
@login_required
def admin_services():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = ServiceForm()
    
    if form.validate_on_submit():
        service = Service(
            title=form.title.data,
            description=form.description.data,
            icon=form.icon.data,
            is_active=True
        )
        
        db.session.add(service)
        db.session.commit()
        
        flash('New service has been added.', 'success')
        return redirect(url_for('admin_services'))
    
    services = Service.query.all()
    return render_template('admin/services.html', services=services, form=form)

@app.route('/admin/service/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    service = Service.query.get_or_404(service_id)
    form = ServiceForm()
    
    if form.validate_on_submit():
        service.title = form.title.data
        service.description = form.description.data
        service.icon = form.icon.data
        
        db.session.commit()
        
        flash('Service has been updated.', 'success')
        return redirect(url_for('admin_services'))
    
    # Pre-fill the form with service data
    if request.method == 'GET':
        form.title.data = service.title
        form.description.data = service.description
        form.icon.data = service.icon
    
    return render_template('admin/edit_service.html', form=form, service=service)

@app.route('/admin/service/<int:service_id>/toggle')
@login_required
def toggle_service(service_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    service = Service.query.get_or_404(service_id)
    service.is_active = not service.is_active
    db.session.commit()
    
    status = "activated" if service.is_active else "deactivated"
    flash(f'Service has been {status}.', 'success')
    return redirect(url_for('admin_services'))

@app.route('/admin/internships', methods=['GET', 'POST'])
@login_required
def admin_internships():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = InternshipForm()
    
    if form.validate_on_submit():
        internship = Internship(
            title=form.title.data,
            description=form.description.data,
            duration=form.duration.data,
            stipend=form.stipend.data,
            requirements=form.requirements.data,
            is_active=True
        )
        
        db.session.add(internship)
        db.session.commit()
        
        flash('New internship opportunity has been added.', 'success')
        return redirect(url_for('admin_internships'))
    
    internships = Internship.query.all()
    return render_template('admin/internships.html', internships=internships, form=form)

@app.route('/admin/internship/<int:internship_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_internship(internship_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    internship = Internship.query.get_or_404(internship_id)
    form = InternshipForm()
    
    if form.validate_on_submit():
        internship.title = form.title.data
        internship.description = form.description.data
        internship.duration = form.duration.data
        internship.stipend = form.stipend.data
        internship.requirements = form.requirements.data
        
        db.session.commit()
        
        flash('Internship opportunity has been updated.', 'success')
        return redirect(url_for('admin_internships'))
    
    # Pre-fill the form with internship data
    if request.method == 'GET':
        form.title.data = internship.title
        form.description.data = internship.description
        form.duration.data = internship.duration
        form.stipend.data = internship.stipend
        form.requirements.data = internship.requirements
    
    return render_template('admin/edit_internship.html', form=form, internship=internship)

@app.route('/admin/internship/<int:internship_id>/toggle')
@login_required
def toggle_internship(internship_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    internship = Internship.query.get_or_404(internship_id)
    internship.is_active = not internship.is_active
    db.session.commit()
    
    status = "activated" if internship.is_active else "deactivated"
    flash(f'Internship opportunity has been {status}.', 'success')
    return redirect(url_for('admin_internships'))

@app.route('/admin/messages')
@login_required
def admin_messages():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    messages = Contact.query.order_by(Contact.date_sent.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/message/<int:message_id>')
@login_required
def view_message(message_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    message = Contact.query.get_or_404(message_id)
    
    # Mark the message as read
    if not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return render_template('admin/view_message.html', message=message)

@app.route('/admin/testimonials', methods=['GET', 'POST'])
@login_required
def admin_testimonials():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = TestimonialForm()
    
    if form.validate_on_submit():
        # Handle image upload
        image_filename = 'default-profile.jpg'
        if form.image.data:
            # Save the image
            image_file = form.image.data
            image_filename = secure_filename(f"{form.name.data}_{secrets.token_hex(8)}.{image_file.filename.rsplit('.', 1)[1].lower()}")
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', image_filename)
            image_file.save(image_path)
        
        testimonial = Testimonial(
            name=form.name.data,
            position=form.position.data,
            company=form.company.data,
            content=form.content.data,
            image=image_filename,
            is_featured=form.is_featured.data
        )
        
        db.session.add(testimonial)
        db.session.commit()
        
        flash('New testimonial has been added.', 'success')
        return redirect(url_for('admin_testimonials'))
    
    testimonials = Testimonial.query.all()
    return render_template('admin/testimonials.html', testimonials=testimonials, form=form)

@app.route('/admin/signature', methods=['GET', 'POST'])
@login_required
def admin_signature():
    if request.method == 'POST':
        if 'signature' in request.files:
            signature_file = request.files['signature']
            if signature_file and allowed_file(signature_file.filename):
                # Save the signature
                signature_filename = secure_filename(f"{current_user.username}.png")
                signature_path = os.path.join(app.config['UPLOAD_FOLDER'], 'signatures', signature_filename)
                signature_file.save(signature_path)
                
                flash('Your signature has been uploaded.', 'success')
                return redirect(url_for('admin_signature'))
    
    signature_exists = os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'signatures', f"{current_user.username}.png"))
    return render_template('admin/signature.html', signature_exists=signature_exists)

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create an admin user if none exists
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        logger.info('Admin user created.')

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)