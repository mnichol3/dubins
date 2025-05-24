A Python module to construct simple Dubins paths.


## Requirements
* Python >= 3.11
* matplotlib


## Example Usage
```python
from dubins import DubinsPath, Turn
from point import Waypoint
from plotting import plot_path

origin = Waypoint(10, 0, 60)
terminus = Waypoint(0, 4, 120)
radius = 2
turns = [Turn.RIGHT, Turn.LEFT]

dub = DubinsPath(origin, terminus, radius, turns)
points = dub.create_path(delta_psi=delta_psi, delta_d=delta_d)

plot_path(points, dub.circles)
```
![alt text](https://github.com/mnichol3/dubins/blob/master/example/example.png "Example RSL path")


## References
Lugo-Cárdenas, Israel & Flores, Gerardo & Salazar, Sergio & Lozano, R.. (2014).
Dubins path generation for a fixed wing UAV. 339-346. 10.1109/ICUAS.2014.6842272.
