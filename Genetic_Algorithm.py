import random
import math

from Network_Simulation import Node, DangerZones, GridSpace

class GenAlgo:
    def get_fit(self, route):
        engergy_fit = 0
        dist_fit = 0
        cong_fit = 0
        safe_count = 0

        source = route[0]
        sink = route[-1]

        for i in range(len(route)-1):
            node = route[i]
            next = route[i+1]

            engergy_fit += node.battery

            dist_fit += math.sqrt((next.location[0] - node.location[0]) ** 2 + (next.location[1] - node.location[1]) ** 2 )

            #TODO: need to add
            cong_fit += 0

            if not node.danger:
                safe_count += 1

            if next.id == sink.id:
                engergy_fit += next.battery

                if not next.danger:
                    safe_count += 1

        ideal_dist = math.sqrt((sink.location[0] - source.location[0]) ** 2 + (sink.location[1] - source.location[1]) ** 2 )

        ideal_engergy = len(route) * 100

        ideaal_safe = len(route)

        cong_fit = dist_fit / (3*10**8)
        ideal_cong = 1

        fit_score = (((ideal_dist / dist_fit) + (engergy_fit / ideal_engergy) + (ideal_cong / cong_fit) + (safe_count / ideaal_safe)) / 4) *100
        return fit_score
        #TODO: idk
        ideal_cong = 0

        #im trying to set up our fitness to be the higher the better
        #distance:
            #the ideal distance would be a straight shot from souce to sink
            #this is very unlikly because dist_fit will almost always be longer
            #because there is never going to be one correct answer we want to reward the clsoer the better
            #so the closer to ideal the better
            #to do this i have ideal_dist over fit_dist
                #if the distance is equal to the ideal then this will = 1
                #but normally this will result in a decimal, the smaller this decimal the worse
                #say ideal = 5 and the current dist is 10 that would output .5
                #if ideal is 5 and current is 100 that will be .05
                #but if it is 6 then it will be .833 a very close to ideal distance
            #total dist over the ideal dist will output a number

        #energy:
            #similar to the dist our ideal energy is all 100% charged nodes
            #but our node will never all be charged so we want to represent the closer to that the better
            # so here we want the reverse of dist, curr_energy / ideal
                #if all are charged then this is 1
                #if half are charged then 500 / 1000 for a route charge of 50%
                # if nearly none are charged then 100/ 1000 for a 10% charge

        #congestion:

        #danger nodes:
            #the ideal number of danger nodes is zero
            #so we want to represent a score that is 1 when none of the nodes are in danger and 0 when they all are
            #to do this we count the number of nodes in the route that are not in danger
            #so safe_nodes / total_nodes
                #if all the nodes are safe the output will be 1
                # the more that are in danger the lower the score

        #all of our fitness values are on a scale of 0 to 1 so we add them together and divide by 3 to average
        #mult the result by 100 to get a 1-100 fitness scale per route
        fit_score = (((ideal_dist / dist_fit) + (engergy_fit / ideal_engergy) + 0 + (safe_count / ideaal_safe)) / 3) *100 #need to change 3 to 4 after
        return fit_score

    def dfs(self, begin, end, nodes):
        '''
        DFS for our system
        '''
        visited = []
        stack = []

        stack.append((begin, [begin]))

        while len(stack) != 0:
            node, path = stack.pop()
            if node.id == end.id:
                return path
            if node.id not in visited:
                visited.append(node.id)
                for nb in node.adj:
                    if nb not in visited:
                        new_path = path[:]
                        new_path.append(nodes[int(nb)])
                        stack.append((nodes[int(nb)], new_path))
        return []



    # we could always make it so there is a chance for each node? nah
    #does not work
    def new_mut(self, child, nodes):
        options = []
        child_nodes = []

        for i in child:
            child_nodes.append(i.id)


        for node in nodes:
            if node.id not in child_nodes:
                options.append(node.id)

        new_node = nodes[int(random.choice(options))]
        old_node = random.randint(1, len(child)-2)

        before = self.dfs(child[old_node-1], new_node, nodes)
        after = self.dfs(new_node, child[old_node+1], nodes)

        new_path = child[:old_node] + before[1:-1] + [new_node] + after[1:-1] + child[old_node+1:]

        test = []
        for i in new_path:
            test.append(i.id)

        final_child = []
        seen = set()

        # fix redundant nodes
        test = []
        for i in final_child:
            if i.id in test:
                pass
            test.append(i.id)
        pass

        return new_path

    def mutation(self, child, nodes):
        options = []
        child_nodes = []

        for i in child:
            child_nodes.append(i.id)

        # Select node to delete
        old_node = random.randint(1, len(child)-2)

        if child[old_node+1] in child[old_node-1].neighbors and child[old_node-1] in child[old_node+1].neighbors:
            new_path = child[:old_node] + child[old_node+1:]
        else:
            connection = self.dfs(child[old_node-1], child[old_node+1], nodes)
            new_path = child[:old_node] + connection[1: -1] + child[old_node + 1:]

        return new_path

    def tornament_selection(self, pop, tor_size):
        tornament = random.sample(pop, tor_size)
        tornament.sort(reverse=True, key=lambda i: self.get_fit(i))
        return tornament[0]


    def new_cross(self, par1, par2):
        possible_points = par1[1:-1]

        while possible_points:

            cross_point = random.choice(possible_points)

            if cross_point in par2:
                par1_index = par1.index(cross_point)
                par2_index = par2.index(cross_point)

                child1 = par1[:par1_index] + par2[par2_index:]
                child2 = par2[:par2_index] + par1[par1_index:]

                return [child1, child2]

            else:
                possible_points.remove(cross_point)

        return []


    def GA(self, max_gen, next_gen, routes, nodes, p_c, p_m, tor_size=5):

        pop_size = len(routes)

        for generation in range(max_gen):

            children = []

            for i in range(int(next_gen/2)):
                kids = []

                if p_c > random.random():
                    while len(kids) == 0:
                        par1 = self.tornament_selection(routes, tor_size)
                        par2 = self.tornament_selection(routes, tor_size)

                        kids = self.new_cross(par1, par2)


                        if p_m > random.random() and len(kids) != 0:
                            kids[0] = self.mutation(kids[0], nodes)
                            kids[1] = self.mutation(kids[1], nodes)

                children = children + kids

            routes = routes + children
            routes.sort(reverse=True, key=lambda i: self.get_fit(i))
            routes = routes[:pop_size]

        routes.sort(reverse=True, key=lambda i: self.get_fit(i))

        return routes