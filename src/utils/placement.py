"""Application node placement related functionalities."""


def decide_placement(name, intent):
    """
    Function that takes into account placement constraints
    and finds an optimal placement.
    """

    if name == 'vo1':
        return ['netmode-cluster']
    else:
        return ['netmode-cluster2']
