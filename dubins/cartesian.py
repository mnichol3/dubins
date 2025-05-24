"""Math functions for the Cartesian coordinate system."""
from math import sqrt

from .mathlib import arctan2, cos, sin
from .util import round_return


def azimuth(val: float) -> float:
    """Make sure an azimuth falls in [0, 360]."""
    return val % 360.


def azimuth_to_uangle(azi: float) -> float:
    """Convert an azimuth to its corresponding angle on the unit circle.

    Parameters
    ----------
    azi: float
        Azimuth, in degrees.

    Returns
    -------
    float
        Unit angle, in degrees.
    """
    return (90 - azi) % 360


@round_return(2)
def calc_azimuth(
    point1: tuple[float, float],
    point2: tuple[float, float],
) -> float:
    """Calculate the azimuth of the vector defined by two points.

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


@round_return(2)
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

    return sqrt((x2-x1)**2 + (y2-y1)**2)


@round_return(8)
def calc_fwd(
    origin: tuple[float, float],
    azimuth: float,
    dist: float,
) -> tuple[float, float]:
    """Calculate the coordinates of a new point given a starting point,
    azimuth, and distance.

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
