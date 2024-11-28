from __future__ import annotations

import math

import requests


class PrometheusHelper:
    """Helper class to execute Prometheus queries.

    This class provides methods to query a Prometheus server for specific metrics
    related to service latency, request rate, and CPU utilization. It constructs
    Prometheus query strings and processes the results.

    Attributes:
        prometheus_host: The URL or IP address of the Prometheus server.
        time_window: The time duration for which metrics are queried.
        time_unit: The unit of time for the time window (default is seconds "s").
    """

    def __init__(self, prometheus_host, time_window, time_unit="s"):
        self.prometheus_host = prometheus_host
        self.time_window = time_window
        self.time_unit = time_unit

    def get_latency(self, name):
        """Return the latency of a service."""

        prometheus_latency_metric_query = (
            "(sum(rate(flask_http_request_duration_seconds_sum"
            '{{service="{0}"}}[{1}{2}])) by (service))'
            "/(sum(rate(flask_http_request_duration_seconds_count"
            '{{service="{0}"}}[{1}{2}])) by (service))'.format(
                name, self.time_window, self.time_unit
            )
        )

        # Get latency
        latency = self._query(prometheus_latency_metric_query)
        if math.isnan(latency):
            latency = 30
        return latency

    def get_request_rate(self, name):
        """Return the request completion rate of the service."""

        prometheus_request_rate_metric_query = (
            f'sum(rate(flask_http_request_total{{service="{name}"}}'
            f"[{self.time_window}{self.time_unit}]))by(service)"
        )

        # Get arrival rate
        request_rate = self._query(prometheus_request_rate_metric_query)
        if math.isnan(request_rate):
            request_rate = 0.0
        return request_rate

    def get_cpu_util(self, name):
        """Returns the CPU utilizations percentage of the service."""

        cpu_util_metric_query = (
            "round(100 *sum(rate(container_cpu_usage_seconds_total"
            '{{container=~"{0}.*"}}[40s])) by (pod_name, container_name)'
            '/sum(kube_pod_container_resource_limits{{container=~"{0}.*",resource="cpu"}})'
            "by (pod_name, container_name))".format(name)
        )

        # Get cpu_util
        cpu_util = self._query(cpu_util_metric_query)
        if math.isnan(cpu_util):
            cpu_util = 0
        return cpu_util

    def _query(self, query_name: str):
        """Helper function that fetches the desired metric from the prometheus
        endpoint."""

        prometheus_endpoint = f"{self.prometheus_host}/api/v1/query"
        response = requests.get(
            prometheus_endpoint,
            params={
                "query": query_name,
            },
            timeout=5,
        )

        # Parse the JSON response and extract the result
        results = response.json()["data"]["result"]
        if len(results) > 0:
            return float(results[0]["value"][1])
        else:
            return float("NaN")
