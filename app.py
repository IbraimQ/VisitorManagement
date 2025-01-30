from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from datetime import datetime, timezone
import os
from mailjet_rest import Client
import pytz
from flask import session
import secrets

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)  # Secure random secret key
app.config['DEBUG'] = True

# Error handler for detailed error logging
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    return jsonify(error=str(e)), 500

# Configuration for SQL Server with Windows Authentication
server = 'LAPTOP-77204R0A\\SQLEXPRESS'
database = 'pyVisitor'
driver = 'ODBC Driver 17 for SQL Server'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configuration for Mailjet
MAILJET_API_KEY = 'da6ba1e0f448a281debaf01c0476fe3a'
MAILJET_API_SECRET = '58f716e364714d179d4875163c9a3482'

mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')

# Manager Model
class Manager(db.Model):
    __tablename__ = 'Managers'
    id = db.Column('ManagerID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(50), nullable=False)
    email = db.Column('Email', db.String(120), nullable=False, unique=True)
    password = db.Column('Password', db.String(120), nullable=False)
    department = db.Column('Department', db.String(100), nullable=True)

# ManagerAccount Model
class ManagerAccount(db.Model):
    __tablename__ = 'ManagerAccounts'
    id = db.Column('ManagerAccountID', db.Integer, primary_key=True)
    manager_id = db.Column('ManagerID', db.Integer, db.ForeignKey('Managers.ManagerID'), nullable=False)
    username = db.Column('Username', db.String(50), nullable=False)
    password = db.Column('Password', db.String(120), nullable=False)
    role = db.Column('Role', db.String(20), nullable=False, default='manager')  # Add role column

    manager = db.relationship('Manager', backref=db.backref('accounts', lazy=True))


# Visitor Model
class Visitor(db.Model):
    __tablename__ = 'Visitors'
    VisitorID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)
    IDNumber = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(120), nullable=False)
    VisitRequestID = db.Column(db.Integer, db.ForeignKey('VisitRequests.VisitRequestID'), nullable=False)

    visit_request = db.relationship('VisitRequest', back_populates='visitors')

# VisitRequest Model
class VisitRequest(db.Model):
    __tablename__ = 'VisitRequests'
    VisitRequestID = db.Column(db.Integer, primary_key=True)
    ManagerID = db.Column(db.Integer, db.ForeignKey('Managers.ManagerID'), nullable=False)
    GateID = db.Column(db.Integer, db.ForeignKey('Gates.GateID'), nullable=False)
    Status = db.Column(db.String(20), nullable=False, default='Pending')
    SubmissionTime = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Riyadh')))
    CheckedInTime = db.Column(db.DateTime, nullable=True)  # Add this line
    CheckedOutTime = db.Column(db.DateTime, nullable=True)

    manager = db.relationship('Manager', backref=db.backref('visit_requests', lazy=True))
    gate = db.relationship('Gate', backref=db.backref('visit_requests', lazy=True))
    visitors = db.relationship('Visitor', back_populates='visit_request')
    visit_times = db.relationship('VisitTime', backref='visit_request', lazy=True)



# VisitTime Model
class VisitTime(db.Model):
    __tablename__ = 'VisitTimes'
    VisitTimeID = db.Column(db.Integer, primary_key=True)
    VisitRequestID = db.Column(db.Integer, db.ForeignKey('VisitRequests.VisitRequestID'), nullable=False)
    VisitDate = db.Column(db.Date, nullable=False)
    StartTime = db.Column(db.Time, nullable=False)
    EndTime = db.Column(db.Time, nullable=False)

# Gate Model
class Gate(db.Model):
    __tablename__ = 'Gates'
    id = db.Column('GateID', db.Integer, primary_key=True)
    gate_number = db.Column('GateNumber', db.String(50), nullable=False)
    location = db.Column('Location', db.String(100), nullable=False)

