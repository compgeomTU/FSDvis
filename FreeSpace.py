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

        # itterate though all cells of free space graph
        for key in cells.cells.keys():

            xs, ys = self.build2DFreeSpace(key)

            # transform function 

    def build2DFreeSpace(self, ids):

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

        print(list_)

        if len(list_) > 2:
            x, y = zip(*list_)
            return list(x), list(y)
        else:
            return x.clear(), y.clear()


    # e: edge of graph
    # l: lower bound of cells elevation
    # u: upper bound of cells elevation
    def transform(self, e, lower_b, upper_b, xs, ys):

        # e: 2 3D coord points that define the edge
        e0_x, e0_y = e[0][0], e[0][1]
        e1_x, e1_y = e[1][0], e[1][1]

        # l: lenght of horizonal boundry of surface
        l = sqrt((e1_x-e0_x)**2+(e1_y-e0_y)**2)

        # h: height of cell
        h = upper_b - lower_b

        # t: index of left most point of edge
        t = 0 if e0_x < e1_x else 1

        ## u, v, w = liniar tranfomation (system of equations) from 2D to 3D
        # mapping 2D domain to 3D range

        # c^2 - b^2 = a^2 => a = sqrt(c^2 - b^2)
        # a = sqrt((l * x)^2 - ((e1_y - e0_y) * x)^2)
        # u = a + et_x
        u = lambda x: math.sqrt((l*x)**2-((e1_y-e0_y)*x)**2)+ e[t][0]
        us = list(map(u, xs))

        # v = (et_x - et^_x) * x - et_y
        v = lambda x: (e[abs(t-1)][1] - e[t][1])*x + e[t][1]
        vs = list(map(v, xs))

        # w = y + lower
        w = lambda y: (y * h) + lower_b
        ws = list(map(w, ys))

        return us, vs, ws

    def __str__(self):
        str_ = f"Number of CB's: {len(self.cell_boundaries_3D)} \n\n"
        for id, cb in self.cell_boundaries_3D.items():
            str_ += f"{id}: {cb} \n"

        return str_
