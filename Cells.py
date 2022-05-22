# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching Cells.py
#

import numpy as np

class Cells:

    cells: dict

    def __init__(self, G, C):
        self.cells = dict()

        for G_edge in G.edges.values():

            G_n1_id, G_n2_id = G_edge[0], G_edge[1]
            G_n1, G_n2 = G.nodes[G_n1_id], G.nodes[G_n2_id]

            for C_edge in C.sorted_edges.values():

                C_n1_id, C_n2_id = C_edge[0], C_edge[1]
                C_n1, C_n2 = G.nodes[C_n1_id], G.nodes[C_n2_id]
                C_lower_vertex, C_upper_vertex = \
                    C.vertex_dists[C_n1_id], C.vertex_dists[C_n2_id]

                cell = Cell(G_n1, G_n2, C_lower_vertex, C_upper_vertex)
                self.cells[(G_n1_id, G_n2_id, C_n1_id, C_n2_id)] = cell

    def __str__(self):
        return str(self.cells)

class Cell:

    x_proj: np.ndarray
    y_proj: np.ndarray
    z_proj: np.ndarray

    __area: float

    def __init__(self, G_edge_v1, G_edge_v2, C_edge_lower_vertex, C_edge_upper_vertex):
        x = np.linspace(G_edge_v1[0], G_edge_v2[0], 3)
        y = np.linspace(C_edge_lower_vertex, C_edge_upper_vertex, 3)

        self.__area = abs(x[-1] - x[0]) * abs(y[-1] - y[0])
        self.x_proj, self.z_proj = np.meshgrid(x, y)
        self.y_proj = np.linspace(G_edge_v1[1], G_edge_v2[1], 3)

    def __str__(self):
        return "Area: {:04.2f}".format(self.__area)

    def __repr__(self):
        return self.__str__()
