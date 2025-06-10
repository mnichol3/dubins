from math import ceil

from ._dubins_base import Turn
from .dubins_csc import DubinsCSC
from .dubins_loopback import DubinsLoopback
from .mathlib import calc_fwd, sin
from .point import IntermediatePoint, Waypoint


def create_path(
    origin: Waypoint,
    terminus: Waypoint,
    radius: float,
    turns: list[Turn],
    **kwargs,
) -> list[IntermediatePoint]:
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
    list of IntermediatePoint
        IntermediatePoints forming the Dubins path.
    """
    d = get_dubins(origin, terminus, radius, turns)

    if isinstance(d, DubinsLoopback):
        kwargs.pop('delta_d', None)

    return d.create_path(**kwargs)


def get_dubins(
    origin: Waypoint,
    terminus: Waypoint,
    radius: float,
    turns: list[Turn],
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
    wpt_dist = round(origin.distance_to(terminus), 2)
    beta = origin.calc_beta(terminus)
    are_orthogonal = (89 < beta < 91) or (269 < beta < 271)

    if are_orthogonal:
        xtrack_dist = wpt_dist
    else:
        xtrack_dist = round(
            abs(origin.distance_to(terminus)
                * sin(origin.calc_beta(terminus))), 2)

    if are_orthogonal:
        if xtrack_dist < 2 * radius:
            return DubinsLoopback(origin, terminus, radius, turns)
        else:
            return DubinsCSC(origin, terminus, radius, turns)
    else:
        if xtrack_dist >= 2 * radius:
            return DubinsCSC(origin, terminus, radius, turns)
        else:
            # if wpt_dist >= 2 * radius:
            #     return DubinsCSC(origin, terminus, radius,
            #                      [turns[0], Turn.reverse(turns[1])])
            # else:

            loopback = DubinsLoopback(origin, terminus, radius, turns)

            if beta > 90:
                delta_y = wpt_dist * sin(beta - 90)
                if delta_y > loopback.d:
                    origin = Waypoint(
                        *calc_fwd(origin.xy, origin.crs,
                                  ceil(abs(loopback.d - delta_y))),
                        origin.crs,
                    )

                    return DubinsLoopback(origin, terminus, radius, turns)


            return loopback
