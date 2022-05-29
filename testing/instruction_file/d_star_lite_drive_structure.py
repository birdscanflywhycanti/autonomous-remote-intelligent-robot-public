import copy
import heapq
import math
from os.path import dirname, abspath
import json

class Node:
    def __init__(self, id):
        self.id = id
        self.parents = {}
        self.children = {}
        self.g = float("inf")
        self.rhs = float("inf")

    def __str__(self):
        return "Node: " + self.id + " g: " + str(self.g) + " rhs: " + str(self.rhs)

    def __repr__(self):
        return self.__str__()

    def update_parents(self, parents):
        self.parents = parents


class Graph:
    def __init__(self):
        self.graph = {}

    def __str__(self):
        msg = "Graph:"
        for i in self.graph:
            msg += (
                "\n  node: "
                + i
                + " g: "
                + str(self.graph[i].g)
                + " rhs: "
                + str(self.graph[i].rhs)
            )
        return msg

    def __repr__(self):
        return self.__str__()

    def setStart(self, id):
        if self.graph[id]:
            self.start = id
        else:
            raise ValueError("start id not in graph")

    def setGoal(self, id):
        if self.graph[id]:
            self.goal = id
        else:
            raise ValueError("goal id not in graph")


class Grid(Graph):
    def __init__(self, x_dim, y_dim):
        self.x_dim = x_dim
        self.y_dim = y_dim
        # First make an element for each row (height of grid)
        self.cells = [0] * y_dim
        # Go through each element and replace with row (width of grid)
        for i in range(y_dim):
            self.cells[i] = [0] * x_dim
        self.graph = {}

        self.generateGraphFromGrid()
        # self.printGrid()

    def __str__(self):
        msg = "Graph:"
        for i in self.graph:
            msg += (
                "\n  node: "
                + i
                + " g: "
                + str(self.graph[i].g)
                + " rhs: "
                + str(self.graph[i].rhs)
                + " neighbors: "
                + str(self.graph[i].children)
            )
        return msg

    def __repr__(self):
        return self.__str__()

    def printGrid(self, start, end, current=None):
        d = D_Star_Lite()
        test = [0] * len(self.cells)
        for i in range(len(self.cells)):
            test[i] = [0] * len(self.cells[0])
        
        for i in range(len(self.cells)):
            for j in range(len(self.cells[i])):
                test[i][j] = self.cells[i][j]
        start = d.stateNameToCoords(start)
        end = d.stateNameToCoords(end)
        current = d.stateNameToCoords(current)
        test[start[1]][start[0]] = "S"
        test[end[1]][end[0]] = "E"
        test[current[1]][current[0]] = "X"
        for row in test:
            string = ""
            for col in row:
                string += f'{col:>3}'
            print(string)

    def printGValues(self, start, end, current=None):
        d = D_Star_Lite()
        tmp = [0] * len(self.cells)
        for i in range(len(self.cells)):
           tmp[i] = [0] * len(self.cells[0])
           
        for i in range(len(self.cells)):        
            for j in range(len(self.cells[i])):
                tmp[i][j] = self.cells[i][j]        
        start = d.stateNameToCoords(start)
        end = d.stateNameToCoords(end)
        current = d.stateNameToCoords(current)
        for j in range(len(self.cells)):
            for i in range(len(self.cells[0])):
                node_id = "x" + str(i) + "y" + str(j)
                node = self.graph[node_id]
                if tmp[j][i] == 0:
                    if node.g == float("inf"):
                        tmp[j][i] = "-"
                    else:
                        tmp[j][i] = str(node.g)
                if tmp[j][i] == -2:
                    tmp[j][i] = "⬛"
                    
        tmp[start[1]][start[0]] = "🟢"
        tmp[end[1]][end[0]] = "🔴"
        tmp[current[1]][current[0]] = "🚗"
        for row in tmp:
            string = ""
            for col in row:
                if col != "⬛" and col != "🟢" and col != "🔴" and col != "🚗":
                    string += f'{col:>3}'
                else:
                    string += f'{col:>2}'
            print(string)
        return tmp

    def generateGraphFromGrid(self):
        edge = 1
        for i in range(len(self.cells)):
            row = self.cells[i]
            for j in range(len(row)):
                # print('graph node ' + str(i) + ',' + str(j))
                node = Node("x" + str(i) + "y" + str(j))
                if i > 0:  # not top row
                    node.parents["x" + str(i - 1) + "y" + str(j)] = edge
                    node.children["x" + str(i - 1) + "y" + str(j)] = edge
                if i + 1 < self.y_dim:  # not bottom row
                    node.parents["x" + str(i + 1) + "y" + str(j)] = edge
                    node.children["x" + str(i + 1) + "y" + str(j)] = edge
                if j > 0:  # not left col
                    node.parents["x" + str(i) + "y" + str(j - 1)] = edge
                    node.children["x" + str(i) + "y" + str(j - 1)] = edge
                if j + 1 < self.x_dim:  # not right col
                    node.parents["x" + str(i) + "y" + str(j + 1)] = edge
                    node.children["x" + str(i) + "y" + str(j + 1)] = edge
                self.graph["x" + str(i) + "y" + str(j)] = node


