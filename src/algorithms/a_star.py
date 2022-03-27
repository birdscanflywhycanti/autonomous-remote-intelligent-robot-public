from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

def a_star(matrix, start_node, end_node):
    grid = Grid(matrix=matrix)

    start = grid.node(*start_node)
    end = grid.node(*end_node)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)

    # pathing instruction
    print(path)

    # visualisation
    print("operations:", runs, "path length:", len(path))
    print(grid.grid_str(path=path, start=start, end=end))

    return path