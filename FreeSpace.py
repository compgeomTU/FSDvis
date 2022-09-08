# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching Cells.py
#

import math
from collections import OrderedDict

from FreeSpaceGraph import FreeSpaceGraph

class FreeSpace(FreeSpaceGraph):
    cell_boundaries_3D: list

    def __init__(self, G, C, cells, epsilon):
        super().__init__(G, C, epsilon)
        self.cell_boundaries_3D = list()

        for e, v in cells.cell_ids.items():
            xs, ys = self.buildFreeSpaceCell(e, v)

            if xs and ys:
                G_n1_id, G_n2_id = G.edges[e[0]][0], G.edges[e[0]][1]
                G_n1_x, G_n2_x = G.nodes[G_n1_id][0], G.nodes[G_n2_id][0]
                G_n1_y, G_n2_y = G.nodes[G_n1_id][1], G.nodes[G_n2_id][1]

                C_n1_id, C_n2_id = C.edges[e[1]][0], C.edges[e[1]][1]
                C_l_z, C_u_z = C.vertex_dists[C_n1_id], C.vertex_dists[C_n2_id]

                us, vs, ws = self.map_(G_n1_x, G_n2_x, G_n1_y, G_n2_y, C_l_z, C_u_z, xs, ys)

                self.cell_boundaries_3D.append((us, vs, ws))

    def buildFreeSpaceCell(self, e, v):
        list_ = list()

        def append(a):
            if a not in list_: list_.append(a)

        ### LOOK INTO ########################### 09/01/2022

        class TestCellBoundary():
            start_fs = 0.50
            end_fs = 0.50

        # horizonal lower CB
        cb_1 = TestCellBoundary()

        # vertical left CB
        cb_2 = TestCellBoundary()

        # horizonal upper CB
        cb_3 = TestCellBoundary()

        # vetical right CB
        cb_4 = TestCellBoundary()

        ### LOOK INTO #############################

        # check CB values and add to coordinate system
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
            return list(), list()

    @staticmethod
    def map_(G_n1_x, G_n2_x, G_n1_y, G_n2_y, C_l_z, C_u_z, xs, ys):

        # slope of cell in XY-plane
        if (G_n2_x - G_n1_x) != 0.0:
            a = ((G_n2_y - G_n1_y) / (G_n2_x - G_n1_x)) * abs(G_n2_x - G_n1_x)
        else:
            a = G_n2_y - G_n1_y

        if a > 0.0:
            b = min(G_n1_y, G_n2_y)
        elif a == 0.0:
            b = min(G_n1_y, G_n2_y)
        else:
            b = max(G_n1_y, G_n2_y)

        # <x, y> => <u, v, w> linear map
        u = lambda x: (abs(G_n2_x - G_n1_x) * x) + min(G_n1_x, G_n2_x)
        v = lambda x:  a * x + b
        w = lambda y: (abs(C_u_z - C_l_z) * y) + min(C_l_z, C_u_z)

        us = list(map(u, xs))
        vs = list(map(v, xs))
        ws = list(map(w, ys))

        return us, vs, ws

    def __str__(self):
        str_ = f"Number of CB's: {len(self.cell_boundaries_3D)} \n\n"
        for id, cb in self.cell_boundaries_3D.items():
            str_ += f"{id}: {cb} \n"

        return str_
