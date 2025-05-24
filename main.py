import matplotlib.pyplot as plt

from dubins import DubinsPath, Turn
from point import Waypoint
from plotting import plot_path


delta_psi = 1
delta_d = 0.5

# RSR
# origin = Waypoint(0, 0, 0)
# terminus = Waypoint(10, 0, 180)
# radius = 4
# turns = [Turn.RIGHT, Turn.RIGHT]

# LSL
# origin = Waypoint(10, 0, 80)
# terminus = Waypoint(0, 2, 150)
# radius = 2
# turns = [Turn.LEFT, Turn.LEFT]

# RSL
# origin = Waypoint(0, 0, 300)
# terminus = Waypoint(10, 4, 330)
# radius = 2
# turns = [Turn.RIGHT, Turn.LEFT]

# LSR
origin = Waypoint(10, 0, 60)
terminus = Waypoint(0, 4, 120)
radius = 2
turns = [Turn.RIGHT, Turn.LEFT]


dub = DubinsPath(origin, terminus, radius, turns)
points = dub.create_path(delta_psi=delta_psi, delta_d=delta_d)

plot_path(points, dub.circles)
