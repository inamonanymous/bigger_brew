from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db
from app.models.QRCodes import QR_Codes

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

            return True
        except Exception as e:
            print(f"Error during user creation: {e}")
            return False
        
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
                    'qr_code_path': qr_code_path
                }
                for user, qr_code_path in users_with_qr
            ]

            return users_list
        except Exception as e:
            print(f"Error fetching users with QR code: {e}")
            return []
