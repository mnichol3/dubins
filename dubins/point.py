from __future__ import annotations

from .mathlib import (
    calc_azimuth, calc_distance, normalize_angle, subtract_azimuths)


class PointBase:
    """Container for a point defined by an x- and y-coordinate.

     Attributes
    ----------
    x: float
        X-coordinate.
    y: float
        Y-coordinate.
    """

    def __init__(self, x: float, y: float):
        """Container for circle parameters.

        Parameters
        ----------
        x: float
            X-coordinate of the center of the point.
        y: float
            Y-coordinate of the center of the point.
        """
        self.x = x
        self.y = y

    @property
    def xy(self) -> tuple[float, float]:
        """Return the x- and y-coordinates."""
        return self.x, self.y

    def azimuth_to(self, p: PointBase) -> float:
        """Calculate the azimuth from the point to another Point."""
        return calc_azimuth(self.xy, p.xy)

    def distance_to(self, p: PointBase) -> float:
        """Calculate the Euclidean distance from the point to another Point."""
        return calc_distance(self.xy, p.xy)

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f'<{self.__class__.__name__} ({self.x}, {self.y})>'


class Circle(PointBase):
    """Container for circle parameters.

    Attributes
    ----------
    x: float
        X-coordinate of the Circle center.
    y: float
        Y-coordinate of the Circle center.
    s: int
        Rotation direction. 1 for clockwise, -1 for counter-clockwise.
    """

    def __init__(self, x: float, y: float, s: int):
        """Instantiate a new Circle.

        Parameters
        ----------
        x: float
            X-coordinate of the center of the circle.
        y: float
            Y-coordinate of the center of the circle.
        s: int
            Direction of rotation about the circle.
            1 for clockwise, -1 for counter-clockwise.
        """
        if s not in [-1, 1]:
            raise ValueError(f'"s" parameter must be in [-1, 1], got {s}')

        super().__init__(x, y)
        self.s = s

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f'<{self.__class__.__name__} ({self.x}, {self.y}), s={self.s}>'


class IntermediatePoint(PointBase):
    """Container for intermediate points along the Dubins path.

    Attributes
    ----------
    x: float
        Waypoint x-coordinate.
    y: float
        Waypoint y-coordinate.
    crs: float
        Course, in degrees [0, 360).
    crs_norm: float
        Course, in degrees, normalized to (-180, 180].
    seg_length: float
        Length of the segment connecting the IntermediatePoint to the previous
        IntermediatePoint.
    """

    def __init__(self, x: float, y: float, crs_norm: float, seg_length: float):
        """Instantiate a new Waypoint.

        Parameters
        ----------
        x: float
            X-coordinate of the center of the waypoint.
        y: float
            Y-coordinate of the center of the waypoint.
        crs_norm: int
            Inbound course defined over (-180, 180].
        seg_length: float
            Length of the segment connecting the IntermediatePoint to the
            previous IntermediatePoint.
        """
        super().__init__(x, y)
        self.crs_norm = round(crs_norm, 2)
        self.crs = round(crs_norm % 360., 2)
        self.seg_length = seg_length

    @classmethod
    def from_waypoint(
        cls,
        wpt: Waypoint,
        seg_length: float = 0.,
    ) -> IntermediatePoint:
        """Instantiate a IntermediatePoint from a Waypoint.

        Parameters
        -----------
        wpt: Waypoint
        seg_length: float, optional
            Segment length. Default is 0.

        Returns
        -------
        IntermediatePoint
        """
        return cls(*wpt.xy, wpt.crs_norm, seg_length)


class Waypoint(PointBase):
    """Container for a waypoint consisting of an x-coordinate, y-coordinate,
    and an inbound course.

    Attributes
    ----------
    x: float
        Waypoint x-coordinate.
    y: float
        Waypoint y-coordinate.
    crs: float
        Course, in degrees [0, 360).
    crs_norm: float
        Course, in degrees, normalized to (-180, 180].
    """

    def __init__(self, x: float, y: float, crs: float):
        """Instantiate a new Waypoint.

        Parameters
        ----------
        x: float
            X-coordinate of the center of the waypoint.
        y: float
            Y-coordinate of the center of the waypoint.
        crs: int
            Inbound course.
        """
        super().__init__(x, y)
        self.crs = crs % 360.
        self.crs_norm = round(normalize_angle(self.crs), 2)

    def calc_beta(self, wpt: Waypoint) -> float:
        """Calculate the beta angle between the Waypoint and another Waypoint.

        The beta angle is defined as the angle between the vector connecting
        the origin and terminus points and the origin course, in degrees.

        Parameters
        ----------
        wpt: Waypoint

        Returns
        -------
        float
            Beta angle, in degrees.
        """
        return subtract_azimuths(self.azimuth_to(wpt), self.crs + 180.)

    def course_to(self, wpt: Waypoint) -> float:
        """Calculate the course from the Waypoint to another Waypoint.

        The is similar to Waypoint.azimuth_to(), but takes the origin
        Waypoint's course into account.

        Parameters
        ----------
        wpt: Waypoint

        Returns
        -------
        float
            Beta angle, in degrees.
        """
        return (self.azimuth_to(wpt) - self.crs) % 360.

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return (f'<{self.__class__.__name__} ({self.x}, {self.y}),'
                f' crs={self.crs}>')
