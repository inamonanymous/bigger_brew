from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from datetime import datetime, timezone, timedelta

def get_ph_date_time():
    utc_now = datetime.now(timezone.utc)
    # Add 8 hours to convert to Philippine Time
    return utc_now + timedelta(hours=8)