import math

from ichor.core.common.types.itypes import Scalar


def order_of_magnitude(n: Scalar) -> int:
    """
    Returns the order of magnitude of n
    e.g.

    .. code-block:: text

        >>> order_of_magnitude(100)
        2
        >>> order_of_magnitude(0.0001)
        -4

    :param n: number to calculate order of magnitude of
    :return: order of magnitude of n
    """
    return math.floor(math.log(n, 10))


def kronecker_delta(p1, p2):

    if p1 == p2:
        return 1
    return 0
