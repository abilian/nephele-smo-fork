"""Application graph table."""

from models import db
from sqlalchemy.dialects.postgresql import JSONB


class Graph(db.Model):
    __tablename__ = 'graph'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )
    graph_descriptor = db.Column(JSONB)

    services = db.relationship(
        'Service',
        back_populates='graph',
        cascade='all,delete'
    )
