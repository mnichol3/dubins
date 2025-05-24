"""This module contains various math constants and functions.

Constants
---------
* NMI_2_M: Nautical miles (nmi) to meters conversion factor.
* M_2_NMI: Meters to nautical miles conversion factor.
"""
import math


NMI_2_M = 1852
M_2_NMI = round(1 / NMI_2_M, 8)


def arccos(val: float) -> float:
    """Compute the trigonometric inverse cosine and return the value
    in degrees."""
    return math.degrees(math.acos(val))


def arcsin(val: float) -> float:
    """Compute the trigonometric inverse sine and return the value
    in degrees."""
    return math.degrees(math.asin(val))


def arctan(val: float) -> float:
    """Compute the trigonometric inverse tangent and return the value
    in degrees."""
    return math.degrees(math.atan(val))


def arctan2(y: float, x: float) -> float:
    """Compute the trigonometric inverse tangent and return the value
    in degrees."""
    return math.degrees(math.atan2(y, x))


def cos(val: float) -> float:
    """Compute the cosine of an angle given in degrees.

    Parameters
    ----------
    val: float
        Angle, in degrees.

    Returns
    -------
    float
    """
    return math.cos(math.radians(val))


def sin(val: float) -> float:
    """Compute the sine of an angle given in degrees.

    Parameters
    ----------
    val: float
        Angle, in degrees.

    Returns
    -------
    float
    """
    return math.sin(math.radians(val))


def sec(val: float) -> float:
    """Compute the secant of an angle given in degrees.

    Parameters
    ----------
    val: float
        Angle, in degrees.

    Returns
    -------
    float
    """
    return 1 / math.cos(math.radians(val))


def sech(val: float) -> float:
  """Compute the hyperbolic secant of the given value."""
  return 1 / math.cosh(val)


def tan(val: float) -> float:
    """Compute the tangent of an angle given in degrees.

    Parameters
    ----------
    val: float
        Angle, in degrees.

    Returns
    -------
    float
    """
    return math.tan(math.radians(val))


def normalize_angle(val: float) -> float:
    """Normalize an angle to (-180, 180]."""
    if val > 180:
        return val % -360
    elif val <= -180:
        return val % 360

    return val
