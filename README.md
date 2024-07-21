# CSE812-project
## By Nicole Schneider, Alec Said, & Abhinay Devapatla

### Genetic_Algorithm.py
In this file, you will find our custom GA we created. It contains all the componenets of a GA: tournament selection, fitness function, congestion,crossover, and mutation. 

### Network_Simulation.py
In this file, you will find out custom node network simulation we created. It creates our nodes, our danger zones, and our grid space (the node network). This file contains all the functionality needed to simulate the node network (generating nodes, a sink node, node locations, node energy changes) and simulate the affects of danger zones (danger zone movement, node deaths). You can also plot the danger zones and node network via the DangerZone class. 

### a_star.py and dvr.py
This is where we run the network simulation and compare it against the greedy search algorithm A* and Distance Vector Routing (DVR) Protocol, respestively. Each file generates a network for the GA and A*/DVR to run on, plots the remaining energy and number of dead nodes, and outputs the percentage better or worse the GA is against A*/DVR. To replicate the results in the project report, do the following: 

For number of nodes = 200,
- a_star.py
    - change line 19 to 'network.populate_grid(200, 10, 0.9)'
    - change line 110 to 'network1.populate_grid(200, 10, 0.9)'
- dvr.py
    - change line 19 to 'network.populate_grid(200, 10, 0.9)'
    - change line 110 to 'network1.populate_grid(200, 10, 0.9)'

For number of nodes = 250,
- a_star.py
    - change line 19 to 'network.populate_grid(250, 10, 0.9)'
    - change line 110 to 'network1.populate_grid(250, 10, 0.9)'
- dvr.py
    - change line 19 to 'network.populate_grid(250, 10, 0.9)'
    - change line 110 to 'network1.populate_grid(250, 10, 0.9)'

For number of nodes = 300,
- a_star.py
    - change line 19 to 'network.populate_grid(300, 10, 0.9)'
    - change line 110 to 'network1.populate_grid(300, 10, 0.9)'
- dvr.py
    - change line 19 to 'network.populate_grid(300, 10, 0.9)'
    - change line 110 to 'network1.populate_grid(300, 10, 0.9)'