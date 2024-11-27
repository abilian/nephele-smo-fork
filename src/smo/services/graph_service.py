"""Application graph deployment business logic."""

from __future__ import annotations

import subprocess
import tempfile
import threading
from os import path, walk
from typing import TYPE_CHECKING

import yaml
from flask import current_app
from werkzeug.exceptions import BadRequest, NotFound

from smo.models import Graph, Service, db
# TODO: replace constant values
from smo.utils.constant import (ACCELERATION, ACCELERATION_LIST, ALPHA, BETA,
                                CLUSTER_ACCELERATION,
                                CLUSTER_ACCELERATION_LIST, CLUSTER_CAPACITY,
                                CLUSTER_CAPACITY_LIST, CLUSTERS,
                                CPU_LIMITS_LIST, DECISION_INTERVAL,
                                GRAPH_GRAFANA, INITIAL_PLACEMENT,
                                MAXIMUM_REPLICAS, PROMETHEUS_HOST,
                                REPLICAS_LIST, RESOURCES, SERVICES,
                                SERVICES_GRAFANA)
from smo.utils.kube_helper import KubeHelper
from smo.utils.placement import (convert_placement, decide_placement,
                                 swap_placement)
from smo.utils.scaling import scaling_loop

if TYPE_CHECKING:
    from collections.abc import Iterable

background_scaling_threads = [None, None]
stop_events = [threading.Event(), threading.Event()]


def fetch_project_graphs(project):
    """Retrieves all the descriptors of a project.

    Input:
    - project: The project instance or ID for which graphs are retrieved.

    Returns:
    - A list of dictionaries where each dictionary represents a graph descriptor.
    """
    # Query the database for all Graph instances related to the given project
    graphs = db.session.query(Graph).filter_by(project=project).all()

    # Convert each graph to a dictionary
    project_graphs = [graph.to_dict() for graph in graphs]

    return project_graphs


def deploy_graph(project, graph_descriptor):
    """Instantiates an application graph by using Helm to deploy each service's
    artifact.

    Args:
        project (str): The project name under which the graph is to be deployed.
        graph_descriptor (dict): The descriptor of the graph, containing details
            such as graph id and services configuration.
    """

    global graph_placement

    hdag_config = graph_descriptor
    name = hdag_config["id"]

    # Query the database to check if a graph with the same name already exists
    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is not None:
        raise BadRequest(f"Graph with name {name} already exists")

    # Create a new Graph object and add it to the database
    graph = Graph(
        name=name,
        graph_descriptor=graph_descriptor,
        project=project,
        status="Running",
        grafana=GRAPH_GRAFANA,
    )
    db.session.add(graph)
    db.session.commit()

    services = hdag_config["services"]

    # Decide the initial placement of services across clusters
    placement = decide_placement(
        CLUSTER_CAPACITY_LIST,
        CLUSTER_ACCELERATION_LIST,
        CPU_LIMITS_LIST,
        ACCELERATION_LIST,
        REPLICAS_LIST,
        INITIAL_PLACEMENT,
        initial_placement=True,
    )
    graph_placement = placement

    # Convert the placement to service-specific placement
    service_placement = convert_placement(placement, services, CLUSTERS)
    cluster_placement = swap_placement(service_placement)

    # Create service import clusters for cross-cluster communication
    import_clusters = create_service_imports(services, service_placement)

    for service in services:
        name = service["id"]
        artifact = service["artifact"]
        artifact_ref = artifact["ociImage"]
        implementer = artifact["ociConfig"]["implementer"]
        artifact_type = artifact["ociConfig"]["type"]
        values_overwrite = artifact["valuesOverwrite"]
        placement_dict = values_overwrite

        # Handle specific overwrites for 'WOT' implementer
        if implementer == "WOT":
            if "voChartOverwrite" not in values_overwrite:
                values_overwrite["voChartOverwrite"] = {}
            placement_dict = values_overwrite["voChartOverwrite"]

        # Update placement dict with cluster affinity and service import clusters
        placement_dict["clustersAffinity"] = [service_placement[name]]
        placement_dict["serviceImportClusters"] = import_clusters[name]

        # Create and add a Service object to the database
        svc = Service(
            name=name,
            values_overwrite=values_overwrite,
            graph_id=graph.id,
            status="Deployed",
            cluster_affinity=service_placement[name],
            artifact_ref=artifact_ref,
            artifact_type=artifact_type,
            artifact_implementer=implementer,
            resources=RESOURCES[name],
            grafana=SERVICES_GRAFANA[name],
        )
        db.session.add(svc)
        db.session.commit()

        # Deploy the artifact using Helm
        helm_install_artifact(name, artifact_ref, values_overwrite, "install")

    # Spawn processes for scaling the deployed services
    spawn_scaling_processes(graph.name, cluster_placement)


