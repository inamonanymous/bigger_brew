from flask import Flask
from app.config import AppConfig
from app.main import main
from app.models import Attendance, Inventory, QRCodes, Users, db
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__, static_folder='static')
    app.register_blueprint(main)
    app.config.from_object(AppConfig)
    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        Attendance, Inventory, QRCodes, Users
        db.create_all()

    return app