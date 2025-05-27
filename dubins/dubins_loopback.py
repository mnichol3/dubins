from typing import TypeAlias

from math import sqrt

from ._dubins_base import DubinsBase, DubinsType, Circle, Turn
from .cartesian import calc_fwd
from .point import Circle, Waypoint
from .mathlib import arccos, normalize_angle


Point: TypeAlias = tuple[float, float]


class DubinsLoopback(DubinsBase):

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
        """
        super().__init__(origin, terminus, radius)

        turn1 = Turn.reverse(turns[0])
        track_spacing = self.origin.distance_to(self.terminus)
        h = sqrt((2 * radius)**2 - track_spacing**2)
        a = (round(arccos(h / (2 * radius)), 4) + origin.crs) * -turn1.value

        circle1 = self._init_circle(origin, turn1)
        self.circles = [
            circle1,
            Circle(*calc_fwd(circle1.xy, a, self.radius*2), turns[1].value),
        ]

        self.d = h
        self.theta = normalize_angle(a + (90 * turn1.value))
        self.psi = origin.crs_norm

    def create_path(self, delta_psi: float = 1) -> list[Point]:
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
        list of Point
            X- and y-coordinates of path waypoints.
        """
        waypoints = []

        waypoints.extend(
            self._calc_arc_points(self.circles[0], self.theta, delta_psi))

        waypoints.extend(
            self._calc_arc_points(
                self.circles[1],
                self.terminus.crs_norm,
                delta_psi))

        waypoints.append(calc_fwd(waypoints[-1], self.terminus.crs, self.d))

        return waypoints