class D_Star_Lite:
    def topKey(self, queue):
        queue.sort()
        # print(queue)
        if len(queue) > 0:
            return queue[0][:2]
        else:
            # print('empty queue!')
            return (float("inf"), float("inf"))

    def heuristic_from_s(self, graph, id, s):
        x_distance = abs(int(id.split("x")[1][0]) - int(s.split("x")[1][0]))
        y_distance = abs(int(id.split("y")[1][0]) - int(s.split("y")[1][0]))
        return max(x_distance, y_distance)

    def calculateKey(self, graph, id, s_current, k_m):
        return (
            min(graph.graph[id].g, graph.graph[id].rhs)
            + self.heuristic_from_s(graph, id, s_current)
            + k_m,
            min(graph.graph[id].g, graph.graph[id].rhs),
        )

    def updateVertex(self, graph, queue, id, s_current, k_m):
        s_goal = graph.goal
        if id != s_goal:
            min_rhs = float("inf")
            for i in graph.graph[id].children:
                min_rhs = min(min_rhs, graph.graph[i].g + graph.graph[id].children[i])
            graph.graph[id].rhs = min_rhs
        id_in_queue = [item for item in queue if id in item]
        if id_in_queue != []:
            if len(id_in_queue) != 1:
                raise ValueError("more than one " + id + " in the queue!")
            queue.remove(id_in_queue[0])
        if graph.graph[id].rhs != graph.graph[id].g:
            heapq.heappush(queue, self.calculateKey(graph, id, s_current, k_m) + (id,))

    def computeShortestPath(self, graph, queue, s_start, k_m):
        while (graph.graph[s_start].rhs != graph.graph[s_start].g) or (
            self.topKey(queue) < self.calculateKey(graph, s_start, s_start, k_m)
        ):
            # print(graph.graph[s_start])
            # print('topKey')
            # print(topKey(queue))
            # print('calculateKey')
            # print(calculateKey(graph, s_start, 0))
            k_old = self.topKey(queue)
            u = heapq.heappop(queue)[2]
            if k_old < self.calculateKey(graph, u, s_start, k_m):
                heapq.heappush(queue, self.calculateKey(graph, u, s_start, k_m) + (u,))
            elif graph.graph[u].g > graph.graph[u].rhs:
                graph.graph[u].g = graph.graph[u].rhs
                for i in graph.graph[u].parents:
                    self.updateVertex(graph, queue, i, s_start, k_m)
            else:
                graph.graph[u].g = float("inf")
                self.updateVertex(graph, queue, u, s_start, k_m)
                for i in graph.graph[u].parents:
                    self.updateVertex(graph, queue, i, s_start, k_m)


    def nextInShortestPath(self, graph, s_current):
        min_rhs = float("inf")
        s_next = None
        if graph.graph[s_current].rhs == float("inf"):
            print("You are done stuck")
        else:
            for i in graph.graph[s_current].children:
                # print(i)
                child_cost = graph.graph[i].g + graph.graph[s_current].children[i]
                # print(child_cost)
                if (child_cost) < min_rhs:
                    min_rhs = child_cost
                    s_next = i
            if s_next:
                return s_next
            else:
                raise ValueError("could not find child for transition!")

    def scanForObstacles(self, graph, queue, s_current, scan_range, k_m):
        return False

    def moveAndRescan(self, graph, queue, s_current, scan_range, k_m):
        if s_current == graph.goal:
            return "goal", k_m
        else:
            s_last = s_current
            s_new = self.nextInShortestPath(graph, s_current)
            new_coords = self.stateNameToCoords(s_new)

            if (
                graph.cells[new_coords[1]][new_coords[0]] == -1
            ):  # just ran into new obstacle
                s_new = s_current  # need to hold tight and scan/replan first
            self.updateObsticles(graph, queue, s_new, k_m, scan_range)
            # print(graph)
            k_m += self.heuristic_from_s(graph, s_last, s_new)
            self.computeShortestPath(graph, queue, s_current, k_m)

            return s_new, k_m

    def stateNameToCoords(self, name):
        return [
            int(name.split("x")[1].split("y")[0]),
            int(name.split("x")[1].split("y")[1]),
        ]

    def initDStarLite(self, graph, queue, s_start, s_goal, k_m):
        graph.graph[s_goal].rhs = 0
        heapq.heappush(
            queue, self.calculateKey(graph, s_goal, s_start, k_m) + (s_goal,)
        )
        self.computeShortestPath(graph, queue, s_start, k_m)
        return (graph, queue, k_m)

    def updateObsticles(self, graph, queue, s_current, k_m, scan_range=20):
        states_to_update = {}
        range_checked = 0
        if scan_range >= 1:
            for neighbor in graph.graph[s_current].children:
                neighbor_coords = self.stateNameToCoords(neighbor)
                states_to_update[neighbor] = graph.cells[neighbor_coords[1]][
                    neighbor_coords[0]
                ]
            range_checked = 1
        # print(states_to_update)

        while range_checked < scan_range:
            new_set = {}
            for state in states_to_update:
                new_set[state] = states_to_update[state]
                for neighbor in graph.graph[state].children:
                    if neighbor not in new_set:
                        neighbor_coords = self.stateNameToCoords(neighbor)
                        new_set[neighbor] = graph.cells[neighbor_coords[1]][ neighbor_coords[0]]
            range_checked += 1
            states_to_update = new_set

        new_obstacle = False
        for state in states_to_update:
            if states_to_update[state] < 0:  # found cell with obstacle
                # print('found obstacle in ', state)
                for neighbor in graph.graph[state].children:
                    # first time to observe this obstacle where one wasn't before
                    if graph.graph[state].children[neighbor] != float("inf"):
                        neighbor_coords = self.stateNameToCoords(state)
                        graph.cells[neighbor_coords[1]][neighbor_coords[0]] = -2
                        graph.graph[neighbor].children[state] = float("inf")
                        graph.graph[state].children[neighbor] = float("inf")
                        self.updateVertex(graph, queue, state, s_current, k_m)
                        new_obstacle = True
            # elif states_to_update[state] == 0: #cell without obstacle
            # for neighbor in graph.graph[state].children:
            # if(graph.graph[state].children[neighbor] != float('inf')):

        # print(graph)
        return new_obstacle







