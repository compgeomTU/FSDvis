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

if __name__ == "__main__":

    graph_filename = str(sys.argv[1])
    curve_filename = str(sys.argv[2])

    ctg = GraphByCurve(graph_filename, curve_filename)
    figure_filename = None

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

    if '-e' in sys.argv:
        index = sys.argv.index('-e') + 1
        epsilon = float(sys.argv[index])
        logging.info(f"Epsilon: {epsilon}")
        ctg.buildCells()
        ctg.buildFreeSpace(epsilon)
        ctg.plotFreeSpace(figure_filename)
    else:
        ctg.plot(figure_filename)
