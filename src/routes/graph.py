"""
Application graph Blueprints.
"""

from flask import Blueprint
from flask import request

from services.graph_service import deploy_graph

graph = Blueprint('graph', __name__)


@graph.route('/graph/deploy', methods=['POST'])
def deploy():
    """Handles the graph deployment."""

    data = request.get_json()
    return_value = deploy_graph(data)

    return return_value, 200
