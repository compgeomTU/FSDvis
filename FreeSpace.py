# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching Cells.py
#

import math, logging
from collections import OrderedDict

from traversalDistance.FreeSpaceGraph import FreeSpaceGraph
from traversalDistance.Graph import Graph
from Curve import Curve

class FreeSpace(FreeSpaceGraph):
    cell_boundaries_3D: list
    C: Curve
    G: Graph

    def __init__(self, G, C, cells, epsilon):
        super().__init__(G, C, epsilon)
        self.cell_boundaries_3D = list()
        self.C = C
        self.G = G

        logging.info("--------------- FreeSpace Structure ---------------")
        for G_id, G_edge in G.edges.items():
            for C_id, C_edge in C.sorted_edges.items():
                xs, ys = self.buildFreeSpaceCell(G_id, C_id, G_edge, C_edge)
                logging.info(f"   Cell:   GEID: {G_id}   CEID: {C_id}   GE: {G_edge}   CE: {C_edge})")

                if xs is not None and ys is not None:
                    logging.info(f"      FS          x: {xs}")
                    logging.info(f"                  y: {ys}")

                    G_n1_id, G_n2_id = G_edge[0], G_edge[1]
                    G_n1_x, G_n2_x = G.nodes[G_n1_id][0], G.nodes[G_n2_id][0]
                    G_n1_y, G_n2_y = G.nodes[G_n1_id][1], G.nodes[G_n2_id][1]

                    C_n1_id, C_n2_id = C_edge[0], C_edge[1]
                    C_l_z, C_u_z = C.vertex_dists[C_n1_id], C.vertex_dists[C_n2_id]

                    us, vs, ws = self.map_(G_n1_x, G_n2_x, G_n1_y, G_n2_y, C_l_z, C_u_z, xs, ys)
                    self.cell_boundaries_3D.append((us, vs, ws))
                    logging.info(f"      Mapped FS   u(x): {us}")
                    logging.info(f"                  v(y): {vs}")
                    logging.info(f"                  w(z): {ws}")

                else:
                    logging.info(f"      EMPTY")

    def buildFreeSpaceCell(self, G_id, C_id, G_edge, C_edge):
        list_ = list()

        def append(a):
            if a not in list_: list_.append(a)

        # horizonal lower CB
        cb_1 = self.cell_boundaries[(self.C, C_edge[0], self.G, G_id)]

        # vertical left CB
        cb_2 = self.cell_boundaries[(self.G, G_edge[0], self.C, C_id)]

        # horizonal upper CB
        cb_3 = self.cell_boundaries[(self.C, C_edge[1], self.G, G_id)]

        # vetical right CB
        cb_4 = self.cell_boundaries[(self.G, G_edge[1], self.C, C_id)]

        if cb_1.end_fs != -1.0: append((cb_1.end_fs, 0.0))

        if cb_1.start_fs != -1.0: append((cb_1.start_fs, 0.0))

        if cb_2.start_fs != -1.0: append((0.0, cb_2.start_fs))

        if cb_2.end_fs != -1.0: append((0.0, cb_2.end_fs))

        if cb_3.start_fs != -1.0: append((cb_3.start_fs, 1.0))

        if cb_3.end_fs != -1.0: append((cb_3.end_fs, 1.0))

        if cb_4.end_fs != -1.0: append((1.0, cb_4.end_fs))

        if cb_4.start_fs != -1.0: append((1.0, cb_4.start_fs))

        if len(list_) > 2:
            x, y = zip(*list_)
            return list(x), list(y)
        else:
            return None, None

    @staticmethod
    def map_(G_n1_x, G_n2_x, G_n1_y, G_n2_y, C_l_z, C_u_z, xs, ys):

        # <x, y> => <u, v, w> linear map
        u = lambda x: (G_n2_x - G_n1_x) * x + G_n1_x
        v = lambda x: (G_n2_y - G_n1_y) * x + G_n1_y
        w = lambda y: (C_u_z - C_l_z) * y + C_l_z

        us = list(map(u, xs))
        vs = list(map(v, xs))
        ws = list(map(w, ys))

        return us, vs, ws
