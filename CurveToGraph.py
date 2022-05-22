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
import numpy as np
import time

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

    # no of CBs in FreeSpace class = no. of cells * 4
    def buildFreeSpace(self, epsilon):
        self.__freespace = FreeSpace(self.__G, self.__C, self.__cells, epsilon)

    def plotFreeSpace(self):
        ax = plt.gca(projection = '3d')
        ax.grid(False)
        ax._axis3don = False

        for id, cell in self.__cells.cells.items():
            ax.plot_surface(cell.x_proj, cell.y_proj, cell.z_proj, alpha=0.5, color='lightgray')

            if id in self.__freespace.cell_boundaries_3D:
                cell_cb = self.__freespace.cell_boundaries_3D[id]
                verticies = [list(zip(cell_cb[0], cell_cb[1], cell_cb[2]))]
                poly_cell = Poly3DCollection(verticies, alpha=1.0,facecolor='dimgray')
                ax.add_collection3d(poly_cell)

        plt.show()

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
    ctg.buildFreeSpace(2.0)
    ctg.plotFreeSpace()

# python3 CurveToGraph.py
