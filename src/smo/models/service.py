"""Application graph service node table."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import JSON

from smo.models import db


class ServiceStatus(Enum):
    deployed = "Deployed"
    not_deployed = "Not deployed"


class Service(db.Model):
    __tablename__ = "service"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    # TODO: status should be an enum
    status = db.Column(db.String(255))
    grafana = db.Column(db.String(255))
    cluster_affinity = db.Column(db.String(255))
    artifact_ref = db.Column(db.String(255))
    artifact_type = db.Column(db.String(255))
    artifact_implementer = db.Column(db.String(255))

    resources = db.Column(JSON)
    values_overwrite = db.Column(JSON)

    graph = db.relationship("Graph", back_populates="services")
    graph_id = db.Column(db.Integer, db.ForeignKey("graph.id"), nullable=False)

    def deploy(self):
        """Deploys the service."""
        # TODO: implement

    def undeploy(self):
        """Undeploys the service."""
        # TODO: implement

    def to_dict(self):
        """Returns a dictionary representation of the class."""

        instance_dict = {
            "name": self.name,
            "status": self.status,
            "grafana": self.grafana,
            "cluster_affinity": self.cluster_affinity,
            "resources": self.resources,
            "values_overwrite": self.values_overwrite,
            "artifact_ref": self.artifact_ref,
            "artifact_type": self.artifact_type,
            "artifact_implementer": self.artifact_implementer,
        }

        return instance_dict
