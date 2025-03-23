from app.models import db

class ItemCategory(db.Model):
    item_category_id = db.Column(db.Integer, primary_key=True)
    item_category_name = db.Column(db.String(30), nullable=False)
    added_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classmethod
    def edit_item_category(cls, item_category_id, new_name):
        try:
            category = cls.query.filter_by(item_category_id=item_category_id).first()
            if not category:
                return None
            category.item_category_name = new_name
            db.session.commit()
            return category
        except Exception as e:
            db.session.rollback()
            print(f"Error updating category: {e}")
            return None

    @classmethod
    def get_all_categories(cls):
        try:
            return cls.query.all()  # Fetch all item categories
        except Exception as e:
            print(f"Error fetching item categories: {e}")
            return []

    @classmethod
    def insert_item_category(cls, item_category_name):
        try:
            new_item_category = cls(
                item_category_name=item_category_name
            )
            db.session.add(new_item_category)
            db.session.commit()
            return new_item_category  # Return the created item category
        except Exception as e:
            db.session.rollback()
            print(f"Error inserting item: {e}")
            return None