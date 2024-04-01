"""Replica scaling algorithm."""

import time

import requests
from gurobipy import Model, GRB, quicksum

from utils.kube_helper import KubeHelper
from utils.prometheus_helper import PrometheusHelper


def scaling_loop(
    graph_name, acceleration, alpha, beta, cluster_capacity, cluster_acceleration,
    maximum_replicas, managed_services, decision_interval, config_file_path,
    prometheus_host, stop_event
):
    """Runs the scaling algorithm periodically."""

    kube_helper = KubeHelper(config_file_path)
    prometheus_helper = PrometheusHelper(prometheus_host, decision_interval)
    while True:
        previous_replicas = [kube_helper.get_replicas(service) for service in managed_services]
        if None in previous_replicas:
            time.sleep(5)
        else:
            break

    previous_replicas = [kube_helper.get_replicas(service) for service in managed_services]
    cpu_limits = [kube_helper.get_cpu_limit(service) for service in managed_services]

    while not stop_event.is_set():
        request_rates = []
        for service in managed_services:
            if service == 'image-compression-vo':
                request_rates.append(prometheus_helper.get_request_rate('noise-reduction'))
            else:
                request_rates.append(prometheus_helper.get_request_rate(service))
        print(request_rates, previous_replicas, cpu_limits, acceleration, alpha,
            beta, cluster_capacity, cluster_acceleration, maximum_replicas)

        new_replicas = decide_replicas(
            request_rates, previous_replicas, cpu_limits, acceleration, alpha,
            beta, cluster_capacity, cluster_acceleration, maximum_replicas
        )
        if new_replicas is None:
            requests.get(f'http://localhost:8000/graph/{graph_name}/placement')
        else:
            for idx, replicas in enumerate(new_replicas):
                kube_helper.scale_deployment(managed_services[idx], replicas)
        print(new_replicas)

        previous_replicas = new_replicas
        time.sleep(decision_interval)


def decide_replicas(
    request_rates, previous_replicas, cpu_limits, acceleration, alpha, beta,
    cluster_capacity, cluster_acceleration, maximum_replicas
):
    """
    Parameters
    ---
    request_rates: List of incoming rates of requests
    previous_replicas: List of previous replicas
    cpu_limits: List of CPU limits
    acceleration: List of acceleration flags
    alpha: Coefficient of the equation y = a * x + b
           where x is the number of replicas and y is the
           maximum number of request the service can handle
    beta: Coefficient in the same equation as alpha mentioned above
    cluster_capacity: Cluster CPU capacity in cores
    cluster_acceleration: Acceleration enabled for cluster flag

    Return value
    ---
    solution: List with replicas for each service
    """

    # Define the number of application nodes
    num_nodes = len(previous_replicas)

    # Create a Gurobi model
    model = Model("AutoScalingOptimization")

    # Define decision variables
    r_current = {}
    r_prev = {}
    abs_diff = {}  # to define the scaling (transformation) cost with absolute of difference

    for s in range(num_nodes):
        r_current[s] = model.addVar(vtype=GRB.INTEGER, name=f"r_{s}_current")
        r_prev[s] = previous_replicas[s]  # Set the previously deployed replicas
        abs_diff[s] = model.addVar(vtype=GRB.INTEGER, name=f"abs_diff_{s}")

    # Update model
    model.update()

    # Absolute difference constraints
    for s in range(num_nodes):
        model.addConstr(abs_diff[s] >= r_prev[s] - r_current[s], name=f"abs_diff_pos_{s}")
        model.addConstr(abs_diff[s] >= -(r_prev[s] - r_current[s]), name=f"abs_diff_neg_{s}")

    # Example weights (adjust as needed)
    w_util = 0.4
    w_trans = 0.4
    # w_penalty = 0.2

    # Max values for normalization
    max_util_cost = max(maximum_replicas[s] * cpu_limits[s] for s in range(num_nodes))
    max_trans_cost = maximum_replicas

    # Penalty term: normalized percentage of over-provisioning
    # penalty_term =  quicksum((r_current[s]*q[s] - request_rates[s] / q[s]) / (maximum_replicas*q[s] - request_rates[s] / q[s]) for s in range(num_nodes))

    # Objective function
    model.setObjective(
        w_util * quicksum(r_current[s] * cpu_limits[s] / max_util_cost for s in range(num_nodes)) +
        w_trans * quicksum(abs_diff[s] / max_trans_cost[s] for s in range(num_nodes)),
        # w_penalty * penalty_term,
        GRB.MINIMIZE
    )

    # Constraints
    model.addConstr(quicksum(cpu_limits[s] * r_current[s] for s in range(num_nodes)) <= cluster_capacity, name="cluster_cpu_limit_constraint")
    # Constraints
    for s in range(num_nodes):
        model.addConstr(acceleration[s] <= cluster_acceleration, name=f"constraint_acceleration_{s}")
        model.addConstr(alpha[s] * r_current[s] + beta[s] >= request_rates[s], name=f"constraint_service_rate_{s}")
        model.addConstr(1 <= r_current[s], name=f"lower_bound_replicas{s}")
        model.addConstr(r_current[s] <= maximum_replicas[s], name=f"upper_bound_replicas_{s}")

    # Solve the model
    model.optimize()

    # Check the solution status
    if model.status == GRB.Status.OPTIMAL:
        solution = [int(r.X) for r in r_current.values()]
        return solution
    else:
        return None