def fetch_graph(name):
    """Retrieves the descriptor of an application graph.

    Input:
    - name (str): The name of the graph to retrieve.

    Returns:
    - Graph: The graph object retrieved from the database, or None if no graph is found with the given name.
    """

    # Query the database for the graph with the specified name
    # TODO: replace with a "get" method
    graph = db.session.query(Graph).filter_by(name=name).first()

    return graph  # Return the first matching graph object, or None if no match is found


def trigger_placement(name: str) -> None:
    """Triggers the placement algorithm for the given graph.

    Input:
    - name (str): The name of the graph for which the placement algorithm is to be triggered.
    """

    global graph_placement

    # Query the graph object from the database using the provided name
    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f"Graph with name {name} not found")

    # Stop all currently running placement processes
    for stop_event in stop_events:
        stop_event.set()

    # Initialize KubeHelper with the current configuration for Karmada
    kube_helper = KubeHelper(current_app.config["KARMADA_KUBECONFIG"])
    # Retrieve the current number of replicas for each service
    current_replicas = [kube_helper.get_replicas(service) for service in SERVICES]
    # Decide on a new placement for the services based on various parameters
    placement = decide_placement(
        CLUSTER_CAPACITY_LIST,
        CLUSTER_ACCELERATION_LIST,
        CPU_LIMITS_LIST,
        ACCELERATION_LIST,
        current_replicas,
        graph_placement,
        initial_placement=False,
    )
    # Extract services from the graph descriptor and update global placement
    descriptor_services = graph.graph_descriptor["services"]
    graph_placement = placement
    # Convert placement data into a format suitable for services and clusters
    service_placement = convert_placement(placement, descriptor_services, CLUSTERS)
    cluster_placement = swap_placement(service_placement)
    import_clusters = create_service_imports(descriptor_services, service_placement)

    for service in graph.services:
        # Update service's JSON fields; requires creating a new dictionary
        values_overwrite = dict(service.values_overwrite)
        placement_dict = values_overwrite

        # Adjust placement dictionary for services implemented with "WOT"
        if service.artifact_implementer == "WOT":
            if "voChartOverwrite" not in values_overwrite:
                values_overwrite["voChartOverwrite"] = {}
            placement_dict = values_overwrite["voChartOverwrite"]

        # Update the service placement if it has changed and apply the changes
        if placement_dict["clustersAffinity"][0] != service_placement[service.name]:
            placement_dict["clustersAffinity"] = [service_placement[service.name]]
            placement_dict["serviceImportClusters"] = import_clusters[service.name]
            service.values_overwrite = values_overwrite
            db.session.commit()

            # Install or upgrade the service using Helm
            helm_install_artifact(
                service.name, service.artifact_ref, values_overwrite, "upgrade"
            )

    # Spawn scaling processes for the services based on the new cluster placement
    spawn_scaling_processes(name, cluster_placement)


