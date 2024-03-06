"""
Application graph service node table.
"""

from models.models import db
from sqlalchemy.dialects.postgresql import JSONB


class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )
    values_overwrite = db.Column(JSONB)

    graph = db.relationship('Graph', back_populates='services')
