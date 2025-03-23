from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db
from app.models.QRCodes import QR_Codes
from app.models.Attendance import Attendance
from sqlalchemy import desc, asc, text
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from datetime import timedelta, datetime
from collections import defaultdict
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    middlename = db.Column(db.String(100))
    lastname = db.Column(db.String(100), nullable=False)
    suffix = db.Column(db.String(100))
    role = db.Column(db.Enum('Admin', 'Employee'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    attendance = db.relationship('Attendance', backref='user', lazy='dynamic')

    @classmethod
    def get_employee_work_hours_report(cls, user_id):
        last_30_days = (datetime.utcnow() - timedelta(days=30)).date()  # Convert to DATE

        work_hours = (
            db.session.query(
                func.date(Attendance.attendance_date).label('date'),
                func.sec_to_time(
                    func.ifnull(func.sum(func.time_to_sec(Attendance.time_spent)), 0)  # Fix NULL issue
                ).label('total_hours')
            )
            .filter(Attendance.attendance_date >= last_30_days)  # Ensure correct date comparison
            .filter(Attendance.user_id == user_id)  # Filter by user ID
            .group_by(Attendance.attendance_date)
            .order_by(Attendance.attendance_date)
            .all()
        )

        # Convert to dictionary with default value "00:00:00" for missing days
        report = defaultdict(lambda: "00:00:00", {str(date): str(total) for date, total in work_hours})

        # Ensure all last 30 days (including today) are included
        result = []
        for i in range(30):
            day = (datetime.utcnow() - timedelta(days=i)).date()
            result.append({'date': str(day), 'total_hours': report[str(day)]})

        return result[::-1]  # Reverse for chronological order


    @classmethod
    def get_user_with_qr_by_username(cls, username):
        try:
            # Fetch a single user and their QR code by joining Users and QR_Codes
            user_with_qr = db.session.query(
                Users, QR_Codes.qr_code_path
            ).join(QR_Codes, QR_Codes.user_id == Users.user_id).filter(Users.username == username).first()

            if not user_with_qr:
                return None  # If user is not found, return None

            user, qr_code_path = user_with_qr

            # Prepare the user data with QR code
            return {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'role': user.role,
                'created_at': user.created_at.isoformat(),
                'qr_code_path': qr_code_path
            }
        except Exception as e:
            print(f"Error fetching user with QR code: {e}")
            return None


    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username.strip()).first()

    from datetime import datetime

    @classmethod
    def get_attendance_summary(cls, user_id):
        """Fetch attendance summary for a specific user."""
        attendance_data = db.session.query(
            func.sec_to_time(func.sum(func.time_to_sec(Attendance.time_spent))).label("total_hours"),
            func.count(Attendance.attendance_id).label("attendance_days"),
            func.min(Attendance.check_in_time).label("earliest_check_in"),
            func.max(Attendance.check_out_time).label("latest_check_out")
        ).filter(Attendance.user_id == user_id).first()

        return {
            "total_hours": str(attendance_data.total_hours or "00:00:00"),
            "attendance_days": attendance_data.attendance_days or 0,
            "earliest_check_in": attendance_data.earliest_check_in,  # Keep as datetime
            "latest_check_out": attendance_data.latest_check_out,  # Keep as datetime
        }


    @classmethod
    def get_detailed_time_spent_report(cls):
        """
        Fetch total time spent by employees, including:
        - Total attendance days
        - Average daily time spent
        - Earliest check-in and latest check-out
        """

        time_spent_query = (
            db.session.query(
                cls.user_id,
                cls.firstname,
                cls.lastname,
                func.sec_to_time(func.sum(func.time_to_sec(Attendance.time_spent))).label("total_time_spent"),
                func.count(Attendance.attendance_id).label("attendance_days"),
                func.sec_to_time(
                    func.avg(func.time_to_sec(Attendance.time_spent))
                ).label("avg_daily_time_spent"),
                func.min(Attendance.check_in_time).label("earliest_check_in"),
                func.max(Attendance.check_out_time).label("latest_check_out")
            )
            .join(Attendance, cls.user_id == Attendance.user_id)
            .group_by(cls.user_id)
            .order_by(desc("total_time_spent"))
            .all()
        )

        # Convert results to a list of dictionaries
        result = [
            {
                "user_id": row.user_id,
                "name": f"{row.firstname} {row.lastname}",
                "total_time_spent": str(row.total_time_spent) if row.total_time_spent else "00:00:00",
                "attendance_days": row.attendance_days,
                "avg_daily_time_spent": str(row.avg_daily_time_spent) if row.avg_daily_time_spent else "00:00:00",
                "earliest_check_in": row.earliest_check_in.strftime("%Y-%m-%d %I:%M %p") if row.earliest_check_in else "N/A",
                "latest_check_out": row.latest_check_out.strftime("%Y-%m-%d %I:%M %p") if row.latest_check_out else "N/A"
            }
            for row in time_spent_query
        ]

        return result


    @classmethod
    def change_password(cls, user_id, old_password, new_password):
        user = cls.query.get(user_id)
        if not user:
            return False, "User not found"

        if not check_password_hash(user.password_hash, old_password):
            return False, "Old password is incorrect"

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, "Password updated successfully"

    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def delete_user(cls, user_id):
        target_user = cls.query.filter_by(user_id=user_id).first()
        if target_user is None:
            return False
        try:
            db.session.delete(target_user) 
            db.session.commit()
            return True
        except Exception as e:
            print(f"exception at users.delete_user: {e}")
            return False


    @classmethod 
    def edit_user(cls, user_id, email=None, firstname=None, middlename=None, lastname=None, suffix=None):
        target_user = cls.query.filter_by(user_id=user_id).first()
        if target_user is None:
            return None
        
        try:
            if email:
                target_user.email = email
            if firstname:
                target_user.firstname=firstname
            if middlename:
                target_user.middlename=middlename
            if lastname:
                target_user.lastname=lastname
            target_user.suffix=suffix
            db.session.commit()
            return target_user
        except Exception as e:
            print(f'error at edituser {e}')
            return None


    @classmethod
    def get_users_with_checkout_with_user(cls, specific_date):
        """
        Get all users who have attendance on a specific date but no check-out time,
        including user details.
        
        :param specific_date: The date to filter attendance records (datetime.date object).
        :return: A list of user records with attendance details or an empty list if none are found.
        """
        try:
            records = db.session.query(cls, Attendance).join(Attendance, cls.user_id == Attendance.user_id).filter(
                Attendance.attendance_date == specific_date,
                Attendance.check_out_time != None,  # noqa: E711 - Explicit check for NULL
                
            ).order_by(desc(Attendance.attendance_date)).all()
            return records
        except Exception as e:
            print(f"Error fetching users without checkout: {e}")
            return []
        
    @classmethod
    def get_users_without_checkout_with_user(cls, specific_date):
        """
        Get all users who have attendance on a specific date but no check-out time,
        including user details.
        
        :param specific_date: The date to filter attendance records (datetime.date object).
        :return: A list of user records with attendance details or an empty list if none are found.
        """
        try:
            records = db.session.query(cls, Attendance).join(Attendance, cls.user_id == Attendance.user_id).filter(
                Attendance.attendance_date == specific_date,
                Attendance.check_out_time == None  # noqa: E711 - Explicit check for NULL
            ).order_by(desc(Attendance.attendance_date)).all()
            return records
        except Exception as e:
            print(f"Error fetching users without checkout: {e}")
            return []


    @classmethod
    def auth(cls, username, password):
        try:
            user = cls.query.filter_by(username=username.strip()).first()
            if not (user and check_password_hash(user.password_hash, password.strip())):
                return None
            return user
        except Exception as e:
            print(f"Error during authentication: {e}")
            return None

    @classmethod
    def create_user(cls, firstname, middlename, lastname, suffix, username, password, email, role):
        try:
            user_entry = cls(
                firstname=firstname.strip(),
                middlename=middlename.strip(),
                lastname=lastname.strip(),
                suffix=suffix.strip(),
                username=username.strip(),
                password_hash=generate_password_hash(password.strip()),
                email=email.strip(),
                role=role.strip()
            )
            db.session.add(user_entry)
            db.session.commit()

            if role.strip() == 'Employee':
                QR_Codes.generate_qr_code(user_entry)

            return {"message": f"Employee: {firstname}, added!"}, 200
        except Exception as e:
            print(f"Error during user creation: {e}")
            return {"message": f"Internal server error, Please try again later!"}, 500
        
    @classmethod
    def get_users(cls):
        query = cls.query.all()
        return query
    
    @classmethod
    def get_users_with_qr(cls):
        try:
            # Join Users table with QR_Codes table to get user details and QR code path
            users_with_qr = db.session.query(Users, QR_Codes.qr_code_path).join(QR_Codes, QR_Codes.user_id == Users.user_id).all()

            # Prepare the results as a list of dictionaries
            users_list = [
                {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'role': user.role,
                    'created_at': user.created_at.isoformat(),
                    'qr_code_path': qr_code_path
                }
                for user, qr_code_path in users_with_qr
            ]

            return users_list
        except Exception as e:
            print(f"Error fetching users with QR code: {e}")
            return []


    @classmethod
    def get_employee_count(cls):
        return db.session.query(func.count(cls.user_id)).filter(cls.role == 'Employee').scalar()
    
    @classmethod
    def get_present_employees(cls, specific_date):
        """
        Get all employees who have checked in on the given date.
        :param specific_date: The date to check attendance.
        :return: List of present employee user records.
        """
        try:
            present_employees = db.session.query(cls).join(Attendance, cls.user_id == Attendance.user_id).filter(
                cls.role == "Employee",
                Attendance.attendance_date == specific_date
            ).all()
            return present_employees
        except Exception as e:
            print(f"Error fetching present employees: {e}")
            return []

    @classmethod
    def get_absent_employees(cls, specific_date):
        """
        Get all employees who have NOT checked in on the given date.
        :param specific_date: The date to check attendance.
        :return: List of absent employee user records.
        """
        try:
            AttendanceAlias = aliased(Attendance)
            absent_employees = db.session.query(cls).outerjoin(
                AttendanceAlias, cls.user_id == AttendanceAlias.user_id
            ).filter(
                cls.role == "Employee",
                (AttendanceAlias.attendance_date != specific_date) | (AttendanceAlias.attendance_id == None)
            ).all()
            return absent_employees
        except Exception as e:
            print(f"Error fetching absent employees: {e}")
            return []