# GateAccount Model
class GateAccount(db.Model):
    __tablename__ = 'GateAccounts'
    id = db.Column('GateAccountID', db.Integer, primary_key=True)
    gate_id = db.Column('GateID', db.Integer, db.ForeignKey('Gates.GateID'), nullable=False)
    username = db.Column('Username', db.String(50), nullable=False)
    password = db.Column('Password', db.String(120), nullable=False)
    name = db.Column('Name', db.String(50), nullable=False)

    gate = db.relationship('Gate', backref=db.backref('gate_accounts', lazy=True))

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/form')
def form():
    managers = Manager.query.all()
    gates = Gate.query.all()
    return render_template('form.html', managers=managers, gates=gates)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        manager_account = ManagerAccount.query.filter_by(username=username, password=password).first()
        if manager_account:
            session['manager_id'] = manager_account.manager_id
            return redirect(url_for('manager_dashboard'))
        else:
            flash('Sorry, your password was incorrect. Please double-check your password.', 'error')
    return render_template('login.html')

@app.route('/gate_security_login', methods=['GET', 'POST'])
def gate_login():
    if request.method == 'POST':
        # Handle POST request (login form submission)
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt: username={username}, password={password}")
        
        gate_account = GateAccount.query.filter_by(username=username, password=password).first()
        if gate_account:
            print(f"Login successful for user: {username}")
            session['gate_id'] = gate_account.gate_id
            session['role'] = 'gate_security'  # Ensure this is set to differentiate roles
            return redirect(url_for('gate_security_dashboard'))
        else:
            print(f"Invalid username or password for user: {username}")
            flash('Sorry, your password was incorrect. Please double-check your password.', 'error')
            return redirect(url_for('gate_login'))
    else:
        # Handle GET request (render login page)
        return render_template('gate_security_login.html')

@app.route('/gate_security_dashboard')
def gate_security_dashboard():
    if 'gate_id' not in session:
        return redirect(url_for('gate_login'))

    # Extract query parameters
    sort_by = request.args.get('sort', 'newest')
    status_filter = request.args.getlist('status')
    search_query = request.args.get('search')
    page = request.args.get('page', 1, type=int)

    # Base query
    query = VisitRequest.query.filter_by(GateID=session['gate_id'])

    # Apply status filter
    if status_filter:
        query = query.filter(VisitRequest.Status.in_(status_filter))

    # Apply search filter
    if search_query:
        query = query.filter(VisitRequest.VisitRequestID.like(f'%{search_query}%'))

    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(VisitRequest.SubmissionTime.desc())
    elif sort_by == 'oldest':
        query = query.order_by(VisitRequest.SubmissionTime.asc())

    # Pagination
    paginated_visits = query.paginate(page=page, per_page=10)

    visit_details = []
    for visit in paginated_visits.items:
        visitors = Visitor.query.filter_by(VisitRequestID=visit.VisitRequestID).all()
        visit_times = VisitTime.query.filter_by(VisitRequestID=visit.VisitRequestID).all()

        # Fetch gate account details
        gate_account = GateAccount.query.filter_by(gate_id=visit.GateID).first()
        gate_security_username = gate_account.username if gate_account else 'N/A'

        visit_details.append({
            'visit': visit,
            'visitors': visitors,
            'visit_times': visit_times,
            'gate_number': visit.gate.gate_number,
            'manager_name': visit.manager.name,
            'manager_department': visit.manager.department,
            'gate_security_username': gate_account.username if gate_account else 'N/A',
            'gate_security_name': gate_account.name if gate_account else 'N/A' 
        })

    total_forms = paginated_visits.total
    pending_forms = query.filter_by(Status='Pending').count()
    checked_in_forms = query.filter_by(Status='Checked In').count()

    return render_template(
        'gate_security_dashboard.html',
        visit_details=visit_details,
        total_forms=total_forms,
        pending_forms=pending_forms,
        checked_in_forms=checked_in_forms,
        paginated_visits=paginated_visits
    )

@app.route('/check_in/<int:visit_id>', methods=['POST'])
def check_in(visit_id):
    if 'gate_id' not in session:
        return jsonify(success=False, message='Unauthorized access'), 403
    
    visit = VisitRequest.query.get(visit_id)
    if visit and visit.Status == 'Approved':
        visit.Status = 'Checked In'
        visit.CheckedInTime = datetime.now(pytz.timezone('Asia/Riyadh'))
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False, message='Visit not found or not approved'), 404

