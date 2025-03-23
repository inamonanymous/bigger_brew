from app.models import db
from sqlalchemy.exc import SQLAlchemyError

class Inventory(db.Model):
    inventory_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    alter_type = db.Column(db.Enum('In', 'Out'), nullable=False)
    added_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classmethod
    def delete_all_records_by_item_id(cls, item_id):
        try:
            query = cls.query.filter_by(item_id=item_id).all()
            for i in query:
                db.session.delete(i)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f'error deleting inventory: {e}')
            return False

    @classmethod
    def insert_inventory(cls, item_id, quantity, alter_type):
        """Adds a new inventory record."""
        try:
            new_entry = cls(item_id=item_id, quantity=quantity, alter_type=alter_type)
            db.session.add(new_entry)
            db.session.commit()
            print(f"Inventory entry added: {new_entry.inventory_id}")  # Debugging log
            return new_entry
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error inserting inventory: {e}")  # Debugging log
            return None
