from app.models import db
from datetime import datetime

class Attendance(db.Model):
    attendance_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.TIMESTAMP)
    check_out_time = db.Column(db.TIMESTAMP)
    
    @classmethod
    def get_users_without_checkout(cls, specific_date):
        """
        Get all users who have attendance on a specific date but no check-out time.

        :param specific_date: The date to filter attendance records (datetime.date object).
        :return: A list of attendance records or an empty list if none are found.
        """
        try:
            records = cls.query.filter(
                cls.attendance_date == specific_date,
                cls.check_out_time == None  # noqa: E711 - Explicit check for NULL
            ).all()
            return records
        except Exception as e:
            print(f"Error fetching users without checkout: {e}")
            return []

    @classmethod
    def get_distinct_dates(cls):
        """
        Retrieve all distinct attendance dates.

        :return: List of distinct dates, or an empty list if an error occurs.
        """
        try:
            distinct_dates = (
                db.session.query(cls.attendance_date)
                .distinct()
                .order_by(cls.attendance_date)
                .all()
            )
            # Extracting the dates from the result tuples
            return [date[0] for date in distinct_dates]
        except Exception as e:
            print(f"Error fetching distinct attendance dates: {e}")
            return []
    
    @classmethod
    def add_attendance(cls, user_id, check_in_time=None, check_out_time=None):
        """
        Add an attendance entry for a user.

        :param user_id: The ID of the user.
        :param check_in_time: The check-in timestamp (optional, defaults to current time).
        :param check_out_time: The check-out timestamp (optional).
        :return: The created attendance object or None if an error occurs.
        """
        try:
            # Check if the user already has an attendance entry for today
            today = datetime.now().date()
            existing_attendance = cls.query.filter_by(user_id=user_id, attendance_date=today).first()

            if existing_attendance:
                print(f"Attendance already exists for user ID {user_id} on {today}.")
                return "Attendance already exists for today."
            
            attendance_entry = cls(
                user_id=user_id,
                attendance_date=datetime.now().date(),
                check_in_time=check_in_time or datetime.now(),
                check_out_time=check_out_time
            )
            db.session.add(attendance_entry)
            db.session.commit()
            return attendance_entry
        except Exception as e:
            print(f"Error adding attendance: {e}")
            db.session.rollback()
            return None
        
    @classmethod
    def add_checkout(cls, user_id):
        """
        Add a check-out time for the user for today's attendance record.

        :param user_id: The ID of the user.
        :return: The updated attendance object, a message if no record exists, or None if an error occurs.
        """
        try:
            # Get today's attendance record for the user
            today = datetime.now().date()
            attendance_record = cls.query.filter_by(user_id=user_id, attendance_date=today).first()

            if not attendance_record:
                print(f"No attendance record found for user ID {user_id} on {today}.")
                return "No attendance record found for today."

            if attendance_record.check_out_time:
                print(f"Check-out time already exists for user ID {user_id} on {today}.")
                return "Check-out time already exists for today."

            # Update the check-out time
            attendance_record.check_out_time = datetime.now()
            db.session.commit()
            return attendance_record

        except Exception as e:
            print(f"Error adding check-out: {e}")
            db.session.rollback()
            return None
