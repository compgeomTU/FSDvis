# python3 main.py <CTG_SAMPLE_NO> <EPSILON>
# Example: python3 main.py 4 1.25

import sys, logging
from CurveToGraph import CurveToGraph

if __name__ == "__main__":

    CTG_SAMPLE_NO = int(sys.argv[1])

    if CTG_SAMPLE_NO == 1:
        graphfile, curvefile = "samples/P", "samples/Q"

    elif CTG_SAMPLE_NO == 2:
        graphfile, curvefile = "samples/H", "samples/G"

    elif CTG_SAMPLE_NO == 3:
        graphfile, curvefile = "samples/arc_de_triomphe", "samples/vehicle_path"

    elif CTG_SAMPLE_NO == 4:
        graphfile, curvefile = "samples/A", "samples/B"

    logging.basicConfig(filename=f"logs/{CTG_SAMPLE_NO}.log",
                        format='%(asctime)s %(message)s',
                        level=logging.INFO,
                        filemode='w')
    logging.info(f"Graph: {graphfile} Curve: {curvefile}")
    ctg = CurveToGraph(graphfile, curvefile)

    if len(sys.argv) > 2:
        EPSILON = float(sys.argv[2])
        logging.info(f"Epsilon: {EPSILON}")
        ctg.buildCells()
        ctg.buildFreeSpace(EPSILON)
        ctg.plotFreeSpace()
    else:
        ctg.plot()
