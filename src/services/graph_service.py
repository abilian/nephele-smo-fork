"""
Application graph deployment business logic.
"""

import subprocess
import tempfile

import yaml
from flask import current_app
from werkzeug.exceptions import BadRequest, NotFound

from models import db, Graph, Service
from utils.placement import decide_placement


def create_service_imports(services, service_placement):
    """
    Loops through each service i and checks if service j
    has a value of 1 in its `connectionPoints` list at index i.
    e.g. connection_points[0] = [0, 1]
         connection_points[1] = [0, 0]
         service_placement = ['cluster1' , 'cluster2']
         The return value will be [[], 'cluster1'] meaning that
         the service at index 1 needs to be imported to wherever
         the service at index 0 is deployed.
    """

    # For each service a list of clusters to which its service will be imported
    service_import_clusters = [[] for _ in range(len(services))]

    for i in range(len(services)):
        for j, service in enumerate(services):
            connection_points = service['connectionPoints']
            if connection_points[i]:
                service_import_clusters[i].append(service_placement[j])

    return service_import_clusters


def deploy_graph(data):
    """
    Instantiates an application graph by using Helm to
    deploy each service'sartifact.
    """

    graph_descriptor = data
    hdag_config = graph_descriptor['hdaGraph']
    name = hdag_config['id']

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is not None:
        raise BadRequest(f'Graph with name {name} already exists')

    graph = Graph(name=name, graph_descriptor=graph_descriptor)
    db.session.add(graph)
    db.session.commit()

    graph_id = graph.id

    services = hdag_config['services']

    # List of cluster names where each service is placed
    service_placement = [
        decide_placement(service['deployment']['intent']) for service in services
    ]
    service_import_clusters = create_service_imports(services, service_placement)

    for service in services:
        name = service['id']
        artifact = service['artifact']
        artifact_ref = artifact['ref']
        values_overwrite = artifact['valuesOverwrite']

        values_overwrite['placementClustersAffinity'] = str(service_placement)
        values_overwrite['serviceImportClusters'] = str(service_import_clusters)

        svc = Service(name=name, values_overwrite=values_overwrite, graph_id=graph_id)
        db.session.add(svc)
        db.session.commit()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as values_file:
            yaml.dump(values_overwrite, values_file)

            """return_value = subprocess.check_output([
                'helm',
                'install',
                name,
                artifact_ref,
                '--values',
                values_file,
                '--kubeconfig',
                current_app['KARMADA_KUBECONFIG']
            ], stderr=subprocess.STDOUT)"""

            # return return_value
            return "ok"


def fetch_graph(name):
    """Retrieves the descriptor of an application graph."""

    graph = db.session.query(Graph).filter_by(name=name).first()

    return graph


def remove_graph(name):
    """Removes all artifacts of an application graph using Helm."""

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f'Graph with name {name} not found')

    db.session.delete(graph)
    db.session.commit()

    """return_value = subprocess.check_output([
        'helm',
        'uninstall',
        name,
        '--kubeconfig',
        current_app['KARMADA_KUBECONFIG']
    ], stderr=subprocess.STDOUT)"""

    return "ok"
    # return return_value
