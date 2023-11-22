from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.schema import UniqueConstraint, ForeignKeyConstraint


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    nfc_uid = db.Column(db.String(255), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('nfc_uid', name='uq_user_nfc_uid'),
    )

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer)

    __table_args__ = (
        ForeignKeyConstraint([user_id], [User.id], name='fk_note_user_id'),
    )

class FilamentInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(150), unique=True)  # SKU from the barcode
    weight = db.Column(db.Float)  # Weight in grams or any unit you prefer

    __table_args__ = (
        UniqueConstraint('sku', name='uq_filament_inventory_sku'),
    )

class CurrentSKU(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(150), unique=True, nullable=False)

    def __repr__(self):
        return f'<CurrentSKU {self.sku}>'
