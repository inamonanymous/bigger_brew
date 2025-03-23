from app.models import db, get_ph_date_time
from datetime import datetime, date
from sqlalchemy.sql import func

class Attendance(db.Model):
    attendance_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.TIMESTAMP)
    check_out_time = db.Column(db.TIMESTAMP)
    time_spent = db.Column(db.Time)
    status = db.Column(db.Enum('Early', 'Late', 'Overtime'))

    @classmethod
    def get_attendance_today_count(cls):
        """Returns the count of users who checked in today."""
        today = date.today()
        count = db.session.query(func.count(cls.attendance_id)).filter(cls.attendance_date == today).scalar()
        return count or 0  # Ensures it returns 0 if no attendance records exist

    @classmethod
    def delete_record_by_id(cls, attendance_id):
        record = cls.query.filter_by(attendance_id=attendance_id).first()
        try:
            if record is None:
                return False
            db.session.delete(record)
            db.session.commit()
            return True
        
        except Exception as e:
            print(f'error at delte records by id {e}')
            return False
        
        
    @classmethod
    def delete_records_by_date(cls, specific_date):
        records = cls.query.filter(
                cls.attendance_date == specific_date
            ).all()
        try:
            for i in records:    
                db.session.delete(i)
            db.session.commit()
            return True
        except Exception as e:
            print(f"exception at attendance.delete_records_by_user")
            return False
        
        
    @classmethod
    def delete_records_by_user(cls, user_id):
        target_records = cls.query.filter_by(user_id=user_id).all()
        if not target_records:
            return False
        try:
            for i in target_records:    
                db.session.delete(i)
            db.session.commit()
            return True
        except Exception as e:
            print(f"exception at attendance.delete_records_by_user")
            return False
    
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
            return [date[0].isoformat() for date in distinct_dates]
        except Exception as e:
            print(f"Error fetching distinct attendance dates: {e}")
            return []
    
    @classmethod
    def add_check_out_to_attendance(cls, user_id):
        try:
            today = datetime.now().date()
            target_attendance = cls.query.filter_by(user_id=user_id, attendance_date=today).first()
            if not target_attendance:
                print('no attendance found')
                return None
            if target_attendance.check_out_time:
                print('user already checked out')
                return None
            print(f'added checkout to attendance {target_attendance.user_id}')
            target_attendance.check_out_time = datetime.now() #get_ph_date_time() alter to this when production

            time_diff = target_attendance.check_out_time - target_attendance.check_in_time
            target_attendance.time_spent = (datetime.min + time_diff).time()  # Convert timedelta to TIME

            db.session.commit()
            return target_attendance

        except Exception as e:
            print(f"add check out to attendance error: {e}")
            return None

    @classmethod
    def add_attendance(cls, user_id, check_in_time=None):
        """
        Add an attendance entry for a user.

        :param user_id: The ID of the user.
        :param check_in_time: The check-in timestamp (optional, defaults to current time).
        :param check_out_time: The check-out timestamp (optional).
        :return: The created attendance object or None if an error occurs.
        """


        # Get today's Philippine date from our custom getter 
        #code when in production
        """ today = get_ph_date_time().date()
        ph_now = get_ph_date_time()

        # Create a naive datetime for the cutoff time
        naive_cutoff = datetime.combine(today, datetime.strptime("10:15:00", "%H:%M:%S").time())

        # Make the cutoff datetime timezone-aware by using the same timezone as ph_now
        late_cutoff = naive_cutoff.replace(tzinfo=ph_now.tzinfo)

        # Now compare the two
        status = "Early" if ph_now < late_cutoff else "Late" """

        try:
            # Check if the user already has an attendance entry for today
            today = datetime.now().date()
            existing_attendance = cls.query.filter_by(user_id=user_id, attendance_date=today).first()

            if existing_attendance:
                print(f"Attendance already exists for user ID {user_id} on {today}.")
                return None
            
            late_cutoff = datetime.combine(today, datetime.strptime("10:15:00", "%H:%M:%S").time())

            status = "Early" if datetime.now() < late_cutoff else "Late"

            attendance_entry = cls(
                user_id=user_id,
                attendance_date=datetime.now().date(),
                check_in_time=check_in_time or datetime.now(), #get_ph_date_time() alter to this when production
                status=status
            )
            db.session.add(attendance_entry)
            db.session.commit()
            return attendance_entry
        except Exception as e:
            print(f"Error adding attendance: {e}")
            db.session.rollback()
            return None
