"""Tests for Circle, and Waypoint classes."""
from dubins.point import Circle, Waypoint


def test_circle():
    """Test Circle instantiation."""
    point = Circle(4, 5, -1)

    assert point.xy == (4, 5)


def test_waypoint():
    """Test Waypoint instantiation."""
    wpt = Waypoint(4, 5, 330)

    assert wpt.xy == (4, 5)
    assert wpt.crs == 330
    assert wpt.crs_norm == -30


def test_waypoint_distance():
    """Assert Waypoint.distance() returns the correct distance."""
    wpt = Waypoint(2, 2, 330)
    wpt2 = Waypoint(6, 8, 120)

    assert round(wpt.distance_to(wpt2), 2) == 7.21
