"""This module contains classes to construct Dubins paths in Cartesian space."""
from __future__ import annotations
from enum import Enum
from typing import TypeAlias

import math

from point import Circle, Waypoint
from mathlib import arccos, arctan, arctan2, cos, sin, normalize_angle


Point: TypeAlias = tuple[float, float]


class DubinsType(Enum):
    """Enum for Dubins path type.

    Members
    -------
    LSL: Left-Straight-Left path.
    RSR: Right-Straight-Right path.
    LSR: Left-Straight-Right path.
    RSL: Right-Straight-Left path.
    """
    LSL = 1
    RSR = 2
    LSR = 3
    RSL = 4

    @classmethod
    def from_turns(cls, turns: list[Turn]) -> DubinsType:
        """Get the DubinsType from a list of Turns.

        Parameters
        ----------
        turns: list of Turn
            Prescribed turns.

        Returns
        -------
        DubinsType

        Raises
        ------
        ValueError
            If an invalid combination of turns are passed in the `turns` param.
        """
        ttype = None
        t1, t2 = turns

        if t1 == t2 == Turn.RIGHT:
            ttype = cls.RSR
        elif t1 == t2 == Turn.LEFT:
            ttype = cls.LSL
        elif t1 == Turn.RIGHT and t2 == Turn.LEFT:
            ttype = cls.RSL
        elif t1 == Turn.LEFT and t2 == Turn.RIGHT:
            ttype = cls.LSR
        else:
            raise ValueError(f'Invalid turn combination: {turns}')

        return ttype


class Turn(Enum):
    """Enum for turn direction."""
    LEFT = -1
    RIGHT = 1

    @classmethod
    def reverse(cls, turn: Turn) -> Turn:
        """Return a new Turn in the direction opposite of the given Turn."""
        if not isinstance(turn, Turn):
            raise TypeError(
                f'turn parameter must be of type Turn, got {type(turn)}')

        return Turn.RIGHT if turn == Turn.LEFT else Turn.LEFT


class DubinsPath:
    """Class to compute Dubins paths in Cartesian space.

    Example usage
    -------------
    >>> origin = Waypoint(10, 0, 60)
    >>> terminus = Waypoint(0, 4, 120)
    >>> radius = 4
    >>> turns = [Turn.RIGHT, Turn.LEFT]
    >>> dub = DubinsPath(origin, terminus, radius, turns)
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
          however its correct for is:
            gamma = arctan(d / (2 * radius))
        * Eq. 20 is given as:
            gamma = arccos((2 * radius) / d)
          however its correct for is:
            gamma = arccos(d / (2 * radius))
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
        self.origin = origin
        self.origin.normalize()

        self.terminus = terminus
        self.terminus.normalize()

        self.case = DubinsType.from_turns(turns)
        self.radius = radius
        self.circles = self._init_circles(turns)

        self.psi = self.origin.crs
        self.d = self._calc_d()
        self.theta = self._calc_theta()

    def create_path(
        self,
        delta_psi: float = 1,
        delta_d: float = 0.5,
    ) -> list[Point]:
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
        waypoints.extend(self._calc_line_points(waypoints[-1], delta_d))
        waypoints.extend(
            self._calc_arc_points(
                self.circles[1], self.terminus.crs, delta_psi))

        return waypoints

    def _init_circles(self, turns: list[Turn]) -> list[Circle]:
        """Compute the center of the circles to rotate about."""
        return [
            Circle(
                point.x + (t.value * self.radius * cos(point.crs)),
                point.y - (t.value * self.radius * sin(point.crs)),
                t.value)
            for point, t in zip([self.origin, self.terminus], turns)
        ]

    def _calc_arc_points(
        self,
        circle: Circle,
        psi_f: float,
        delta_psi: float,
    ) -> list[Point]:
        """Compute the points along an arc defined by a circle.

        Parameters
        ----------
        circle: Circle
            Circle to rotate about.
        psi_f: float
            Final heading.
        delta_psi: float
            Interval at which to compute arc points, in degrees.

        Returns
        -------
        list of Point
        """
        waypoints = []
        psi_f = round(psi_f, 2)

        while abs(self.psi - psi_f) > delta_psi:
            waypoints.append((
                circle.x - (circle.s * self.radius * sin(90 - self.psi)),
                circle.y + (circle.s * self.radius * cos(90 - self.psi)),
            ))

            self.psi = normalize_angle(self.psi + delta_psi * circle.s)

        return waypoints

    def _calc_line_points(self, origin: Point, delta: float) -> list[Point]:
        """Compute points along the tangent line connecting the two arcs.

        Parameters
        ----------
        origin: Point
            origin x- and y-coordinate.
        delta: float
            Distance delta.

        Returns
        -------
        list of Point
        """
        waypoints = []
        d_sum = 0
        x_p, y_p = origin
        d_max = self.d - (delta / 2) # prevent overrun

        while d_sum < d_max:
            x_n = x_p + delta * sin(self.theta)
            y_n = y_p + delta * cos(self.theta)
            waypoints.append((x_n, y_n))

            x_p = x_n
            y_p = y_n
            d_sum += delta

        return waypoints

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
        d = self.circles[0].distance_to(self.circles[1])

        if self.case in [DubinsType.LSL, DubinsType.RSR]:
            return d

        return math.sqrt(d**2 - (4 * self.radius**2))

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
            * Eq. 20 is given as:
                gamma = arccos((2 * radius) / d)
              however its correct form is:
                gamma = arccos(d / (2 * radius))
        """
        x_i, y_i = self.circles[0].xy
        x_f, y_f = self.circles[1].xy

        if self.case in [DubinsType.LSL, DubinsType.RSR]:
            return 90 - arctan2((y_f - y_i), (x_f - x_i))

        if self.case == DubinsType.LSR:
            eta = 90 + arctan2((y_f - y_i), (x_f - x_i))
            gamma = arccos(self.d / (2 * self.radius))

            return eta + gamma - 90

        eta = 90 - arctan2((y_f - y_i), (x_f - x_i))
        gamma = arctan(self.d / (2 * self.radius))

        return eta - gamma + 90