def d_star_loop():
    # load instrutions from file
    script_path = abspath(dirname(__file__))
    with open(f'{script_path}/instructions.json') as json_file:
        data = json.load(json_file)
    
        input_matrix = data['input_matrix']
        instructions = data['instructions']
        unit_size = data['unit_size']
        s_current = data['start']

    print(unit_size, s_current)

    for instruction in instructions:
        s_goal = instruction['goal']
        final_rotation = instruction['final_rotation']

        print(s_current, s_goal, final_rotation)

        s_current = navigate(input_matrix, s_current, s_goal)


def navigate(input_matrix, s_start, s_goal):
    graph = Grid(len(input_matrix), len(input_matrix[0]))
    d_star_lite = D_Star_Lite()
    
    print("**Initial Environment**")
    
    graph.cells = input_matrix
    
    goal_coords = d_star_lite.stateNameToCoords(s_goal)
    graph.setStart(s_start)
    graph.setGoal(s_goal)

    k_m = 0
    s_last = s_start
    queue = []
    graph, queue, k_m = d_star_lite.initDStarLite(graph, queue, s_start, s_goal, k_m)
    s_current = s_start
    pos_coords = d_star_lite.stateNameToCoords(s_current)
    max_dim = len(input_matrix)
    if len(input_matrix[0]) > max_dim:
        max_dim = len(input_matrix[0])
    
    d_star_lite.updateObsticles(graph, queue, s_current, k_m, max_dim)
    curr_angle=0
    s_new = None
    
    d_star_lite.computeShortestPath(graph, queue, s_current, k_m)
    graph.printGValues(s_start, s_goal, s_current)
    i = 0
    while s_new != s_goal:
        s_new, x_, y_, distance, curr_angle = scan_next(i, graph, d_star_lite, s_current, curr_angle)

        # logical bounds checking
        if distance < 60 and distance != -1:
            s_new = s_current
            graph.cells[y_][x_] = -2
            d_star_lite.updateObsticles(graph, queue, s_current, k_m, 2)
            print("**Obsticle Detected at " + s_new + "**")
            graph.printGValues(s_start, s_goal, s_current)
        else:
            #perform_drive(1,TB, mpu, max_power)
            s_current = s_new
            graph.printGValues(s_start, s_goal, s_current)
            
            
        k_m += d_star_lite.heuristic_from_s(graph, s_last, s_new)
        d_star_lite.computeShortestPath(graph, queue, s_current, k_m)      
        d_star_lite.updateObsticles(graph, queue, s_current, k_m, 2)
        i += 1
        #print("\n")
    
    return s_current


def scan_next(i, graph, d_star_lite, s_current, curr_angle):
    next_location = d_star_lite.nextInShortestPath(graph, s_current)
    current = d_star_lite.stateNameToCoords(s_current)
    next = d_star_lite.stateNameToCoords(next_location)
    
    
    x, y = (current[0], current[1])
    x_, y_ = (next[0],next[1])
    
    unit_target_vector = (x_ - x, y - y_)
    target_angle = calculate_angle(unit_target_vector)

    delta_angle = (target_angle - curr_angle)
    print("Facing " + str(target_angle) + " || Turn " + str(delta_angle))
    #perform_spin(delta_angle, target_angle, TB, mpu, max_power)
    #distance = hcsr.pulse()
    #distance = round(distance, 3)
    distance = 66

    return next_location, x_, y_,distance, target_angle


def calculate_angle(unit_target_vector):

    origin_vector_x, origin_vector_y = (0, 1)
    target_vector_x, target_vector_y = unit_target_vector

    rad = math.atan2(origin_vector_y, origin_vector_x) - math.atan2(
        target_vector_y, target_vector_x
    )

    angle = math.degrees(rad)

    # print(r)
    return angle

d_star_loop()