@app.route('/check_out/<int:visit_id>', methods=['POST'])
def check_out(visit_id):
    if 'gate_id' not in session:
        return jsonify(success=False, message='Unauthorized access'), 403

    visit = VisitRequest.query.get(visit_id)
    if visit and visit.Status == 'Checked In':
        visit.Status = 'Checked Out'
        visit.CheckedOutTime = datetime.now(pytz.timezone('Asia/Riyadh'))
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False, message='Visit not found or not checked in'), 404

def notify_check_out(visit):
    manager = visit.manager
    visitors = visit.visitors
    # Notify manager
    send_email(manager, visitors, visit_times=visit.visit_times, visit_request_id=visit.VisitRequestID, gate_id=visit.GateID, action='Check Out')

    # Notify visitors
    for visitor in visitors:
        send_status_email(visitor, 'Checked Out', visit.gate.gate_number if visit.gate else None)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    gates = Gate.query.all()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        username = request.form['username']
        department = request.form.get('department', '')  # For managers
        role = request.form.get('role', 'manager')  # Default to manager

        print(f"Received data: name={name}, email={email}, username={username}, role={role}")

        if not all([name, email, password, confirm_password, username, role]):
            flash('All fields are required')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        existing_account = ManagerAccount.query.filter_by(username=username).first() if role == 'manager' else GateAccount.query.filter_by(username=username).first()
        if existing_account:
            flash('Username already exists')
            return redirect(url_for('signup'))

        if role == 'manager':
            new_manager = Manager(name=name, email=email, password=password, department=department)
            db.session.add(new_manager)
            db.session.commit()
            manager_account = ManagerAccount(manager_id=new_manager.id, username=username, password=password, role=role)
            db.session.add(manager_account)
        elif role == 'gate_security':
            gate_id = request.form['gate_id']  # Gate ID from form
            gate_account = GateAccount(gate_id=gate_id, username=username, password=password, name=name)  # Include name field
            db.session.add(gate_account)
        else:
            flash('Invalid role specified')
            return redirect(url_for('signup'))

        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', gates=gates)


@app.route('/manager_dashboard')
def manager_dashboard():
    if 'manager_id' not in session:
        return redirect(url_for('login'))

    sort_by = request.args.get('sort', 'newest')
    status_filter = request.args.getlist('status')
    search_query = request.args.get('search')
    page = request.args.get('page', 1, type=int)

    query = VisitRequest.query.filter_by(ManagerID=session['manager_id'])

    if status_filter:
        query = query.filter(VisitRequest.Status.in_(status_filter))

    if sort_by == 'newest':
        query = query.order_by(VisitRequest.SubmissionTime.desc())
    elif sort_by == 'oldest':
        query = query.order_by(VisitRequest.SubmissionTime.asc())

    if search_query:
        query = query.filter(VisitRequest.VisitRequestID.like(f'%{search_query}%'))

    paginated_visits = query.paginate(page=page, per_page=10)

    visit_details = []
    for visit in paginated_visits.items:
        visitors = Visitor.query.filter_by(VisitRequestID=visit.VisitRequestID).all()
        visit_times = VisitTime.query.filter_by(VisitRequestID=visit.VisitRequestID).all()
        gate_account = GateAccount.query.filter_by(gate_id=visit.GateID).first()
        gate_security_username = gate_account.username if gate_account else 'N/A'

        gate = Gate.query.get(visit.GateID)
        gate_number = visit.gate.gate_number if visit.gate else 'N/A'

        visit_details.append({
            'visit': visit,
            'visitors': visitors,
            'visit_times': visit_times,
            'gate_number': visit.gate.gate_number if visit.gate else 'N/A',  # Handle None case
            'manager_name': visit.manager.name,
            'manager_department': visit.manager.department,
            'gate_security_username': gate_account.username if gate_account else 'N/A',
            'gate_security_name': gate_account.name if gate_account else 'N/A' 
        })

    total_forms = paginated_visits.total
    pending_forms = len([vr for vr in paginated_visits.items if vr.Status == 'Pending'])
    approved_forms = len([vr for vr in paginated_visits.items if vr.Status == 'Approved'])
    gates = Gate.query.all()

    managers = Manager.query.all()  # Fetch all managers

    return render_template('manager_dashboard.html', visit_details=visit_details,
                           total_forms=total_forms, pending_forms=pending_forms,
                           approved_forms=approved_forms, paginated_visits=paginated_visits, gates=gates, managers=managers)

