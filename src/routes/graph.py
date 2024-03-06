"""Application graph Blueprints."""

import yaml
from flask import Blueprint, request

from services.graph_service import deploy_graph, fetch_graph, remove_graph

graph = Blueprint('graph', __name__)


@graph.route('/graph', methods=['POST'])
def deploy():
    """Handles the graph deployment."""

    hdag_yaml_file = request.files['hdag']
    if request.files:
        hdag_yaml_file = request.files['hdag'].read().decode('utf-8')
        descriptor = yaml.safe_load(hdag_yaml_file)
        return_value = deploy_graph(descriptor)

        return return_value, 200
    else:
        return 'Descriptor missing', 400


@graph.route('/graph/<name>', methods=['GET'])
def fetch(name):
    """Retrieves an application graph descriptor."""

    graph = fetch_graph(name)

    if graph is not None:
        return graph.graph_descriptor, 200
    else:
        return f'Graph with name {name} not found', 404


@graph.route('/graph/<name>', methods=['DELETE'])
def remove(name):
    """Handles the graph removal."""

    return_value = remove_graph(name)

    return return_value, 200
