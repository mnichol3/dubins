"""This module contains various math constants and functions."""
import math


def calc_azimuth(
    point1: tuple[float, float],
    point2: tuple[float, float],
) -> float:
    """Calculate the azimuth of the vector defined by two points in the
    Cartesian plane.

    Parameters
    ----------
    point1: tuple of float, float
        Point 1 x- and y-coordinates.
    point2: tuple of float, float
        Point 2 x- and y-coordinates.

    Returns
    -------
    float
        Azimuth, in degrees from positive y-axis.
    """
    x1, y1 = point1
    x2, y2 = point2

    return arctan2((x2-x1), (y2-y1)) % 360.


def calc_distance(
    point1: tuple[float, float],
    point2: tuple[float, float],
) -> float:
    """Calculate the Euclidean distance of the vector defined by two points.

    Parameters
    ----------
    point1: tuple of float, float
        Point 1 x- and y-coordinates.
    point2: tuple of float, float
        Point 2 x- and y-coordinates.

    Returns
    -------
    float
        Unitless Euclidean distance.
    """
    x1, y1 = point1
    x2, y2 = point2

    return math.sqrt((x2-x1)**2 + (y2-y1)**2)


def calc_fwd(
    origin: tuple[float, float],
    azimuth: float,
    dist: float,
) -> tuple[float, float]:
    """Calculate the coordinates of a new point in the Cartesian plane given
    a starting point, azimuth, and distance.

    Parameters
    ----------
    origin: tuple of float, float
        Origin x- and y-coordinates.
    azimuth: float
        Azimuth to move along.
    dist: float
        Unitless distance.

    Returns
    -------
    tuple of float, float
        X- and y-coodinates of the new point.
    """
    x, y = origin
    azimuth %= 360.

    return x + dist * sin(azimuth), y + dist * cos(azimuth)


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


def azimuth(val: float) -> float:
    """Make sure an azimuth falls in [0, 360]."""
    return val % 360.


def normalize_angle(val: float) -> float:
    """Normalize an angle to (-180, 180]."""
    normalized = ((val + 180) % 360) - 180

    return 180 if normalized == -180 else normalized


def subtract_azimuths(azi1: float, azi2: float) -> float:
    """Compute the minimum angle between two azimuths.

    Parameters
    ----------
    azi1: float
    azi2: float

    Returns
    -------
    float
    """
    diff = abs(azimuth(azi1) - azimuth(azi2))

    return min(diff, 360 - diff)
