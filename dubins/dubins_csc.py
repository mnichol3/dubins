"""This module a class to construct Dubins paths in Cartesian space."""
from __future__ import annotations
from math import isclose, sqrt
from typing import TypeAlias

from ._dubins_base import DubinsBase, DubinsType, Circle, Turn
from .point import Circle, IntermediatePoint, Waypoint
from .mathlib import arctan, arctan2, normalize_angle


Point: TypeAlias = tuple[float, float]


class DubinsCSC(DubinsBase):
    """Class to compute Curve-Straight-Curve Dubins paths in Cartesian space.

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

    Example usage
    -------------
    >>> from dubins import DubinsCSC, Turn, Waypoint
    >>> origin = Waypoint(10, 0, 60)
    >>> terminus = Waypoint(0, 4, 120)
    >>> radius = 4
    >>> turns = [Turn.RIGHT, Turn.LEFT]
    >>> dub = DubinsCSC(origin, terminus, radius, turns)
    >>> points = dub.create_path(delta_psi=1, delta_d=0.5)

    Reference
    ---------
    Lugo-Cárdenas, Israel & Flores, Gerardo & Salazar, Sergio & Lozano, R..
    (2014). Dubins path generation for a fixed wing UAV. 339-346.
    10.1109/ICUAS.2014.6842272.

    Notes
    -----
    * Contains the following equation & algorithm corrections:
        * Eq. 14 is given as:
                gamma = arctan((2 * radius) / d),
              however its correct form is:
                gamma = arctan(d / (2 * radius))
        * Eq. 20:
            * Eta is given as:
                n = 90 + arctan...
                however its correct form is:
                n = 90 - arctan...
            * Gamma is given as:
                g = arccos((2 * radius) / d)
                however its correct form is:
                g = arctan(d / (2 * radius))
        * The descriptions of the algorithms for all 4 Dubins path types
          (RSR, RSL, LSL, LSR) state psi_n shall start at 0. It should instead
          start at the aircraft's heading measured from the positive y-axis
          over (-180, 180].
    """

    def __init__(
        self,
        origin: Waypoint,
        terminus: Waypoint,
        radius: float,
        turns: list[Turn],
    ):
        """Instantiate a new DubinsCSC.

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
        self.case = DubinsType.from_turns(turns)
        self.circles = self._init_circles(turns)
        self.psi = origin.crs_norm

        if (
            89 <= abs(origin.calc_beta(terminus)) <= 91
            and isclose(origin.distance_to(terminus), 2*radius, abs_tol=1e-3)
        ):
            # Hemisphere case
            self.d = -1
            self.theta = terminus.crs_norm
        else:
            self.d = self._calc_d()
            self.theta = self._calc_theta()

    def create_path(
        self,
        delta_psi: float = 1,
        delta_d: float = 1,
    ) -> list[IntermediatePoint]:
        """Construct a LSL or RSR path.

        Parameters
        ----------
        delta_psi: float, optional
            Interval at which to compute arc points, in degrees. Default is 1.
        delta_d: float, optional
            Interval at which to compute tangent line connecting the two
            circles, in meters. Default is 1.

        Returns
        -------
        list of IntermediatePoint
            IntermediatePoints forming the Dubins path.
        """
        waypoints = []
        waypoints.extend(
            self._calc_arc_points(self.circles[0], self.theta, delta_psi))

        if self.d != -1:
            try:
                prev_wpt = waypoints[-1]
            except IndexError:
                prev_wpt = IntermediatePoint.from_waypoint(self.origin)
                waypoints = [prev_wpt]

            waypoints.extend(self._calc_line_points(prev_wpt, delta_d))

        if self.psi != self.terminus.crs_norm:
            waypoints.extend(
                self._calc_arc_points(
                    self.circles[1], self.terminus.crs_norm, delta_psi))

        return waypoints

    def _init_circles(self, turns: list[Turn]) -> list[Circle]:
        """Compute the center of the circles to rotate about."""
        return [
            self._init_circle(point, t)
            for point, t in zip([self.origin, self.terminus], turns)]

    def _calc_d(self) -> float:
        """Calculate the length of the line segment connecting the tangent
        points on the two circles.

        Parameters
        ----------
        None

        Returns
        -------
        float
            Length of the tangent line, unitless.

        Raises
        ------
        ValueError
            If the turn radius is too large, attempting to take the square
            root in the last line of the method becomes invalid.
        """
        dist = self.circles[0].distance_to(self.circles[1])

        if self.case in [DubinsType.LSL, DubinsType.RSR]:
            return dist

        return sqrt(dist**2 - (4 * self.radius**2))

    def _calc_theta(self) -> float:
        """Compute the angle of the line connecting the tangent points
        on the two circles.

        Parameters
        ----------
        None

        Returns
        -------
        float
            Angle formed by the tangent line and the positive y-axis,
            in degrees.

        Notes
        -----
        * Uses eqs. 14 and 20 in their correct forms:
            * Eq. 14 is given as:
                gamma = arctan((2 * radius) / d),
              however its correct form is:
                gamma = arctan(d / (2 * radius))
            * Eq. 20:
                * Eta is given as:
                    n = 90 + arctan...
                  however its correct form is:
                    n = 90 - arctan...
                * Gamma is given as:
                    g = arccos((2 * radius) / d)
                  however its correct form is:
                    g = arctan(d / (2 * radius))
        """
        x_i, y_i = self.circles[0].xy
        x_f, y_f = self.circles[1].xy
        theta = None

        if self.case in [DubinsType.LSL, DubinsType.RSR]:
            theta = 90 - arctan2((y_f - y_i), (x_f - x_i))
        elif self.case == DubinsType.LSR:
            eta = 90 - arctan2((y_f - y_i), (x_f - x_i))
            gamma = arctan(self.d / (2 * self.radius))
            theta = eta + gamma - 90
        else:
            # RSL case
            eta = 90 - arctan2((y_f - y_i), (x_f - x_i))
            gamma = arctan(self.d / (2 * self.radius))
            theta = eta - gamma + 90

        return normalize_angle(theta)
