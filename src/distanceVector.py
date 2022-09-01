"""
Código para el algoritmo de DVR.
Ale Gudiel 
Majo Morales 
Marisa Montoya
"""
import networkx as nx

class DistanceVector():
    '''Distance Vector Routing'''

    def __init__(self, graph, graph_dict, source, names):
        self.graph = graph
        self.graph_dict = graph_dict
        self.source = source
        self.distance, self.predecessor = self.bellman_ford(graph_dict, source)
        self.names = names
        self.neighbors = self.get_neighbors(graph_dict, source)

    def initialize(self, graph_dict, source):
        '''For each node prepare the destination and predecessor'''
        d = {} # Stands for destination
        p = {} # Stands for predecessor
        for node in graph_dict:
            d[node] = float('Inf') # We start admiting that the rest of nodes are very very far
            p[node] = None
        d[source] = 0 # For the source we know how to reach
        return d, p

    def relax(self, node, neighbour, graph_dict, d, p):
        '''If the distance between the node and the neighbour is lower than the one I have now'''
        if d[neighbour] > d[node] + graph_dict[node][neighbour]:
            # Record this lower distance
            d[neighbour]  = d[node] + graph_dict[node][neighbour]
            p[neighbour] = node

    def bellman_ford(self, graph_dict, source):
        '''Bellman Ford Alg'''

        d, p = self.initialize(graph_dict, source)
        for i in range(len(graph_dict)-1): #Run this until is converges
            for u in graph_dict:
                for v in graph_dict[u]: #For each neighbour of u
                    self.relax(u, v, graph_dict, d, p) #Lets relax it

        # Step 3: check for negative-weight cycles
        for u in graph_dict:
            for v in graph_dict[u]:
                assert d[v] <= d[u] + graph_dict[u][v]

        return d, p

    def get_neighbors(self, graph_dict, source):
        '''List of neighbors'''

        return list(graph_dict[source].keys())


    def update_graph(self, graph_dict):
        '''Update graph_dict'''

        updated_graph = {}

        for node in graph_dict:
            updated_graph[node] = {}
            for neighbor_node in graph_dict[node]:
                updated_graph[node][neighbor_node] = graph_dict[node][neighbor_node]['weight']

        self.graph_dict = updated_graph
        self.distance, self.predecessor = self.bellman_ford(updated_graph, self.source)
        self.neighbors = self.get_neighbors(updated_graph, self.source)

    def shortest_path(self, target):
        '''Find shortest path'''
        for key in self.names:
            if self.names[key] == target:
                return nx.bellman_ford_path(self.graph, self.source, key)
        return None
