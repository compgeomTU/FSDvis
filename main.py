# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching main.py

import sys, logging
from GraphByCurve import GraphByCurve
from traversalDistance.Graph import Graph
from Curve import Curve

if __name__ == "__main__":
    graph_filename = str(sys.argv[1])
    curve_filename = str(sys.argv[2])
    graph = Graph(graph_filename)
    curve = Curve(curve_filename)
    figure_filename, n_approximation = None, None

    if '-l' in sys.argv:
        index = sys.argv.index('-l') + 1
        log_filename = str(sys.argv[index])
        print(log_filename)
        logging.basicConfig(filename=log_filename,
                            format='%(asctime)s %(message)s',
                            level=logging.INFO,
                            filemode='w',
                            force=True)
        logging.info(f"Graph: {graph_filename} Curve: {curve_filename}")

    if '-f' in sys.argv:
        index = sys.argv.index('-f') + 1
        figure_filename = str(sys.argv[index])

    if '-n' in sys.argv:
        index = sys.argv.index('-n') + 1
        n_approximation = int(sys.argv[index])

    ctg = GraphByCurve(graph, curve, n_approximation)

    if '-a' in sys.argv:
        index = sys.argv.index('-a') + 1
        epsilon = float(sys.argv[index])
        ctg.buildFreeSpace(epsilon)
        area = ctg.calculateArea(epsilon)
        print("Free Space Area: ", area)

    if '-e' in sys.argv:
        index = sys.argv.index('-e') + 1
        epsilon = float(sys.argv[index])
        logging.info(f"Epsilon: {epsilon}")
        ctg.buildCells()
        ctg.buildFreeSpace(epsilon)
        ctg.plotFreeSpace(figure_filename)
    else:
        ctg.plot(figure_filename)
