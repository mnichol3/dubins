from ._dubins_base import Turn
from .dubins_csc import DubinsCSC
from .dubins_loopback import DubinsLoopback
from .mathlib import cos, subtract_azimuths
from .point import Waypoint


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
    d = get_dubins(origin, terminus, radius, turns)

    if isinstance(d, DubinsLoopback):
        kwargs.pop('delta_d', None)

    return d.create_path(**kwargs)


def get_dubins(
    origin: Waypoint,
    terminus: Waypoint,
    radius: float,
    turns: Turn,
) -> DubinsCSC | DubinsLoopback:
    """Instantiate and return a Dubins class.

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

    Returns
    -------
    DubinsCSC | DubinsLoopback
    """
    wpt_azi = subtract_azimuths(origin.azimuth_to(terminus), origin.crs)
    are_orthogonal = 89 < wpt_azi < 91

    if are_orthogonal:
        wpt_dist = origin.distance_to(terminus)
    else:
        wpt_dist = abs(origin.distance_to(terminus) * cos(wpt_azi))

    if wpt_dist < 2 * radius:
        if are_orthogonal:
            return DubinsLoopback(origin, terminus, radius, turns)

        return DubinsCSC(
            origin, terminus, radius, [Turn.reverse(turns[0]), turns[1]])

    return DubinsCSC(origin, terminus, radius, turns)