def send_email_to_new_manager(new_manager_id, visit_request):
    new_manager = Manager.query.get(new_manager_id)

    if not new_manager or not visit_request:
        print(f"Could not send email: Manager ID or Visit Request ID is invalid.")
        return

    visitors = visit_request.visitors
    visit_times = visit_request.visit_times

    # Prepare the email content
    body_html = f"""
    <html>
    <body>
        <h2>New Visitor Request Assigned to You</h2>
        <p>Visit Request ID: {visit_request.VisitRequestID}</p>
        <h2>Visitor Details</h2>
        <table border="1" cellpadding="5" cellspacing="0">
    """
    for i, visitor in enumerate(visitors):
        body_html += f"""
            <tr>
                <th colspan="2">Visitor {i + 1}</th>
            </tr>
            <tr>
                <th>First Name</th><td>{visitor.FirstName}</td>
            </tr>
            <tr>
                <th>Last Name</th><td>{visitor.LastName}</td>
            </tr>
            <tr>
                <th>Phone Number</th><td>{visitor.PhoneNumber}</td>
            </tr>
            <tr>
                <th>ID/Iqama</th><td>{visitor.IDNumber}</td>
            </tr>
        """
    body_html += f"""
            <tr>
                <th>Number of Visitors</th><td>{len(visitors)}</td>
            </tr>
            <tr>
                <th>Gate Number</th><td>{visit_request.GateID}</td>
            </tr>
        </table>
        <h2>Visit Times</h2>
        <table border="1" cellpadding="5" cellspacing="0">
    """
    for visit_time in visit_times:
        body_html += f"""
            <tr>
                <th>Visit Date</th><td>{visit_time.VisitDate}</td>
                <th>From</th><td>{visit_time.StartTime}</td>
                <th>To</th><td>{visit_time.EndTime}</td>
            </tr>
        """
    body_html += """
        </table>
    </body>
    </html>
    """

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "ihemaa.4@gmail.com",
                    "Name": "Cameron Al-rushaid"
                },
                "To": [
                    {
                        "Email": new_manager.email,
                        "Name": new_manager.name
                    }
                ],
                "Subject": "New Visitor Request Assigned",
                "HTMLPart": body_html
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code == 200:
        print(f"Email sent successfully to {new_manager.name}")
    else:
        print(f"Error sending email: {result.json()}")

def send_email_to_visitor(visitor, new_manager_name, new_manager_department):
    subject = "Update on Your Visit Request"
    body_html = f"""
    <html>
    <body>
        <h2>Your Visit Request Has Been Updated</h2>
        <p>Your visit request has been reassigned to a new manager.</p>
        <p>New Manager: {new_manager_name}</p>
        <p>Department: {new_manager_department}</p>
    </body>
    </html>
    """

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "ihemaa.4@gmail.com",
                    "Name": "Cameron Al-rushaid"
                },
                "To": [
                    {
                        "Email": visitor.Email,
                        "Name": visitor.FirstName
                    }
                ],
                "Subject": subject,
                "HTMLPart": body_html
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        print(f"Error sending email to visitor: {result.json()}")

def send_email_to_visitor_about_manager_change(visit_request):
    visitors = visit_request.visitors
    new_manager = Manager.query.get(visit_request.ManagerID)

    if not visitors or not new_manager:
        print(f"Could not send email: Visitors or New Manager details are invalid.")
        return

    for visitor in visitors:
        body_html = f"""
        <html>
        <body>
            <h2>Your Visit Request Has Been Updated</h2>
            <p>Your visit request ID: {visit_request.VisitRequestID}</p>
            <p>The new manager assigned to your visit is {new_manager.name} from the {new_manager.department} department.</p>
        </body>
        </html>
        """

        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "your_email@example.com",  # Replace with your email
                        "Name": "Your Company Name"
                    },
                    "To": [
                        {
                            "Email": visitor.Email,
                            "Name": visitor.FirstName
                        }
                    ],
                    "Subject": "Your Visit Request Has Been Updated",
                    "HTMLPart": body_html
                }
            ]
        }

        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print(f"Email sent successfully to {visitor.FirstName} {visitor.LastName}")
        else:
            print(f"Error sending email to {visitor.FirstName} {visitor.LastName}: {result.json()}")

