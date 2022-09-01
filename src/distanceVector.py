"""
Código para el algoritmo de DVR.
Ale Gudiel 
Majo Morales 
Marisa Montoya
"""
import networkx as nx

class DistanceVector():
    def __init__(self, graph, graphNx, source, name):
        self.graph = graph
        self.graphNx = graphNx
        self.source = source
        self.name = name
        self.distance, self.prev = self.bellman_ford(graphNx, source)

    def start(self, graphNx, source):
        d = {}
        p = {}
        for node in graphNx:
            d[node] = float('inf')
            p[node] = None
        d[source] = 0
        return d, p

    def neighbors(self, graphNx, source):
        return list(graphNx[source].keys())
    
    def bellman_ford(self, graphNx, source):
        d, p = self.start(graphNx, source)
        for i in range(len(graphNx) - 1):
            for node in graphNx:
                for neighbor in graphNx[node]:
                    if d[neighbor] > d[node] + graphNx[node][neighbor]:
                        d[neighbor] = d[node] + graphNx[node][neighbor]
                        p[neighbor] = node
        return d, p

    def updateGraph(self, graphNx):
        updateGraph = {}

        for node in graphNx:
            updateGraph[node] = {}
            for neighbor in graphNx[node]:
                updateGraph[node][neighbor] = graphNx[node][neighbor]
        
        self.graphNx = updateGraph
        self.distance, self.prev = self.bellman_ford(self.graphNx, self.source)
        self.neighbors = self.neighbors(updateGraph, self.source)

    def shortest_path(self, target):
        for key in self.name:
            if self.name[key] == target:
                return nx.bellman_ford_path(self.graphNx, self.source, key)
        return None
    

