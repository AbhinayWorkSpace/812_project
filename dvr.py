import random
import math

from Network_Simulation import Node, DangerZones, GridSpace
from Genetic_Algorithm import GenAlgo

# crossover rate : 80%
p_c = 0.8
# mutation rate: 10%
p_m = 0.1
# population size
pop_size = 100
# max number of children each gen
offspring_size = 20

# Create a network of nodes
print("Creating network of nodes...")
network = GridSpace(100, 100)
network.populate_grid(250, 10, 0.9)
network.add_danger_zones(5, max_width=10, max_height=10)
network.connect_network()
print("Network of nodes created.")

# Make a request for the available routes from sink to destination node
source = "10"

print("Generating initial population of routes...")
# Generate initial population of routes
routes = network.gen_routes(source, pop_size)
print("Initial population of routes generated.")

# number of generations
max_gen = 50
# nodes in network
nodes = network.nodes

# set up GA class
test = GenAlgo()

# number of signals sent
sigs = 100

# use ga
#network.plot_grid()

average_fit_per = []
average_energy_per_node = []
nodes_each_it = []
dead_per_it = []

efficient_routes = []
for s in range(sigs):
    # Find a source node
    # source = str(random.randint(0, len(nodes)-1))
    # while nodes[int(source)].dead:
    #     source = str(random.randint(0, len(nodes)-1))

    # print("Generating initial population of routes...")
    # # Generate initial population of routes
    # routes = network.gen_routes(source, pop_size)
    # print("Initial population of routes generated.")

    nodes_each_it.append(nodes)

    ded = 0
    for i in nodes:
        if i.dead:
            ded+=1
    dead_per_it.append(ded)

    tot = 0
    for i in efficient_routes:
        tot += test.get_fit(i)
    average_fit_per.append(tot / pop_size)

    bat = 0
    for i in nodes:
        bat += i.battery
    average_energy_per_node.append(bat/(len(nodes)))

    print("Running genetic algorithm...")
    efficient_routes = test.GA(max_gen, offspring_size, routes, nodes, p_c, p_m)
    print("Genetic algorithm finished.")

    #update danger zones 20% chance they shift
    if 2 > random.random():
        network.add_danger_zones(5, max_width=10, max_height=10)

    #used to kill nodes to see if my funcs work
    #network.nodes[random.randint(0, 199)].battery = 0

    #update all nodes battery and if dead
    print("Updating all nodes in network...")
    network.send_data(efficient_routes[0])
    network.check_danger(efficient_routes[0])
    network.node_status()
    nodes = network.nodes
    network.connect_network()
    print("All nodes in network updated.")

#network.plot_energy(average_energy_per_node)
#network.plot_avfit(average_fit_per)
#network.plot_dead(dead_per_it)

#print('Efficient Routes: ', (efficient_routes))

print("Finishing up...")

network2 = GridSpace(100, 100)
network2.populate_grid(250, 10, 0.9)
network2.add_danger_zones(5, max_width=10, max_height=10)
network2.connect_network()

nodes = network2.nodes

average_fit_per = []
average_energy_per_node2 = []
nodes_each_it = []
dead_per_it2 = []
efficient_routes = []
for s in range(100):
    nodes_each_it.append(nodes)

    ded = 0
    for i in nodes:
        if i.dead:
            ded+=1
    dead_per_it2.append(ded)

    bat = 0
    for i in nodes:
        bat += i.battery
    average_energy_per_node2.append(bat/(len(nodes)))

    print("Finding new DVR routes...sigs = ", s)
    network2.distance_vector_routing()
    print("Finished sigs = ", s)

    temp = network2.dvr_shortest_path("10", network2.sink)
    temp1 = []
    print(temp)
    for n in temp:
        temp1.append(network2.vertices[n])
    #print(temp, temp1)
    efficient_routes.append(temp1)

    network2.battery_prob(efficient_routes)

    #update danger zones 20% chance they shift
    if 2 > random.random():
        network2.add_danger_zones(5, max_width=10, max_height=10)

    #used to kill nodes to see if my funcs work
    #network.nodes[random.randint(0, 199)].battery = 0

    #update all nodes battery and if dead
    network2.send_data(efficient_routes[-1])
    network2.check_danger(efficient_routes[-1])
    network2.node_status()
    nodes = network2.nodes
    network2.connect_network()

print("Calculating accuracy score...")

mth = []
for i in range(len(average_energy_per_node)):
    mth.append(average_energy_per_node[i] - average_energy_per_node2[i])

print("DVR Energy Performance", sum(mth)/len(mth))

mth = []
for i in range(len(dead_per_it)):
    mth.append(dead_per_it2[i] - dead_per_it[i])

print("DVR Dead Node Performance: ", sum(mth)/len(mth))

network.plot_dead_nodes_over_iterations(dead_per_it, dead_per_it2, "DVR")
network.plot_energy_over_iterations(average_energy_per_node, average_energy_per_node2, "DVR")