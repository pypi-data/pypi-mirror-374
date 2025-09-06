"""
IQ data represents the in-phase (I) and quadrature (Q) components of a signal. There are two ways to represent
single-channel IQ signals:

#. **Complex 1xN Format:** In the complex 1xN format, the IQ data is represented as a 2D array of complex numbers with
   shape 1xN. In this format, the real part of each complex number represents the in-phase component, while the
   imaginary part represents the quadrature component.
#. **Real 2xN Format:** In the real 2xN format, the IQ data is represented as a 2D array of real numbers with shape
   2xN. In this format, the first row contains the in-phase components, while the second row contains the quadrature
   components.

This submodule provides functions to verify and convert between these two formats.
"""

import numpy as np
from numpy.typing import ArrayLike


def convert_to_2xn(arr: np.ndarray) -> np.ndarray:
    """Convert arr to the real 2xN format. If arr is already real 2xN, then you'll get back a copy.

    :param arr: Array of IQ samples, in the complex 1XN format.
    :type arr: array_like

    :return: The provided signal, in the real 2xN format.
    :rtype: np.ndarray
    """
    if is_1xn(arr):
        return np.vstack((np.real(arr[0]), np.imag(arr[0])))

    elif is_2xn(arr):
        return np.copy(arr)

    else:
        raise ValueError("arr is neither complex 1xN nor real 2xN.")


def convert_to_1xn(arr: np.ndarray) -> np.ndarray:
    """Convert arr to the complex 1xN format. If arr is already complex 1xN, then you'll get back a copy.

    :param arr: Array of IQ samples, in the real 2xN format.
    :type arr: np.ndarray

    :return: The provided signal, in the complex 1xN format.
    :rtype: np.ndarray
    """
    if is_2xn(arr):
        return np.expand_dims(a=arr[0, :] + 1j * arr[1, :], axis=0)

    elif is_1xn(arr):
        return np.copy(arr)

    else:
        raise ValueError("arr is neither complex 1xN nor real 2xN.")


def is_1xn(arr: ArrayLike) -> bool:
    """
    :return: True is arr is complex 1xN, False otherwise.
    :rtype: bool
    """
    a = np.asarray(arr)

    if a.ndim == 2 and a.shape[0] == 1 and np.iscomplexobj(a):
        return True
    else:
        return False


def is_2xn(arr: ArrayLike) -> bool:
    """
    :return: True is arr is real 2xN, False otherwise.
    :rtype: bool
    """
    a = np.asarray(arr)

    if a.ndim == 2 and a.shape[0] == 2 and not np.iscomplexobj(a):
        return True
    else:
        return False
