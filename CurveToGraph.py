# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching Cells.py
#

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from Graph import Graph
from Curve import Curve
from Cells import Cells
from FreeSpace import FreeSpace

class CurveToGraph:

    __graph_verticefile: str
    __graph_edgefile: str
    __curve_verticefile: str
    __curve_edgefile: str

    __C: Curve
    __G: Graph

    __cells: Cells
    __freespace: FreeSpace

    def __init__(self, graph_verticefile, graph_edgefile,
                    curve_verticefile, curve_edgefile):

        self.__graph_verticefile = graph_verticefile
        self.__graph_edgefile = graph_edgefile
        self.__curve_verticefile = curve_verticefile
        self.__curve_edgefile = curve_edgefile

        self.__G = Graph(graph_verticefile, graph_edgefile)
        self.__C = Curve(curve_verticefile, curve_edgefile)

    # no. of cells = no. of G edges x no. of C edges
    def buildCells(self):
        self.__cells = Cells(self.__G, self.__C)

    def buildFreeSpace(self, epsilon):
        self.__freespace = FreeSpace(self.__G, self.__C, self.__cells, epsilon)

    def plotFreeSpaceCells():
        pass

    def plot(self):
        plt.gca().set_aspect(1.0)
        G_n = list()

        for edge in self.__G.edges.values():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]

            if n1 not in G_n: G_n.append(n1)
            if n2 not in G_n: G_n.append(n2)

            plt.plot([n1[0], n2[0]], [n1[1], n2[1]],
                    color='dimgray', linewidth=2)

        lons, lats = map(list, zip(*G_n))
        plt.scatter(lons, lats, s=75, c='dimgray')

        for edge in self.__C.edges.values():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__C.nodes[n1_id], self.__C.nodes[n2_id]
            plt.plot([n1[0], n2[0]], [n1[1], n2[1]], '--', color='black', linewidth=3)

        plt.show()


if __name__ == "__main__":

    ctg = CurveToGraph("sample_files/P_vertices.txt",
                        "sample_files/P_edges.txt",
                        "sample_files/Q_vertices.txt",
                        "sample_files/Q_edges.txt")
    ctg.buildCells()
    ctg.buildFreeSpace(19.0)

# python3 CurveToGraph.py
