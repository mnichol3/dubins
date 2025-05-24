"""Tests for classes in dubins.py."""
from dubins import DubinsPath, DubinsType, Turn


def test_turn():
    """Test functionality of Turn enum class."""
    assert Turn.RIGHT.value == 1
    assert Turn.LEFT.value == -1
    assert Turn.reverse(Turn.LEFT) == Turn.RIGHT


def test_dubins_type():
    """Test functionality of DubinsType enum class."""
    assert DubinsType.from_turns([Turn.LEFT, Turn.LEFT]) == DubinsType.LSL
    assert DubinsType.from_turns([Turn.RIGHT, Turn.RIGHT]) == DubinsType.RSR
    assert DubinsType.from_turns([Turn.LEFT, Turn.RIGHT]) == DubinsType.LSR
    assert DubinsType.from_turns([Turn.RIGHT, Turn.LEFT]) == DubinsType.RSL
