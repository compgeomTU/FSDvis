# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching FreeSpace.py
#

import math, logging
from collections import OrderedDict
import numpy as np

from traversalDistance.FreeSpaceGraph import FreeSpaceGraph
from traversalDistance.Graph import Graph
from Curve import Curve

class FreeSpace(FreeSpaceGraph):
    cell_boundaries_3D: list
    free_space_area: float

    def __init__(self, G, C, epsilon):
        super().__init__(G, C, epsilon)
        self.cell_boundaries_3D = list()
        self.free_space_area = 0.0

    def build_cell_boundaries_3D(self):
        logging.info("--------------- Cell Boundary Structure ---------------")
        for k, cb in self.cell_boundaries.items():
            is_log = False

            if k[0].__class__.__name__  == "Graph":
                for edge in self.g1.edges.values():
                    if k[1] in edge:
                        is_log = True
                        break
            elif k[0].__class__.__name__  == "Curve":
                is_log = True

            if is_log and (cb.start_fs != -1.0 and cb.end_fs != -1.0):
                logging.info(f"   CB Key: ({k[0].__class__.__name__} {k[1]} {k[2].__class__.__name__} {k[3]})   Boundery: |{cb.start_fs} --- {cb.end_fs}|")


        logging.info("--------------- FreeSpace Structure ---------------")
        for G_id, G_edge in self.g1.edges.items():
            for C_id, C_edge in self.g2.edges.items():
                xs, ys = self.buildFreeSpaceCell(G_id, C_id, G_edge, C_edge)
                logging.info(f"   Cell:   GEID: {G_id}   CEID: {C_id}   GE: {G_edge}   CE: {C_edge})")

                if len(xs) > 2 and len(ys) > 2:
                    logging.info(f"      FS          x:    {xs}")
                    logging.info(f"                  y:    {ys}")

                    G_n1_id, G_n2_id = G_edge[0], G_edge[1]
                    G_n1_x, G_n2_x = self.g1.nodes[G_n1_id][0], self.g1.nodes[G_n2_id][0]
                    G_n1_y, G_n2_y = self.g1.nodes[G_n1_id][1], self.g1.nodes[G_n2_id][1]

                    C_n1_id, C_n2_id = C_edge[0], C_edge[1]
                    C_l_z, C_u_z = self.g2.vertex_dists[C_n1_id], self.g2.vertex_dists[C_n2_id]

                    us, vs, ws = self.map_(G_n1_x, G_n2_x, G_n1_y, G_n2_y, C_l_z, C_u_z, xs, ys)
                    self.cell_boundaries_3D.append((us, vs, ws))
                    logging.info(f"      Mapped FS   u(x): {us}")
                    logging.info(f"                  v(y): {vs}")
                    logging.info(f"                  w(z): {ws}")

                else:
                    logging.info(f"      EMPTY       x:    {xs}")
                    logging.info(f"                  y:    {ys}")

    def calculateArea(self):

        for G_id, G_edge in self.g1.edges.items():
            for C_id, C_edge in self.g2.edges.items():
                xs, ys = self.buildFreeSpaceCell(G_id, C_id, G_edge, C_edge)

                if len(xs) > 2 and len(ys) > 2:
                    cb_area = 0.5 * np.abs(np.dot(xs, np.roll(ys, 1)) - np.dot(ys, np.roll(xs, 1)))

                    G_n1_id, G_n2_id = G_edge[0], G_edge[1]
                    G_n1_x, G_n2_x = self.g1.nodes[G_n1_id][0], self.g1.nodes[G_n2_id][0]
                    G_n1_y, G_n2_y = self.g1.nodes[G_n1_id][1], self.g1.nodes[G_n2_id][1]

                    C_n1_id, C_n2_id = C_edge[0], C_edge[1]
                    C_l_z, C_u_z = self.g2.vertex_dists[C_n1_id], self.g2.vertex_dists[C_n2_id]

                    scale = math.dist([G_n1_x, G_n1_y], [G_n2_x, G_n2_y]) * (C_u_z - C_l_z)
                    self.free_space_area += cb_area * scale

    def buildFreeSpaceCell(self, G_id, C_id, G_edge, C_edge):
        list_ = list()

        def append(a):
            if a not in list_: list_.append(a)

        # horizonal lower CB
        cb_1 = self.cell_boundaries[("g2", C_edge[0], "g1", G_id)]

        # vertical left CB
        cb_2 = self.cell_boundaries[("g1", G_edge[0], "g2", C_id)]

        # horizonal upper CB
        cb_3 = self.cell_boundaries[("g2", C_edge[1], "g1", G_id)]

        # vetical right CB
        cb_4 = self.cell_boundaries[("g1", G_edge[1], "g2", C_id)]

        if cb_1.end_fs != -1.0: append((cb_1.end_fs, 0.0))

        if cb_1.start_fs != -1.0: append((cb_1.start_fs, 0.0))

        if cb_2.start_fs != -1.0: append((0.0, cb_2.start_fs))

        if cb_2.end_fs != -1.0: append((0.0, cb_2.end_fs))

        if cb_3.start_fs != -1.0: append((cb_3.start_fs, 1.0))

        if cb_3.end_fs != -1.0: append((cb_3.end_fs, 1.0))

        if cb_4.end_fs != -1.0: append((1.0, cb_4.end_fs))

        if cb_4.start_fs != -1.0: append((1.0, cb_4.start_fs))

        if list_:
            x, y = zip(*list_)
            return list(x), list(y)
        else:
            return list(), list()

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
