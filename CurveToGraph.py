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
import sys

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

    #def __init__(self, graph_filename, curve_filename):

    #    self.__G = Graph(graph_filename)
    #    self.__C = Curve(curve_filename)

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

        for ids, cell in self.__cells.cells.items():
            ax.plot_surface(cell.x_proj, cell.y_proj, cell.z_proj, alpha=0.25, color='lightgray')

            #labeling vertices
            # ids = [(G_n1_id, G_n2_id, C_n1_id, C_n2_id)]
            G_n1_x, G_n2_x = cell.x_proj[0][0], cell.x_proj[0][1]
            G_n1_y, G_n2_y = cell.y_proj[0], cell.y_proj[1]

            C_n1_z, C_n2_z = cell.z_proj[0][0], cell.z_proj[1][0]

            ax.text(G_n1_x, G_n1_y, C_n1_z - 1,  ids[0], color='red', size=12)
            ax.text(G_n2_x, G_n2_y, C_n1_z - 1,  ids[1], color='red', size=12)

            ax.text(G_n1_x - 1, G_n1_y, C_n1_z,  ids[2], color='blue', size=12)
            ax.text(G_n1_x - 1, G_n1_y, C_n2_z,  ids[3], color='blue', size=12)

        for cell_cb in self.__freespace.cell_boundaries_3D:
            verticies = [list(zip(cell_cb[0], cell_cb[1], cell_cb[2]))]
            poly_cell = Poly3DCollection(verticies, alpha=1.0, facecolor='dimgray')
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

            # labeling vertices
            plt.text(n1[0], n1[1], f"{n1_id}", color='dimgray', size=12)
            plt.text(n2[0], n2[1], f"{n2_id}", color='dimgray', size=12)

        lons, lats = map(list, zip(*G_n))
        plt.scatter(lons, lats, s=35, c='dimgray')

        for edge in self.__C.edges.values():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__C.nodes[n1_id], self.__C.nodes[n2_id]
            plt.plot([n1[0], n2[0]], [n1[1], n2[1]], '--', color='black', linewidth=3)

            # labeling vertices
            plt.text(n1[0], n1[1], f"{n1_id}", color='black', size=12)
            plt.text(n2[0], n2[1], f"{n2_id}", color='black', size=12)

        plt.show()


if __name__ == "__main__":

    CTG_SAMPLE_NO = int(sys.argv[1])

    if CTG_SAMPLE_NO == 1:
        ctg = CurveToGraph("sample_files/P_vertices.txt",
                            "sample_files/P_edges.txt",
                            "sample_files/Q_vertices.txt",
                            "sample_files/Q_edges.txt")

    elif CTG_SAMPLE_NO == 2:
        ctg = CurveToGraph("sample_files/H_vertices.txt",
                            "sample_files/H_edges.txt",
                            "sample_files/G_vertices.txt",
                            "sample_files/G_edges.txt")

    elif CTG_SAMPLE_NO == 3:
        ctg = CurveToGraph("sample_files/arc_de_triomphe_vertices.txt",
                            "sample_files/arc_de_triomphe_edges.txt",
                            "sample_files/vehicle_path_vertices.txt",
                            "sample_files/vehicle_path_edges.txt")

    elif CTG_SAMPLE_NO == 4:
        ctg = CurveToGraph("sample_files/A_vertices.txt",
                            "sample_files/A_edges.txt",
                            "sample_files/B_vertices.txt",
                            "sample_files/B_edges.txt")

    #ctg = CurveToGraph("sample_files/P", "sample_files/Q")
    #ctg = CurveToGraph("sample_files/H", "sample_files/G")
    #ctg = CurveToGraph("sample_files/arc_de_triomphe", "sample_files/vehicle_path")

    if len(sys.argv) > 2:
        EPSILON = float(sys.argv[2])
        ctg.buildCells()
        ctg.buildFreeSpace(EPSILON)
        ctg.plotFreeSpace()

    else:
        ctg.plot()

    # python3 CurveToGraph.py <CTG_SAMPLE_NO> <EPSILON>
    # Example:
    # python3 CurveToGraph.py 4 1.25
