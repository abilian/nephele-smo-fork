"""Kubernetes helper class and utility functions."""

from __future__ import annotations

from kubernetes import client, config


class KubeHelper:
    """Kubernetes helper class."""

    def __init__(self, config_file_path, namespace="default"):
        self.namespace = namespace
        self.config_file_path = config_file_path

        config.load_kube_config(config_file=self.config_file_path)

        self.v1_api_client = client.AppsV1Api()

    def get_desired_replicas(self, name):
        """Returns the desired number of replicas for the specified
        deployment."""

        response = self.v1_api_client.read_namespaced_deployment_scale(
            name, self.namespace
        )
        return response.spec.replicas

    def get_replicas(self, name):
        """Returns the current number of replicas for the specified
        deployment."""

        response = self.v1_api_client.read_namespaced_deployment(name, self.namespace)
        return response.status.available_replicas

    def get_cpu_limit(self, name):
        """Returns the current CPU limit for the specific deployment."""

        response = self.v1_api_client.read_namespaced_deployment(name, self.namespace)
        cpu_lim = response.spec.template.spec.containers[0].resources.limits["cpu"]
        if "m" in cpu_lim:
            return float(cpu_lim.replace("m", "")) * 1e-3
        else:
            return float(cpu_lim)

    def scale_deployment(self, name, replicas):
        """Scales the given application to the desired number of replicas."""

        try:
            self.v1_api_client.patch_namespaced_deployment_scale(
                name=name,
                namespace=self.namespace,
                body={"spec": {"replicas": replicas}},
            )
        except Exception as exception:
            print(str(exception))
