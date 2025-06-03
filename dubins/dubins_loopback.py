from math import sqrt
from typing import TypeAlias

from ._dubins_base import DubinsBase, DubinsType, Circle, Turn
from .point import Circle, IntermediatePoint, Waypoint
from .mathlib import (
    calc_distance, calc_fwd, arccos, sin, normalize_angle, subtract_azimuths)


Point: TypeAlias = tuple[float, float]


class DubinsLoopback(DubinsBase):
    """
    Class to construct a Dubins "loopback" path, where the size of the turn
    radius forces the platform to turn away from the terminus point before
    turning back towards it and completing the path.

    Attributes
    ----------
    origin: Waypoint
        Fly-to Point defining the beginning of the dubins path.
    terminus: Waypoint
            Fly-to Point defining the end of the dubins path.
    radius: float
        Turn radius, unitless.
    length: float
        Length of the path, unitless.
    circles: list[Circle]
        Circles defining the arcs to rotate about to create the path.
    psi: float
        Instantaneous platform heading, in degrees (-180, 180].
    theta: float
        Heading of the vector connecting the two tangent points of the circles
        defining the arcs in the curves, in degrees (-180, 180].
    d: float
        Length of the vector connecting the two tangent points of the circles
        defining the arcs in the curves, untiless.
    case: DubinsType
        Enum defining the Dubins path type.

    Example Usage
    -------------
    >>> from dubins import DubinsLoopback, Turn, Waypoint
    >>> origin = Waypoint(10, 0, 0)
    >>> terminus = Waypoint(0, 4, 180)
    >>> radius = 6
    >>> turns = [Turn.LEFT, Turn.LEFT]
    >>> dub = DubinsLoopback(origin, terminus, radius, turns)
    >>> points = dub.create_path(delta_psi=1)
    """

    case = DubinsType.LOOPBACK

    def __init__(
        self,
        origin: Waypoint,
        terminus: Waypoint,
        radius: float,
        turns: list[Turn],
    ):
        """Instantiate a new DubinsPath.

        Parameters
        ----------
        origin: Waypoint
            Fly-to Point defining the beginning of the dubins path.
        terminus: Waypoint
            Fly-to Point defining the end of the dubins path.
        radius: float
            Turn radius, in meters.
        turns: list[Turn]
            Turns to execute. Must have a length of 2.

        Notes
        -----
        * variable `a` is the angle, measured in degrees from the positive
          y-axis, between the centers of the two circles forming the arcs
          of the Dubins path.
        * variable `h` is something
        """
        super().__init__(origin, terminus, radius)

        wpt_azi = subtract_azimuths(origin.azimuth_to(terminus), origin.crs)

        if 89 < wpt_azi < 91:
            track_spacing = self.origin.distance_to(self.terminus)
        else:
            track_spacing = abs(origin.distance_to(terminus) * sin(wpt_azi))

        turn1 = Turn.reverse(turns[0])
        h = sqrt((2 * radius)**2 - track_spacing**2)
        # a = (round(arccos(h / (2 * radius)), 4) + origin.crs) * -turn1.value
        a = origin.crs + (-turn1.value * round(arccos(h / (2 * radius)), 4))

        circle1 = self._init_circle(origin, turn1)
        self.circles = [
            circle1,
            Circle(*calc_fwd(circle1.xy, a, self.radius*2), turns[1].value),
        ]

        self.d = h
        self.theta = normalize_angle(a + (90 * turn1.value))
        self.psi = origin.crs_norm

    def create_path(
        self,
        delta_d = 1,
        delta_psi: float = 1,
    ) -> list[IntermediatePoint]:
        """Construct a LSL or RSR path.

        Parameters
        ----------
        delta_psi: float, optional
            Interval at which to compute arc points, in degrees. Default is 10.
        delta_d: float, optional
            Interval at which to compute tangent line connecting the two
            circles, in meters. Default is 10.

        Returns
        -------
        list of IntermediatePoint
            IntermediatePoints forming the Dubins path.
        """
        waypoints = []

        waypoints.extend(
            self._calc_arc_points(self.circles[0], self.theta, delta_psi))

        waypoints.extend(
            self._calc_arc_points(
                self.circles[1],
                self.terminus.crs_norm,
                delta_psi))

        if waypoints[-1].distance_to(self.terminus) > delta_d:
            self.d = waypoints[-1].distance_to(self.terminus)
            self.theta = self.terminus.crs_norm
            waypoints.extend(self._calc_line_points(waypoints[-1], delta_d))

        self.length += calc_distance(waypoints[-1].xy, self.terminus.xy)

        return waypoints
