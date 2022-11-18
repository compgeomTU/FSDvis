# python3 main.py <graph_filename> <curve_filename> -e <epsilon> -f <figue_filename> -l <log_filename>
# Example: python3 main.py samples/A samples/B -e 1.5

# Sample Filenames:
#   graphfile, curvefile = samples/P samples/Q
#   graphfile, curvefile = samples/H samples/G
#   graphfile, curvefile = samples/arc_de_triomphe samples/vehicle_path
#   graphfile, curvefile = samples/A samples/B
#   graphfile, curvefile = samples/arc_de_triomphe_sub samples/vehicle_path_sub

import sys, logging
from CurveToGraph import CurveToGraph

if __name__ == "__main__":

    graph_filename = str(sys.argv[1])
    curve_filename = str(sys.argv[2])

    ctg = CurveToGraph(graph_filename, curve_filename)
    figure_filename = None

    if '-l' in sys.argv:
        index = sys.argv.index('-l') + 1
        log_filename = str(sys.argv[index])

        logging.basicConfig(filename=f"logs/{log_filename}",
                            format='%(asctime)s %(message)s',
                            level=logging.INFO,
                            filemode='w')
        logging.info(f"Graph: {graph_filename} Curve: {curve_filename}")

    if '-f' in sys.argv:
        global figure_filename
        index = sys.argv.index('-f') + 1
        figure_filepath = str(sys.argv[index])

    if '-e' in sys.argv:
        index = sys.argv.index('-e') + 1
        epsilon = float(sys.argv[index])
        logging.info(f"Epsilon: {epsilon}")
        ctg.buildCells()
        ctg.buildFreeSpace(epsilon)
        ctg.plotFreeSpace(figure_filename)
    else:
        ctg.plot(figure_filename)
