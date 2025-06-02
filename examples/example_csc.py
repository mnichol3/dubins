"""Generate a Right-Straight-Left Dubins path."""
from dubins import DubinsCSC, Turn, Waypoint, plot_path


origin = Waypoint(10, 0, 60)
terminus = Waypoint(0, 4, 120)
radius = 4
turns = [Turn.RIGHT, Turn.LEFT]

dub = DubinsCSC(origin, terminus, radius, turns)
points = dub.create_path(delta_psi=1, delta_d=0.5)

plot_path(points, dub.circles)
