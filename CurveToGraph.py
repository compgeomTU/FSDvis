import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from Graph import Graph
from Curve import Curve
from Cell import Cell

class CurveToGraph:

    __verticefile: str
    __edgefile: str
    __curvefile: str

    __C: Curve
    __G: Graph

    __cells: list

    def __init__(self, verticefile, edgefile, curvefile):
        self.__verticefile = verticefile
        self.__edgefile = edgefile
        self.__curvefile = curvefile

        self.__C = Curve(curvefile)
        self.__G = Graph(verticefile, edgefile)

        self.__cells = list()


    def buildCells(self):
        for id, G_edge in self.__G.edges.items():

            n1_id, n2_id = G_edge[0], G_edge[1]
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]

            for i in range(self.__C.edge_count):
                cell = Cell(n1, n2, self.__C.edge_dists[i], self.__C.edge_dists[i+1])
                self.__cells.append(cell)

    def buildFreeSpace(self):
        pass

    def plotFreeSpaceCells():
        pass


    def plot(self):
        plt.gca().set_aspect(1.0)
        n = list()

        # building a graph
        for id, edge in self.__G.edges.items():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]

            if n1 not in n: n.append(n1)
            if n2 not in n: n.append(n2)

            plt.plot([n1[0], n2[0]], [n1[1], n2[1]],
                    color='dimgray', linewidth=2)

        lons, lats = map(list, zip(*n))
        plt.scatter(lons, lats, s=75, c='dimgray')

        for i in range(1, len(self.__C.edges)+1):
            X, Y = self.__C.xs[i-1:i+1], self.__C.ys[i-1:i+1]
            plt.plot(X, Y, '--', color='black', linewidth=3)

        plt.show()


if __name__ == "__main__":

    ctg = CurveToGraph("sample_files/P_vertices.txt",
                        "sample_files/P_edges.txt",
                        "sample_files/P_curve.txt")
    ctg.buildCells()

# python3 CurveToGraph.py
