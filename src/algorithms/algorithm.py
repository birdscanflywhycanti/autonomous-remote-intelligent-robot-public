from algorithms.a_star import a_star
from algorithms.d_star_lite import d_star_lite

class Algorithm:
    def __init__(self, matrix, start_node, end_node):
        self.matrix = matrix
        self.start_node = start_node
        self.end_node = end_node

    def use_a_star(self):
        return a_star(self.matrix, self.start_node, self.end_node)

    def use_d_star_lite(self):
        return d_star_lite(self.matrix, self.start_node, self.end_node)