@app.route('/update_manager/<int:visit_id>', methods=['POST'])
def update_manager(visit_id):
    try:
        data = request.json
        new_manager_id = data.get('new_manager_id')

        if not new_manager_id:
            return jsonify(success=False, message='Manager ID is missing'), 400

        new_manager = Manager.query.get(new_manager_id)
        if not new_manager:
            return jsonify(success=False, message='Manager not found'), 404

        visit_request = VisitRequest.query.get(int(visit_id))
        if visit_request:
            old_manager_id = visit_request.ManagerID
            visit_request.ManagerID = int(new_manager_id)
            visit_request.LastEdited = datetime.now(pytz.timezone('Asia/Riyadh'))
            db.session.commit()

            send_email_to_new_manager(new_manager_id, visit_request)

            for visitor in visit_request.visitors:
                send_email_to_visitor(visitor, new_manager.name, new_manager.department)

            return jsonify(success=True)
        return jsonify(success=False, message='Visit request not found'), 404
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/suggestions')
def suggestions():
    query = request.args.get('query', '')
    if query.isdigit():  # Ensure the query is numeric
        suggestions = VisitRequest.query.filter(VisitRequest.VisitRequestID.like(f'%{query}%')).limit(10).all()
        suggestion_list = [str(vr.VisitRequestID) for vr in suggestions]
        return jsonify(suggestion_list)
    return jsonify([])

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        num_visitors = int(request.form['numVisitors'])
        manager_id = request.form['manager']
        status = request.form['status']

        # Validate input fields
        if num_visitors <= 0:
            return "Number of visitors must be greater than 0", 400
        if not manager_id:
            return "Manager selection is required", 400
        if not status:
            return "Status is required", 400

        # Create the visit request
        visit_request = VisitRequest(
            ManagerID=manager_id,
            GateID=None,
            Status=status,
            SubmissionTime=datetime.now(pytz.timezone('Asia/Riyadh'))
        )
        db.session.add(visit_request)
        db.session.commit()

        visit_request_id = visit_request.VisitRequestID  # Capture the ID after commit

        visitors = []
        for i in range(num_visitors):
            first_name = request.form.get(f'firstName[{i}]')
            last_name = request.form.get(f'lastName[{i}]')
            phone_number = request.form.get(f'phoneNumber[{i}]')
            id_number = request.form.get(f'idNumber[{i}]')
            email = request.form.get(f'email[{i}]')
            id_attachment = request.files.get(f'idAttachment[{i}]')

            if not (first_name and last_name and phone_number and id_number and email and id_attachment):
                missing_fields = []
                if not first_name: missing_fields.append("First Name")
                if not last_name: missing_fields.append("Last Name")
                if not phone_number: missing_fields.append("Phone Number")
                if not id_number: missing_fields.append("ID/Iqama Number")
                if not email: missing_fields.append("Email")
                if not id_attachment: missing_fields.append("ID Attachment")
                print(f"Missing fields for visitor {i}: {', '.join(missing_fields)}")
                return f"Missing required fields for visitor {i}: {', '.join(missing_fields)}", 400

            file_path = os.path.join('uploads', id_attachment.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            id_attachment.save(file_path)

            visitor = Visitor(
                FirstName=first_name,
                LastName=last_name,
                PhoneNumber=phone_number,
                IDNumber=id_number,
                Email=email,
                VisitRequestID=visit_request_id  # Use the captured ID
            )
            db.session.add(visitor)
            visitors.append(visitor)

        visit_dates = request.form.getlist('visitDate[]')
        start_times = request.form.getlist('startTime[]')
        end_times = request.form.getlist('endTime[]')

        if not visit_dates or not start_times or not end_times:
            return "At least one visit time slot is required", 400

        visit_times = []
        for visit_date, start_time, end_time in zip(visit_dates, start_times, end_times):
            visit_time = VisitTime(
                VisitRequestID=visit_request_id,  # Use the captured ID
                VisitDate=visit_date,
                StartTime=start_time,
                EndTime=end_time
            )
            db.session.add(visit_time)
            visit_times.append(visit_time)

        db.session.commit()

        # Send email to the manager with visit_request_id
        manager = Manager.query.get(manager_id)
        if manager:
            send_email(manager, visitors, visit_times, visit_request_id)

        return redirect(url_for('submission_success', visit_request_id=visit_request_id))
    except Exception as e:
        # Log the error
        app.logger.error(f"Error during form submission: {str(e)}")
        return str(e), 400

def send_status_email(visitor, status, gate_number=None):
    subject = "Update on Your Visit Request"
    gate_info = f"Your assigned gate is: {gate_number}." if gate_number else ""
    body = f"Your visit request has been {status.lower()}. {gate_info}"

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "ihemaa.4@gmail.com",
                    "Name": "Cameron Al-rushaid"
                },
                "To": [
                    {
                        "Email": visitor.Email,
                        "Name": visitor.FirstName
                    }
                ],
                "Subject": subject,
                "TextPart": body
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        print(f"Error sending status email to visitor: {result.json()}")

