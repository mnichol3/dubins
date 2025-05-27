"""
Python module for generating simple Dubins paths.

Requirements: Python 3.11, matplotlib.

Download: https://github.com/mnichol3/dubins
"""
from ._dubins_base import DubinsType, Turn
from .dubins_csc import DubinsCSC
from .dubins_loopback import DubinsLoopback
from .point import Waypoint
from .plotting import plot_path

__all__ = [
    "DubinsLoopback",
    "DubinsCSC",
    "DubinsType",
    "Turn",
    "Waypoint",
    "plot_path",
]


def create_path(
    origin: Waypoint,
    terminus: Waypoint,
    radius: float,
    turns: Turn,
    **kwargs,
) -> list[tuple[float, float]]:
    """Create a Dubins path and return the waypoints.

    This function handles the determination of which Dubins class to use
    based on the distance between the origin and terminus points and the
    specified turn radius.

    Parameters
    ----------
    origin: Waypoint
        Fly-to Point defining the beginning of the Dubins path.
    terminus: Waypoint
        Fly-to Point defining the end of the Dubins path.
    radius: float
        Turn radius, in meters.
    turns: list[Turn]
            Turns to execute. Must have a length of 2.
    kwargs: str, optional
        Keyword arguments to pass to construct_path() methods.

    Returns
    -------
    list of tuple[float, float]
        Dubins path waypoint x- and y-coordinates.
    """
    if origin.distance_to(terminus) >= 2 * radius:
        path = DubinsCSC(origin, terminus, radius, turns)
    else:
        path = DubinsLoopback(origin, terminus, radius, turns)
        kwargs.pop('delta_d', None)

    return path.create_path(**kwargs)
