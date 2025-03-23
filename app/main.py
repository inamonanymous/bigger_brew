from io import BytesIO
import openpyxl
from flask import Response, Blueprint, render_template, request, session, redirect, url_for, flash, jsonify,abort
from app.models.Users import Users
from app.models.QRCodes import QR_Codes
from app.models.Attendance import Attendance
from app.models.Inventory import Inventory
from app.models.Item import Item
from app.models import get_ph_date_time
from app.models.ItemCategory import ItemCategory
from functools import wraps
from datetime import date, datetime

main = Blueprint('main', 
                 __name__,
                 static_folder='static',
                 template_folder='templates'
                 )

def get_current_user():
    return Users.query.filter_by(username=session['user_username']).first()

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

@main.route('/registration/helloworld.pypy')
def registration():
    return render_template('create-user.html')

@main.route('/')
def index():
    return render_template('login.html')


@main.route('/logout')
def logout():
    session.pop('user_username')
    return redirect(url_for('main.index'))
    
@main.route('/auth', methods=['POST', 'GET'])
def auth():
    args  = request.form
    user_auth = Users.auth(args['username'], args['password'])
    if  user_auth is None:
        return render_template('error.html', message="Invalid username or password")

    session['user_username'] = user_auth.username
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
@require_user_session
def dashboard():    
    current_user = get_current_user()
    employee_count = Users.get_employee_count()
    inventory_total_price = Item.get_total_inventory_value()
    inventory_released_value = Item.get_total_value_released()
    get_attendance_today_count = Attendance.get_attendance_today_count()
    most_time_spent = Users.get_detailed_time_spent_report()
    employee_work_hours = Users.get_employee_work_hours_report(current_user.user_id)  # New function
    return render_template('dashboard-new.html', 
                        current_user=current_user,
                        employee_count=employee_count,
                        inventory_total_price=inventory_total_price,
                        inventory_released_value=inventory_released_value,
                        get_attendance_today_count=get_attendance_today_count,
                        most_time_spent=most_time_spent,
                        employee_work_hours=employee_work_hours  # Pass to template
    )


@main.route('/profile')
@require_user_session
def profile():
    current_user = get_current_user()
    user = Users.get_user_with_qr_by_username(session['user_username'])
    attendance_summary = Users.get_attendance_summary(current_user.user_id)
    print(user)
    return render_template("profile.html", current_user=current_user, user=user, attendance_summary=attendance_summary)


@main.route('/change-password', methods=['POST'])
@require_user_session
def change_password():
    data = request.json
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    current_user = get_current_user()
    success, message = Users.change_password(current_user.user_id, old_password, new_password)

    if success:
        return jsonify({"message": message}), 200
    return jsonify({"message": message}), 400


@main.route('/api/edit-current-user', methods=['POST'])
@require_user_session
def api_edit_current_user():
    """API endpoint to edit the current user's profile"""
    current_user = get_current_user()
    data = request.json  # Get JSON data from the request

    # Ensure suffix is stored as None if it's not provided
    suffix = data.get('suffix')
    suffix = "" if (suffix == "" or not suffix) else suffix  # Convert empty string to None

    success = Users.edit_user(
        user_id=current_user.user_id,
        firstname=data.get('firstname', current_user.firstname),
        middlename=data.get('middlename', current_user.middlename),
        lastname=data.get('lastname', current_user.lastname),
        suffix=suffix  # Ensure it saves as None if empty
    )

    if not success:
        return jsonify({"success": False, "message": "Failed to update profile"}), 400

    return jsonify({"success": True, "message": "Profile updated successfully"}), 200



