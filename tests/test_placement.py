from __future__ import annotations

from smo.utils import constant as c
from smo.utils.placement import (convert_placement, decide_placement,
                                 swap_placement)


def test_convert_placement():
    """
    Input:
        placement:[[1, 0], [1, 0]]
        services: [{'id': 'service1'}, {'id': 'service2'}]
        clusters ['cluster1', 'cluster2']
    Output:
        {'service1': 'cluster1', 'service2': 'cluster1'}
    """
    placement = [[1, 0], [1, 0]]
    services = [{"id": "service1"}, {"id": "service2"}]
    clusters = ["cluster1", "cluster2"]

    expected = {"service1": "cluster1", "service2": "cluster1"}

    result = convert_placement(placement, services, clusters)
    assert result == expected


def test_swap_placement():
    """
    Input:
        {'service1': 'cluster1', 'service2': 'cluster1'}
    Output:
        {'cluster1': ['service1', 'service2']}
    """
    service_dict = {"service1": "cluster1", "service2": "cluster1"}
    expected = {"cluster1": ["service1", "service2"]}

    result = swap_placement(service_dict)
    assert result == expected


def test_decide_placement():
    placement = decide_placement(
        c.CLUSTER_CAPACITY_LIST,
        c.CLUSTER_ACCELERATION_LIST,
        c.CPU_LIMITS_LIST,
        c.ACCELERATION_LIST,
        c.REPLICAS_LIST,
        c.INITIAL_PLACEMENT,
        initial_placement=True,
    )
    expected = [[1, 0], [1, 0], [1, 0]]
    assert placement == expected
