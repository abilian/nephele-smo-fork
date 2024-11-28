"""Kubernetes helper class and utility functions."""

from __future__ import annotations

from kubernetes import client, config


class KubeHelper:
    """Kubernetes helper class.

    This class provides utility methods to interact with a Kubernetes cluster,
    specifically focusing on deployments within a specified namespace. It allows
    retrieving and modifying deployment details such as replicas and CPU limits.

    Input:
    - config_file_path: Path to the Kubernetes configuration file.
    - namespace: The namespace to operate within, default is "default".
    """

    namespace: str
    config_file_path: str
    client: client.AppsV1Api

    def __init__(self, config_file_path, namespace="default"):
        self.namespace = namespace
        self.config_file_path = config_file_path

        config.load_kube_config(config_file=self.config_file_path)

        self.client = client.AppsV1Api()

    def get_desired_replicas(self, name):
        """Return the desired number of replicas for the specified
        deployment."""

        response = self.client.read_namespaced_deployment_scale(name, self.namespace)
        return response.spec.replicas

    def get_replicas(self, name):
        """Return the current number of replicas for the specified
        deployment."""

        response = self.client.read_namespaced_deployment(name, self.namespace)
        return response.status.available_replicas

    def get_cpu_limit(self, name):
        """Returns the current CPU limit for the specific deployment."""

        response = self.client.read_namespaced_deployment(name, self.namespace)
        cpu_lim = response.spec.template.spec.containers[0].resources.limits["cpu"]
        # If CPU limit is specified in millicores, convert it to cores
        if "m" in cpu_lim:
            return float(cpu_lim.replace("m", "")) * 1e-3
        else:
            # Convert CPU limit directly to float if in cores
            return float(cpu_lim)

    def scale_deployment(self, name, replicas):
        """Scales the given application to the desired number of replicas."""

        try:
            self.client.patch_namespaced_deployment_scale(
                name=name,
                namespace=self.namespace,
                body={"spec": {"replicas": replicas}},
            )
        except Exception as exception:
            print(str(exception))
            raise
