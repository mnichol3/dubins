"""
Python module for generating simple Dubins paths.

Requirements: Python 3.11, matplotlib.

Download: https://github.com/mnichol3/dubins
"""
from ._dubins_base import DubinsType, Turn
from .dubins import DubinsPath
from .dubins_loopback import DubinsLoopback
from .point import Waypoint
from .plotting import plot_path

__all__ = [
    "DubinsLoopback",
    "DubinsPath",
    "DubinsType",
    "Turn",
    "Waypoint",
    "plot_path",
]