@app.route('/update_visit_status/<int:visit_id>', methods=['POST'])
def update_visit_status(visit_id):
    if 'manager_id' not in session:
        return jsonify(success=False, message='Unauthorized'), 403
    
    visit = VisitRequest.query.get_or_404(visit_id)
    data = request.json
    status = data.get('status')
    gate_id = data.get('gate_id')

    if not status:
        return jsonify(success=False, message='Status is required'), 400

    visit.Status = status
    if gate_id:
        visit.GateID = gate_id  # Update the gate ID
    db.session.commit()
    # Notify visitors or other relevant actions
    
    for visitor in visit.visitors:
        send_status_email(visitor, status, visit.gate.gate_number if visit.gate else None)
    
    return jsonify(success=True, message='Status updated')

@app.route('/api/managers_and_gates', methods=['GET'])
def get_managers_and_gates():
    managers = Manager.query.all()
    gates = Gate.query.all()
    data = {
        'managers': [{'id': manager.id, 'name': manager.name, 'department': manager.department} for manager in managers],
        'gates': [{'id': gate.id, 'gate_number': gate.gate_number} for gate in gates]
    }
    return jsonify(data)

def send_email(manager, visitors, visit_times, visit_request_id, gate_id=None, action='New Visitor Request'):
    action_message = {
        'New Visitor Request': 'New Visitor Request',
        'Check Out': 'Visitor Check-Out Notification'
    }


    body_html = """
    <html>
    <body>
        <h2>Visitor Details</h2>
        <table border="1" cellpadding="5" cellspacing="0">
    """
    for i, visitor in enumerate(visitors):
        body_html += f"""
            <tr>
                <th colspan="2">Visitor {i + 1}</th>
            </tr>
            <tr>
                <th>First Name</th><td>{visitor.FirstName}</td>
            </tr>
            <tr>
                <th>Last Name</th><td>{visitor.LastName}</td>
            </tr>
            <tr>
                <th>Phone Number</th><td>{visitor.PhoneNumber}</td>
            </tr>
            <tr>
                <th>ID/Iqama</th><td>{visitor.IDNumber}</td>
            </tr>
        """
    body_html += f"""
            <tr>
                <th>Number of Visitors</th><td>{len(visitors)}</td>
            </tr>
            <tr>
                <th>Gate Number</th><td>{gate_id}</td>
            </tr>
        </table>
        <h2>Visit Request ID: {visit_request_id}</h2>
        <h2>Visit Times</h2>
        <table border="1" cellpadding="5" cellspacing="0">
    """
    for visit_time in visit_times:
        body_html += f"""
            <tr>
                <th>Visit Date</th><td>{visit_time.VisitDate}</td>
                <th>From</th><td>{visit_time.StartTime}</td>
                <th>To</th><td>{visit_time.EndTime}</td>
            </tr>
        """
    body_html += """
        </table>
    </body>
    </html>
    """

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "ihemaa.4@gmail.com",
                    "Name": "Cameron Al-rushaid"
                },
                "To": [
                    {
                        "Email": manager.email,
                        "Name": manager.name
                    }
                ],
                "Subject": "New Visitor Request",
                "HTMLPart": body_html
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        print(f"Error sending email to manager: {result.json()}")

@app.route('/submission_success')
def submission_success():
    visit_request_id = request.args.get('visit_request_id')
    return render_template('submit.html', visit_request_id=visit_request_id)