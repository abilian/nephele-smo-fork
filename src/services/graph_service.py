"""Application graph deployment business logic."""

import subprocess
import tempfile
import threading
from os import path, walk

import yaml
from flask import current_app
from werkzeug.exceptions import BadRequest, NotFound

from utils.kube_helper import KubeHelper
from models import db, Graph, Service
from utils.placement import convert_placement, decide_placement, swap_placement
from utils.scaling import scaling_loop

# TODO: replace constant values
from utils.constant import CLUSTERS, CLUSTER_CAPACITY, CLUSTER_ACCELERATION, \
    ACCELERATION, graph_placement, ALPHA, BETA, \
    MAXIMUM_REPLICAS, DECISION_INTERVAL, PROMETHEUS_HOST, GRAPH_GRAFANA, \
    CPU_LIMITS_LIST, ACCELERATION_LIST, REPLICAS_LIST, CLUSTER_CAPACITY_LIST, \
    CLUSTER_ACCELERATION_LIST, RESOURCES, SERVICES_GRAFANA, SERVICES


background_scaling_threads = [None, None]
stop_events = [threading.Event(), threading.Event()]


def fetch_project_graphs(project):
    """Retrieves all the descriptors of a project"""

    graphs = db.session.query(Graph).filter_by(project=project).all()
    project_graphs = [graph.to_dict() for graph in graphs]

    return project_graphs


def deploy_graph_artifact(project, artifact_ref):
    """
    Instantiates an application graph by using Helm to
    deploy each service's artifact.
    """

    global graph_placement

    graph_descriptor = get_descriptor_from_artifact(project, artifact_ref)
    hdag_config = graph_descriptor['hdaGraph']
    name = hdag_config['id']

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is not None:
        raise BadRequest(f'Graph with name {name} already exists')

    graph = Graph(
        name=name,
        graph_descriptor=graph_descriptor,
        project=project,
        status='Running',
        grafana=GRAPH_GRAFANA
    )
    db.session.add(graph)
    db.session.commit()

    services = hdag_config['services']

    placement = decide_placement(
        CLUSTER_CAPACITY_LIST, CLUSTER_ACCELERATION_LIST, CPU_LIMITS_LIST,
        ACCELERATION_LIST, REPLICAS_LIST, graph_placement,
        initial_placement=True
    )
    graph_placement = placement
    service_placement = convert_placement(placement, services, CLUSTERS)
    cluster_placement = swap_placement(service_placement)
    import_clusters = create_service_imports(services, service_placement)

    for service in services:
        name = service['id']
        artifact = service['artifact']
        artifact_ref = artifact['ref']
        implementer = artifact['spec']['implementer']
        artifact_type = artifact['spec']['type']
        values_overwrite = artifact['valuesOverwrite']
        placement_dict = values_overwrite

        if implementer == 'WOT':
            if 'voChartOverwrite' not in values_overwrite:
                values_overwrite['voChartOverwrite'] = {}
            placement_dict = values_overwrite['voChartOverwrite']

        placement_dict['clustersAffinity'] = [service_placement[name]]
        placement_dict['serviceImportClusters'] = import_clusters[name]

        svc = Service(
            name=name,
            values_overwrite=values_overwrite,
            graph_id=graph.id,
            status='Deployed',
            cluster_affinity=service_placement[name],
            artifact_ref=artifact_ref,
            artifact_type=artifact_type,
            resources=RESOURCES[name],
            grafana=SERVICES_GRAFANA[name]
        )
        db.session.add(svc)
        db.session.commit()

        helm_install_artifact(name, artifact_ref, values_overwrite, 'install')

    spawn_scaling_processes(graph.name, cluster_placement)


def fetch_graph(name):
    """Retrieves the descriptor of an application graph."""

    graph = db.session.query(Graph).filter_by(name=name).first()

    return graph


def trigger_placement(name):
    """Triggers the placement algorithm for the given graph."""

    global graph_placement

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f'Graph with name {name} not found')

    for stop_event in stop_events:
        stop_event.set()
    kube_helper = KubeHelper(current_app.config['KARMADA_KUBECONFIG'])
    current_replicas = [kube_helper.get_replicas(service) for service in SERVICES]
    placement = decide_placement(
        CLUSTER_CAPACITY_LIST, CLUSTER_ACCELERATION_LIST, CPU_LIMITS_LIST,
        ACCELERATION_LIST, current_replicas, graph_placement,
        initial_placement=False
    )
    descriptor_services = graph.graph_descriptor['hdaGraph']['services']
    graph_placement = placement
    service_placement = convert_placement(placement, descriptor_services, CLUSTERS)
    cluster_placement = swap_placement(service_placement)
    import_clusters = create_service_imports(descriptor_services, service_placement)

    for service in graph.services:
        values_overwrite = service.values_overwrite
        values_overwrite['clustersAffinity'] = [service_placement[service.name]]
        values_overwrite['serviceImportClusters'] = import_clusters[service.name]
        db.session.commit()

        helm_install_artifact(service.name, service.artifact_ref, values_overwrite, 'upgrade')

    spawn_scaling_processes(name, cluster_placement)


