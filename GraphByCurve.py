# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching GraphByCurve.py
#

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import time, logging

from traversalDistance.Graph import Graph
from Curve import Curve
from Cells import Cells
from FreeSpace import FreeSpace

class GraphByCurve:
    __C: Curve
    __G: Graph
    __cells: Cells
    __freespace: FreeSpace

    def __init__(self, G, C):
        self.__G = G
        self.__C = C

        logging.info("--------------- Graph Structure ---------------")
        for id, edge in self.__G.edges.items():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]
            logging.info(f"   E: {id}   V1: {n1_id} -> {n1}   V2: {n2_id} -> {n2}")

        logging.info("--------------- Curve Structure ---------------")
        for id, edge in self.__C.edges.items():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__C.nodes[n1_id], self.__C.nodes[n2_id]
            logging.info(f"   E: {id}   V1: {n1_id} -> {n1}   V2: {n2_id} -> {n2}")

    # no. of cells = no. of G edges x no. of C edges
    def buildCells(self):
        self.__cells = Cells(self.__G, self.__C)

    # no of CBs in FreeSpace class = no. of cells * 4
    def buildFreeSpace(self, epsilon):
        self.__freespace = FreeSpace(self.__G, self.__C, self.__cells, epsilon)

    def plotFreeSpace(self, figue_filename=None):
        ax = plt.gca(projection = '3d')
        ax.grid(False)
        ax._axis3don = False

        for ids, cell in self.__cells.cells.items():
            ax.plot_surface(cell.x_proj, cell.y_proj, cell.z_proj, alpha=0.25, color='lightgray', edgecolor ='black')

        for cell_cb in self.__freespace.cell_boundaries_3D:
            verticies = [list(zip(cell_cb[0], cell_cb[1], cell_cb[2]))]
            poly_cell = Poly3DCollection(verticies, alpha=1.0, facecolor='dimgray', edgecolor='black')
            ax.add_collection3d(poly_cell)

        for id, edge in self.__G.edges.items():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]
            ax.text((n2[0]+n1[0])/2, (n2[1]+n1[1])/2, 0.25,  id, color='black', size=12)

        if figue_filename is None:
            plt.show()
        else:
            plt.savefig(figue_filename)

    def plot(self, figue_filename):
        plt.gca().set_aspect(1.0)
        G_n = list()

        for id, edge in self.__G.edges.items():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]

            if n1 not in G_n: G_n.append(n1)
            if n2 not in G_n: G_n.append(n2)

            plt.plot([n1[0], n2[0]], [n1[1], n2[1]], color='black', linewidth=2)
            plt.text((n2[0]+n1[0])/2, ((n2[1]+n1[1])/2)+0.25,  id, color='black', size=12)

        lons, lats = map(list, zip(*G_n))
        plt.scatter(lons, lats, s=35, c='black')

        for edge in self.__C.edges.values():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.__C.nodes[n1_id], self.__C.nodes[n2_id]
            plt.plot([n1[0], n2[0]], [n1[1], n2[1]], '--', color='dimgray', linewidth=3)

        if figue_filename is None:
            plt.show()
        else:
            plt.savefig(figue_filename)

    def set_graph(G):
        self.__G = G

    def set_curve(C):
        self.__C = C
