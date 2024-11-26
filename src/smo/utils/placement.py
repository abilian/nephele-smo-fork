"""Application node placement related functionalities."""

from __future__ import annotations

from gurobipy import GRB, Model, quicksum


def swap_placement(service_dict: dict) -> dict:
    """Converts a mapping of services to clusters into a mapping of clusters to
    the list of services deployed there.

    Args:
        service_dict (dict): A dictionary where keys are services and values are clusters.

    Returns:
        dict: A dictionary where keys are clusters and values are lists of services.

    Example:
        >>> swap_placement({'service1': 'clusterA', 'service2': 'clusterB'})
        {'clusterA': ['service1'], 'clusterB': ['service2']}
    """

    cluster_dict = {}
    for key, value in service_dict.items():
        # Add the service to the list of services for the cluster
        cluster_dict.setdefault(value, []).append(key)
    return cluster_dict


def convert_placement(placement, services, clusters):
    """Convert placement from list of lists to dictionary mapping a service
    with the name of its cluster.

    E.g. Input
        placement:[[1, 0], [1, 0]]
        services: [{'id': 'service1'}, {'id': 'service2'}]
        clusters ['cluster1', 'cluster2']
     Output: {'service1': 'cluster1', 'service2': 'cluster1'}

    Input:
        placement (list of list of int): A binary matrix where each row corresponds to a service
            and each column corresponds to a cluster. A '1' indicates the service is placed on
            the corresponding cluster.
        services (list of dict): A list of dictionaries where each dictionary has a key 'id'
            representing the service name.
        clusters (list of str): A list of cluster names which correspond to the columns in the
            placement matrix.

    Returns:
        dict: A dictionary mapping each service's name to its respective cluster name.
    """

    service_placement = {}
    for service_index, cluster_list in enumerate(placement):
        # Get the index of the element that has a value of 1
        cluster_index = cluster_list.index(1)
        service_name = services[service_index]["id"]
        service_placement[service_name] = clusters[cluster_index]

    return service_placement


def decide_placement(
    cluster_capacities,
    cluster_acceleration,
    cpu_limits,
    acceleration,
    replicas,
    current_placement,
    initial_placement=False,
):
    """Determines the optimal placement of services across multiple clusters.

    Input:
    ---
    cluster_capacities: List of CPU capacity for each cluster
    cluster_acceleration: List of GPU acceleration feature for each cluster
    cpu_limits: List of CPU limits for each service
    acceleration: List of GPU acceleration feature for each service
    replicas: List of number of replicas
    current_placement: List of current placement
    initial_placement: If True, doesn't attempt to change the input placement
                       and can leave it the same. Else forces a change.

    Returns:
    ---
    placement: 2D List of placement. If the element at index [i][j] is 1,
               it means that service i is placed at cluster j

    Raises:
    ---
    GurobiError: If there is an issue with the Gurobi optimization model
    ValueError: If input lists have inconsistent lengths
    """

    num_clusters = len(cluster_capacities)
    num_nodes = len(cpu_limits)

    model = Model("MultiClusterPlacement")

    # Define decision variables
    E = [f"E{i}" for i in range(1, num_clusters + 1)]  # List of EC clusters
    S = [f"s{i}" for i in range(num_nodes)]  # List of application graph nodes

    # Replicas and dependencies
    d = [0, 0]

    # Assume you have the previous placement as described before
    y = {
        f"s{app_node_index}": {
            cluster: current_placement[app_node_index][cluster_index]
            for cluster_index, cluster in enumerate(E)
        }
        for app_node_index in range(num_nodes)
    }

    # Define decision variables
    x = {}

    for s in S:
        for e in E:
            x[s, e] = model.addVar(vtype=GRB.BINARY, name=f"x_{s}_{e}")

    # Update model
    model.update()

    # Define objective function
    w_dep = 1  # Deployment cost weight
    w_re = 1  # Re-optimization cost weight

    # Set objective to minimize the combined deployment and re-optimization costs
    model.setObjective(
        quicksum(w_dep * x[s, e] for s in S for e in E)
        + quicksum(w_re * y[s][e] * (y[s][e] - x[s, e]) for s in S for e in E),
        GRB.MINIMIZE,
    )

    # Define constraints
    for s in S:
        model.addConstr(quicksum(x[s, e] for e in E) == 1, name=f"constraint1_{s}")

    change_placement_value = 0 if initial_placement else -1
    # Define the additional constraints for placement changes
    model.addConstr(
        quicksum(y[s][e] * (x[s, e] - y[s][e]) for s in S[1:] for e in E)
        <= change_placement_value,
        name="constraint_additional_less_than",
    )

    for e in E:
        model.addConstr(
            quicksum(
                x[s, e] * cpu_limits[S.index(s)] * replicas[S.index(s)] for s in S[1:]
            )
            <= cluster_capacities[E.index(e)],
            name=f"constraint2_{e}",
        )

    for e in E:
        for s in S[1:]:
            model.addConstr(
                x[s, e] * acceleration[S.index(s)] <= cluster_acceleration[E.index(e)],
                name=f"constraint4_{s}_{e}",
            )

    for i in range(1, num_nodes):
        model.addConstr(quicksum(x[S[i], e] * x[S[i - 1], e] for e in E) >= d[i - 1])

    # Add constraint for fixed placement of s0
    model.addConstr(x["s0", "E1"] == 1, name="constraint_s0_placement")

    model.optimize()

    placement = [[0] * num_clusters for _ in range(num_nodes)]
    for service_index, s in enumerate(S):
        for cluster_index, e in enumerate(E):
            if int(x[s, e].X) == 1:
                placement[service_index][cluster_index] = 1
    return placement