def start_graph(name):
    """Starts a stopped graph"""

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f'Graph with name {name} not found')
    if graph.status == 'Running':
        raise BadRequest(f'Graph with name {name} is already running')
    graph.status = 'Running'
    for service in graph.services:
        helm_install_artifact(
            service.name,
            service.artifact_ref,
            service.values_overwrite
        )
        service.status = 'Deployed'
    db.session.commit()


def stop_graph(name):
    """Removes a graph's artifacts and sets its status to `Stopped`"""

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f'Graph with name {name} not found')
    if graph.status == 'Stopped':
        raise BadRequest(f'Graph with name {name} is already stopped')

    helm_uninstall_graph(graph.services)

    graph.status = 'Stopped'
    for service in graph.services:
        service.status = 'Not deployed'
    db.session.commit()


def remove_graph(name):
    """Removes a graph's artifacts and removes it from the database."""

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f'Graph with name {name} not found')

    helm_uninstall_graph(graph.services)

    db.session.delete(graph)
    db.session.commit()


def create_service_imports(services, service_placement):
    """
    Checks to which other services each service connects to and
    returns a dictionary whose keys are the service names and
    the values are a list of cluster names to which the service
    needs to be imported.
    """

    # For each service a list of clusters to which its service will be imported
    service_import_clusters = {
        service['id']: [] for service in services
    }

    for service in services:
        connection_points = service['connectionPoints']
        for other_service in services:
            if other_service['id'] in connection_points:
                service_import_clusters[other_service['id']].extend(
                    [service_placement[service['id']]]
                )

    return service_import_clusters


def get_descriptor_from_artifact(project, artifact_ref):
    """
    Calls the hdarctl cli to pull an artifact and deploys
    the descriptor inside after untaring the artifact.
    """

    with tempfile.TemporaryDirectory() as dirpath:
        subprocess.run([
            'hdarctl',
            'pull',
            artifact_ref,
            '--untar',
            '--destination',
            dirpath
        ])

        for (root, dirs, files) in walk(dirpath):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    with open(path.join(root, file), 'r') as yaml_file:
                        data = yaml.safe_load(yaml_file)
                        return data


def helm_install_artifact(name, artifact_ref, values_overwrite, command):
    """Executes helm command (install/upgrade) for artifact."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as values_file:
        yaml.dump(values_overwrite, values_file)

        subprocess_arguments = [
            'helm',
            command,
            name,
            artifact_ref,
            '--values',
            values_file.name,
            '--kubeconfig',
            current_app.config['KARMADA_KUBECONFIG']
        ]
        if command == 'upgrade':
            subprocess_arguments.append('--reuse-values')
        subprocess.run(subprocess_arguments)


def helm_uninstall_graph(services):
    """Uninstalls all service artifacts."""

    for service in services:
        subprocess.run([
            'helm',
            'uninstall',
            service.name,
            '--kubeconfig',
            current_app.config['KARMADA_KUBECONFIG']
        ])
    for stop_event in stop_events:
        stop_event.set()


def spawn_scaling_processes(graph_name, cluster_placement):
    """Spawns background threads that periodically run the scaling algorithm."""

    for cluster_index, cluster in enumerate(CLUSTERS):
        if cluster not in cluster_placement.keys():
            break
        # Fetch cluster specific values
        managed_services = cluster_placement[cluster]
        acceleration = [ACCELERATION[service] for service in managed_services]
        alpha = [ALPHA[service] for service in managed_services]
        beta = [BETA[service] for service in managed_services]
        maximum_replicas = [MAXIMUM_REPLICAS[service] for service in managed_services]

        stop_events[cluster_index].clear()
        background_scaling_threads[cluster_index] = threading.Thread(
            target=scaling_loop,
            args=(
                graph_name,
                acceleration,
                alpha,
                beta,
                CLUSTER_CAPACITY[cluster],
                CLUSTER_ACCELERATION[cluster],
                maximum_replicas,
                managed_services,
                DECISION_INTERVAL,
                current_app.config['KARMADA_KUBECONFIG'],
                PROMETHEUS_HOST,
                stop_events[cluster_index]
            )
        )
        background_scaling_threads[cluster_index].daemon = True
        background_scaling_threads[cluster_index].start()
