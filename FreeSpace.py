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

        for e_ids, v_ids in cells.cell_ids.items():
            xs, ys = self.buildFreeSpaceCell(e_ids, v_ids)

            if xs and ys:
                G_n1_id, G_n2_id = G.edges[e_ids[0]][0], G.edges[e_ids[0]][1]
                G_n1_x, G_n2_x = G.nodes[G_n1_id][0], G.nodes[G_n2_id][0]
                G_n1_y, G_n2_y = G.nodes[G_n1_id][1], G.nodes[G_n2_id][1]

                C_n1_id, C_n2_id = C.edges[e_ids[1]][0], C.edges[e_ids[1]][1]
                C_l_z, C_u_z = C.vertex_dists[C_n1_id], C.vertex_dists[C_n2_id]

                us, vs, ws = self.map_(G_n1_x, G_n2_x, G_n1_y, G_n2_y, C_l_z, C_u_z, xs, ys)

                self.cell_boundaries_3D.append((us, vs, ws))

    def buildFreeSpaceCell(self, e_ids, v_ids):
        list_ = list()

        def append(a):
            if a not in list_: list_.append(a)

        # horizonal lower CB
        cb_1 = self.cell_boundaries[('Curve', v_ids[1][0], 'Graph', e_ids[0])]

        # vertical left CB
        cb_2 = self.cell_boundaries[('Graph', v_ids[0][0], 'Curve', e_ids[1])]

        # horizonal upper CB
        cb_3 = self.cell_boundaries[('Curve', v_ids[1][1], 'Graph', e_ids[0])]

        # vetical right CB
        cb_4 = self.cell_boundaries[('Graph', v_ids[0][1], 'Curve', e_ids[1])]

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

        # <x, y> => <u, v, w> linear map
        u = lambda x: (G_n2_x - G_n1_x) * x + G_n1_x
        v = lambda x: (G_n2_y - G_n1_y) * x + G_n1_y
        w = lambda y: (C_u_z - C_l_z) * y + C_l_z

        us = list(map(u, xs))
        vs = list(map(v, xs))
        ws = list(map(w, ys))

        return us, vs, ws
