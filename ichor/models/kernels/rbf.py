import numpy as np
from typing import Optional

from ichor.models.kernels.distance import Distance
from ichor.models.kernels.kernel import Kernel


class RBF(Kernel):
    """Implementation of Radial Basis Function (RBF) kernel
    When each dimension has a separate lengthscale, this is also called the RBF-ARD kernel. Note that
    we use thetas instead of true lengthscales.

    .. math::
        \theta = \frac{1}{2l^2}

    where `l` is the lengthscale value.
    """

    def __init__(self, thetas: np.ndarray, active_dims: Optional[np.ndarray] = None):
        super().__init__(active_dims)
        self._thetas = thetas

    @property
    def params(self):
        return self._thetas

    def k(self, x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
        """
        Calculates RBF covariance matrix from two sets of points

        Args:
            :param: `x1` np.ndarray of shape n x ndimensions:
                First matrix of n points
            :param: `x2` np.ndarray of shape m x ndimensions:
                Second matrix of m points, can be identical to the first matrix `x1`

        Returns:
            :type: `np.ndarray`
                The RBF covariance matrix of shape (n, m)
        """

        true_lengthscales = np.sqrt(1.0/(2 * self._thetas))
        tmp_x1 = x1[:,self.active_dims] / true_lengthscales[self.active_dims]
        tmp_x2 = x2[:,self.active_dims] / true_lengthscales[self.active_dims]
        dist = Distance.squared_euclidean_distance(tmp_x1, tmp_x2)
        return np.exp(-0.5 * dist)

    def __repr__(self):
        return f"{self.__class__.__name__}: thetas: {self._thetas}"
