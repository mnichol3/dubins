import matplotlib.pyplot as plt

from .point import Circle


def plot_path(
    path: list[tuple[float, float]],
    circles: list[Circle] | None = None,
) -> None:
    """Plot a Dubins path.

    Parameters
    ----------
    path: list of tuple[float, float]
        Dubins path points.
    circles: list of Circle, optional
        Circles used to construct the path. If given, their centroids are
        plotted as black dots.

    Returns
    -------
    None
    """
    x, y = list(zip(*path))

    plt.plot(x, y, zorder=0)

    plt.scatter(*path[0], color='green', marker='o', zorder=1)
    plt.scatter(*path[-1], color='red', marker='o', zorder=1)

    if circles:
        plt.scatter(*circles[0].xy, color='black', marker='o', zorder=2)
        plt.scatter(*circles[1].xy, color='black', marker='o', zorder=2)

    plt.axis('equal')
    plt.show()
