from __future__ import annotations

import math

import requests


class PrometheusHelper:
    """Helper class to execute Prometheus queries."""

    def __init__(self, prometheus_host, time_window, time_unit="s"):
        self.prometheus_host = prometheus_host
        self.time_window = time_window
        self.time_unit = time_unit

    def get_latency(self, name):
        """Returns the latency of a service."""

        prometheus_latency_metric_name = (
            "(sum(rate(flask_http_request_duration_seconds_sum"
            '{{service="{0}"}}[{1}{2}])) by (service))'
            "/(sum(rate(flask_http_request_duration_seconds_count"
            '{{service="{0}"}}[{1}{2}])) by (service))'.format(
                name, self.time_window, self.time_unit
            )
        )

        # Get latency
        latency = self.query_prometheus(
            self.prometheus_host, prometheus_latency_metric_name
        )
        if math.isnan(latency):
            latency = 30
        return latency

    def get_request_rate(self, name):
        """Returns the request completion rate of the service."""

        prometheus_request_rate_metric_name = (
            'sum(rate(flask_http_request_total{{service="{0}"}}'
            "[{1}{2}]))by(service)".format(name, self.time_window, self.time_unit)
        )

        # Get arrival rate
        request_rate = self.query_prometheus(
            self.prometheus_host, prometheus_request_rate_metric_name
        )
        if math.isnan(request_rate):
            request_rate = 0.0
        return request_rate

    def get_cpu_util(self, name):
        """Returns the CPU utilizations percentage of the service."""

        cpu_util_metric_name = (
            "round(100 *sum(rate(container_cpu_usage_seconds_total"
            '{{container=~"{0}.*"}}[40s])) by (pod_name, container_name)'
            '/sum(kube_pod_container_resource_limits{{container=~"{0}.*",resource="cpu"}})'
            "by (pod_name, container_name))".format(name)
        )

        # Get cpu_util
        cpu_util = self.query_prometheus(self.prometheus_host, cpu_util_metric_name)
        if math.isnan(cpu_util):
            cpu_util = 0
        return cpu_util

    def query_prometheus(self, prometheus_host, query_name):
        """Helper function that fetches the desired metric from the prometheus
        endpoint."""

        prometheus_endpoint = f"{prometheus_host}/api/v1/query"
        response = requests.get(
            prometheus_endpoint,
            params={
                "query": query_name,
            },
            timeout=5,
        )

        results = response.json()["data"]["result"]
        if len(results) > 0:
            return float(results[0]["value"][1])
        else:
            return float("NaN")
