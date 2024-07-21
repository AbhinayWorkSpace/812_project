import numpy as np
import matplotlib.pyplot as plt
import random
import queue

random.seed(812)


class Node:
    def __init__(self, name, x, y, battery=100, dead=False, range=10):
        self.id = name  # I made it a str, int could work as well
        self.adj = {}  # dictionary {id : weight} of outgoing edges

        self.location = [x, y]
        self.battery = battery
        self.dead = dead
        self.range = range
        self.danger = False
        self.neighbors = []  # since you added adk we can prob get rid of this

        self.sink = False
        self.routes = []

    def __repr__(self):
        return f"Node: ({self.id})"

class DangerZones:
    def __init__(self):
        self.zones = []

    def generate_zone(self, width, height, num_zones, max_width=None, max_height=None):
        """
        Generate inputed number of danger zones based on option width and hight guides
        """
        # if no max ellipse conrol is input then it will use the size of the grid as a guide
        if max_width is None:
            max_width = width
        if max_height is None:
            max_height = height

        # generate x numver of random ellipses for the danger zones
        for zone in range(num_zones):
            center_x = random.uniform(0, width)
            center_y = random.uniform(0, height)
            major_axis = random.uniform(0, min(width / 2, max_width))
            minor_axis = random.uniform(0, min(height / 2, max_height))
            rotation_angle = random.uniform(0, 2 * 3.1416)
            self.zones.append((center_x, center_y, major_axis, minor_axis, rotation_angle))

    def plot_zones(self):
        """
        Plot the generated zones.
        """
        for zone in self.zones:
            center_x, center_y, major_axis, minor_axis, rotation_angle = zone
            theta = np.linspace(0, 2 * 3.1416, 100)

            x = center_x + major_axis * np.cos(theta) * np.cos(rotation_angle) - minor_axis * np.sin(theta) * np.sin(
                rotation_angle)
            y = center_y + major_axis * np.cos(theta) * np.sin(rotation_angle) + minor_axis * np.sin(theta) * np.cos(
                rotation_angle)

            plt.fill(x, y, color='red', alpha=0.3)


