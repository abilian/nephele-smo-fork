"""
Application graph deployment business logic.
"""

import subprocess
import tempfile

import yaml

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
    service_import_clusters = [[] for _ in len(services)]

    for i in range(len(services)):
        for j, service in services:
            connection_points = service['connectionPoints']
            if connection_points[i]:
                service_import_clusters[i].append(service_placement[j])

    return service_import_clusters


def deploy_graph(data):
    """
    Instantiates an application graph.
    """

    hdag_config = data['hdag']['hdaGraph']
    name = hdag_config['id']
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

        values_overwrite['placementClustersAffinity'] = service_placement
        values_overwrite['serviceImportClusters'] = service_import_clusters

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as values_file:
            yaml.dump(values_overwrite, values_file)

            return_value = subprocess.check_output([
                'helm',
                'install',
                name,
                artifact_ref,
                '--values',
                values_file
            ], stderr=subprocess.STDOUT)

            return return_value
