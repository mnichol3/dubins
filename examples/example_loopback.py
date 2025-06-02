"""Generate a Right-Straight-Left Dubins path."""
from dubins import DubinsLoopback, Turn, Waypoint, plot_path


origin = Waypoint(0, 0, 0)
terminus = Waypoint(4, 4, 180)
radius = 6
turns = [Turn.RIGHT, Turn.RIGHT]

dub = DubinsLoopback(origin, terminus, radius, turns)
points = dub.create_path(delta_psi=1)

plot_path(points, dub.circles)
