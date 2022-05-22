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

    cell_boundaries_3D: OrderedDict

    def __init__(self, G, C, cells, epsilon):
        super().__init__(G, C, epsilon)
        self.cell_boundaries_3D = OrderedDict()

        for ids, cell in cells.cells.items():
            xs, ys = self.buildFreeSpaceCell(ids)

            if xs and ys:
                us, vs, ws = self.map_(self, cell, xs, ys)
                self.cell_boundaries_3D[ids] = (us, vs, ws)

        print(self.cell_boundaries_3D)



    def buildFreeSpaceCell(self, ids):

        list_ = list()

        def append(a):
            if a not in list_: list_.append(a)

        # for each cell , get 4 cell bounderies
        G_n1_id, G_n2_id, C_n1_id, C_n2_id = ids[0], ids[1], ids[2], ids[3]

        # horizonal lower CB
        cb_1 = self.cell_boundaries[(G_n1_id, C_n1_id, "Graph", "Curve")]

        # vertical left CB
        cb_2 = self.cell_boundaries[(G_n1_id, C_n1_id, "Curve", "Graph")]

        # horizonal upper CB
        cb_3 = self.cell_boundaries[(G_n1_id, C_n2_id, "Graph", "Curve")]

        # vetical right CB
        cb_4 = self.cell_boundaries[(G_n2_id, C_n1_id, "Curve", "Graph")]

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
    def map_(self, cell, xs, ys):

        # corner points of cell
        G_n1_x, G_n2_x = cell.x_proj[0][0], cell.x_proj[0][-1]
        G_n1_y, G_n2_y = cell.y_proj[0], cell.y_proj[-1]
        C_l_z, C_u_z = cell.z_proj[0][0], cell.z_proj[-1][0]

        # slope of cell in XY-plane
        a = (G_n2_y - G_n1_y) / (G_n2_x - G_n1_x)

        # lenght of cell in XY-plane
        l = math.sqrt((G_n2_x - G_n1_x)**2 + (G_n2_y - G_n1_y)**2)

        # <x, y> => <u, v, w> liniar map
        u = lambda x: (abs(G_n2_x - G_n1_x) * x) + min(G_n1_x, G_n2_x)
        v = lambda x: (a * l * x) + min(G_n1_x, G_n2_x)
        w = lambda y: (abs(C_u_z - C_l_z) * y) + min(C_l_z, C_u_z)

        us = list(map(u, xs))
        vs = list(map(v, xs))
        ws = list(map(w, ys))

        #print()
        #print(cell)
        #print("G Edge n1: ", G_n1_x, G_n1_y)
        #print("G Edge n2: ", G_n2_x, G_n2_y)
        #print("Curve l and u bounds: ", C_l_z, "--", C_u_z)

        #print(a)
        #print(l)
        #print(us)
        #print(vs)
        #print(ws)
        #print()

        return us, vs, ws

    def __str__(self):
        str_ = f"Number of CB's: {len(self.cell_boundaries_3D)} \n\n"
        for id, cb in self.cell_boundaries_3D.items():
            str_ += f"{id}: {cb} \n"

        return str_
