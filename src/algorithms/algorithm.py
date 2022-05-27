"""A Class used for selecting which algorithm to use
"""
from algorithms.a_star import a_star
from algorithms.d_star_lite import D_Star_Lite, Node, Graph, Grid

class Algorithm:
    """A Class used for selecting which algorithm to use

    Constructor Arguments:
        matrix: a matrix representing the space the robot is in
        start_node: the node the robot is starting from
        end_node: the node the robot is trying to reach

    Methods:
        use_a_star: a function that returns a path using the A* algorithm
    """

    def __init__(self, matrix, start_node, end_node):
        self.matrix = matrix
        self.start_node = start_node
        self.end_node = end_node

    def use_a_star(self):
        """A function that returns a path using the A* algorithm

        Returns:
            path: a list of nodes representing the path the robot should take
        """
        return a_star(self.matrix, self.start_node, self.end_node)
