"""Contains the A* algorithm.
"""

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

import logging

def a_star(matrix, start_node, end_node):
    """A function that returns a path using the A* algorithm

    Args:
        matrix (list): a matrix representing the space the robot is in
        start_node (tuple): the node the robot is starting from
        end_node (tuple): the node the robot is trying to reach

    Returns:
        path (list) : a list of nodes representing the path the robot should take
    """
    grid = Grid(matrix=matrix)

    start = grid.node(*start_node)
    end = grid.node(*end_node)

    #finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    finder = AStarFinder()
    path, runs = finder.find_path(start, end, grid)

    # pathing instruction
    logging.debug(path)

    # visualisation
    logging.debug("operations:", runs, "path length:", len(path))
    logging.debug(grid.grid_str(path=path, start=start, end=end))

    return path