@main.route('/delete-one-attendance/<int:attendance_id>', methods=['DELETE'])
def delete_one_attendance(attendance_id):
    try:
        success = Attendance.delete_record_by_id(attendance_id)
        if success:
            return jsonify({"message": "Attendance record deleted successfully!"}), 200
        else:
            return jsonify({"error": "Failed to delete attendance record."}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@main.route('/delete-attendances/<string:date>', methods=['DELETE'])
def delete_attendance(date):
    try:
        success = Attendance.delete_records_by_date(date)
        if success:
            return jsonify({"message": "Attendance records deleted successfully!"}), 200
        else:
            return jsonify({"error": "Failed to delete attendance records."}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@main.route('/manage-user/<int:user_id>', methods=['PUT', 'DELETE', 'GET'])
@require_admin
def manage_user(user_id):
    if request.method == 'PUT':
        args = request.json  # Use JSON for better API handling

        # Validate required fields
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # Extract user details with defaults
        firstname = args.get('firstname', '')
        middlename = args.get('middlename', '')
        lastname = args.get('lastname', '')
        suffix = args.get('suffix', '')

        # Call the edit_user method
        if not Users.edit_user(
            user_id=user_id,
            firstname=firstname,
            middlename=middlename,
            lastname=lastname,
            suffix=suffix
        ):
            return jsonify({'error': 'Failed to edit user'}), 400

        return jsonify({'message': 'User successfully updated'}), 200

    elif request.method == 'DELETE':
        Attendance.delete_records_by_user(user_id)
        QR_Codes.delete_qr_code(user_id)
        if not Users.delete_user(user_id):
            return jsonify({'error': 'Failed to delete user'}), 400
        
        return jsonify({'message': 'User successfully deleted'}), 200

    user = Users.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.user_id,
        "firstname": user.firstname,
        "middlename": user.middlename,
        "lastname": user.lastname
    })


@main.route('/create-user', methods=['POST', 'GET'])
@require_admin
def create_user():
    args = request.form
    required_fields = ['firstname', 'lastname', 'username', 'password', 'email']
    missing_fields = [field for field in required_fields if not args.get(field)]

    if missing_fields:
        return {"message": f"Missing fields: {', '.join(missing_fields)} is required!"}, 400

    message, status = Users.create_user(
        firstname=args['firstname'],
        middlename=args['middlename'],
        lastname=args['lastname'],
        suffix=args['suffix'],
        username=args['username'],
        password=args['password'],
        email=args['email'],
        role='Employee'
    )

    return message, status

@main.route('/api/add-attendance-checkout', methods=['POST'])
@require_admin
def add_attendance_checkout():
    data = request.get_json()
    if not data or 'qr_code' not in data:
        return jsonify({'message': 'Invalid QR code data'}), 400

    qr_code = data['qr_code']
    print(f"Received QR Code: {qr_code}")

    attendance = Attendance.add_check_out_to_attendance(qr_code['user_id'])
    user = Users.get_user_by_id(qr_code['user_id'])
    if attendance is None:
        abort(400, message="Check out not added")
    return jsonify({'message': f'Check out for {user.firstname} {user.lastname} added to Attendance'}), 200

@main.route('/api/generate_qr_code-code', methods=['POST'])
@require_admin
def handle_qr_code():
    data = request.get_json()
    if not data or 'qr_code' not in data:
        return jsonify({'message': 'Invalid QR code data'}), 400

    qr_code = data['qr_code']
    print(f"Received QR Code: {qr_code}")
    attendance = Attendance.add_attendance(
        user_id=qr_code['user_id']
        )
    user = Users.get_user_by_id(qr_code['user_id'])
    if attendance is None:
        return jsonify({"error": "Attendance record not added"}), 410
    
    return jsonify({'message': f'Attendance for {user.firstname} {user.lastname} added'}), 200


@main.route('/export/attendance_report_xlsx', methods=['GET'])
def export_attendance_report_xlsx():
    date_str = request.args.get('date')
    if not date_str:
        return render_template('error.html', message='Date is required. Use the format YYYY-MM-DD.'), 400
    
    try:
        specific_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return render_template('error.html', message='Invalid date format. Use YYYY-MM-DD.'), 400

    present_employees = Users.get_present_employees(date_str)
    absent_employees = Users.get_absent_employees(date_str)
    
    # Create an Excel workbook and sheet
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = f'Attendance Report {specific_date}'

    # Define the headers
    headers = ['Employee Name', 'Employee Status', 'Check-in Time', 'Check-out Time', 'Time Spent', 'Attendance Status']
    sheet.append(headers)

    # Add present employees with check-in/check-out times
    for emp in present_employees:
        fullname = f"{emp.firstname} {emp.middlename} {emp.lastname}"
        check_in_time = emp.attendance[0].check_in_time.strftime('%I:%M %p') if emp.attendance and emp.attendance[0].check_in_time else 'N/A'
        check_out_time = emp.attendance[0].check_out_time.strftime('%I:%M %p') if emp.attendance and emp.attendance[0].check_out_time else 'N/A'
        time_spent_str = emp.attendance[0].time_spent.strftime('%H:%M:%S') if emp.attendance[0].time_spent else 'N/A'
        status = emp.attendance[0].status
        sheet.append([fullname, 'Present', check_in_time, check_out_time, time_spent_str, status])
    
    # Add absent employees
    for emp in absent_employees:
        fullname = f"{emp.firstname} {emp.middlename} {emp.lastname}"
        sheet.append([fullname, 'Absent', 'N/A', 'N/A', 'N/A', 'N/A'])

    # Prepare the file as a response to be downloaded
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return Response(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename=attendance_report_{specific_date}.xlsx"}
    )


