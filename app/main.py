import openpyxl
from flask import Response, Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.models.Users import Users
from app.models.QRCodes import QR_Codes
from app.models.Attendance import Attendance

from functools import wraps
from datetime import date, datetime

main = Blueprint('main', 
                 __name__,
                 static_folder='static',
                 template_folder='templates'
                 )

def require_user_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_username' not in session:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs) 
    return wrapper

def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Check if the user is logged in
        if 'user_username' not in session:
            flash("You need to log in first.", "warning")
            return redirect(url_for('main.index'))

        # Query the user's role
        user = Users.query.filter_by(username=session['user_username']).first()
        if not user or user.role != 'Admin':
            flash("Access restricted to administrators only.", "danger")
            return redirect(url_for('main.dashboard'))

        # If the user is an admin, proceed with the request
        return f(*args, **kwargs)
    return wrapper

@main.route('/registration')
def registration():
    return render_template('create-user.html')

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/auth', methods=['POST', 'GET'])
def auth():
    args  = request.form
    user_auth = Users.auth(args['username'], args['password'])
    if  user_auth is None:
        return render_template('index.html')

    session['user_username'] = user_auth.username
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
@require_user_session
def dashboard():    
    QR_Codes.generate_qr_code(Users.query.filter_by(user_id=14).first())
    return render_template('dashboard.html')

@main.route('/create-user', methods=['POST', 'GET'])
@require_user_session
def create_user():
    args = request.form
    required_fields = ['firstname', 'lastname', 'username', 'password', 'email']
    missing_fields = [field for field in required_fields if not args.get(field)]

    if missing_fields:
        return render_template('error.html', message=f"Missing fields: {', '.join(missing_fields)}"), 400

    if not Users.create_user(
        firstname=args['firstname'],
        middlename=args['middlename'],
        lastname=args['lastname'],
        suffix=args['suffix'],
        username=args['username'],
        password=args['password'],
        email=args['email'],
        role=args['role']
    ):
        flash("Account not created")
        return redirect(url_for('main.create_user'))  # Redirect back to the same page or another route
    flash("Account successfully created")
    return redirect(url_for('main.dashboard'))

@main.route('/api/generate_qr_code-code', methods=['POST'])
def handle_qr_code():
    data = request.get_json()
    if not data or 'qr_code' not in data:
        return jsonify({'message': 'Invalid QR code data'}), 400

    qr_code = data['qr_code']
    print(f"Received QR Code: {qr_code}")

    # Process the QR code here (e.g., verify it, store it in the database, etc.)
    # Example: Checking if the QR code matches a record
    # if qr_code == "VALID_QR_CODE":
    #     return jsonify({'message': 'QR code is valid!'}), 200
    # else:
    #     return jsonify({'message': 'Invalid QR code'}), 400

    attendance = Attendance.add_attendance(
        user_id=qr_code['user_id']
        )
    if attendance is None:
        return jsonify({'message': f'attendance not added'}), 200
    return jsonify({'message': f'Successfully received QR code: {attendance}'}), 200

@main.route('/export/attendance_xlsx', methods=['GET'])
def export_attendance_xlsx():
    specific_date_str = request.args.get('date')
    if not specific_date_str:
        return render_template('error.html', message='Date is required. Use the format YYYY-MM-DD.'), 400

    try:
        specific_date = datetime.strptime(specific_date_str, '%Y-%m-%d').date()
    except ValueError:
        return render_template('error.html', message='Invalid date format. Use YYYY-MM-DD.'), 400

    # Fetch attendance records without checkouts for the given date
    records = Attendance.get_users_without_checkout(specific_date)

    # Create an Excel workbook and sheet
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = 'Attendance Records'

    # Define the headers
    headers = ['User ID', 'Check-In Time']
    sheet.append(headers)

    # Add the records to the sheet
    for record in records:
        check_in_time_str = record.check_in_time.strftime('%I:%M %p') if record.check_in_time else 'N/A'
        sheet.append([record.user_id, check_in_time_str])

    # Prepare the file as a response to be downloaded
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return Response(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename=attendance_records_{specific_date}.xlsx"}
    )

@main.route('/attendance/no-checkout', methods=['GET'])
def render_users_without_checkout():
    """
    Render a template with all users who have attendance on a specific date but no check-out time.

    Query Parameters:
    - date: The date to filter attendance records (in YYYY-MM-DD format).

    Returns:
    - Rendered HTML page with user IDs and check-in times.
    """
    try:
        # Extract the 'date' query parameter from the request
        specific_date_str = request.args.get('date')
        if not specific_date_str:
            return render_template('error.html', message='Date is required. Use the format YYYY-MM-DD.'), 400

        # Parse the date from the query string
        try:
            specific_date = datetime.strptime(specific_date_str, '%Y-%m-%d').date()
        except ValueError:
            return render_template('error.html', message='Invalid date format. Use YYYY-MM-DD.'), 400

        # Fetch attendance records without checkouts for the given date
        records = Attendance.get_users_without_checkout(specific_date)

        # Render the template with records
        if records:
            return render_template(
                'attendance-without-checkout.html',
                records=records,
                specific_date=specific_date
            )
        else:
            return render_template(
                'attendance-without-checkout.html',
                records=[],
                specific_date=specific_date,
                message=f'No users without checkouts found for {specific_date}.'
            )
    except Exception as e:
        return render_template('error.html', message=f'An error occurred: {str(e)}'), 500

@main.route('/manage-records')
@require_user_session
def manage_records():
    users_list = Users.get_users_with_qr()
    specific_date = date(2025, 1, 28)

# Fetch users without checkouts for the specified date
    records_without_checkouts = Attendance.get_users_without_checkout(specific_date)

    if records_without_checkouts:
        for record in records_without_checkouts:
            print(f"User ID: {record.user_id}, Check-in: {record.check_in_time}")
    else:
        print(f"No users without checkouts found for {specific_date}.")
    distinct_dates = Attendance.get_distinct_dates()
    return render_template('manage-records.html', users=users_list, dates=distinct_dates)

@main.route('/manage-inventory')
@require_user_session
def manage_inventory():
    return render_template('manage-inventory.html')

@main.route('/qr-code-scanner')
@require_user_session
def qr_code_scanner():
    return render_template('qr-code-scanner.html')


