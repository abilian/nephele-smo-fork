"""Application graph service node table."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import JSON

from smo.models import db


class ServiceStatus(Enum):
    """Enumeration for representing the deployment status of a service.

    Attributes:
    deployed (str): Indicates that the service is deployed.
    not_deployed (str): Indicates that the service is not deployed.
    """

    deployed = "Deployed"
    not_deployed = "Not deployed"


class Service(db.Model):
    """Represents a service within the application.

    This class models a service with various attributes in the database,
    allowing for deployment and undeployment operations, and provides a
    method to convert its attributes to a dictionary format.

    Attributes:
        id (int): The primary key identifier for the service.
        name (str): The name of the service, must be unique and not nullable.
        status (str): The current status of the service.
                      TODO: Should be implemented as an enum.
        grafana (str): Grafana URL or dashboard information related to the service.
        cluster_affinity (str): Information about cluster affinity for this service.
        artifact_ref (str): The reference to the service's artifact.
        artifact_type (str): The type of artifact.
        artifact_implementer (str): The implementer of the artifact.
        resources (JSON): JSON object containing resource specifications.
        values_overwrite (JSON): JSON object for value overwrites.
        graph (Graph): A relationship to the Graph model this service is associated with.
        graph_id (int): Foreign key linking to the associated Graph model.
    """

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
