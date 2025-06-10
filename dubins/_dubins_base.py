"""This module contains the base class for creating Dubins paths."""
from __future__ import annotations
from enum import Enum
from math import pi
from typing import TypeAlias

from .point import Circle, IntermediatePoint, Waypoint
from .mathlib import cos, sin, normalize_angle


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
    LOOPBACK = 5

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


class DubinsBase:
    """Base class for Dubins paths.

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
    """

    def __init__(
        self,
        origin: Waypoint,
        terminus: Waypoint,
        radius: float,
    ):
        """Instantiate a new DubinsBase.

        Parameters
        ----------
        origin: Waypoint
            Fly-to Point defining the beginning of the dubins path.
        terminus: Waypoint
            Fly-to Point defining the end of the dubins path.
        radius: float
            Turn radius, in meters.
        """
        self.origin = origin
        self.terminus = terminus
        self.radius = radius
        self.length = 0.
        self.d = 0.
        self.theta = 0.

    @property
    def beta(self) -> float:
        """Return the beta angle.

        The beta angle is defined as the angle between the vector connecting
        the origin and terminus points and the origin course, in degrees.
        """
        return self.origin.calc_beta(self.terminus)

    def _init_circle(self, point: Waypoint, turn: Turn) -> Circle:
        """Compute the center a circle to rotate about.

        Parameters
        ----------
        point: Waypoint
            Either origin or terminus waypoint.
        turn: Turn
            Turn direction for the given waypoint.

        Returns
        -------
        Circle
        """
        return Circle(
            point.x + (turn.value * self.radius * cos(point.crs_norm)),
            point.y - (turn.value * self.radius * sin(point.crs_norm)),
            turn.value,
        )

    def _calc_arc_points(
        self,
        circle: Circle,
        psi_f: float,
        delta_psi: float,
    ) -> list[IntermediatePoint]:
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
        list of IntermediatePoint
        """
        waypoints = []
        psi_f = round(psi_f, 2)
        theta = 0

        while abs(self.psi - psi_f) > delta_psi:
            curr_point = IntermediatePoint(
                circle.x - (circle.s * self.radius * sin(90 - self.psi)),
                circle.y + (circle.s * self.radius * cos(90 - self.psi)),
                self.psi,
                (pi * self.radius * delta_psi) / 180.,
            )
            waypoints.append(curr_point)

            self.psi = normalize_angle(self.psi + delta_psi * circle.s)
            theta += delta_psi

        self.length += (pi * self.radius * theta) / 180.

        return waypoints

    def _calc_line_points(
        self,
        origin: IntermediatePoint,
        delta: float,
    ) -> list[IntermediatePoint]:
        """Compute points along the tangent line connecting the two arcs.

        Parameters
        ----------
        origin: IntermediatePoint
            origin x- and y-coordinate.
        delta: float
            Distance delta.

        Returns
        -------
        list of IntermediatePoint
        """
        waypoints = []
        d_sum = 0
        x_p, y_p = origin.xy
        d_max = self.d - delta # prevent overrun

        while d_sum < d_max:
            x_n = x_p + delta * sin(self.theta)
            y_n = y_p + delta * cos(self.theta)
            waypoints.append(IntermediatePoint(x_n, y_n, self.psi, delta))

            x_p = x_n
            y_p = y_n
            d_sum += delta

        self.length += d_sum

        return waypoints