# this grid space represents the forest or area these nodes could be dropped in
class GridSpace:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.nodes = []
        self.danger_zones = None

        self.vertices = {}
        self.size = 0
        self.sink = ""

        self.routing_tables = {}

    # now likely useless function with the addition of the populate grid space function
    '''def add_node(self, node):
        """
        Add a single node to the grid space.
        """
        if 0 <= node.location[0] < self.width and 0 <= node.location[1] < self.height:
            self.nodes.append(node)
        else:
            print("outside bounds of grid space")'''

    def populate_grid(self, num_nodes, node_range, success_rate=1.0):
        """
        this generates a ton of nodes at once so that we can mimic a plane dropping nodes within a forest
        """
        # populate some nodes as dead to test what dead nodes do to network
        # also to mimic nodes being destroyed by demployment?
        sink = str(random.randint(0, num_nodes - 1))
        self.sink = sink

        for i in range(num_nodes):
            if random.random() > success_rate:
                status = True
            else:
                status = False

            # each x and y are genrated from 0 to the max grid value
            # range of node is how far it can contact other nodes
            temp = Node(str(i), random.randint(0, self.width - 1), random.randint(0, self.height - 1), dead=status,
                        range=node_range)

            if i == int(sink):
                temp.sink = True

            self.nodes.append(temp)

            self.vertices[temp.id] = temp

    def plot_grid(self):
        """
        Plot forest representation as a grid with each node and the danger zones
        """
        plt.figure(figsize=(8, 8))
        plt.xlim(0, self.width - 1)
        plt.ylim(0, self.height - 1)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlabel('X Axis')
        plt.ylabel('Y Axis')
        plt.title('Grid Space')

        # made this to test if all the nodes within danger zones were marked as danger = True
        # left it incase we want to have changing danger zones
        # can also be used to update nodes that died by energy use, battery =< zero
        self.node_status()

        # nodes
        # these are the living nodes to be ploted in blue
        # first get each x and y then plot on grid space
        x_coords_live = [node.location[0] for node in self.nodes if not node.dead]
        y_coords_live = [node.location[1] for node in self.nodes if not node.dead]
        plt.scatter(x_coords_live, y_coords_live, color='blue', label='Live Nodes')

        # similarly get sink nodes and plot it as green
        x_coords_sink = [node.location[0] for node in self.nodes if node.sink]
        y_coords_sink = [node.location[1] for node in self.nodes if node.sink]
        plt.scatter(x_coords_sink, y_coords_sink, color='green', label='Sink Node')

        # similarly get dead nodes and plot them as black
        x_coords_dead = [node.location[0] for node in self.nodes if node.dead]
        y_coords_dead = [node.location[1] for node in self.nodes if node.dead]
        plt.scatter(x_coords_dead, y_coords_dead, color='black', label='Dead Nodes')

        # this is the code that fines danger = true nodes and plots them as red
        x_coords_danger = [node.location[0] for node in self.nodes if node.danger]
        y_coords_danger = [node.location[1] for node in self.nodes if node.danger]
        plt.scatter(x_coords_danger, y_coords_danger, color='red', label='Nodes in Danger')

        # plot danger zones
        # in other class to keep code need
        if self.danger_zones:
            self.danger_zones.plot_zones()

        # plot connection between nodes
        # this way we can see what nodes are connected in our structure
        for node in self.nodes:
            for neighbor in node.neighbors:

                # check if either of the nodes are dead, if so then dont connect them cuz dead nodes are useless
                if neighbor.dead == False and node.dead == False:
                    plt.plot([node.location[0], neighbor.location[0]], [node.location[1], neighbor.location[1]],
                             color='black', linewidth=0.2)

        plt.grid(True)
        plt.legend()
        plt.show()

    def add_danger_zones(self, num_zones, max_width=None, max_height=None):
        """
        add danger zones to the grid space
        """
        #clear
        self.danger_zones = None

        # add the lost of danger zones from class to grid plot info
        self.danger_zones = DangerZones()

        # actually create the zones
        self.danger_zones.generate_zone(self.width, self.height, num_zones, max_width, max_height)

    def check_danger(self, route, odds=.05):
        for node in route:
            if node.danger and random.random() < odds:
                self.nodes[int(node.id)].dead = True

    def new_sink(self, dead_sink):
        """
        untested func to find a new sink node if the existing one dies
        unsure if we need this
        """
        for nbs in dead_sink.adj:
            temp = self.nodes[int(nbs)]
            if not temp.dead:
                temp.sink = True
                return

        for nbs in dead_sink.adj:
            return self.new_sink(self.nodes[int(nbs)])

    def node_status(self):
        """
        set the danger bool of each node to true if they are located within a danger zone
        also check if battery value is less than ot equal to 0
            if so set dead = true
        """
        for node in self.nodes:
            # set to false incase we want to have shifting danger zones, then this can update the nodes
            node.danger = False
            if self.danger_zones:
                for zone in self.danger_zones.zones:
                    # get location information for node and zone
                    center_x, center_y, major_axis, minor_axis, rotation_angle = zone
                    x, y = node.location

                    # this was annoying
                    # use rotation informtion to shift node date
                    # maybe remove and only use circle danger zone if this is annoying in testing??
                    x_rotated = (x - center_x) * np.cos(-rotation_angle) - (y - center_y) * np.sin(
                        -rotation_angle) + center_x
                    y_rotated = (x - center_x) * np.sin(-rotation_angle) + (y - center_y) * np.cos(
                        -rotation_angle) + center_y

                    # project the danger zone onto a single xy vecor that goes from the center on the elipse to the edge
                    distance_squared = ((x_rotated - center_x) / major_axis) ** 2 + (
                                (y_rotated - center_y) / minor_axis) ** 2

                    # see if the vector is long enough to reach the node
                    if distance_squared <= 1:
                        node.danger = True

            # check energy status
            if node.battery <= 0:
                node.dead = True

            # check if the sink is dead if so resolve
            # untested
            if node.sink == True and node.dead == True:
                self.new_sink(node)

    def connect_network(self):
        """
        dummy seach algo
        not meant for real network transmission

        I believe we can use this to assign all the neighbors for our grid
        """
        # step through each node in grid
        for curr_node in self.nodes:
            if curr_node.dead:
                continue

            # compare all other nodes in grid to current node
            for node in self.nodes:
                # make sure a node cant be its own neighor
                if curr_node != node:
                    distance = ((curr_node.location[0] - node.location[0]) ** 2 + (
                                curr_node.location[1] - node.location[1]) ** 2) ** 0.5
                    # node within range?
                    if distance <= curr_node.range:
                        curr_node.neighbors.append(node)

                        dt = self.vertices[curr_node.id].adj
                        if node.id not in dt:
                            dt[node.id] = 1

    def bfs(self, begin_id, end_id):
        '''
        BFS for our system
        '''
        visited = []
        q = queue.SimpleQueue()

        q.put((begin_id, [begin_id]))

        while not q.empty():
            node_id, path = q.get()
            if node_id == end_id:
                return path
            if node_id not in visited:
                visited.append(node_id)
                for nb_id in self.vertices[node_id].adj:
                    if nb_id not in visited:
                        new_path = path[:]
                        new_path.append(nb_id)
                        q.put((nb_id, new_path))
        return []

    def dfs(self, begin_id, end_id):
        '''
        DFS for our system
        '''
        visited = []
        stack = []

        stack.append((begin_id, [begin_id]))

        while len(stack) != 0:
            node_id, path = stack.pop()
            if node_id == end_id:
                return path
            if node_id not in visited:
                visited.append(node_id)
                for nb_id in self.vertices[node_id].adj:
                    if nb_id not in visited:
                        new_path = path[:]
                        new_path.append(nb_id)
                        stack.append((nb_id, new_path))
        return []

    def euclidean_distance(self, node1, node2):
        import math 

        return math.sqrt((node1.location[0] - node2.location[1])**2 + (node1.location[1] - node2.location[1])**2)

    def a_star(self, begin_id, end_id):
        '''
        A* for our system
        '''
        visited = []
        q = queue.PriorityQueue()

        begin_node = self.vertices[begin_id]
        end_node = self.vertices[end_id]
        dist = self.euclidean_distance(begin_node, end_node)

        q.put( (dist, (begin_id, [begin_id], dist)) )

        while not q.empty():
            node_id, path, dist = q.get()[1]
            if node_id == end_id:
                return path
            if node_id not in visited:
                visited.append(node_id)
                for nb_id in self.vertices[node_id].adj:
                    if nb_id not in visited:
                        new_path = path[:]
                        new_path.append(nb_id)
                        new_dist = self.euclidean_distance(self.vertices[nb_id], end_node) + dist
                        q.put( (new_dist, (nb_id, new_path, new_dist)) )
        return []

    def distance_vector_routing(self):
        '''
        Distance Vector Routing: filling in the routing tables for the entirr system
        '''
        self.routing_tables = {}
        for node in self.nodes:
            self.routing_tables[node.id] = {n.id: (float('inf'), None) for n in self.nodes}
            self.routing_tables[node.id][node.id] = (0, node.id)  

        converged = False
        while not converged:
            converged = True

            for node in self.nodes:
                for neighbor_id, weight in node.adj.items():

                    for dest_id in self.routing_tables[node.id]:
                        if dest_id == neighbor_id:
                            continue

                        current_cost, next_hop = self.routing_tables[neighbor_id][dest_id]
                        potential_cost = self.routing_tables[node.id][dest_id][0] + weight

                        if potential_cost < current_cost:
                            self.routing_tables[neighbor_id][dest_id] = (potential_cost, node.id)
                            converged = False
        return "Success"
    
    def dvr_shortest_path(self, source_id, sink_id):
        '''
        Finding the shortest path from source to sink in the routing tables
        '''
        path = []
        next_hop = source_id

        while next_hop != sink_id:
            path.append(next_hop)
            next_hop = self.routing_tables[next_hop][sink_id][1]

            if next_hop is None:
                return None  

        path.append(sink_id)
        return path

    """
    super simple function to mimic probing singles while searching for routes
    i just took every node in the routes population and subtracted .2 from battery everytime it got hit
    once we have energy data we can make that a better value but for now i needed something that took out a chunk but not too much
    using 1 hits the sink and source 100 times so that kills them but .2 jsut puts them to like 80%
    tested node 156 it gets hit 35 times 35*.2 = 7 and it is at about 93% so looks good 
    """
    def battery_prob(self, routes):
        for route in routes:
            for node in route:
                self.nodes[int(node.id)].battery -= .2

        return 0

    def send_data(self, route):
        max_engergy_usage = 2
        min_energy_usage = 1
        for node in route:
            self.nodes[int(node.id)].battery -= random.randint(min_energy_usage, max_engergy_usage)

        self.node_status()

        return 0


    def gen_routes(self, source_node, pop_size):
        pop = []
        paths = set()

        # input into unique_dfs for as long as it takes to gen pop
        while len(pop) < pop_size:
            # start route at source
            route = [self.vertices[source_node]]

            # get route
            self.unique_dfs(route, paths)

            # sometimes the route deadends becasue all the nodes have been used, idk but this stops that
            if len(route) > 1:
                pop.append(route)

        self.battery_prob(pop)

        return pop

    def unique_dfs(self, route, paths):
        curr_node = route[-1]

        if curr_node.id == self.sink:
            # check if the route that is being genrated is in the already existing list of routes
            route_check = tuple(route)
            if route_check not in paths:
                paths.add(route_check)
                return True
            else:
                return False

        unused_nodes = []
        # step through adj nodes
        for neighbor in curr_node.adj:
            # check is any of the nodes in route match curr node
            # this avoids using the same node over and over
            if self.vertices[neighbor] not in route[:-1]:
                unused_nodes.append(self.vertices[neighbor])

        if not unused_nodes:
            return False

        # pick next random node to attemp
        # makes paths random
        ran_index = random.randint(0, len(unused_nodes)-1)
        nxt_node = unused_nodes[ran_index]
        route.append(nxt_node)

        # reenter recursion to test next node, if sink
        if self.unique_dfs(route, paths):
            return True

        # remove last node as it was a dead end
        route.pop()

        return False

    def plot_energy(self, average_energy_per_node):
        plt.plot(range(1, len(average_energy_per_node) + 1), average_energy_per_node, marker='o', linestyle='-')
        plt.xlabel('Signal Number')
        plt.ylabel('Energy Value (Joules)')
        plt.title('Energy Values At Each Signal Sent')
        plt.grid(True)
        plt.show()

    def plot_avfit(self, average_fit_per):
        plt.plot(range(1, len(average_fit_per) + 1), average_fit_per, marker='o', linestyle='-')
        plt.xlabel('Signal Number')
        plt.ylabel('Average Fitness')
        plt.title('Average Fitness At Each Signal Sent')
        plt.grid(True)
        plt.ylim(0, 100)  # Set the y-axis limits to 0 and 100
        plt.show()

    def plot_dead(self, dead_per_it):
        plt.plot(range(1, len(dead_per_it) + 1), dead_per_it, marker='o', linestyle='-')
        plt.xlabel('Signal Number')
        plt.ylabel('Number of Dead Nodes')
        plt.title('Number of Dead Nodes At Each Signal Sent')
        plt.grid(True)
        plt.show()
    
    def plot_dead_nodes_over_iterations(self, dead_nodes_counts_ga, dead_nodes_counts_as, algo_name=""):
        plt.plot(range(1, len(dead_nodes_counts_ga) + 1), dead_nodes_counts_ga, marker='o', linestyle='-', color='blue', label='GA')
        plt.plot(range(1, len(dead_nodes_counts_as) + 1), dead_nodes_counts_as, marker='o', linestyle='-', color='black', label=f'{algo_name}')
        plt.xlabel('Iteration')
        plt.ylabel('Number of Dead Nodes')
        plt.title('Number of Dead Nodes over Iterations')
        plt.grid(True)
        plt.legend()
        plt.show()
    
    def plot_energy_over_iterations(self, dead_nodes_counts_ga, dead_nodes_counts_as, algo_name=""):
        plt.plot(range(1, len(dead_nodes_counts_ga) + 1), dead_nodes_counts_ga, marker='o', linestyle='-', color='blue', label='GA')
        plt.plot(range(1, len(dead_nodes_counts_as) + 1), dead_nodes_counts_as, marker='o', linestyle='-', color='black', label=f'{algo_name}')
        plt.xlabel('Iteration')
        plt.ylabel('Energy Value')
        plt.title('Energy Value over Iterations')
        plt.grid(True)
        plt.legend()
        plt.show()