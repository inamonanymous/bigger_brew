from app.models import db
from sqlalchemy.sql import func, case
from app.models.ItemCategory import ItemCategory
from app.models.Inventory import Inventory

class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    item_category_id = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(60), nullable=False, unique=True)
    item_description = db.Column(db.String(255), nullable=False)
    item_measurement = db.Column(db.String(15), nullable=False)
    item_price = db.Column(db.Integer, nullable=False)
    item_stock = db.Column(db.Integer, nullable=False, default=0)
    added_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classmethod
    def update_item_details(cls, item_id, item_name, item_description, item_price, item_measurement, item_category_id):
        item = cls.query.filter_by(item_id=item_id).first()
        if not item:
            return None
        item.item_name = item_name
        item.item_description = item_description
        item.item_price = item_price
        item.item_measurement = item_measurement
        item.item_category_id=item_category_id
        db.session.commit()
        return item


    @classmethod
    def delete_item_category_and_items(cls, item_category_id):
        try:
            item_category = ItemCategory.query.filter_by(item_category_id=item_category_id).first()
            if not item_category:
                return False
            items = cls.query.filter_by(item_category_id=item_category_id).all()
            for i in items:
                db.session.delete(i)
            
            db.session.delete(item_category)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error deleting item category: {e}")
            return False


    @classmethod
    def delete_item(cls, item_id):
        item = cls.query.filter_by(item_id=item_id).first()
        if not item:
            print('Item does not exist')
            return False
        
        delete_inventory_records = Inventory.delete_all_records_by_item_id(item_id)
        
        if not delete_inventory_records:
            print('error deleting inventory records')
            return False

        db.session.delete(item)
        db.session.commit()
        return True


    @classmethod
    def update_quantity(cls, item_id, quantity, action):
        item = cls.query.get(item_id)
        if not item:
            print("Item does not exist")  # Debug print
            return None

        if action == "In":
            item.item_stock += quantity
        elif action == "Out":
            if item.item_stock < quantity:
                print("Not enough stock")  # Debug print
                return None  # Not enough stock
            item.item_stock -= quantity
        else:
            print("Invalid action")  # Debug print
            return None 

        try:
            db.session.commit()
            print(f"Successfully updated stock: {item.item_stock}")  # Debug print
        
        except Exception as e:
            db.session.rollback()
            print(f"Database commit error: {e}")  # Debug print
            return None
        
        inventory_entry = Inventory.insert_inventory(item_id, quantity, action)
        if inventory_entry is None:
            print("Error logging inventory entry")  # Debug print
            return None

        print(f"Stock updated: {item.item_stock}, Inventory logged: {inventory_entry.inventory_id}")  # Debug print
        return item

    @classmethod
    def get_item_by_id(cls, item_id):
        return db.session.query(
            cls, 
            ItemCategory.item_category_name
        ).select_from(cls).join(
            ItemCategory, cls.item_category_id == ItemCategory.item_category_id
        ).filter(cls.item_id == item_id).first() 


    @classmethod
    def get_all_inventory(cls):
        query = (
            db.session.query(
                cls.item_id,
                cls.item_name,
                Inventory.inventory_id,
                Inventory.quantity,
                Inventory.alter_type,
                Inventory.added_at,
                Inventory.updated_at
            )
            .join(Inventory, cls.item_id == Inventory.item_id)  # Join Item with Inventory
            .order_by(Inventory.added_at.desc())  # Optional: Sort by latest inventory records
        )
        return query.all()

    @classmethod
    def get_all_items(cls):
        try:
            return cls.query.all()  # Fetch all items
        except Exception as e:
            print(f"Error fetching items: {e}")
            return []

    @classmethod
    def get_all_items_with_category(cls):
        try:
            return db.session.query(cls, ItemCategory.item_category_name).select_from(cls).join(ItemCategory, cls.item_category_id == ItemCategory.item_category_id).all()
        except Exception as e:
            print(f"Error fetching items: {e}")
            return []

    @classmethod
    def insert_item(cls, item_category_id, item_name, item_measurement, item_description, item_price, item_stock):
        try:
            new_item = cls(
                item_category_id=item_category_id,
                item_name=item_name,
                item_measurement=item_measurement,
                item_description=item_description,
                item_price=item_price,
                item_stock=item_stock
            )
            db.session.add(new_item)
            db.session.commit()
            
            new_inventory = Inventory.insert_inventory(new_item.item_id, new_item.item_stock, 'In')
            if new_inventory is None:
                db.session.rollback()
                return None

            return new_item  # Return the created item
        except Exception as e:
            db.session.rollback()
            print(f"Error inserting item: {e}")
            return None
        

    @classmethod
    def get_total_inventory_value(cls):
        """Computes total inventory value using stock from the item table."""
        total_value = db.session.query(func.sum(cls.item_price * cls.item_stock)).scalar()
        return total_value or 0  # Ensure it returns 0 if no items exist

    @classmethod
    def get_total_value_released(cls):
        """Computes total value released based on inventory records (Out transactions)."""
        total_released = (
            db.session.query(func.sum(Inventory.quantity * cls.item_price))
            .join(cls, cls.item_id == Inventory.item_id)
            .filter(Inventory.alter_type == 'Out')
            .scalar()
        )
        return total_released or 0  # Return 0 if no 'Out' transactions exist

    @classmethod
    def get_total_count_from_inventory(cls):
        """Computes total count of an item based on inventory records (In transactions)."""
        total_count = (
            db.session.query(func.sum(Inventory.quantity))
            .filter(Inventory.alter_type == 'In')
            .scalar()
        )
        return total_count or 0  # Return 0 if no 'In' transactions exist