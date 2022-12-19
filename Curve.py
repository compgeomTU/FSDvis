# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching Curve.py
#

import math, logging
from collections import OrderedDict

from traversalDistance.Graph import Graph

class Curve(Graph):
    vertex_dists: list

    def __init__(self, filename=None):
        super().__init__(filename)

        if not self.__isCurve():
            msg = f"Files are unsupported for {self.__class__.__name__}"
            raise TypeError(msg)
        else:
            self.compute_vertex_dists()

    def __isCurve(self):
        for i in range(len(self.edges)-1):
            if self.edges[i][1] != self.edges[i+1][0]:
                return False
        return True

    def compute_vertex_dists(self):
        self.vertex_dists = list([0.0])

        for id, edge in self.edges.items():
            n1_id, n2_id = edge[0], edge[1]
            n1, n2 = self.nodes[n1_id], self.nodes[n2_id]
            dist_ = math.dist([n1[0], n1[1]], [n2[0], n2[1]]) + self.vertex_dists[-1]
            self.vertex_dists.append(dist_)