@main.route('/api/attendance/report', methods=['GET'])
def get_attendance_report():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Date is required"}), 400

    present_employees = Users.get_present_employees(date)
    absent_employees = Users.get_absent_employees(date)

    present_data = [{
        "fullname": f"{emp.firstname} {emp.middlename} {emp.lastname}",
        "check_in_time": emp.attendance[0].check_in_time if emp.attendance[0].check_in_time else None,
        "check_out_time": emp.attendance[0].check_out_time if emp.attendance[0].check_out_time else None,
        "attendance_id": emp.attendance[0].attendance_id,
        "time_spent": emp.attendance[0].time_spent.strftime('%H:%M:%S') if emp.attendance[0].time_spent else None,
        "status": emp.attendance[0].status,
    } for emp in present_employees]

    absent_data = [{
        "fullname": f"{emp.firstname} {emp.middlename} {emp.lastname}"
    } for emp in absent_employees]

    return jsonify({"present": present_data, "absent": absent_data})



@main.route("/api/reports/detailed_time_spent", methods=["GET"])
def get_detailed_time_spent():
    """
    API endpoint to get detailed time spent data for employees.
    """
    data = Users.get_detailed_time_spent_report()
    return jsonify(data)


@main.route('/manage-employees')
@require_admin
def manage_employees():
    users_list = Users.get_users_with_qr()
    return render_template('manage-employees.html', users=users_list, current_user=get_current_user())

@main.route('/manage-attendance')
@require_user_session
def manage_attendance():
    
    distinct_dates = Attendance.get_distinct_dates()
    return render_template('manage-attendance.html', dates=distinct_dates, current_user=get_current_user())


