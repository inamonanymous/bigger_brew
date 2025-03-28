from app.models import db
import qrcode
import os
import json

class QR_Codes(db.Model):
    qr_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, unique=True)
    qr_code_path = db.Column(db.String(255), nullable=False)
    generated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    @classmethod
    def delete_qr_code(cls, user_id):
        target_qr = cls.query.filter_by(user_id=user_id).first()

        if target_qr is None:
            return False  # QR code does not exist

        try:
            # Delete the QR code image file from storage
            if os.path.exists(target_qr.qr_code_path):
                os.remove(target_qr.qr_code_path)

            # Delete the QR code record from the database
            db.session.delete(target_qr)
            db.session.commit()
            return True

        except Exception as e:
            print(f"Error deleting QR code: {e}")
            db.session.rollback()
            return False


    @classmethod
    def delete_user_qr_code(cls, user_id):
        target_user = cls.query.filter_by(user_id=user_id).first()
        if target_user is None:
            return False
        try:
            db.session.delete(target_user) 
            db.session.commit()
            return True
        except Exception as e:
            print(f"exception at qr_codes.delete_user_qr_code: {e}")
            return False

    @classmethod
    def get_user_qr_code_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def generate_qr_code(user):
        try:
            # Define QR code content as JSON
            qr_content = {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email
            }

            # Convert the dictionary to a JSON string
            qr_content_json = json.dumps(qr_content)

            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(qr_content_json)
            qr.make(fit=True)
            qr_image = qr.make_image(fill='black', back_color='white')

            # Define file path
            output_dir = 'app/static/qr_codes'  # Ensure this directory exists in your project
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"user_{user.user_id}.png").replace("\\", "/")

            # Save the QR code image to the file path
            qr_image.save(file_path)

            # Save the file path in the database
            qr_entry = QR_Codes(user_id=user.user_id, qr_code_path=file_path)
            db.session.add(qr_entry)
            db.session.commit()

        except Exception as e:
            print(f"Error generating QR code: {e}")