def start_graph(name: str) -> None:
    """Starts a stopped graph.

    Input:
        name (str): The name of the graph to be started.

    Raises:
        NotFound: If the graph with the given name is not found in the database.
        BadRequest: If the graph is already running.
    """

    # Query the database to find the graph by name.
    graph = db.session.query(Graph).filter_by(name=name).first()

    # Raise an exception if the graph does not exist.
    if graph is None:
        raise NotFound(f"Graph with name {name} not found")

    # Raise an exception if the graph is already running.
    if graph.status == "Running":
        raise BadRequest(f"Graph with name {name} is already running")

    # Set the graph's status to 'Running'.
    graph.status = "Running"

    # Iterate through each service in the graph to deploy them.
    for service in graph.services:
        # Install the service using helm, updating its status.
        helm_install_artifact(
            service.name, service.artifact_ref, service.values_overwrite, "install"
        )
        service.status = "Deployed"

    # Commit the changes to the database.
    db.session.commit()


def stop_graph(name: str) -> None:
    """Stops a running graph by removing its artifacts and updating its status.

    Input:
    - name (str): The name of the graph to stop.

    Raises:
    - NotFound: If no graph with the specified name is found.
    - BadRequest: If the graph with the specified name is already stopped.
    """

    graph: Graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f"Graph with name {name} not found")
    if graph.status == "Stopped":
        raise BadRequest(f"Graph with name {name} is already stopped")

    # Uninstall all services associated with the graph using Helm
    helm_uninstall_graph(graph.services)

    # Update the graph's status to 'Stopped'
    graph.status = "Stopped"
    # Update each service's status to 'Not deployed'
    for service in graph.services:
        service.status = "Not deployed"

    # Commit the changes to the database
    db.session.commit()


def remove_graph(name: str) -> None:
    """Removes a graph's artifacts and removes it from the database.

    Input:
    - name (str): The name of the graph to be removed.

    Raises:
    - NotFound: If no graph with the given name is found in the database.
    """

    graph = db.session.query(Graph).filter_by(name=name).first()
    if graph is None:
        raise NotFound(f"Graph with name {name} not found")

    # Uninstall services associated with the graph
    helm_uninstall_graph(graph.services)

    # Delete the graph object from the database
    db.session.delete(graph)
    # Commit changes to persist the deletion
    db.session.commit()


def create_service_imports(services, service_placement):
    """Determine which other services each service connects to and return a
    dictionary with service names as keys and a list of cluster names where the
    service needs to be imported as values.

    Input:
    - services: A list of service dictionaries, each containing the keys "id"
      and "deployment", which further contains "intent" and "connectionPoints".
    - service_placement: A dictionary mapping each service "id" to a cluster
      name where the service is placed.

    Returns:
    - A dictionary with keys as service IDs and values as lists of cluster
      names where each service needs to be imported.

    Raises:
    - KeyError: If expected keys are missing in the `services` dictionaries or
      if a service ID is not found in the `service_placement` dictionary.
    """

    # Initialize a dictionary with service IDs as keys and empty lists as values
    # for storing clusters where the service will be imported.
    service_import_clusters = {service["id"]: [] for service in services}

    for service in services:
        # Retrieve the connection points for each service
        connection_points = service["deployment"]["intent"]["connectionPoints"]
        for other_service in services:
            # Check if another service is in the connection points of the current service
            if other_service["id"] in connection_points:
                # Extend the list of clusters for the connected service
                service_import_clusters[other_service["id"]].extend(
                    [service_placement[service["id"]]]
                )

    return service_import_clusters


def get_descriptor_from_artifact(project, artifact_ref):
    """Calls the hdarctl cli to pull an artifact and deploys the descriptor
    inside after untaring the artifact.

    Inputs:
        project: The project associated with the artifact. (Unused in the function)
        artifact_ref: A string reference to the artifact to be pulled.

    Returns:
        A Python object representing the YAML descriptor contained within the artifact.

    Raises:
        FileNotFoundError: If no YAML file is found within the untarred artifact.
        yaml.YAMLError: If an error occurs while parsing the YAML file.
        subprocess.CalledProcessError: If the hdarctl command fails.
    """

    with tempfile.TemporaryDirectory() as dirpath:
        # Run the hdarctl command to pull and untar the artifact to a temporary directory
        subprocess.run(
            [
                "hdarctl",
                "pull",
                artifact_ref,
                "--untar",
                "--destination",
                dirpath,
            ]
        )

        # Search for YAML files in the directory tree
        # TODO: refact using pathlib
        for root, dirs, files in walk(dirpath):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    # Open and parse the first YAML file found
                    with open(path.join(root, file), "r") as yaml_file:
                        data = yaml.safe_load(yaml_file)
                        return data


