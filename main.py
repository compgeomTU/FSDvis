# python3 main.py <CTG_SAMPLE_NO> <EPSILON>
# Example: python3 main.py 4 1.25

import sys, logging
from CurveToGraph import CurveToGraph

if __name__ == "__main__":
    logging.basicConfig(filename="main.log",
                        format='%(asctime)s %(message)s',
                        level=logging.INFO,
                        filemode='w')

    CTG_SAMPLE_NO = int(sys.argv[1])

    if CTG_SAMPLE_NO == 1:
        graphfile, curvefile = "sample_files/P", "sample_files/Q"

    elif CTG_SAMPLE_NO == 2:
        graphfile, curvefile = "sample_files/H", "sample_files/G"

    elif CTG_SAMPLE_NO == 3:
        graphfile, curvefile = "sample_files/arc_de_triomphe", "sample_files/vehicle_path"

    elif CTG_SAMPLE_NO == 4:
        graphfile, curvefile = "sample_files/A", "sample_files/B"

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
