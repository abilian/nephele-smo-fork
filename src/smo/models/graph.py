"""Application graph table."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import JSON

from smo.models import db


class GraphStatus(Enum):
    started = "Started"
    stopped = "Stopped"


class Graph(db.Model):
    __tablename__ = "graph"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    # TODO: status should be an enum
    status = db.Column(db.String(255))
    project = db.Column(db.String(255))
    grafana = db.Column(db.String(255))

    graph_descriptor = db.Column(JSON)

    services = db.relationship("Service", back_populates="graph", cascade="all,delete")

    def start(self):
        """Starts the graph."""
        # TODO: implement

    def stop(self):
        """Stops the graph."""
        # TODO: implement

    def to_dict(self):
        """Returns a dictionary representation of the class."""

        instance_dict = {
            "name": self.name,
            "status": self.status,
            "project": self.project,
            "grafana": self.grafana,
            "hdaGraph": self.graph_descriptor,
            "services": [service.to_dict() for service in self.services],
        }

        return instance_dict
