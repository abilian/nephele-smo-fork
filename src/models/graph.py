"""Application graph table."""

from models import db
from sqlalchemy.dialects.postgresql import JSONB


class Graph(db.Model):
    __tablename__ = 'graph'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(255))
    project = db.Column(db.String(255))
    grafana = db.Column(db.String(255))
    graph_descriptor = db.Column(JSONB)

    services = db.relationship(
        'Service',
        back_populates='graph',
        cascade='all,delete'
    )

    def to_dict(self):
        """Returns a dictionary representation of the class."""

        instance_dict = {
            'name': self.name,
            'status': self.status,
            'project': self.project,
            'grafana': self.grafana,
            'hdaGraph': self.graph_descriptor,
        }

        instance_dict['services'] = [
            service.to_dict() for service in self.services
        ]

        return instance_dict
