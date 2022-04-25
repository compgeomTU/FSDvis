# Author: Dr. Carola Wenk - Tulane University
# Contributor: Emily Powers - Tulane University

import math

class FreeSpace():

    # bottom horizontal cell wall - free space start
    __x0_s: float

    # bottom horizontal cell wall - free space end
    __x0_e: float

    # top horizontal cell wall - free space start
    __x1_s: float

    # top horizontal cell wall - free space end
    __x1_e: float

    # left vertical cell wall - free space start
    __y0_s: float

    # left vertical cell wall - free space end
    __y0_e: float

    # right vertical cell wall - free space start
    __y1_s: float

    # right vertical cell wall - free space end
    __y1_e: float

    @classmethod
    def nullFreeSpace(cls):
        x0_s = -1.0
        x0_e = -1.0
        x1_s = -1.0
        x1_e = -1.0
        y0_s = -1.0
        y0_e = -1.0
        y1_s = -1.0
        y1_e = -1.0

        return cls(x0_s, x0_e, x1_s, x1_e,
                    y0_s, y0_e, y1_s, y1_e)


    #easier to rewrite calfreespace than to worry about the import since it's in C
    #(x1, y1) is starting point of edge of G1 (x2, y2) is ending point of edge of G1 (xa, ya) is vertex of G2
    #(start, end) will start as (0,1) and will return as the reachable boundary of free space on that edge as a value between 0-1
    def boundary(x1, y1, x2, y2, xa, ya, Epsilon):
        xdiff = x2 - x1
        ydiff = y2 - y1
        divisor = xdiff * xdiff + ydiff * ydiff
        if divisor == 0:
        print("divisor =", divisor, "x1 =", x1, "x2 =", x2, "y1 =", y1, "y2 =", y2)
        b = (xa-x1) * xdiff + (ya-y1) * ydiff
        q = (x1 * x1 + y1 * y1 + xa * xa + ya * ya - 2 * x1 * xa - 2 * y1 * ya - Epsilon * Epsilon) * divisor
        root = b * b - q
        if root < 0:
            start = end =- 1
            return (start, end)
        root = math.sqrt(root)
        t2 = (b + root) / divisor
        t1 = (b - root) / divisor
        if t1 < 0: t1 = 0
        if t2 < 0: t2 = 0
        if t1 > 1: t1 = 1
        if t2 > 1: t2 = 1
        start = t1
        end = t2
        if start == end:
            start -=1
            end -=1
        return (start, end)

    def build(self, precision=0.0001):
        xs, ys = list(), list()

        def addPoint(x, y):
            for x_, y_ in zip(xs, ys):
                if abs(x-x_) < precision and abs(y-y_) < precision: return

            xs.append(x)
            ys.append(y)

        if self.__x0_s != -1.0:
            x = self.__x0_s
            y = 0.0
            addPoint(x, y)

        if self.__x0_e != -1.0:
            x = self.__x0_e
            y = 0.0
            addPoint(x, y)

        if self.__y1_s != -1.0:
            x = 1.0
            y = self.__y1_s
            addPoint(x, y)

        if self.__y1_e != -1.0:
            x = 1.0
            y = self.__y1_e
            addPoint(x, y)

        if self.__x1_e != -1.0:
            x = self.__x1_e
            y = 1.0
            addPoint(x, y)

        if self.__x1_s != -1.0:
            x = self.__x1_s
            y = 1.0
            addPoint(x, y)

        if self.__y0_e != -1.0:
            x = 0.0
            y = self.__y0_e
            addPoint(x, y)

        if self.__y0_s != -1.0:
            x = 0.0
            y = self.__y0_s
            addPoint(x, y)

        # free space exsits in line, no sufrace space exsits and cannot be seen
        if len(xs) < 3:
            return list(), list()
        else:
            return xs, ys

    # e: edge of graph
    # l: lower bound of cells elevation
    # u: upper bound of cells elevation
    def transform(self, e, lower_b=0, upper_b=1):
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

        format = string.format(self.__x1_s, self.__x1_e,
                                self.__y0_e, self.__y1_e,
                                self.__y0_s, self.__y1_s,
                                self.__x0_s, self.__x0_e)

        return format
