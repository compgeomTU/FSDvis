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
import time, logging

from traversalDistance.Graph import Graph
from Curve import Curve
from Cells import Cells
from FreeSpace import FreeSpace

class CurveToGraph:
    __C: Curve
    __G: Graph

    __cells: Cells
    __freespace: FreeSpace

    def __init__(self, graph_filename, curve_filename):
        self.__G = Graph(graph_filename)
        self.__C = Curve(curve_filename)

        logging.info("--------------- Graph Structure ---------------")
        for id, edge in self.__G.edges.items():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]
            logging.info(f"   E: {id}   V1: {n1_id} -> {n1}   V2: {n2_id} -> {n2}")

        logging.info("--------------- Sorted Curve Structure ---------------")
        for id, edge in self.__C.sorted_edges.items():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]
            logging.info(f"   E: {id}   V1: {n1_id} -> {n1}   V2: {n2_id} -> {n2}")

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
