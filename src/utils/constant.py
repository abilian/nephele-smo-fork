"""Constant values for development ease.

To be replaced int the future.
"""

from __future__ import annotations

SERVICES = ["image-compression-vo", "noise-reduction", "image-detection"]
CLUSTERS = ["netmode-cluster", "netmode-cluster2"]
CLUSTER_CAPACITY = {"netmode-cluster": 4, "netmode-cluster2": 6}
CLUSTER_CAPACITY_LIST = [value for value in CLUSTER_CAPACITY.values()]
CLUSTER_ACCELERATION = {"netmode-cluster": 0, "netmode-cluster2": 0}
CLUSTER_ACCELERATION_LIST = [value for value in CLUSTER_ACCELERATION.values()]
# Info that comes from intent or after intent translation
CPU_LIMITS = {"image-compression-vo": 0.5, "noise-reduction": 1, "image-detection": 1}
CPU_LIMITS_LIST = [value for value in CPU_LIMITS.values()]
ACCELERATION = {"image-compression-vo": 0, "noise-reduction": 0, "image-detection": 0}
ACCELERATION_LIST = [value for value in ACCELERATION.values()]
REPLICAS = {"image-compression-vo": 1, "noise-reduction": 1, "image-detection": 1}
REPLICAS_LIST = [value for value in REPLICAS.values()]
INITIAL_PLACEMENT = [[1, 0], [1, 0], [1, 0]]
graph_placement = [[1, 0], [1, 0], [1, 0]]
MAXIMUM_REPLICAS = {
    "image-compression-vo": 3,
    "noise-reduction": 3,
    "image-detection": 3,
}
ALPHA = {
    "image-compression-vo": 33.33,
    "noise-reduction": 0.533,
    "image-detection": 1.67,
}
BETA = {
    "image-compression-vo": -16.66,
    "noise-reduction": -0.416,
    "image-detection": -0.01,
}
DECISION_INTERVAL = 30
PROMETHEUS_HOST = "http://host.docker.internal:30347"
GRAPH_GRAFANA = "http://10.0.2.114:30150/d/edgr2834xi2v4f/image-detection-graph?from=now-5m&to=now&orgId=1&var-service=All"
SERVICES_GRAFANA = {
    "image-compression-vo": "http://10.0.2.114:30150/d/bdh4oxli71l34b/image-compression-vo?orgId=1&from=now-5m&to=now",
    "noise-reduction": "http://10.0.2.114:30150/d/bdh4ozx4tnw8wd/noise-reduction?orgId=1&from=now-5m&to=now",
    "image-detection": "http://10.0.2.114:30150/d/bdh4p0uz3n3eob/image-detection?orgId=1&from=now-5m&to=now",
}
RESOURCES = {
    "image-compression-vo": {"cpu": "0.5", "memory": "1Gi", "gpu": 0},
    "noise-reduction": {"cpu": "1", "memory": "1Gi", "gpu": 0},
    "image-detection": {"cpu": "1", "memory": "1Gi", "gpu": 0},
}