def helm_install_artifact(name, artifact_ref, values_overwrite, command):
    """Executes a Helm command (install/upgrade) for a given artifact.

    Args:
        name (str): The name of the release to install or upgrade.
        artifact_ref (str): The reference to the Helm chart or artifact.
        values_overwrite (dict): A dictionary of values to overwrite in the Helm chart.
        command (str): The command to execute, either "install" or "upgrade".

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If the Helm command fails.
    """

    # Create a temporary file to store the YAML values used to overwrite the default Helm chart values
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as values_file:
        # Serialize the values_overwrite dictionary into the YAML format and write it to the temporary file
        yaml.dump(values_overwrite, values_file)

        # Create the Helm command with necessary arguments
        cmd = [
            "helm",
            command,
            name,
            artifact_ref,
            "--values",
            values_file.name,
            "--kubeconfig",
            # Kubeconfig file path from the application config
            current_app.config["KARMADA_KUBECONFIG"],
        ]
        if command == "upgrade":
            # Reuse values from the previous release if upgrading
            cmd.append("--reuse-values")

        # Execute the Helm command, raising an error if the command fails
        subprocess.run(cmd, check=True)


def helm_uninstall_graph(services: Iterable[Service]) -> None:
    """Uninstalls all service artifacts.

    Input:
    - services: A list of service objects, each containing a 'name' attribute
                representing the name of the service to be uninstalled.

    Raises:
    - subprocess.CalledProcessError: If the 'helm uninstall' command fails.
    """
    # TODO: raise a domain exception (GraphServiceException) instead of the built-in exceptions

    for service in services:
        # Construct the command to uninstall the service using helm
        cmd = [
            "helm",
            "uninstall",
            service.name,
            "--kubeconfig",
            current_app.config["KARMADA_KUBECONFIG"],
        ]
        # Execute the command and uninstall the service
        subprocess.run(cmd)

    for stop_event in stop_events:
        # Set each stop event to signal stopping of a service
        stop_event.set()


def spawn_scaling_processes(graph_name, cluster_placement) -> None:
    """Spawns background threads that periodically run the scaling algorithm.

    Iterates over predefined clusters, spawning a thread for each
    cluster that is included in the provided cluster placement. Each thread runs
    a scaling loop with parameters specific to the services managed by that cluster.

    Input:
        graph_name (str): The name of the graph used in the scaling algorithm.
        cluster_placement (dict): A dictionary mapping each cluster to the services it manages.

    Raises:
        KeyError: If any of the services referenced in 'cluster_placement' are not found in
                  the predefined constants ACCELERATION, ALPHA, BETA, or MAXIMUM_REPLICAS.
        KeyError: If a cluster in 'cluster_placement' is not found in CLUSTER_CAPACITY
                  or CLUSTER_ACCELERATION.
    """

    for cluster_index, cluster in enumerate(CLUSTERS):
        if cluster not in cluster_placement.keys():
            break
        # Fetch cluster specific values
        managed_services = cluster_placement[cluster]
        # Get acceleration factors for all managed services
        acceleration = [ACCELERATION[service] for service in managed_services]
        # Get alpha values for all managed services
        alpha = [ALPHA[service] for service in managed_services]
        # Get beta values for all managed services
        beta = [BETA[service] for service in managed_services]
        # Get maximum replica numbers for all managed services
        maximum_replicas = [MAXIMUM_REPLICAS[service] for service in managed_services]

        stop_events[cluster_index].clear()
        # Create a new thread for the scaling loop with all necessary arguments
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
                current_app.config["KARMADA_KUBECONFIG"],
                PROMETHEUS_HOST,
                stop_events[cluster_index],
            ),
        )
        background_scaling_threads[cluster_index].daemon = True
        # Start the thread
        background_scaling_threads[cluster_index].start()
