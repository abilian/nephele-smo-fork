"""Application graph Blueprints."""

from __future__ import annotations

import yaml
from flasgger import swag_from
from flask import Blueprint, request

from services.graph_service import (
    deploy_graph,
    fetch_graph,
    fetch_project_graphs,
    get_descriptor_from_artifact,
    remove_graph,
    start_graph,
    stop_graph,
    trigger_placement,
)

graph = Blueprint("graph", __name__)


@graph.route("/graph/project/<project>", methods=["GET"])
@swag_from("swagger/get_all_graphs.yaml")
def get_all_graphs(project):
    """Fetches all graphs under a project."""

    return fetch_project_graphs(project), 200


@graph.route("/graph/project/<project>", methods=["POST"])
@swag_from("swagger/deploy.yaml")
def deploy(project):
    """Handles the graph deployment.

    The input can either be an artifact URL that gets unpacked, read and
    deployed or it can directly be a desciptor file in JSON format.
    """

    request_data = request.get_json()
    if isinstance(request_data, dict) and "artifact" in request_data:
        artifact_ref = request_data["artifact"]
        descriptor = get_descriptor_from_artifact(project, artifact_ref)
    else:
        descriptor = yaml.safe_load(request_data)
    graph_descriptor = descriptor["hdaGraph"]
    deploy_graph(project, graph_descriptor)

    return "Graph deployment successful\n", 200


@graph.route("/graph/<name>", methods=["GET"])
@swag_from("swagger/get_graph.yaml")
def get_graph(name):
    """Retrieves an application graph descriptor."""

    graph = fetch_graph(name)

    if graph is not None:
        return graph.to_dict(), 200
    else:
        return f"Graph with name {name} not found\n", 404


@graph.route("/graph/<name>/placement", methods=["GET"])
@swag_from("swagger/placement.yaml")
def placement(name):
    """Runs the placement algorithm on the graph."""

    trigger_placement(name)

    return f"Placement of graph {name} triggered\n", 200


@graph.route("/graph/<name>/start", methods=["GET"])
@swag_from("swagger/start.yaml")
def start(name):
    """Starts a stopped graph."""

    start_graph(name)

    return "Graph stopped\n", 200


@graph.route("/graph/<name>/stop", methods=["GET"])
@swag_from("swagger/stop.yaml")
def stop(name):
    """Uninstalls graphs artifacts without erasing from the database."""

    stop_graph(name)

    return "Graph stopped\n", 200


@graph.route("/graph/<name>", methods=["DELETE"])
@swag_from("swagger/remove.yaml")
def remove(name):
    """Handles the graph removal."""

    remove_graph(name)

    return "Removal successful\n", 200
