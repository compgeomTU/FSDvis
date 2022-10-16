# python3 FreeSpaceCell.py

from math import sqrt

class FreeSpaceCell():

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

    def __init__(self, x0_s, x0_e, x1_s, x1_e,
                    y0_s, y0_e, y1_s, y1_e):
        self.__x0_s = x0_s
        self.__x0_e = x0_e
        self.__x1_s = x1_s
        self.__x1_e = x1_e
        self.__y0_s = y0_s
        self.__y0_e = y0_e
        self.__y1_s = y1_s
        self.__y1_e = y1_e

    @classmethod
    def fullFreeSpace(cls):
        x0_s = 0.0
        x0_e = 1.0
        x1_s = 0.0
        x1_e = 1.0
        y0_s = 0.0
        y0_e = 1.0
        y1_s = 0.0
        y1_e = 1.0

        return cls(x0_s, x0_e, x1_s, x1_e,
                    y0_s, y0_e, y1_s, y1_e)

    @classmethod
    def emptyFreeSpace(cls):
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

    @classmethod
    def sampleFreeSpace(cls):
        x0_s = 0.25000001
        x0_e = 0.75000002
        x1_s = 0.25000003
        x1_e = 0.75000004
        y0_s = 0.25000005
        y0_e = 0.75000006
        y1_s = 0.25000007
        y1_e = 0.75000008

        return cls(x0_s, x0_e, x1_s, x1_e,
                    y0_s, y0_e, y1_s, y1_e)

    def buildFreeSpace(self, precision=0.0001):
        xs = list()
        ys = list()

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

        if len(xs) < 3:
            xs = list()
            ys = list()

        return xs, ys

    def build3DFreeSpace(self, e):
        xs, ys = self.buildFreeSpace()

        # e: 2 3D coord points that define the edge
        e0_x, e0_y = e[0][0], e[0][1]
        e1_x, e1_y = e[1][0], e[1][1]

        # l: lenght of horizonal boundry of surface
        l = sqrt((e1_x-e0_x)**2+(e1_y-e0_y)**2)

        # t: index of left most point of edge
        t = 0 if e0_x < e1_x else 1

        ## u, v, w = liniar tranfomation (system of equations) from 2D to 3D
        # mapping 2D domain to 3D range

        # c^2 - b^2 = a^2 => a = sqrt(c^2 - b^2)
        # a = sqrt((l * x)^2 - ((e1_y - e0_y) * x)^2)
        # u = a + et_x
        u = lambda x: sqrt((l*x)**2-((e1_y-e0_y)*x)**2)+ e[t][0]
        us = list(map(u, xs))

        # v = (et_x - et^_x) * x - et_y
        v = lambda x: (e[abs(t-1)][1] - e[t][1])*x + e[t][1]
        vs = list(map(v, xs))

        # w = y
        w = lambda y: y
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

if __name__ == "__main__":
    pass
