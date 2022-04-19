import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from Graph import Graph
from Curve import Curve

class CurveToGraph:

    __verticefile: str
    __edgefile: str
    __curvefile: str

    def __init__(self, verticefile, edgefile, curvefile):
        self.__verticefile = verticefile
        self.__edgefile = edgefile
        self.__curvefile = curvefile

    def plotGraphToCurve(self):
        plt.gca().set_aspect(1.0)
        g = Graph(self.__verticefile, self.__edgefile)
        c = Curve(self.__curvefile)
        c_x, c_y = c.x, c.y
        n = list()

        # building a graph
        for id, edge in g.edges.items():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = g.nodes[n1_id], g.nodes[n2_id]

            if n1 not in n:
                n.append(n1)
            if n2 not in n:
                n.append(n2)

            plt.plot([n1[0], n2[0]], [n1[1], n2[1]],
                    color='dimgray', linewidth=2)

        lons, lats = map(list, zip(*n))
        plt.scatter(lons, lats, s=75, c='dimgray')

        plt.plot([c_x[0], c_x[1]], [c_y[0], c_y[1]], '--', color='black', linewidth=3)
        for i in range(1, len(c_x)):
            plt.plot([c_x[i-1], c_x[i]], [c_y[i-1], c_y[i]], '--', color='black', linewidth=3)

        plt.show()


if __name__ == "__main__":

    ctg = CurveToGraph("sample_files/H_vertices.txt",
                        "sample_files/H_edges.txt",
                        "sample_files/H_curve.txt")
    ctg.plotGraphToCurve()
