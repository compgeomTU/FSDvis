# ext file in command line:
# python3 Visualizer.py

# Considering the way that planes are constructed using np.meshgrid,
# I have realized a solution to stitching ajacent planes together in matplotlib
# might by building the planes using equations in polar coods.
#
# These planes will be translated into rectangular coords before being plotted
# inorder to keep the general space in rectangular coords. Because of the
# limited precision of Floating Point numbers, translation from
# (r, 0, z) ~> (x, y, z) will force irrational numebers stored in trigometric
# funtions/pi notation to be tranclated to rational numbers.
#
# This facts is seemily irrevlevent consdering the NumPy engine must
# imput all values into the matplotlib engine using rectangular coords, however,
# this translation will cause coord points to diverge from their true orgin
# (there where problems finding duplicate points beccause of this is the
# Frechet lib).
#
# Once planes exits in general space, their free space can be plotted using
# liniar transformation functions such that (u, v, w) -> (x, y, z) for an
# ellipse (will actually be a polygon) planes cordionding cell plane.

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from Graph import Graph
from FreeSpaceCell import FreeSpaceCell


def graph_3d_plot():
    # build graph and then add z-axis to the matplotlib engine
    # paramitization will build verticies as cells
    # once graph is in 3d, example images can be transformed to the cell meshgrids

    # edges
    # e: dict of edge {e_n: (x_n, y_n)}
    e = {1: (1.5, 1.5, 0.5),
         2: (3.5, 4, 0.5),
         3: (4.5, 6, 1),
         4: (4.5, 10, 1.5),
         5: (8, 8, 2),
         6: (10, 13, 2),
         7: (9, 15, 3),
         }

    # verticies
    # v: list of edge pairs (e1 ,e2) that make up verticies
    v = [(1, 2), (2, 3), (3, 4), (3, 5), (4, 6), (5, 6), (4, 7)]

    ax = plt.gca(projection='3d')

    for i in v:
        x0 = e[i[0]][0]
        y0 = e[i[0]][1]
        z0 = e[i[0]][2]

        x1 = e[i[1]][0]
        y1 = e[i[1]][1]
        z1 = e[i[1]][2]

        ax.plot([x0, x1], [y0, y1], [z0, z1], color='blue', linewidth=3)

    mp = [[], [], []]

    for value, item in e.items():
        mp[0].append(item[0])
        mp[1].append(item[1])
        mp[2].append(item[2])

        ax.scatter(item[0], item[1], item[2], s=100, c='green')

    mp_x = sum(mp[0]) / len(e)
    mp_y = sum(mp[1]) / len(e)
    mp_z = sum(mp[2]) / len(e)

    ax.scatter(mp_x, mp_y, mp_z, s=200, c='red')

    plt.show()


def graph_2d_parameterization(file):
    g = Graph(file)
    ax = plt.gca(projection='3d')
    ax.grid(False)
    ax._axis3don = False

    for id, edge in g.edges.items():
        n1_id, n2_id = edge[0], edge[1]
        n1, n2 = g.nodes[n1_id], g.nodes[n2_id]

        xs = np.linspace(n1[0], n2[0], 10)
        zs = np.linspace(0, 1, 10)

        X, Z = np.meshgrid(xs, zs)
        Y = np.linspace(n1[1], n2[1], 10)
        ax.plot_surface(X, Y, Z, alpha=0.5, color='lightgray')

        cell = FreeSpaceCell.sampleFreeSpace()
        us, vs, ws = cell.build3DFreeSpace([n1, n2])
        verticies = [list(zip(us, vs, ws))]
        poly_cell = Poly3DCollection(verticies, alpha=1.0,facecolor='dimgray')
        ax.add_collection3d(poly_cell)

        #hack to change propotion of 3d projection
        alpha = 5
        yy_, zz_ = np.meshgrid([0], range(alpha))
        xx_ = yy_*0
        ax.plot_surface(xx_, yy_, zz_, alpha=0.0, color='white')

    xLabel = ax.set_xlabel('X')
    yLabel = ax.set_ylabel('Y')
    zLabel = ax.set_zlabel('Z')

    #plt.show()
    plt.savefig(f"{file}.svg")
    plt.close()

if __name__ == "__main__":
    graph_2d_parameterization('sample_graphs/R')
    # add
