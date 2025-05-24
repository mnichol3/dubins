"""
Python module for generating simple Dubins paths.

Requirements: Python 3.11, matplotlib.

Download: https://github.com/mnichol3/dubins
"""
from .dubins import DubinsPath, DubinsType, Turn
from .point import Waypoint
from .plotting import plot_path

__all__ = [
    "DubinsPath",
    "DubinsType",
    "Turn",
    "Waypoint",
    "plot_path",
]