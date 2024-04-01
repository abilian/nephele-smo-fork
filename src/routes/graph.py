"""Application graph Blueprints."""

from flask import Blueprint, request

from services.graph_service import deploy_graph, fetch_graph, \
    fetch_project_graphs, remove_graph, start_graph, stop_graph, \
    trigger_placement, get_descriptor_from_artifact

graph = Blueprint('graph', __name__)


@graph.route('/graph/project/<project>', methods=['GET'])
def get_all_graphs(project):
    """Fetches all graphs under a project."""

    return fetch_project_graphs(project), 200


@graph.route('/graph/project/<project>', methods=['POST'])
def deploy(project):
    """
    Handles the graph deployment. The input can either be an artifact
    URL that gets unpacked, read and deployed or it can directly
    be a desciptor file in JSON format.
    """

    request_data = request.json
    if 'artifact' in request_data:
        artifact_ref = request_data['artifact']
        descriptor = get_descriptor_from_artifact(project, artifact_ref)
        graph_descriptor = descriptor['hdaGraph']
    else:
        graph_descriptor = request_data['descriptor']
    deploy_graph(project, graph_descriptor)

    return 'Graph deployment successful\n', 200


@graph.route('/graph/<name>', methods=['GET'])
def get_graph(name):
    """Retrieves an application graph descriptor."""

    graph = fetch_graph(name)

    if graph is not None:
        return graph.to_dict(), 200
    else:
        return f'Graph with name {name} not found\n', 404


@graph.route('/graph/<name>/placement', methods=['GET'])
def placement(name):
    """Runs the placement algorithm on the graph."""

    trigger_placement(name)

    return f'Placement of graph {name} triggered\n', 200


@graph.route('/graph/<name>/start', methods=['GET'])
def start(name):
    """Starts a stopped graph."""

    start_graph(name)

    return 'Graph stopped\n', 200


@graph.route('/graph/<name>/stop', methods=['GET'])
def stop(name):
    """Uninstalls graphs artifacts without erasing from the database."""

    stop_graph(name)

    return 'Graph stopped\n', 200


@graph.route('/graph/<name>', methods=['DELETE'])
def remove(name):
    """Handles the graph removal."""

    remove_graph(name)

    return 'Removal successful\n', 200
