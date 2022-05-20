# Author: Will Rodman - Tulane University

import math

from FreeSpaceGraph import FreeSpaceGraph

class FreeSpace(FreeSpaceGraph):

    cell_boundaries_3D: dict

    def __init__(self, G, C, epsilon):
        super().__init__(G, C, epsilon)

    # e: edge of graph
    # l: lower bound of cells elevation
    # u: upper bound of cells elevation
    def transform(self, e, lower_b, upper_b):
        xs, ys = self.buildFreeSpace()

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
        string = """
                         {:04.2f}    {:04.2f}
                         ------------
                    {:04.2f}              {:04.2f}
                         |          |
                         |          |
                    {:04.2f}              {:04.2f}
                         ------------
                         {:04.2f}    {:04.2f}

                """

        format = string.format(0.0, 0.0, 0.0, 0.0,
                                0.0, 0.0, 0.0, 0.0)

        return format