@main.route('/manage-categories', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_category():
    if request.method == 'POST':
        data = request.json
        new_category = ItemCategory.insert_item_category(data['item_category_name'])
        current_user = get_current_user()
        if not new_category:
            return jsonify({"message": "Failed to add category"}), 400

        return jsonify({"message": "Category added successfully!"}), 200

    elif request.method == 'PUT':
        data = request.json
        item_category_id = request.args.get('item_category_id')
        new_name = data.get('item_category_name')

        if not item_category_id or not new_name:
            return jsonify({"message": "Invalid request"}), 400

        updated_category = ItemCategory.edit_item_category(item_category_id, new_name)

        if not updated_category:
            return jsonify({"message": "Failed to update category"}), 400

        return jsonify({"message": "Category updated successfully!"}), 200

    elif request.method == 'DELETE':
        item_category_id = request.args.get('item_category_id')
        if not Item.delete_item_category_and_items(item_category_id):
            return jsonify({"message": "Failed to delete category"}), 400
        return jsonify({"message": "Successfully deleted category"}), 200

    categories = ItemCategory.get_all_categories()
    
    return render_template('manage-categories-new.html', all_categories=categories, current_user = get_current_user())


@main.route("/edit-item-details/<int:item_id>", methods=["PUT"])
def edit_item_details(item_id):
    data = request.json

    item = Item.update_item_details(
        item_id,
        item_name=data['item_name'],
        item_description=data['item_description'],
        item_price=data['item_price'],
        item_measurement=data['item_measurement'],
        item_category_id=data['item_category_id'],
    )
    if not item:
        return jsonify({"success": False, "message": "Item not updated"}), 404

    return jsonify({"success": True, "message": "Item updated successfully"})

@main.route('/update-item', methods=['POST'])
@require_user_session
def update_item():
    args = request.json
    item_id = args.get('item_id')
    item_quantity = args.get('item_quantity', 0)
    action_type = args.get('action_type')  # "increase" or "decrease"

    # Print for debugging
    print(f"Received item_id: {item_id}, item_quantity: {item_quantity}, action_type: {action_type}")

    if not item_id or not item_quantity.isdigit() or int(item_quantity) <= 0:
        print("Invalid input detected")  # Debug print
        return jsonify({"message": "invalid id or quantity type"}), 400


    item_quantity = int(item_quantity)

    # Ensure item exists before updating
    item = Item.query.get(item_id)
    if not item:
        print("Item not found")  # Debug print
        return render_template('error.html', message="Item not found")

    # Attempt to update quantity
    if action_type == "increase":
        updated_item = Item.update_quantity(item_id, item_quantity, "In")
    elif action_type == "decrease":
        updated_item = Item.update_quantity(item_id, item_quantity, "Out")
    else:
        print("Invalid action type")  # Debug print
        return jsonify({"message": "invalid action type"}), 400

    if updated_item:
        print(f"Updated item: {updated_item.item_id}, New Quantity: {updated_item.item_stock}")  # Debug print
        return jsonify({"message": "successful editing item quantity"}), 200
    else:
        print("Update function returned None")  # Debug print
        return jsonify({"message": "error editing item quantity"}), 400

@main.route('/manage-items', methods=['POST'])
@require_user_session
def add_item():
    args = request.json
    new_item = Item.insert_item(
        item_category_id=args['item_category_id'],
        item_name=args['item_name'],
        item_measurement=args['item_measurement'],
        item_description=args['item_description'],
        item_price=args['item_price'],
        item_stock=args['item_stock']
    )

    if new_item is None:
        return jsonify({"message": "Unsuccessful adding item"}), 400

    return jsonify({"message": "Successfully added item"}), 200


@main.route('/manage-items/<int:item_id>', methods=['POST', 'GET', 'DELETE'])
@require_user_session
def manage_items(item_id):
    # Handle POST request to create a new item
    if request.method == 'POST':
        args = request.json
        new_item = Item.insert_item(
            item_category_id=args['item_category_id'],
            item_name=args['item_name'],
            item_measurement=args['item_measurement'],
            item_description=args['item_description'],
            item_price=args['item_price'],
            item_stock=args['item_stock']
        )

        if new_item is None:
            print('hello world')
            return jsonify({"message": "unsuccessful adding item"}), 400
        
        # Redirect to inventory management after successful insertion
        return jsonify({"message": "successful adding item"}), 200
    
    elif request.method=='GET':
        print(item_id)
        if item_id:
            item_by_id = Item.get_item_by_id(item_id)
            if item_by_id:
                item, category_name = item_by_id  # Unpack tuple
                return jsonify({
                    "item_id": item.item_id,
                    "item_name": item.item_name,
                    "item_measurement": item.item_measurement,
                    "item_description": item.item_description,
                    "item_price": item.item_price,
                    "item_stock": item.item_stock,
                    "category_name": category_name,
                    "added_at": item.added_at.strftime('%Y-%m-%d %H:%M'),
                    "updated_at": item.updated_at.strftime('%Y-%m-%d %H:%M')
                }), 200
            else:
                return jsonify({"message": "Item not found"}), 404
            
    elif request.method=='DELETE':
        if not item_id:
            return jsonify({"message": "Item ID is required"}), 400
        

        delete_item = Item.delete_item(item_id)
        if not delete_item:
            return jsonify({"message": "Item failed to delete"}), 400
        
        return jsonify({"message": "Item deletion success"}), 200

    # Default redirect if no item_id is provided in the GET request
    return redirect(url_for('main.manage_inventory')), 200


@main.route('/manage-inventory-log', methods=['POST', 'GET'])
@require_user_session
def manage_inventory_log():
    all_inventories = Item.get_all_inventory()
    current_user = get_current_user()
    return render_template('manage-inventory-log-new.html',
                           current_user=current_user,
                            all_inventories=all_inventories)

@main.route('/manage-inventory', methods=['POST', 'GET'])
@require_user_session
def manage_inventory():
    all_inventories = Item.get_all_inventory()
    all_categories = ItemCategory.get_all_categories()
    all_items_with_categories = Item.get_all_items_with_category()
    current_user = get_current_user()
    return render_template('manage-inventory-new.html',
                           current_user=current_user,
                            all_inventories=all_inventories,
                            all_categories=all_categories,
                            all_items_with_categories=all_items_with_categories)

@main.route('/qr-code-scanner')
@require_admin
def qr_code_scanner():
    return render_template('qr-code-scanner-new.html', current_user = get_current_user())
