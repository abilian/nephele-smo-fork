"""Replica scaling algorithm."""

from __future__ import annotations

import time

import requests
from devtools import debug
from gurobipy import GRB, Model, quicksum

from .kube_helper import KubeHelper
from .prometheus_helper import PrometheusHelper


def scaling_loop(
    graph_name,
    acceleration,
    alpha,
    beta,
    cluster_capacity,
    cluster_acceleration,
    maximum_replicas,
    managed_services,
    decision_interval,
    config_file_path,
    prometheus_host,
    stop_event,
) -> None:
    """Runs the scaling algorithm periodically.

    The function continuously monitors and adjusts the number of replicas for a
    list of managed services based on request rates and predefined scaling parameters.

    Input:
    - graph_name: Name of the graph used for determining the scaling logic.
    - acceleration: The acceleration factor for scaling decisions.
    - alpha: A scaling parameter that influences decision making.
    - beta: A scaling parameter that influences decision making.
    - cluster_capacity: Maximum capacity of the cluster.
    - cluster_acceleration: The acceleration factor for the cluster.
    - maximum_replicas: The maximum number of replicas allowed for any service.
    - managed_services: List of services that are managed by the scaling loop.
    - decision_interval: The interval (in seconds) between scaling decisions.
    - config_file_path: Path to the Kubernetes configuration file.
    - prometheus_host: Host address of the Prometheus server.
    - stop_event: An event to signal stopping of the scaling loop.
    """

    # Initialize helpers for Kubernetes and Prometheus
    kube_helper = KubeHelper(config_file_path)
    prometheus_helper = PrometheusHelper(prometheus_host, decision_interval)

    # Ensure initial replica counts are available for all services
    while True:
        previous_replicas = [
            kube_helper.get_replicas(service) for service in managed_services
        ]
        if None in previous_replicas:
            # Wait and retry if any replica count is unavailable
            time.sleep(5)
        else:
            break

    # Retrieve current CPU limits for managed services
    previous_replicas = [
        kube_helper.get_replicas(service) for service in managed_services
    ]
    cpu_limits = [kube_helper.get_cpu_limit(service) for service in managed_services]

    # Main scaling loop - runs until stop_event is set
    while not stop_event.is_set():
        request_rates = []
        for service in managed_services:
            # Special handling for 'image-compression-vo' service
            if service == "image-compression-vo":
                request_rates.append(
                    prometheus_helper.get_request_rate("noise-reduction")
                )
            else:
                request_rates.append(prometheus_helper.get_request_rate(service))

        debug(
            request_rates,
            previous_replicas,
            cpu_limits,
            acceleration,
            alpha,
            beta,
            cluster_capacity,
            cluster_acceleration,
            maximum_replicas,
        )

        # Determine new replicas based on decision criteria
        new_replicas = decide_replicas(
            request_rates,
            previous_replicas,
            cpu_limits,
            acceleration,
            alpha,
            beta,
            cluster_capacity,
            cluster_acceleration,
            maximum_replicas,
        )

        if new_replicas is None:
            # TODO: don't hardcode the URL
            requests.get(f"http://localhost:8000/graph/{graph_name}/placement")
        else:
            for idx, replicas in enumerate(new_replicas):
                kube_helper.scale_deployment(managed_services[idx], replicas)

        # TODO: use logging
        debug(new_replicas)

        # Update previous replicas for the next iteration
        previous_replicas = new_replicas

        # Pause before the next decision cycle
        time.sleep(decision_interval)


def decide_replicas(
    request_rates,
    previous_replicas,
    cpu_limits,
    acceleration,
    alpha,
    beta,
    cluster_capacity,
    cluster_acceleration,
    maximum_replicas,
) -> list[int] | None:
    """Determines the optimal number of replicas for each service to handle
    incoming request rates.

    Parameters
    ---
    request_rates: List of incoming rates of requests
    previous_replicas: List of previous replicas
    cpu_limits: List of CPU limits
    acceleration: List of acceleration flags
    alpha: Coefficient of the equation y = a * x + b
           where x is the number of replicas and y is the
           maximum number of requests the service can handle
    beta: Coefficient in the same equation as alpha mentioned above
    cluster_capacity: Cluster CPU capacity in cores
    cluster_acceleration: Acceleration enabled for cluster flag
    maximum_replicas: Maximum number of replicas allowed for each service

    Returns
    ---
    solution: List with replicas for each service, or None if no optimal solution is found.

    Raises
    ---
    GurobiError: If there is an issue with the Gurobi optimization process.
    ValueError: If the input lists are inconsistent in length.
    """

    # Define the number of application nodes
    num_nodes = len(previous_replicas)

    # Create a Gurobi model
    model = Model("AutoScalingOptimization")

    # Define decision variables
    r_current = {}
    r_prev = {}
    # to define the scaling (transformation) cost with absolute of difference
    abs_diff = {}

    for s in range(num_nodes):
        r_current[s] = model.addVar(vtype=GRB.INTEGER, name=f"r_{s}_current")
        r_prev[s] = previous_replicas[s]
        abs_diff[s] = model.addVar(vtype=GRB.INTEGER, name=f"abs_diff_{s}")

    # Update model
    model.update()

    # Absolute difference constraints
    for s in range(num_nodes):
        model.addConstr(
            abs_diff[s] >= r_prev[s] - r_current[s], name=f"abs_diff_pos_{s}"
        )
        model.addConstr(
            abs_diff[s] >= -(r_prev[s] - r_current[s]), name=f"abs_diff_neg_{s}"
        )

    # Example weights (adjust as needed)
    w_util = 0.4
    w_trans = 0.4
    # w_penalty = 0.2

    # Max values for normalization
    max_util_cost = max(maximum_replicas[s] * cpu_limits[s] for s in range(num_nodes))
    max_trans_cost = maximum_replicas

    # Objective function
    model.setObjective(
        w_util
        * quicksum(
            r_current[s] * cpu_limits[s] / max_util_cost for s in range(num_nodes)
        )
        + w_trans * quicksum(abs_diff[s] / max_trans_cost[s] for s in range(num_nodes)),
        # w_penalty * penalty_term,
        GRB.MINIMIZE,
    )

    # Constraints
    model.addConstr(
        quicksum(cpu_limits[s] * r_current[s] for s in range(num_nodes))
        <= cluster_capacity,
        name="cluster_cpu_limit_constraint",
    )
    # Constraints
    for s in range(num_nodes):
        model.addConstr(
            acceleration[s] <= cluster_acceleration, name=f"constraint_acceleration_{s}"
        )
        model.addConstr(
            alpha[s] * r_current[s] + beta[s] >= request_rates[s],
            name=f"constraint_service_rate_{s}",
        )
        model.addConstr(1 <= r_current[s], name=f"lower_bound_replicas{s}")
        model.addConstr(
            r_current[s] <= maximum_replicas[s], name=f"upper_bound_replicas_{s}"
        )

    # Solve the model
    model.optimize()

    # Check the solution status
    if model.status == GRB.Status.OPTIMAL:
        solution = [int(r.X) for r in r_current.values()]
        return solution
    else:
        return None
