"""Application graph table."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import JSON

from smo.models import db


class GraphStatus(Enum):
    """Enumeration for the status of a graph process.

    This class defines the possible statuses for a graph process that
    can either be 'Started' or 'Stopped'.
    """

    started = "Started"
    stopped = "Stopped"


class Graph(db.Model):
    """Represents a Graph in the database.

    This class defines the schema for the `graph` table in the database, with columns for id, name,
    status, project, grafana, and graph_descriptor. It also establishes a relationship with the
    Service class through the `services` attribute.

    Attributes:
        id (int): Primary key of the graph.
        name (str): Unique and non-nullable name of the graph.
        status (str): Status of the graph, should ideally be an enum.
        project (str): Associated project with the graph.
        grafana (str): Grafana dashboard information linked with the graph.
        graph_descriptor (JSON): Descriptor in JSON format for additional graph details.
        services (list): List of Service objects related to this graph, with cascading delete.
    """

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
