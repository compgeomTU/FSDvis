import math

class Curve:

    xs: list
    ys: list
    edge_dists: list

    edge_count: int

    __filename: str

    def __init__(self, filename):
        self.__filename = filename
        self.xs, self.ys = list(), list()
        self.edges, self.edge_dists = list(), list()

        i: int
        for line in open(filename, "r"):
            coords = line.split()
            self.xs.append(float(coords[1]))
            self.ys.append(float(coords[2]))

            i = int(coords[0])

            if i > 0:
                edge = math.dist([self.xs[i-1], self.ys[i-1]],
                                [self.xs[i], self.ys[i]])
                dist = edge + self.edge_dists[i-1]
                self.edge_dists.append(dist)
            else:
                self.edge_dists.append(0)

        self.edge_count = i
