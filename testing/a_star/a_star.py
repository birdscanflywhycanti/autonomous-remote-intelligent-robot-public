# A* algorithm implementation
#!pip install pathfinding

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

#matrix = [
#  [1, 1, 1],
#  [1, 0, 1],
#  [1, 1, 1]
#]
matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]

grid = Grid(matrix=matrix)

start = grid.node(0, 0)
end = grid.node(2, 2)

finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
path, runs = finder.find_path(start, end, grid)

# pathing instruction
print(path)

# visualisation
print('operations:', runs, 'path length:', len(path))
print(grid.grid_str(path=path, start=start, end=end))